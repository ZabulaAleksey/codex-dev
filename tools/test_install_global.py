from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.install_global import (
    InstallError,
    LEDGER_NAME,
    LOCK_NAME,
    TRANSACTION_DIRECTORY,
    apply_install_plan,
    build_install_plan,
    install,
    load_install_policy,
    render_plan,
)


class GlobalInstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "workspace" / "codex-dev"
        self.codex_home = self.root / "home" / ".codex"
        self.skills = self.root / "home" / ".agents" / "skills"
        self.source.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(self.source)], check=True)
        (self.source / "tools").mkdir()
        shutil.copy2(Path(__file__).with_name("sync_global_skills.py"), self.source / "tools" / "sync_global_skills.py")
        self.write_source("AGENTS.md", "router-v1\n")
        self.write_source("rules/global.md", "rule-v1\n")
        self.write_source("skill-sources/example/SKILL.md", "skill-v1\n")
        self.write_manifest(
            "AGENTS.md",
            "MANIFEST.txt",
            "rules/global.md",
            "skill-sources/example/SKILL.md",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_source(self, relative: str, content: str) -> None:
        target = self.source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def write_manifest(self, *entries: str) -> None:
        (self.source / "MANIFEST.txt").write_text("\n".join(entries) + "\n", encoding="utf-8")

    def policy(self):
        return load_install_policy(self.source)

    def apply(self):
        plan = build_install_plan(self.policy(), self.codex_home)
        transaction = apply_install_plan(plan, self.codex_home)
        transaction.finalize()
        return plan

    @staticmethod
    def no_op_runner(_command: list[str]) -> None:
        return None

    def test_source_repository_outside_codex_home_is_allowed(self) -> None:
        plan = install(self.source, self.codex_home, self.skills, dry_run=True, runner=self.no_op_runner)
        self.assertNotEqual(self.source.resolve(), self.codex_home.resolve())
        self.assertTrue(any(action.kind == "create" for action in plan.actions))

    def test_destination_git_repository_is_rejected(self) -> None:
        (self.codex_home / ".git").mkdir(parents=True)
        with self.assertRaisesRegex(InstallError, "must not be a Git"):
            install(self.source, self.codex_home, self.skills, dry_run=True, runner=self.no_op_runner)

    def test_existing_install_lock_fails_closed(self) -> None:
        self.codex_home.mkdir(parents=True)
        (self.codex_home / LOCK_NAME).write_text("existing\n", encoding="ascii")
        with self.assertRaisesRegex(InstallError, "install lock"):
            install(self.source, self.codex_home, self.skills, runner=self.no_op_runner)
        self.assertFalse((self.codex_home / "AGENTS.md").exists())

    def test_pending_recovery_transaction_blocks_new_install(self) -> None:
        pending = self.codex_home / TRANSACTION_DIRECTORY / "interrupted"
        pending.mkdir(parents=True)
        (pending / "journal.json").write_text('{"status":"prepared"}\n', encoding="utf-8")
        with self.assertRaisesRegex(InstallError, "recovery data"):
            install(self.source, self.codex_home, self.skills, runner=self.no_op_runner)
        self.assertTrue((pending / "journal.json").is_file())

    def test_install_into_populated_codex_home_preserves_runtime_files(self) -> None:
        self.codex_home.mkdir(parents=True)
        protected = {
            "auth.json": "synthetic-auth\n",
            "config.toml": "[features]\nhooks = true\n",
            "sessions/current.jsonl": "session\n",
            "cache/item": "cache\n",
            "plugins/plugin/state": "plugin\n",
        }
        for relative, content in protected.items():
            target = self.codex_home / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        before = {relative: (self.codex_home / relative).read_bytes() for relative in protected}

        plan = self.apply()

        self.assertEqual(before, {relative: (self.codex_home / relative).read_bytes() for relative in protected})
        output = render_plan(plan)
        self.assertIn("[protected runtime skip] auth.json", output)
        self.assertIn("[protected runtime skip] sessions", output)

    def test_manifest_only_copying_excludes_unlisted_and_skill_sources(self) -> None:
        self.write_source("unlisted.txt", "do-not-copy\n")
        self.apply()
        self.assertTrue((self.codex_home / "AGENTS.md").is_file())
        self.assertFalse((self.codex_home / "unlisted.txt").exists())
        self.assertFalse((self.codex_home / "skill-sources").exists())

    def test_stale_managed_file_is_removed_only_from_ledger(self) -> None:
        self.write_source("old.txt", "old\n")
        self.write_manifest("AGENTS.md", "MANIFEST.txt", "old.txt", "skill-sources/example/SKILL.md")
        self.apply()
        self.assertTrue((self.codex_home / "old.txt").exists())

        self.write_manifest("AGENTS.md", "MANIFEST.txt", "skill-sources/example/SKILL.md")
        plan = self.apply()

        self.assertFalse((self.codex_home / "old.txt").exists())
        self.assertIn(("delete", "old.txt"), {(action.kind, action.path) for action in plan.actions})

    def test_unknown_destination_file_is_preserved(self) -> None:
        self.codex_home.mkdir(parents=True)
        unknown = self.codex_home / "user-note.txt"
        unknown.write_text("keep\n", encoding="utf-8")
        self.apply()
        self.assertEqual("keep\n", unknown.read_text(encoding="utf-8"))

    def test_unknown_collision_is_reported_without_overwrite(self) -> None:
        self.codex_home.mkdir(parents=True)
        target = self.codex_home / "AGENTS.md"
        target.write_text("local-unknown\n", encoding="utf-8")
        plan = build_install_plan(self.policy(), self.codex_home)
        self.assertEqual("conflict", next(action.kind for action in plan.actions if action.path == "AGENTS.md"))
        with self.assertRaises(InstallError):
            apply_install_plan(plan, self.codex_home)
        self.assertEqual("local-unknown\n", target.read_text(encoding="utf-8"))

    def test_manifest_collision_with_protected_runtime_path_fails_closed(self) -> None:
        for relative in ("config.toml", "state_5.sqlite", "skills/runtime/SKILL.md", "rules/default.rules"):
            with self.subTest(relative=relative):
                self.write_source(relative, "unsafe\n")
                self.write_manifest("AGENTS.md", "MANIFEST.txt", relative)
                with self.assertRaisesRegex(InstallError, "protected runtime"):
                    self.policy()
        self.assertFalse(self.codex_home.exists())

    def test_skills_materialize_through_existing_sync_tool(self) -> None:
        calls: list[list[str]] = []

        def runner(command: list[str]) -> None:
            calls.append(command)
            if command[-1] == "--apply":
                subprocess.run(command, check=True)

        self.codex_home.mkdir(parents=True)
        (self.codex_home / "config.toml").write_text(
            "[shell_environment_policy]\nignore_default_excludes = false\n", encoding="utf-8"
        )
        install(self.source, self.codex_home, self.skills, runner=runner)
        self.assertEqual("skill-v1\n", (self.skills / "example" / "SKILL.md").read_text(encoding="utf-8"))
        self.assertTrue(any("sync_global_skills.py" in " ".join(command) for command in calls))

    def test_dry_run_changes_nothing(self) -> None:
        self.codex_home.mkdir(parents=True)
        marker = self.codex_home / "auth.json"
        marker.write_text("keep\n", encoding="utf-8")
        before = {path.relative_to(self.root).as_posix(): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        install(self.source, self.codex_home, self.skills, dry_run=True, runner=self.no_op_runner)
        after = {path.relative_to(self.root).as_posix(): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_failed_install_rolls_back_managed_files_and_ledger(self) -> None:
        self.apply()
        old_file = (self.codex_home / "AGENTS.md").read_bytes()
        old_ledger = (self.codex_home / LEDGER_NAME).read_bytes()
        self.write_source("AGENTS.md", "router-v2\n")
        plan = build_install_plan(self.policy(), self.codex_home)

        with patch("tools.install_global._write_atomic", side_effect=InstallError("injected failure")):
            with self.assertRaises(InstallError):
                apply_install_plan(plan, self.codex_home)

        self.assertEqual(old_file, (self.codex_home / "AGENTS.md").read_bytes())
        self.assertEqual(old_ledger, (self.codex_home / LEDGER_NAME).read_bytes())

    def test_validation_runs_after_apply_and_repeats_after_skills(self) -> None:
        calls: list[list[str]] = []

        def runner(command: list[str]) -> None:
            if calls:
                self.assertTrue((self.codex_home / "AGENTS.md").is_file())
            calls.append(command)

        install(self.source, self.codex_home, self.skills, runner=runner)
        names = [Path(command[2]).name for command in calls]
        self.assertEqual(
            [
                "validate_context.py",
                "validate_context.py",
                "validate_global_codex.py",
                "sync_global_skills.py",
                "validate_context.py",
                "validate_global_codex.py",
            ],
            names,
        )
        self.assertIn("--skip-skills", calls[2])
        self.assertNotIn("--skip-skills", calls[5])

    def test_second_install_is_idempotent(self) -> None:
        install(self.source, self.codex_home, self.skills, runner=self.no_op_runner)
        ledger = self.codex_home / LEDGER_NAME
        before_bytes = ledger.read_bytes()
        before_mtime = ledger.stat().st_mtime_ns
        plan = install(self.source, self.codex_home, self.skills, runner=self.no_op_runner)
        self.assertFalse(plan.changes)
        self.assertEqual("unchanged", plan.ledger_action)
        self.assertEqual(before_bytes, ledger.read_bytes())
        self.assertEqual(before_mtime, ledger.stat().st_mtime_ns)

    def test_source_update_changes_only_managed_artifacts(self) -> None:
        self.apply()
        unknown = self.codex_home / "device-local.json"
        unknown.write_text("local\n", encoding="utf-8")
        runtime = self.codex_home / "sessions" / "one.jsonl"
        runtime.parent.mkdir()
        runtime.write_text("session\n", encoding="utf-8")
        self.write_source("AGENTS.md", "router-after-pull\n")
        self.write_source("not-in-manifest.txt", "ignored\n")

        plan = self.apply()

        changed = {(action.kind, action.path) for action in plan.actions if action.kind in {"create", "update", "delete"}}
        self.assertEqual({("update", "AGENTS.md")}, changed)
        self.assertEqual("local\n", unknown.read_text(encoding="utf-8"))
        self.assertEqual("session\n", runtime.read_text(encoding="utf-8"))
        self.assertFalse((self.codex_home / "not-in-manifest.txt").exists())

    def test_ledger_is_deterministic_and_contains_no_source_path(self) -> None:
        self.apply()
        raw = json.loads((self.codex_home / LEDGER_NAME).read_text(encoding="utf-8"))
        self.assertEqual(1, raw["schema_version"])
        self.assertNotIn(str(self.source), json.dumps(raw))
        self.assertEqual(sorted(item["path"] for item in raw["files"]), [item["path"] for item in raw["files"]])


if __name__ == "__main__":
    unittest.main()
