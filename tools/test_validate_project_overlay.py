from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.validate_project_overlay import validate_project


REQUIRED_CONTENT = {
    "AGENTS.md": "# Project router\n",
    "prompts/STAGES.md": "# Stage 001\n\n## Status\nPLANNED\n",
    "docs/ARCHITECTURE.md": "# Architecture\n",
    "docs/DECISIONS.md": "# Decisions\n",
    "docs/LEARNING_LOG.md": "# Learning log\n",
    "docs/project-context.md": "# Project context\n",
    "docs/ROADMAP.md": "# Roadmap\n",
    "docs/AI_PLAN.md": "# Current plan\n",
    "docs/AI_STATUS.md": "# Current status\n",
}


class ProjectOverlayValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        canonical = self.workspace / "agents/reviewer.toml"
        canonical.parent.mkdir(parents=True)
        canonical.write_text('name = "reviewer"\n', encoding="utf-8")
        workflow = self.workspace / "docs/WORKFLOW.md"
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text("# Global workflow\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def make_project(self, name: str = "project", *, git: bool = True) -> Path:
        project = self.root / name
        project.mkdir()
        for relative, content in REQUIRED_CONTENT.items():
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        if git:
            subprocess.run(["git", "init", "--quiet", str(project)], check=True, capture_output=True)
        return project

    def issue_codes(self, project: Path) -> set[str]:
        result = validate_project(project, self.workspace)
        return {issue.code for issue in result.issues}

    def document_dependencies(self, project: Path) -> None:
        (project / "docs/DEPENDENCIES.md").write_text(
            "# Dependencies\n\n## Source of truth\nmanifest + lockfile\n\n## Clean restore\ncanonical manager install\n",
            encoding="utf-8",
        )

    def test_complete_overlay_passes(self) -> None:
        result = validate_project(self.make_project(), self.workspace)
        self.assertTrue(result.ok)
        self.assertEqual((), result.issues)

    def test_incomplete_overlay_reports_missing_files_and_alternate_status(self) -> None:
        project = self.make_project()
        (project / "docs/AI_PLAN.md").unlink()
        (project / "docs/PROGRESS.md").write_text("old status\n", encoding="utf-8")
        result = validate_project(project, self.workspace)
        self.assertFalse(result.ok)
        self.assertIn("missing-required-file", self.issue_codes(project))
        self.assertIn("alternate-status-file", self.issue_codes(project))

    def test_legacy_stage_file_and_stale_workspace_path_are_reported(self) -> None:
        project = self.make_project()
        (project / "prompts/01-old-stage.md").write_text("cd ~/codex-workspace/projects/project\n", encoding="utf-8")
        codes = self.issue_codes(project)
        self.assertIn("legacy-stage-file", codes)
        self.assertIn("stale-workspace-path", codes)

    def test_generated_build_tree_is_not_scanned_for_machine_paths(self) -> None:
        project = self.make_project()
        generated = project / ".next/types/app/page.ts"
        generated.parent.mkdir(parents=True)
        generated.write_text(
            r'export const source = "C:\Users\example\codex-workspace\projects\project";\n',
            encoding="utf-8",
        )
        codes = self.issue_codes(project)
        self.assertNotIn("machine-specific-workspace-path", codes)
        self.assertNotIn("stale-workspace-path", codes)

    def test_exact_global_duplicate_is_rejected_even_with_audit(self) -> None:
        project = self.make_project()
        duplicate = project / ".codex/agents/reviewer.toml"
        duplicate.parent.mkdir(parents=True)
        duplicate.write_text('name = "reviewer"\n', encoding="utf-8")
        audit = project / "docs/CONTEXT_COMPATIBILITY.md"
        audit.write_text("| Capability | Status |\n|---|---|\n| Reviewer extension | `EXTEND` |\n", encoding="utf-8")
        self.assertIn("exact-global-duplicate", self.issue_codes(project))

    def test_exact_global_workflow_duplicate_is_rejected(self) -> None:
        project = self.make_project()
        workflow = project / "docs/WORKFLOW.md"
        workflow.write_text("# Global workflow\n", encoding="utf-8")
        audit = project / "docs/CONTEXT_COMPATIBILITY.md"
        audit.write_text("| Capability | Status |\n|---|---|\n| Git workflow | `EXTEND` |\n", encoding="utf-8")
        self.assertIn("exact-global-duplicate", self.issue_codes(project))

    def test_non_git_directory_is_rejected(self) -> None:
        project = self.make_project(git=False)
        self.assertIn("not-git-root", self.issue_codes(project))

    def test_repeated_validation_is_deterministic_and_read_only(self) -> None:
        project = self.make_project()
        before = subprocess.run(
            ["git", "-C", str(project), "status", "--porcelain=v1", "--untracked-files=all"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout
        first = validate_project(project, self.workspace)
        second = validate_project(project, self.workspace)
        after = subprocess.run(
            ["git", "-C", str(project), "status", "--porcelain=v1", "--untracked-files=all"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout
        self.assertEqual(first, second)
        self.assertEqual(before, after)

    def test_local_automation_rejects_heading_only_compatibility_audit(self) -> None:
        project = self.make_project()
        capability = project / ".codex/rules/project.rules"
        capability.parent.mkdir(parents=True)
        capability.write_text("prefix_rule(pattern=[\"project-tool\"], decision=\"allow\")\n", encoding="utf-8")
        audit = project / "docs/CONTEXT_COMPATIBILITY.md"
        audit.write_text("# Compatibility audit\n", encoding="utf-8")
        self.assertIn("invalid-compatibility-audit", self.issue_codes(project))

    def test_local_automation_requires_compatibility_audit_file(self) -> None:
        project = self.make_project()
        capability = project / ".codex/rules/project.rules"
        capability.parent.mkdir(parents=True)
        capability.write_text("prefix_rule(pattern=[\"project-tool\"], decision=\"allow\")\n", encoding="utf-8")
        self.assertIn("missing-compatibility-audit", self.issue_codes(project))

    def test_local_automation_accepts_explicit_project_classification(self) -> None:
        project = self.make_project()
        capability = project / ".codex/rules/project.rules"
        capability.parent.mkdir(parents=True)
        capability.write_text("prefix_rule(pattern=[\"project-tool\"], decision=\"allow\")\n", encoding="utf-8")
        audit = project / "docs/CONTEXT_COMPATIBILITY.md"
        audit.write_text("| Capability | Status |\n|---|---|\n| Project rule | `PROJECT_ONLY` |\n", encoding="utf-8")
        self.assertNotIn("missing-compatibility-audit", self.issue_codes(project))
        self.assertNotIn("invalid-compatibility-audit", self.issue_codes(project))

    def test_ordinary_application_and_ci_directories_are_not_ai_automation(self) -> None:
        project = self.make_project()
        for relative in ("agents/worker.py", "skills/domain.py", "rules/business.json", ".github/workflows/ci.yml"):
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("application content\n", encoding="utf-8")
        self.assertNotIn("missing-compatibility-audit", self.issue_codes(project))

    def test_pnpm_dependency_drift_is_reported(self) -> None:
        project = self.make_project()
        (project / "package.json").write_text('{"packageManager":"pnpm@9.0.0"}\n', encoding="utf-8")
        (project / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n", encoding="utf-8")
        (project / "package-lock.json").write_text("{}\n", encoding="utf-8")
        workflow = project / ".github/workflows/ci.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("- run: npm ci\n", encoding="utf-8")
        cached = project / "node_modules/pkg/index.js"
        cached.parent.mkdir(parents=True)
        cached.write_text("module.exports = {}\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(project), "add", "node_modules/pkg/index.js"], check=True)
        codes = self.issue_codes(project)
        self.assertIn("competing-lockfile", codes)
        self.assertIn("manager-inconsistent-ci", codes)
        self.assertIn("tracked-generated-dependency-path", codes)
        self.assertIn("missing-dependency-contract", codes)

    def test_documented_pnpm_contract_passes_dependency_checks(self) -> None:
        project = self.make_project()
        (project / "package.json").write_text('{"packageManager":"pnpm@9.0.0"}\n', encoding="utf-8")
        (project / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n", encoding="utf-8")
        self.document_dependencies(project)
        codes = self.issue_codes(project)
        self.assertNotIn("competing-lockfile", codes)
        self.assertNotIn("missing-dependency-contract", codes)

    def test_uv_requires_lockfile_and_contract(self) -> None:
        project = self.make_project()
        (project / "pyproject.toml").write_text("[tool.uv]\n", encoding="utf-8")
        codes = self.issue_codes(project)
        self.assertIn("missing-canonical-lockfile", codes)
        self.assertIn("missing-dependency-contract", codes)

    def test_nested_multi_ecosystem_dependencies_are_validated(self) -> None:
        project = self.make_project()
        frontend = project / "apps/frontend"
        frontend.mkdir(parents=True)
        (frontend / "package.json").write_text('{"packageManager":"pnpm@11.23.0"}\n', encoding="utf-8")
        (frontend / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n", encoding="utf-8")
        (frontend / "package-lock.json").write_text("{}\n", encoding="utf-8")
        backend = project / "apps/backend"
        backend.mkdir(parents=True)
        (backend / "pyproject.toml").write_text("[tool.uv]\n", encoding="utf-8")
        codes = self.issue_codes(project)
        self.assertIn("competing-lockfile", codes)
        self.assertIn("missing-canonical-lockfile", codes)
        self.assertIn("missing-dependency-contract", codes)

    def test_generic_manifests_require_dependency_contract(self) -> None:
        project = self.make_project()
        (project / "Cargo.toml").write_text("[package]\nname='demo'\nversion='0.1.0'\n", encoding="utf-8")
        self.assertIn("missing-dependency-contract", self.issue_codes(project))


if __name__ == "__main__":
    unittest.main()
