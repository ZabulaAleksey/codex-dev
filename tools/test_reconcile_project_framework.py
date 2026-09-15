from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.reconcile_project_framework import (
    FRAMEWORK_FILES,
    capture_test_baseline,
    classify_project,
    compare_test_runs,
    dependency_inventory,
    reconcile_project,
)


class ReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        for relative in FRAMEWORK_FILES:
            target = self.workspace / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"canonical {relative}\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def make_project(self, *, files: dict[str, str] | None = None) -> Path:
        project = self.root / "project"
        project.mkdir()
        for relative, content in (files or {}).items():
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        subprocess.run(["git", "init", "--quiet", str(project)],
                       check=True, capture_output=True)
        return project

    def statuses(self, project: Path) -> dict[str, str]:
        report = reconcile_project(project, framework_root=self.workspace)
        return {entry.path: entry.status for entry in report.entries}

    def test_greenfield_is_classified_and_only_needs_framework_additions(self) -> None:
        project = self.make_project()
        report = reconcile_project(project, framework_root=self.workspace)
        self.assertEqual("GREENFIELD", report.classification)
        self.assertTrue(
            all(status == "ADD" for status in self.statuses(project).values()))

    def test_brownfield_clean_preserves_existing_product_file(self) -> None:
        project = self.make_project(files={"src/app.py": "print('product')\n"})
        report = reconcile_project(project, framework_root=self.workspace)
        self.assertEqual("BROWNFIELD", report.classification)
        self.assertEqual("FORBIDDEN_TO_OVERWRITE",
                         self.statuses(project)["src/app.py"])
        self.assertFalse(report.blocked)

    def test_brownfield_conflict_blocks_gate(self) -> None:
        project = self.make_project(
            files={".codex/rules/project.rules": "conflict\n"})
        report = reconcile_project(project, framework_root=self.workspace)
        self.assertEqual("CONFLICT", self.statuses(
            project)[".codex/rules/project.rules"])
        self.assertTrue(report.blocked)

    def test_resolved_conflict_does_not_block_gate(self) -> None:
        project = self.make_project(
            files={".codex/rules/project.rules": "conflict resolved\n"})
        report = reconcile_project(
            project,
            framework_root=self.workspace,
            resolved_conflicts={".codex/rules/project.rules"},
        )
        self.assertEqual(
            "ADAPT",
            {entry.path: entry.status for entry in report.entries}
            [".codex/rules/project.rules"],
        )
        self.assertFalse(report.blocked)

    def test_forbidden_overwrite_is_explicit(self) -> None:
        project = self.make_project(files={"README.md": "owned by project\n"})
        self.assertEqual("FORBIDDEN_TO_OVERWRITE",
                         self.statuses(project)["README.md"])

    def test_keep_and_legacy_execution_files_are_classified_for_merge(self) -> None:
        project = self.make_project(
            files={
                "AGENTS.md": (self.workspace / "AGENTS.md").read_text(encoding="utf-8"),
                "docs/AI_STATUS.md": "project status\n",
                "docs/progress.md": "legacy status\n",
            })
        statuses = self.statuses(project)
        self.assertEqual("KEEP", statuses["AGENTS.md"])
        self.assertEqual("MERGE", statuses["docs/AI_STATUS.md"])
        self.assertEqual("MERGE", statuses["docs/progress.md"])

    def test_pre_existing_failure_is_not_a_regression(self) -> None:
        baseline = capture_test_baseline(
            [sys.executable, "-c", "raise SystemExit(2)"], cwd=self.root)
        refreshed = capture_test_baseline(
            [sys.executable, "-c", "raise SystemExit(2)"], cwd=self.root)
        comparison = compare_test_runs(baseline, refreshed)
        self.assertTrue(comparison.pre_existing_failure)
        self.assertFalse(comparison.regression)

    def test_new_failure_after_refresh_is_regression(self) -> None:
        baseline = capture_test_baseline(
            [sys.executable, "-c", "pass"], cwd=self.root)
        refreshed = capture_test_baseline(
            [sys.executable, "-c", "raise SystemExit(1)"], cwd=self.root)
        self.assertTrue(compare_test_runs(baseline, refreshed).regression)

    def test_pre_existing_failure_is_reported_separately_from_new_failure(self) -> None:
        baseline = capture_test_baseline(
            [sys.executable, "-c", "print('FAIL: old_test')"], cwd=self.root)
        refreshed = capture_test_baseline(
            [sys.executable, "-c", "print('FAIL: old_test\\nFAIL: new_test')"], cwd=self.root)
        comparison = compare_test_runs(baseline, refreshed)
        self.assertEqual(("old_test",), comparison.baseline_failures)
        self.assertEqual(("new_test", "old_test"),
                         comparison.refreshed_failures)
        self.assertTrue(comparison.regression)

    def test_reconciliation_is_read_only_and_idempotent(self) -> None:
        project = self.make_project(files={"src/app.py": "product\n"})
        before = sorted(path.relative_to(project).as_posix()
                        for path in project.rglob("*") if path.is_file())
        first = reconcile_project(project, framework_root=self.workspace)
        second = reconcile_project(project, framework_root=self.workspace)
        after = sorted(path.relative_to(project).as_posix()
                       for path in project.rglob("*") if path.is_file())
        self.assertEqual(first, second)
        self.assertEqual(before, after)

    def test_retired_stages_is_preserved_for_semantic_merge(self) -> None:
        project = self.make_project(files={
            "prompts/STAGES.md": "- Stage ID: OLD-001\n\n## OLD-001\n- Status: partial\n- NEXT: OLD-001\n",
        })
        before = (project / "prompts/STAGES.md").read_bytes()
        report = reconcile_project(project, framework_root=self.workspace)
        entries = {entry.path: entry for entry in report.entries}
        self.assertEqual(entries["docs/STAGES.md"].status, "ADD")
        self.assertEqual(entries["prompts/STAGES.md"].status, "MERGE")
        self.assertEqual((project / "prompts/STAGES.md").read_bytes(), before)

    def test_dependency_inventory_reports_manager_and_drift(self) -> None:
        project = self.make_project(files={
            "package.json": '{"packageManager":"pnpm@9.0.0"}\n',
            "pnpm-lock.yaml": "lockfileVersion: '9.0'\n",
            "package-lock.json": "{}\n",
        })
        generated = project / "node_modules/pkg/index.js"
        generated.parent.mkdir(parents=True)
        generated.write_text("module.exports = {}\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(project), "add", "node_modules/pkg/index.js"], check=True)
        inventory = dependency_inventory(project)
        self.assertEqual("pnpm", inventory.manager)
        self.assertIn("package.json", inventory.manifests)
        self.assertIn("package-lock.json", inventory.lockfiles)
        self.assertIn("node_modules/pkg/index.js", inventory.tracked_generated_paths)
        self.assertIn("competing-node-lockfile", inventory.drift)
        self.assertIn("missing-dependency-contract", inventory.drift)

    def test_dependency_inventory_discovers_nested_multi_ecosystem_project(self) -> None:
        project = self.make_project(files={
            "apps/frontend/package.json": '{"packageManager":"pnpm@11.23.0"}\n',
            "apps/frontend/pnpm-lock.yaml": "lockfileVersion: '9.0'\n",
            "apps/backend/pyproject.toml": "[tool.uv]\n",
            "apps/backend/uv.lock": "version = 1\n",
            "go.mod": "module example.test/demo\n",
        })
        inventory = dependency_inventory(project)
        self.assertEqual("go-modules, pnpm, uv", inventory.manager)
        self.assertIn("apps/frontend/package.json", inventory.manifests)
        self.assertIn("apps/backend/uv.lock", inventory.lockfiles)
        self.assertIn("missing-dependency-contract", inventory.drift)


if __name__ == "__main__":
    unittest.main()
