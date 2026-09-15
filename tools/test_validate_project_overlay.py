from __future__ import annotations

import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tools.validate_project_overlay import main as validator_main, validate_project
from tools.dev_paths import BRIDGE_MARKER


LEGACY_PLAN = """# Plan
- Stage ID: STAGE-001
- Master: MASTER-001
- Status: partial
- NEXT: STAGE-002
- Checkpoint: abc123
- Evidence: L1
"""
LEGACY_STATUS = """# Status
- Current stage: STAGE-001
- Status: partial
"""


REQUIRED_CONTENT = {
    "AGENTS.md": f"# Project router\n\n{BRIDGE_MARKER}\n",
    "docs/STAGES.md": "# Stages\n\n- Stage ID: `STAGE-001`\n\n## STAGE-001 — first slice\n\n- Lifecycle: `planned`\n- NEXT: `STAGE-001`\n",
    "docs/ARCHITECTURE.md": "# Architecture\n",
    "docs/DECISIONS.md": "# Decisions\n",
    "docs/LEARNING_LOG.md": "# Learning log\n",
    "docs/project-context.md": "# Project context\n",
    "docs/ROADMAP.md": "# Roadmap\n",
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
        marker = project / ".codex/dev-project.toml"
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(
            'schema_version = 1\n\n[dev]\nmanaged = true\nrequires_global_dev = true\n'
            'minimum_version = "2026.09.10"\nrequired_capabilities = ["path-resolver-v1"]\n'
            'required_contract_schema = 1\n',
            encoding="utf-8",
        )
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
        self.assertTrue(result.inspection_ok)
        self.assertTrue(result.canonical_valid)
        self.assertTrue(result.execution_allowed)
        self.assertEqual(result.stage_state["status"], "pass_canonical")
        self.assertEqual((), result.issues)

    def test_agents_declaration_without_structured_marker_fails_closed(self) -> None:
        project = self.make_project("agents-only")
        (project / ".codex/dev-project.toml").unlink()
        self.assertIn("missing-dev-project-marker", self.issue_codes(project))

    def test_incomplete_overlay_reports_typed_legacy_migration(self) -> None:
        project = self.make_project()
        (project / "docs/STAGES.md").unlink()
        (project / "docs/AI_PLAN.md").write_text(LEGACY_PLAN, encoding="utf-8")
        (project / "docs/AI_STATUS.md").write_text(LEGACY_STATUS, encoding="utf-8")
        result = validate_project(project, self.workspace)
        self.assertFalse(result.ok)
        self.assertTrue(result.inspection_ok)
        self.assertFalse(result.canonical_valid)
        self.assertFalse(result.execution_allowed)
        self.assertEqual(result.stage_state["status"], "migration_plan_available")
        self.assertIn("stage-migration-plan-available", self.issue_codes(project))
        self.assertNotIn("missing-required-file", self.issue_codes(project))
        self.assertNotIn("competing-execution-state-file", self.issue_codes(project))

    def test_no_stage_state_and_unsafe_legacy_are_typed(self) -> None:
        no_state = self.make_project("no-state")
        (no_state / "docs/STAGES.md").unlink()
        result = validate_project(no_state, self.workspace)
        self.assertEqual(result.stage_state["status"], "no_stage_state")
        self.assertIn("no-stage-state", {issue.code for issue in result.issues})

        unsafe = self.make_project("unsafe")
        (unsafe / "docs/STAGES.md").unlink()
        (unsafe / "docs/AI_PLAN.md").write_text(
            LEGACY_PLAN.replace("- NEXT: STAGE-002\n", ""), encoding="utf-8"
        )
        (unsafe / "docs/AI_STATUS.md").write_text(LEGACY_STATUS, encoding="utf-8")
        result = validate_project(unsafe, self.workspace)
        self.assertEqual(result.stage_state["status"], "migration_plan_unsafe")
        self.assertIn("missing_next_selector", result.stage_state["issue_codes"])

    def test_invalid_canonical_never_falls_back_to_valid_legacy(self) -> None:
        project = self.make_project("invalid-canonical")
        (project / "docs/STAGES.md").write_text(
            "- Stage ID: STAGE-001\n\n- Stage ID: STAGE-002\n", encoding="utf-8"
        )
        (project / "docs/AI_PLAN.md").write_text(LEGACY_PLAN, encoding="utf-8")
        (project / "docs/AI_STATUS.md").write_text(LEGACY_STATUS, encoding="utf-8")
        result = validate_project(project, self.workspace)
        self.assertEqual(result.stage_state["status"], "conflicting_stage_state")
        self.assertFalse(result.execution_allowed)
        self.assertIn("conflicting-stage-state", {issue.code for issue in result.issues})

    def test_cli_json_migration_is_inspectable_but_exit_one(self) -> None:
        project = self.make_project("cli-legacy")
        (project / "docs/STAGES.md").unlink()
        (project / "docs/AI_PLAN.md").write_text(LEGACY_PLAN, encoding="utf-8")
        (project / "docs/AI_STATUS.md").write_text(LEGACY_STATUS, encoding="utf-8")
        output = io.StringIO()
        with redirect_stdout(output):
            code = validator_main([
                str(project), "--json", "--workspace-root", str(self.workspace)
            ])
        payload = json.loads(output.getvalue())
        self.assertEqual(code, 1)
        self.assertTrue(payload["inspection_ok"])
        self.assertFalse(payload["canonical_valid"])
        self.assertFalse(payload["execution_allowed"])
        self.assertEqual(payload["stage_state"]["status"], "migration_plan_available")

    def test_root_legacy_names_remain_competing_state(self) -> None:
        project = self.make_project("root-legacy")
        (project / "AI_PLAN.md").write_text("# competing\n", encoding="utf-8")
        (project / "AI_STATUS.md").write_text("# competing\n", encoding="utf-8")
        result = validate_project(project, self.workspace)
        competing = [issue.path for issue in result.issues
                     if issue.code == "competing-execution-state-file"]
        self.assertEqual(competing, ["AI_PLAN.md", "AI_STATUS.md"])
        self.assertFalse(result.execution_allowed)

    def test_root_legacy_symlink_remains_competing_state(self) -> None:
        project = self.make_project("root-legacy-link")
        outside = self.root / "outside-plan.md"
        outside.write_text("# outside\n", encoding="utf-8")
        try:
            (project / "AI_PLAN.md").symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"file symlink unavailable: {exc}")
        result = validate_project(project, self.workspace)
        self.assertIn(
            "AI_PLAN.md",
            [issue.path for issue in result.issues
             if issue.code == "competing-execution-state-file"],
        )

    def test_legacy_stage_file_and_stale_workspace_path_are_reported(self) -> None:
        project = self.make_project()
        (project / "prompts").mkdir()
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

    def test_stage_selector_requires_exactly_one_valid_id(self) -> None:
        cases = (
            ("missing-stage-id", "# Current plan\n"),
            ("ambiguous-stage-id", (
                "# Current plan\n\n- Stage ID: `STAGE-001`\n- Stage ID: STAGE-002\n"
            )),
            ("invalid-stage-id", "# Current plan\n\n- Stage ID: ``\n"),
            ("invalid-stage-id", "# Current plan\n\n- Stage ID: `STAGE/001`\n"),
        )
        for index, (expected_code, content) in enumerate(cases):
            with self.subTest(expected_code=expected_code, index=index):
                project = self.make_project(f"{expected_code}-{index}")
                (project / "docs/STAGES.md").write_text(
                    content + "\n## STAGE-001 — current\n", encoding="utf-8"
                )
                self.assertIn(expected_code, self.issue_codes(project))

    def test_stage_selector_rejects_missing_or_ambiguous_heading(self) -> None:
        project = self.make_project("missing-heading")
        (project / "docs/STAGES.md").write_text(
            "# Stages\n\n- Stage ID: `STAGE-001`\n\n## STAGE-002 — other\n", encoding="utf-8"
        )
        self.assertIn("missing-stage-heading", self.issue_codes(project))

        project = self.make_project("ambiguous-heading")
        (project / "docs/STAGES.md").write_text(
            "- Stage ID: `STAGE-001`\n\n## STAGE-001 — first\n\nA\n\n## STAGE-001 — duplicate\n\nB\n",
            encoding="utf-8",
        )
        self.assertIn("ambiguous-stage-heading", self.issue_codes(project))

    def test_stage_selector_uses_token_boundaries_and_ignores_fenced_examples(self) -> None:
        project = self.make_project()
        (project / "docs/STAGES.md").write_text(
            "# Stages\n\n- Stage ID: `STAGE-001`\n\n"
            "```markdown\n## STAGE-001 — example only\n```\n\n"
            "## PRE-STAGE-001-POST — not a token match\n\n"
            "## STAGE-001 — selected\n\n- Status: planned\n- NEXT: STAGE-001\n\nRunnable slice\n",
            encoding="utf-8",
        )
        result = validate_project(project, self.workspace)
        self.assertTrue(result.ok, result.issues)

    def test_declared_master_execution_state_must_be_valid(self) -> None:
        project = self.make_project()
        (project / "docs/STAGES.md").write_text(
            "- Stage ID: `MASTER-001`\n\n## MASTER-001\n\n"
            "```master-execution\n{\"schema_version\":1}\n```\n",
            encoding="utf-8",
        )
        self.assertIn("invalid-master-execution-state", self.issue_codes(project))

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
