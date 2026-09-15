from __future__ import annotations

import hashlib
import io
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.stage_compatibility import stage_routing_snapshot

from tools.normalize_user_codex import ConcurrentConfigUpdateError, normalize_text, write_atomic
from tools.validate_global_codex import (
    documentation_layout_issues,
    managed_files,
    skill_registry_issues,
    validate_global_codex,
)
from tools.install_global import LEDGER_NAME, ledger_bytes, load_install_policy


ROOT = Path(__file__).resolve().parents[1]
SESSION_HOOK = ROOT / "hooks/session_context.py"
GUARD_HOOK = ROOT / "hooks/guard_destructive.py"


def load_session_hook_module():
    spec = importlib.util.spec_from_file_location("session_context_hook", SESSION_HOOK)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load session hook module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UserConfigNormalizerTests(unittest.TestCase):
    def test_normalizer_removes_secret_and_stale_routes_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            stale = home / "codex-workspace/projects/ExampleProject"
            stale.mkdir(parents=True)
            source = f'''[mcp_servers.node_repl.env]
NODE_REPL_TRUSTED_SERVICES = '{{"browser":"{(home / "missing/service.mjs").as_posix()}"}}'

[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp", "--api-key", "synthetic-test-token"]

[mcp_servers.github]
url = "https://example.invalid"

[mcp_servers.atlassian]
url = "https://example.invalid"

[plugins."google-calendar@openai-curated"]
enabled = true

[plugins."slack@openai-curated"]
enabled = true

[projects.'{stale}']
trust_level = "trusted"

[projects.'{home}']
trust_level = "trusted"
'''
            normalized, changes = normalize_text(source, home)
            self.assertNotIn("synthetic-test-token", normalized)
            self.assertNotIn("NODE_REPL_TRUSTED_SERVICES", normalized)
            self.assertNotIn(f"[projects.'{home}']", normalized)
            self.assertNotIn("ExampleProject", normalized)
            self.assertNotIn("codex-workspace/projects/", normalized.replace("\\", "/"))
            self.assertIn("ignore_default_excludes = false", normalized)
            self.assertIn("@upstash/context7-mcp@4.0.2", normalized)
            self.assertIn("remove-context7-inline-key", changes)
            second, second_changes = normalize_text(normalized, home)
            self.assertEqual(normalized, second)
            self.assertEqual([], second_changes)

    def test_atomic_write_refuses_concurrent_config_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "config.toml"
            original = b'[features]\nhooks = true\n'
            target.write_bytes(original)
            expected = hashlib.sha256(original).hexdigest()
            target.write_text('[features]\nhooks = false\n', encoding="utf-8")
            with self.assertRaises(ConcurrentConfigUpdateError):
                write_atomic(target, '[features]\nhooks = true\n', expected)
            self.assertIn("hooks = false", target.read_text(encoding="utf-8"))

    def test_normalizer_preserves_existing_browser_service(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            service = home / "browser-service.mjs"
            service.write_text("// verified test service\n", encoding="utf-8")
            source = f'''[mcp_servers.node_repl.env]
NODE_REPL_TRUSTED_SERVICES = '{{"browser":"{service.as_posix()}"}}'

[mcp_servers.context7]
args = ["-y", "@upstash/context7-mcp@4.0.2"]

[mcp_servers.github]
enabled = false

[mcp_servers.atlassian]
enabled = false

[plugins."google-calendar@openai-curated"]
enabled = false

[plugins."slack@openai-curated"]
enabled = false

[shell_environment_policy]
ignore_default_excludes = false
'''
            normalized, changes = normalize_text(source, home)
            self.assertIn(service.as_posix(), normalized)
            self.assertNotIn("remove-missing-browser-service", changes)


class GlobalCodexValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary.name)
        self.codex_home = self.home / ".codex"
        self.codex_home.mkdir()
        self.runtime_skills = self.home / ".agents" / "skills"
        self.runtime_skills.mkdir(parents=True)
        for source in managed_files(ROOT):
            relative = source.relative_to(ROOT)
            destination = self.codex_home / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        (self.codex_home / LEDGER_NAME).write_bytes(ledger_bytes(load_install_policy(ROOT)))
        for source in (ROOT / "skill-sources").iterdir():
            if source.is_dir():
                shutil.copytree(source, self.runtime_skills / source.name)
        project = self.home / "project"
        project.mkdir()
        (self.codex_home / "config.toml").write_text(
            f'''[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp@4.0.2"]

[shell_environment_policy]
ignore_default_excludes = false

[projects.'{project}']
trust_level = "trusted"
''',
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def issue_codes(self) -> set[str]:
        return {issue.code for issue in validate_global_codex(ROOT, self.codex_home)}

    def test_clean_installed_layer_passes(self) -> None:
        self.assertEqual(set(), self.issue_codes())

    def test_missing_document_layout_policy_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            (workspace / "AGENTS.md").write_text("docs/notes/<topic>.md\n", encoding="utf-8")
            issues = documentation_layout_issues(workspace)
            self.assertIn("missing-document-layout-policy", {issue.code for issue in issues})

    def test_optional_skill_registry_is_validated_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            registry = workspace / "skill-sources" / "registry.toml"
            registry.parent.mkdir(parents=True)
            registry.write_text("schema_version = 99\nskills = []\n", encoding="utf-8")
            issues = skill_registry_issues(workspace)
            self.assertEqual({"invalid-skill-registry"}, {issue.code for issue in issues})

    def test_absent_skill_registry_preserves_legacy_workspace_compatibility(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual((), skill_registry_issues(Path(temporary)))

    def test_drift_is_reported(self) -> None:
        (self.codex_home / "hooks/session_context.py").write_text("drift\n", encoding="utf-8")
        self.assertIn("managed-file-drift", self.issue_codes())

    def test_missing_ownership_ledger_is_reported(self) -> None:
        (self.codex_home / LEDGER_NAME).unlink()
        self.assertIn("missing-install-ledger", self.issue_codes())

    def test_installed_codex_home_git_metadata_is_reported(self) -> None:
        (self.codex_home / ".git").mkdir()
        self.assertIn("installed-home-is-git", self.issue_codes())

    def test_pre_skill_validation_can_skip_runtime_skill_parity(self) -> None:
        shutil.rmtree(self.runtime_skills)
        issues = validate_global_codex(ROOT, self.codex_home, validate_skills=False)
        self.assertNotIn("missing-runtime-skill", {issue.code for issue in issues})

    def test_runtime_skill_drift_is_reported(self) -> None:
        skill = next(path for path in self.runtime_skills.iterdir() if path.is_dir())
        (skill / "SKILL.md").write_text("drift\n", encoding="utf-8")
        self.assertIn("runtime-skill-drift", self.issue_codes())

    def test_inline_credential_is_reported_without_value(self) -> None:
        config = self.codex_home / "config.toml"
        config.write_text(
            '[mcp_servers.context7]\nargs = ["--api-key", "synthetic-secret-value"]\n',
            encoding="utf-8",
        )
        issues = validate_global_codex(ROOT, self.codex_home)
        self.assertIn("inline-context7-credential", {issue.code for issue in issues})
        self.assertNotIn("synthetic-secret-value", repr(issues))

    def test_invalid_trusted_services_json_is_reported(self) -> None:
        config = self.codex_home / "config.toml"
        config.write_text(
            '''[mcp_servers.context7]
args = ["-y", "@upstash/context7-mcp@4.0.2"]

[mcp_servers.node_repl.env]
NODE_REPL_TRUSTED_SERVICES = "not-json"

[shell_environment_policy]
ignore_default_excludes = false
''',
            encoding="utf-8",
        )
        self.assertIn("invalid-trusted-services", self.issue_codes())

    def test_invalid_mcp_table_shape_is_reported(self) -> None:
        config = self.codex_home / "config.toml"
        config.write_text('[mcp_servers]\ncontext7 = "not-a-table"\n', encoding="utf-8")
        self.assertIn("invalid-config-structure", self.issue_codes())


class HookRegressionTests(unittest.TestCase):
    def test_repository_containment_rejects_outside_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            repo = base / "repo"
            repo.mkdir()
            outside = base / "outside.txt"
            outside.write_text("outside", encoding="utf-8")
            module = load_session_hook_module()
            self.assertFalse(module.is_within_repo(repo, outside))

    def run_session_hook(self, repo: Path) -> subprocess.CompletedProcess[bytes]:
        payload = json.dumps({"cwd": str(repo), "hook_event_name": "SessionStart"}).encode("utf-8")
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "cp1251"
        return subprocess.run([sys.executable, str(SESSION_HOOK)], input=payload, capture_output=True, env=env, check=True)

    def test_session_hook_emits_utf8_under_legacy_windows_encoding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "AGENTS.md").write_text("Global DEV bridge: enabled\n", encoding="utf-8")
            marker = repo / ".codex/dev-project.toml"
            marker.parent.mkdir(parents=True)
            marker.write_text('schema_version = 1\n\n[dev]\nmanaged = true\nrequires_global_dev = true\nminimum_version = "2026.09.10"\nrequired_capabilities = ["stage-router-v1"]\nrequired_contract_schema = 1\n', encoding="utf-8")
            (repo / "docs").mkdir()
            (repo / "docs/STAGES.md").write_text(
                "- Stage ID: `STAGE-001`\n\n## STAGE-001\n\n"
                "- Status: planned\n- NEXT: STAGE-001\n\nСтатус → готово\n",
                encoding="utf-8",
            )
            result = self.run_session_hook(repo)
            output = json.loads(result.stdout.decode("utf-8"))
            self.assertIn("Статус → готово", output["hookSpecificOutput"]["additionalContext"])

    def test_session_hook_consumes_the_authorized_record_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "AGENTS.md").write_text("Global DEV bridge: enabled\n", encoding="utf-8")
            marker = repo / ".codex/dev-project.toml"
            marker.parent.mkdir(parents=True)
            marker.write_text('schema_version = 1\n\n[dev]\nmanaged = true\nrequires_global_dev = true\nminimum_version = "2026.09.10"\nrequired_capabilities = ["stage-router-v1"]\nrequired_contract_schema = 1\n', encoding="utf-8")
            (repo / "docs").mkdir()
            stages = repo / "docs/STAGES.md"
            stages.write_text(
                "- Stage ID: STAGE-001\n\n## STAGE-001\n\n- Status: planned\n"
                "- NEXT: STAGE-001\n\nORIGINAL-SNAPSHOT\n", encoding="utf-8"
            )
            routing, record = stage_routing_snapshot(repo)
            module = load_session_hook_module()

            def drift(_root):
                stages.write_text(
                    "- Stage ID: OTHER\n\n## OTHER\n\n- Status: planned\n- NEXT: OTHER\n"
                    "MUTATED-STATE\n", encoding="utf-8"
                )
                return routing, record

            payload = json.dumps({"cwd": str(repo), "hook_event_name": "SessionStart"})
            output = io.StringIO()
            with patch.object(module, "stage_routing_snapshot", side_effect=drift), \
                    patch("sys.stdin", io.StringIO(payload)), redirect_stdout(output):
                module.main()
            context = json.loads(output.getvalue())["hookSpecificOutput"]["additionalContext"]
            self.assertIn("ORIGINAL-SNAPSHOT", context)
            self.assertNotIn("MUTATED-STATE", context)

    def test_session_hook_skips_symlink_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repo = base / "repo"
            repo.mkdir()
            (repo / ".git").mkdir()
            (repo / "docs").mkdir()
            outside = base / "outside.txt"
            outside.write_text("DO-NOT-EXPOSE", encoding="utf-8")
            try:
                (repo / "docs/STAGES.md").symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")
            result = self.run_session_hook(repo)
            self.assertNotIn(b"DO-NOT-EXPOSE", result.stdout)

    def test_session_hook_bounds_large_file_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            (repo / ".git").mkdir()
            (repo / "docs").mkdir()
            (repo / "docs/STAGES.md").write_text("x" * 1_000_000, encoding="utf-8")
            result = self.run_session_hook(repo)
            self.assertLess(len(result.stdout), 12_000)

    def test_destructive_guard_denies_hard_reset(self) -> None:
        payload = json.dumps({"tool_input": {"command": "git reset --hard HEAD"}}).encode("utf-8")
        result = subprocess.run([sys.executable, str(GUARD_HOOK)], input=payload, capture_output=True, check=True)
        output = json.loads(result.stdout.decode("utf-8"))
        self.assertEqual("deny", output["hookSpecificOutput"]["permissionDecision"])

    def test_destructive_guard_covers_windows_and_flag_variants(self) -> None:
        commands = (
            'git.exe -C "C:\\work tree" reset --hard HEAD',
            "git clean -fdx",
            "git clean -d -f -x",
            "git clean --force -d -x",
            'git.exe -C "C:\\work tree" clean -n -f',
            "Remove-Item -LiteralPath 'C:\\' -Force -Recurse",
            "rm -fr /",
            "git push --force-with-lease origin main",
            "git push --force; echo ok",
            "git push --force&&echo ok",
            'git -C "C:\\work tree" push --force-with-lease',
        )
        for command in commands:
            with self.subTest(command=command):
                payload = json.dumps({"tool_input": {"command": command}}).encode("utf-8")
                result = subprocess.run([sys.executable, str(GUARD_HOOK)], input=payload, capture_output=True, check=True)
                output = json.loads(result.stdout.decode("utf-8"))
                self.assertEqual("deny", output["hookSpecificOutput"]["permissionDecision"])

    def test_destructive_guard_allows_git_clean_dry_run(self) -> None:
        payload = json.dumps({"tool_input": {"command": "git clean -n -d -x"}}).encode("utf-8")
        result = subprocess.run([sys.executable, str(GUARD_HOOK)], input=payload, capture_output=True, check=True)
        self.assertEqual(b"", result.stdout)


if __name__ == "__main__":
    unittest.main()
