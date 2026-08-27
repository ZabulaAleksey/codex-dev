from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SESSION_HOOK = ROOT / "hooks/session_context.py"

FULL_OVERLAY_DOCS = (
    "AGENTS.md",
    "prompts/STAGES.md",
    "docs/AI_PLAN.md",
    "docs/AI_STATUS.md",
    "docs/ROADMAP.md",
    "docs/ARCHITECTURE.md",
    "docs/DECISIONS.md",
    "docs/LEARNING_LOG.md",
    "docs/project-context.md",
)


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class StageCompletionPolicyTests(unittest.TestCase):
    def assert_markers(self, relative: str, markers: tuple[str, ...]) -> None:
        content = read(relative)
        for marker in markers:
            with self.subTest(path=relative, marker=marker):
                self.assertIn(marker, content)

    def test_system_spec_defines_stage_requirement_and_acceptance(self) -> None:
        self.assert_markers(
            "specs/system.spec.md",
            (
                "FR-007 Архитектурно завершённые этапы",
                "AC-007",
                "dependency DAG",
                "runnable vertical slice",
                "end-to-end PASS evidence",
                "implemented_unverified",
            ),
        )

    def test_governance_owns_one_complete_stage_contract(self) -> None:
        content = read("rules/governance.md")
        self.assertEqual(1, content.count("### Архитектурно завершённый этап"))
        for marker in (
            "self-reference, cycle и forward dependency запрещены",
            "обязательные входные предпосылки",
            "самостоятельный runnable vertical slice",
            "конкретный end-to-end сценарий",
            "PASS-критерии",
            "допустимые временные реализации",
            "функциональность, явно вынесенную в будущие stages",
            "Scaffold evidence не подтверждает",
            "`blocked`, `scaffolded`",
            "`implemented_unverified` или `partial`",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, content)

    def test_full_overlay_baseline_is_consistent(self) -> None:
        for relative in (
            "AGENTS.md",
            "rules/governance.md",
            "docs/PROJECT_FRAMEWORK.md",
            "skill-sources/dev-karkas/references/PROJECT_FILES.md",
        ):
            content = read(relative)
            for marker in FULL_OVERLAY_DOCS:
                with self.subTest(path=relative, marker=marker):
                    self.assertIn(marker, content)

    def test_stage_skills_route_to_governance_and_fail_closed(self) -> None:
        expected = {
            "skill-sources/bootstrap-project-framework/SKILL.md": (
                "Stage contract",
                "dependency DAG",
                "future stage",
            ),
            "skill-sources/plan-stage/SKILL.md": (
                "~/.codex/rules/governance.md",
                "runnable vertical slice",
                "scaffolded",
            ),
            "skill-sources/implement-stage/SKILL.md": (
                "~/.codex/rules/governance.md",
                "concrete end-to-end",
                "implemented_unverified",
            ),
            "skill-sources/resume-project/SKILL.md": (
                "Stage contract",
                "mock/stub-only",
                "partial",
            ),
            "skill-sources/dev-karkas/SKILL.md": (
                "~/.codex/rules/governance.md",
                "completed prerequisites/DAG",
                "Future stage не должен разблокировать",
            ),
        }
        for relative, markers in expected.items():
            self.assert_markers(relative, markers)

    def test_rule_router_and_sdlc_surfaces_route_to_stage_contract(self) -> None:
        self.assert_markers(
            "rules/README.md",
            ("Stage contract", "dependency DAG", "completion statuses"),
        )
        expected = {
            "rules/sdlc/architecture.md": ("Stage contract", "future stage"),
            "rules/sdlc/implementation.md": ("primary vertical slice", "scaffolded"),
            "rules/sdlc/testing.md": ("end-to-end consumer path", "BLOCKED_BY_BACKEND"),
            "rules/sdlc/review.md": ("forward dependency/cycle", "mock/stub-as-production"),
        }
        for relative, markers in expected.items():
            self.assert_markers(relative, markers)

    def test_context_router_loads_only_the_selected_stage_record(self) -> None:
        for relative in (
            "AGENTS.md",
            "docs/CONTEXT_POLICY.md",
            "docs/PROJECT_FRAMEWORK.md",
        ):
            content = read(relative)
            with self.subTest(path=relative, marker="prompts/STAGES.md"):
                self.assertIn("prompts/STAGES.md", content)
            with self.subTest(path=relative, marker="selected record"):
                self.assertTrue("выбран" in content or "selected" in content)
        self.assert_markers(
            "hooks/session_context.py",
            (
                "stage_id_from_plan",
                "select_stage_record",
                "Stage context — DEGRADED",
                "selected_stage_chunk",
            ),
        )
        self.assert_markers(
            "docs/HOOK_POLICY.md",
            ("Stage ID", "Markdown heading", "не разрешает completion claim"),
        )

    def run_session_hook(self, repo: Path) -> str:
        payload = json.dumps(
            {"cwd": str(repo), "hook_event_name": "SessionStart"}
        ).encode("utf-8")
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "cp1251"
        result = subprocess.run(
            [sys.executable, str(SESSION_HOOK)],
            input=payload,
            capture_output=True,
            env=env,
            check=True,
        )
        output = json.loads(result.stdout.decode("utf-8"))
        return output["hookSpecificOutput"]["additionalContext"]

    def create_stage_repo(self, root: Path, stage_id: str = "STAGE-002") -> None:
        (root / ".git").mkdir()
        (root / "docs").mkdir()
        (root / "prompts").mkdir()
        selector = f"`{stage_id}`" if stage_id else ""
        (root / "docs/AI_PLAN.md").write_text(
            f"# Plan\n\n## Stage identity и dependency DAG\n\n- Stage ID: {selector}\n",
            encoding="utf-8",
        )

    def test_session_hook_projects_exact_selected_stage_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            (repo / "prompts/STAGES.md").write_text(
                "# Stage catalog\n\n"
                "## STAGE-001 — first\n\nDO-NOT-LOAD-FIRST\n\n"
                "## STAGE-002 — selected\n\nSELECTED-STAGE-BODY\n\n"
                "### PASS criteria\n\n- selected-pass\n\n"
                "## STAGE-003 — future\n\nDO-NOT-LOAD-FUTURE\n",
                encoding="utf-8",
            )
            context = self.run_session_hook(repo)
            self.assertIn("SELECTED-STAGE-BODY", context)
            self.assertIn("selected-pass", context)
            self.assertNotIn("DO-NOT-LOAD-FIRST", context)
            self.assertNotIn("DO-NOT-LOAD-FUTURE", context)

    def test_session_hook_does_not_load_stage_catalog_without_selector(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo, stage_id="")
            (repo / "prompts/STAGES.md").write_text(
                "# Stages\n\nCATALOG-MUST-STAY-OUT\n", encoding="utf-8"
            )
            context = self.run_session_hook(repo)
            self.assertNotIn("CATALOG-MUST-STAY-OUT", context)
            self.assertNotIn("Stage context — DEGRADED", context)

    def test_session_hook_marks_missing_selected_stage_as_degraded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            (repo / "prompts/STAGES.md").write_text(
                "# Stages\n\n## STAGE-001\n\nOnly stage\n", encoding="utf-8"
            )
            context = self.run_session_hook(repo)
            self.assertIn("Stage context — DEGRADED", context)
            self.assertIn("STAGE-002", context)
            self.assertIn("не найден", context)

    def test_session_hook_rejects_ambiguous_selected_stage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            (repo / "prompts/STAGES.md").write_text(
                "## STAGE-002 — duplicate A\n\nA\n\n"
                "## STAGE-002 — duplicate B\n\nB\n",
                encoding="utf-8",
            )
            context = self.run_session_hook(repo)
            self.assertIn("Stage context — DEGRADED", context)
            self.assertIn("неоднозначен", context)

    def test_session_hook_ignores_heading_inside_fenced_example(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            (repo / "prompts/STAGES.md").write_text(
                "# Examples\n\n```markdown\n## STAGE-002 — example only\nFAKE-BODY\n```\n\n"
                "## STAGE-002 — real\n\nREAL-BODY\n",
                encoding="utf-8",
            )
            context = self.run_session_hook(repo)
            self.assertIn("REAL-BODY", context)
            self.assertNotIn("FAKE-BODY", context)
            self.assertNotIn("Stage context — DEGRADED", context)

    def test_session_hook_rejects_multiple_plan_selectors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            with (repo / "docs/AI_PLAN.md").open("a", encoding="utf-8") as handle:
                handle.write("\n- Stage ID: `STAGE-003`\n")
            (repo / "prompts/STAGES.md").write_text(
                "## STAGE-002\n\nA\n\n## STAGE-003\n\nB\n", encoding="utf-8"
            )
            context = self.run_session_hook(repo)
            self.assertIn("Stage context — DEGRADED", context)
            self.assertIn("selector", context)
            self.assertNotIn("## prompts/STAGES.md — selected", context)

    def test_session_hook_finds_selector_after_old_plan_prefix_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            (repo / "docs/AI_PLAN.md").write_text(
                "# Plan\n\n" + ("x" * 9000) + "\n\n- Stage ID: `STAGE-002`\n",
                encoding="utf-8",
            )
            (repo / "prompts/STAGES.md").write_text(
                "## STAGE-002 — selected\n\nLATE-SELECTOR-BODY\n", encoding="utf-8"
            )
            context = self.run_session_hook(repo)
            self.assertIn("LATE-SELECTOR-BODY", context)
            self.assertNotIn("Stage context — DEGRADED", context)

    def test_session_hook_marks_oversized_plan_as_degraded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            (repo / "docs/AI_PLAN.md").write_text(
                "# Plan\n\n" + ("x" * 100_100) + "\n- Stage ID: `STAGE-002`\n",
                encoding="utf-8",
            )
            (repo / "prompts/STAGES.md").write_text(
                "## STAGE-002\n\nMUST-NOT-BE-SELECTED\n", encoding="utf-8"
            )
            context = self.run_session_hook(repo)
            self.assertIn("Stage context — DEGRADED", context)
            self.assertIn("AI_PLAN.md", context)
            self.assertIn("scan-limit", context)
            self.assertNotIn("MUST-NOT-BE-SELECTED", context)

    def test_prompt_and_ai_templates_collect_operational_fields(self) -> None:
        self.assert_markers(
            "skill-sources/dev-karkas/references/PROMPT_TEMPLATE.md",
            (
                "dependency DAG",
                "Runnable vertical slice",
                "end-to-end",
                "PASS",
                "temporary implementation",
                "Deferred",
            ),
        )
        self.assert_markers(
            "templates/AI_PLAN_TEMPLATE.md",
            (
                "dependency DAG",
                "runnable vertical slice",
                "end-to-end",
                "PASS",
                "Допустимая временная реализация",
                "Deferred",
            ),
        )
        self.assert_markers(
            "templates/AI_STATUS_TEMPLATE.md",
            (
                "Lifecycle:",
                "Evidence level:",
                "implemented_unverified",
                "Concrete end-to-end PASS evidence",
            ),
        )

    def test_status_and_testing_contracts_keep_spec_authority(self) -> None:
        self.assert_markers(
            "skill-sources/dev-karkas/references/STATUS_WORKFLOW.md",
            (
                "Не смешивай lifecycle stage и уровень интеграционного evidence",
                "Requirements принадлежат SPEC/ADR",
                "Blocked primary gate нельзя переносить в `DONE`",
            ),
        )
        testing = read("skill-sources/dev-karkas/references/TESTING_POLICY.md")
        self.assertIn("SPEC/ADR являются источником требований", testing)
        self.assertIn("не заменяют живой user/production E2E evidence", testing)
        self.assertNotIn("Тесты — источник требований", testing)

    def test_canonical_stage_path_has_no_competing_backlog_directory(self) -> None:
        for relative in (
            "skill-sources/dev-karkas/SKILL.md",
            "skill-sources/dev-karkas/references/KARKAS.md",
            "skill-sources/dev-karkas/references/NOTION_INTAKE.md",
        ):
            content = read(relative)
            with self.subTest(path=relative):
                self.assertIn("prompts/STAGES.md", content)
                self.assertNotIn("PROMPTS/BACKLOG", content)

    def test_architecture_records_structural_validation_boundary(self) -> None:
        self.assert_markers(
            "docs/ARCHITECTURE.md",
            (
                "tools/test_stage_completion_policy.py",
                "не объявляет stage",
                "архитектурно завершённым",
                "semantic parser",
            ),
        )
        self.assert_markers(
            "docs/CONTEXT_COMPATIBILITY.md",
            ("CONFLICT` → `INHERITED", "STAGES semantic parser"),
        )


if __name__ == "__main__":
    unittest.main()
