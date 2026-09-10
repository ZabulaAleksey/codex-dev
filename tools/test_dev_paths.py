from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hooks.session_context import dev_integration_enabled

from tools.dev_paths import (
    BRIDGE_MARKER,
    PathResolutionError,
    inspect_project,
    migration_diagnostics,
    normalize_path_text,
    project_move_preflight,
    project_path,
    resolve_layout,
    _sanitize_remote,
)


class ResolverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary.name).resolve()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_defaults_are_the_accepted_layout(self) -> None:
        layout = resolve_layout(environ={}, user_home=self.home)
        self.assertEqual(self.home / "codex-dev", layout.dev_source_root)
        self.assertEqual(self.home / ".codex", layout.codex_home)
        self.assertEqual(self.home, layout.projects_root)
        self.assertEqual({"dev_source_root": "default", "codex_home": "default", "projects_root": "default"}, layout.source)

    def test_environment_overrides_all_roles(self) -> None:
        layout = resolve_layout(
            environ={
                "DEV_SOURCE_ROOT": "~/source",
                "CODEX_HOME": "~/runtime",
                "PROJECTS_ROOT": "~/products",
            },
            user_home=self.home,
        )
        self.assertEqual(self.home / "source", layout.dev_source_root)
        self.assertEqual(self.home / "runtime", layout.codex_home)
        self.assertEqual(self.home / "products", layout.projects_root)
        self.assertEqual({"dev_source_root": "env", "codex_home": "env", "projects_root": "env"}, layout.source)

    def test_local_config_is_fallback_but_environment_wins(self) -> None:
        config = self.home / ".codex" / "dev-layout.toml"
        config.parent.mkdir()
        config.write_text(
            '[paths]\ndev_source_root = "~/configured-source"\n'
            'codex_home = "~/configured-home"\nprojects_root = "~/configured-projects"\n',
            encoding="utf-8",
        )
        layout = resolve_layout(environ={"CODEX_HOME": "~/environment-home"}, user_home=self.home)
        self.assertEqual(self.home / "configured-source", layout.dev_source_root)
        self.assertEqual(self.home / "environment-home", layout.codex_home)
        self.assertEqual(self.home / "configured-projects", layout.projects_root)
        self.assertEqual("local_config", layout.source["dev_source_root"])
        self.assertEqual("env", layout.source["codex_home"])

    def test_windows_path_normalization_is_host_independent(self) -> None:
        value = normalize_path_text(r"~\products\one\..\two", user_home=r"C:\Users\Example", platform="nt")
        self.assertEqual(r"C:\Users\Example\products\two", value)

    def test_invalid_config_and_equal_source_destination_fail_closed(self) -> None:
        config = self.home / ".codex" / "dev-layout.toml"
        config.parent.mkdir()
        config.write_text("[paths]\nunknown = 'x'\n", encoding="utf-8")
        with self.assertRaises(PathResolutionError):
            resolve_layout(environ={}, user_home=self.home)
        config.unlink()
        with self.assertRaises(PathResolutionError):
            resolve_layout(
                environ={"DEV_SOURCE_ROOT": "~/same", "CODEX_HOME": "~/same"},
                user_home=self.home,
            )
        with self.assertRaises(PathResolutionError):
            resolve_layout(
                environ={"DEV_SOURCE_ROOT": "~/.codex/source", "CODEX_HOME": "~/.codex"},
                user_home=self.home,
            )

    def test_product_path_is_direct_child_and_rejects_escape(self) -> None:
        layout = resolve_layout(environ={}, user_home=self.home)
        self.assertEqual(self.home / "math-morph", project_path(layout, "math-morph"))
        for invalid in ("../escape", "nested/project", r"nested\project", ".."):
            with self.subTest(invalid=invalid), self.assertRaises(PathResolutionError):
                project_path(layout, invalid)


class ProjectIsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary.name).resolve()
        self.layout = resolve_layout(environ={}, user_home=self.home)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _repo(self, name: str) -> Path:
        root = self.home / name
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        return root

    def test_plain_repo_does_not_inherit_global_dev(self) -> None:
        state = inspect_project(self._repo("plain"), self.layout)
        self.assertTrue(state.exists)
        self.assertTrue(state.git_repo)
        self.assertEqual("disabled", state.dev_integration)
        self.assertEqual("none", state.bridge)

    def test_generic_agents_file_is_not_an_explicit_bridge(self) -> None:
        root = self._repo("generic-agents")
        (root / "AGENTS.md").write_text("# Local instructions\n", encoding="utf-8")
        self.assertEqual("disabled", inspect_project(root, self.layout).dev_integration)

    def test_canonical_agents_marker_enables_global_dev(self) -> None:
        root = self._repo("enabled")
        (root / "AGENTS.md").write_text(f"# Project overlay\n\n{BRIDGE_MARKER}\n", encoding="utf-8")
        state = inspect_project(root, self.layout)
        self.assertEqual("enabled", state.dev_integration)
        self.assertEqual("agents_marker", state.bridge)
        self.assertEqual(str(self.layout.dev_source_root), state.dev_source_root)

    def test_session_bootstrap_uses_the_same_bridge_gate(self) -> None:
        plain = self._repo("plain-hook")
        enabled = self._repo("enabled-hook")
        (enabled / "AGENTS.md").write_text(BRIDGE_MARKER + "\n", encoding="utf-8")
        with patch("hooks.session_context.resolve_layout", return_value=self.layout):
            self.assertFalse(dev_integration_enabled(plain))
            self.assertTrue(dev_integration_enabled(enabled))


class MigrationDiagnosticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary.name).resolve()
        self.layout = resolve_layout(environ={}, user_home=self.home)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _committed_repo(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
        (root / "README.md").write_text("fixture\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
        subprocess.run(
            ["git", "-C", str(root), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"],
            check=True,
        )

    def test_move_preflight_checks_git_state_and_collision(self) -> None:
        source = self.home / "codex-workspace" / "tutor"
        self._committed_repo(source)
        destination = self.home / "tutor"
        plan = project_move_preflight(source, destination)
        self.assertTrue(plan["safe"])
        for key in ("working_tree_clean", "branch", "remotes_checked", "nested_git_repositories", "additional_worktrees", "submodules_checked", "destination_collision"):
            self.assertIn(key, plan["checks"])
        destination.mkdir()
        self.assertFalse(project_move_preflight(source, destination)["safe"])

    def test_diagnostics_identify_old_layout_and_do_not_delete(self) -> None:
        old_source = self.home / "codex-workspace" / "codex-dev"
        old_product = self.home / "codex-workspace" / "tutor"
        self._committed_repo(old_source)
        self._committed_repo(old_product)
        diagnostic = migration_diagnostics(self.layout, user_home=self.home)
        self.assertIn(str(old_source.resolve()), diagnostic["old_source_detected"])
        self.assertEqual(str(old_product.resolve()), diagnostic["old_project_roots"][0]["source"])
        self.assertFalse(diagnostic["old_project_roots"][0]["deletion_or_archive_automatic"])
        self.assertTrue(old_source.exists())
        self.assertTrue(old_product.exists())

    def test_legacy_and_new_source_collision_fails_safe_result(self) -> None:
        self._committed_repo(self.home / "codex-workspace" / "codex-dev")
        self._committed_repo(self.home / "codex-dev")
        diagnostic = migration_diagnostics(self.layout, user_home=self.home)
        self.assertTrue(diagnostic["collisions"]["source"])
        self.assertFalse(diagnostic["safe"])

    def test_remote_sanitization_does_not_expose_credentials(self) -> None:
        sanitized = _sanitize_remote("https://token:secret@example.invalid/org/codex-dev.git?credential=x")
        self.assertEqual("https://example.invalid/org/codex-dev.git", sanitized)
        self.assertNotIn("secret", sanitized)


class RepositoryContractTests(unittest.TestCase):
    def test_active_surfaces_have_no_legacy_canonical_path(self) -> None:
        root = Path(__file__).resolve().parents[1]
        active = (
            "AGENTS.md",
            "README.md",
            "QUICKSTART.md",
            "docs/ARCHITECTURE.md",
            "docs/CONTEXT_POLICY.md",
            "docs/DEV_LAYOUT.md",
            "docs/PROJECT_FRAMEWORK.md",
            "docs/TEAM_ARCHITECTURE.md",
            "docs/VERIFY_SETUP.md",
            "docs/WORKFLOW.md",
            "rules/governance.md",
            "specs/system.spec.md",
            "specs/features/source-installed-layer.spec.md",
            "templates/AGENTS_PROJECT_TEMPLATE.md",
            "skill-sources/resume-project/SKILL.md",
        )
        for relative in active:
            with self.subTest(relative=relative):
                self.assertNotIn("codex-workspace", (root / relative).read_text(encoding="utf-8"))

    def test_continue_and_prompt_queue_contracts_use_resolver_and_bridge(self) -> None:
        root = Path(__file__).resolve().parents[1]
        resume = (root / "skill-sources/resume-project/SKILL.md").read_text(encoding="utf-8")
        queue = (root / "tools/prompt_queue.py").read_text(encoding="utf-8")
        hook = (root / "hooks/session_context.py").read_text(encoding="utf-8")
        self.assertIn("dev_paths.py project .", resume)
        self.assertIn("project_not_dev_enabled", queue)
        self.assertIn("dev_integration_enabled", hook)
        self.assertIn(BRIDGE_MARKER, (root / "templates/AGENTS_PROJECT_TEMPLATE.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
