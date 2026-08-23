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


if __name__ == "__main__":
    unittest.main()
