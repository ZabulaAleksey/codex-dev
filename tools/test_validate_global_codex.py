from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.normalize_user_codex import ConcurrentConfigUpdateError, normalize_text, write_atomic
from tools.validate_global_codex import managed_files, validate_global_codex


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
            existing = home / "codex-workspace/projects/math-morph"
            existing.mkdir(parents=True)
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

[projects.'{home / "codex-workspace/projects/MathMorph"}']
trust_level = "trusted"

[projects.'{home}']
trust_level = "trusted"
'''
            normalized, changes = normalize_text(source, home)
            self.assertNotIn("synthetic-test-token", normalized)
            self.assertNotIn("NODE_REPL_TRUSTED_SERVICES", normalized)
            self.assertNotIn(f"[projects.'{home}']", normalized)
            self.assertIn("codex-workspace/math-morph", normalized.replace("\\", "/"))
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

    def test_drift_is_reported(self) -> None:
        (self.codex_home / "hooks/session_context.py").write_text("drift\n", encoding="utf-8")
        self.assertIn("managed-file-drift", self.issue_codes())

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
            (repo / ".git").mkdir()
            (repo / "docs").mkdir()
            (repo / "docs/AI_STATUS.md").write_text("Статус → готово\n", encoding="utf-8")
            result = self.run_session_hook(repo)
            output = json.loads(result.stdout.decode("utf-8"))
            self.assertIn("Статус → готово", output["hookSpecificOutput"]["additionalContext"])

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
                (repo / "docs/AI_STATUS.md").symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")
            result = self.run_session_hook(repo)
            self.assertNotIn(b"DO-NOT-EXPOSE", result.stdout)

    def test_session_hook_bounds_large_file_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            (repo / ".git").mkdir()
            (repo / "docs").mkdir()
            (repo / "docs/AI_STATUS.md").write_text("x" * 1_000_000, encoding="utf-8")
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
