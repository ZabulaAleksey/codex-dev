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

    def test_global_execution_state_is_owned_only_by_stages(self) -> None:
        self.assertTrue((ROOT / "prompts/STAGES.md").is_file())
        self.assertTrue((ROOT / "templates/STAGES_TEMPLATE.md").is_file())
        for relative in (
            "docs/AI_PLAN.md",
            "docs/AI_STATUS.md",
            "templates/AI_PLAN_TEMPLATE.md",
            "templates/AI_STATUS_TEMPLATE.md",
        ):
            with self.subTest(path=relative):
                self.assertFalse((ROOT / relative).exists())

        stages = read("prompts/STAGES.md")
        self.assertEqual(1, stages.count("- Stage ID:"))
        self.assertIn("## DEV-CANONICAL-STAGES-001", stages)
        self.assertIn("- Sequence:", stages)
        self.assertIn("- NEXT:", stages)

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
                "stage_routing_snapshot",
                "execution_allowed",
                "Stage context — DEGRADED",
                "routing snapshot missing selected record",
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

    def create_stage_repo(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        (root / "AGENTS.md").write_text("Global DEV bridge: enabled\n", encoding="utf-8")
        marker = root / ".codex/dev-project.toml"
        marker.parent.mkdir(parents=True)
        marker.write_text('schema_version = 1\n\n[dev]\nmanaged = true\nrequires_global_dev = true\nminimum_version = "2026.09.10"\nrequired_capabilities = ["stage-router-v1"]\nrequired_contract_schema = 1\n', encoding="utf-8")
        (root / "docs").mkdir()
        (root / "prompts").mkdir()

    def write_stages(self, root: Path, body: str, stage_id: str | None = "STAGE-002") -> None:
        selector = f"- Stage ID: `{stage_id}`\n\n" if stage_id is not None else ""
        if (stage_id is not None and f"## {stage_id}" in body
                and "- Status:" not in body and "- NEXT:" not in body):
            marker = f"## {stage_id}"
            start = body.rfind(marker)
            end = body.find("\n", start)
            end = len(body) if end < 0 else end
            body = (body[:end] + f"\n\n- Status: planned\n- NEXT: {stage_id}"
                    + body[end:])
        (root / "prompts/STAGES.md").write_text(
            "# Stages\n\n" + selector + body,
            encoding="utf-8",
        )

    def test_session_hook_projects_exact_selected_stage_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            self.write_stages(
                repo,
                "## STAGE-001 — first\n\nDO-NOT-LOAD-FIRST\n\n"
                "## STAGE-002 — selected\n\nSELECTED-STAGE-BODY\n\n"
                "### PASS criteria\n\n- selected-pass\n\n"
                "## STAGE-003 — future\n\nDO-NOT-LOAD-FUTURE\n",
            )
            context = self.run_session_hook(repo)
            self.assertIn("SELECTED-STAGE-BODY", context)
            self.assertIn("selected-pass", context)
            self.assertNotIn("DO-NOT-LOAD-FIRST", context)
            self.assertNotIn("DO-NOT-LOAD-FUTURE", context)

    def test_session_hook_marks_stage_catalog_without_selector_as_degraded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            self.write_stages(repo, "CATALOG-MUST-STAY-OUT\n", stage_id=None)
            context = self.run_session_hook(repo)
            self.assertNotIn("CATALOG-MUST-STAY-OUT", context)
            self.assertIn("Stage routing — DEGRADED", context)
            self.assertIn("missing-stage-id", context)

    def test_session_hook_marks_missing_selected_stage_as_degraded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            self.write_stages(repo, "## STAGE-001\n\nOnly stage\n")
            context = self.run_session_hook(repo)
            self.assertIn("Stage routing — DEGRADED", context)
            self.assertIn("STAGE-002", context)
            self.assertIn("missing-stage-heading", context)

    def test_session_hook_rejects_ambiguous_selected_stage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            self.write_stages(
                repo,
                "## STAGE-002 — duplicate A\n\nA\n\n"
                "## STAGE-002 — duplicate B\n\nB\n",
            )
            context = self.run_session_hook(repo)
            self.assertIn("Stage routing — DEGRADED", context)
            self.assertIn("ambiguous-stage-heading", context)

    def test_session_hook_ignores_heading_inside_fenced_example(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            self.write_stages(
                repo,
                "```markdown\n## STAGE-002 — example only\nFAKE-BODY\n```\n\n"
                "## STAGE-002 — real\n\nREAL-BODY\n",
            )
            context = self.run_session_hook(repo)
            self.assertIn("REAL-BODY", context)
            self.assertNotIn("FAKE-BODY", context)
            self.assertNotIn("Stage routing — DEGRADED", context)

    def test_session_hook_rejects_multiple_stages_selectors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            (repo / "prompts/STAGES.md").write_text(
                "- Stage ID: `STAGE-002`\n- Stage ID: `STAGE-003`\n\n"
                "## STAGE-002\n\nA\n\n## STAGE-003\n\nB\n", encoding="utf-8"
            )
            context = self.run_session_hook(repo)
            self.assertIn("Stage routing — DEGRADED", context)
            self.assertIn("ambiguous-stage-id", context)
            self.assertNotIn("## prompts/STAGES.md — selected", context)

    def test_session_hook_finds_selector_after_old_prefix_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            (repo / "prompts/STAGES.md").write_text(
                "# Stages\n\n" + ("x" * 9000) +
                "\n\n- Stage ID: `STAGE-002`\n\n## STAGE-002 — selected\n\n"
                "- Status: planned\n- NEXT: STAGE-002\n\nLATE-SELECTOR-BODY\n",
                encoding="utf-8",
            )
            context = self.run_session_hook(repo)
            self.assertIn("LATE-SELECTOR-BODY", context)
            self.assertNotIn("Stage routing — DEGRADED", context)

    def test_session_hook_marks_oversized_stages_as_degraded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            (repo / "prompts/STAGES.md").write_text(
                "# Stages\n\n" + ("x" * 500_100) +
                "\n- Stage ID: `STAGE-002`\n\n## STAGE-002\n\nMUST-NOT-BE-SELECTED\n",
                encoding="utf-8",
            )
            context = self.run_session_hook(repo)
            self.assertIn("Stage routing — DEGRADED", context)
            self.assertIn("state_read_error", context)
            self.assertNotIn("MUST-NOT-BE-SELECTED", context)

    def test_session_hook_reports_brownfield_without_materializing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            (repo / "docs/AI_PLAN.md").write_text(
                "# Plan\n- Stage ID: LEGACY-A\n- Master: MASTER-1\n- Status: partial\n"
                "- NEXT: LEGACY-B\n- Checkpoint: abc123\n- Evidence: L1\n",
                encoding="utf-8",
            )
            (repo / "docs/AI_STATUS.md").write_text(
                "# Status\n- Current stage: LEGACY-A\n- Status: partial\n", encoding="utf-8"
            )
            first = self.run_session_hook(repo)
            second = self.run_session_hook(repo)
            self.assertEqual(first, second)
            self.assertIn('"routing_status":"migration_plan_available"', first)
            self.assertIn('"execution_allowed":false', first)
            self.assertNotIn("## prompts/STAGES.md — selected", first)
            self.assertFalse((repo / "prompts/STAGES.md").exists())
            self.assertFalse((repo / ".stage-compatibility.lock").exists())

    def test_session_hook_conflict_is_fail_closed_and_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            self.write_stages(
                repo, "## STAGE-002\n\n- Status: planned\n- NEXT: STAGE-002\n"
            )
            (repo / "docs/AI_PLAN.md").write_text(
                "# Plan\n- Stage ID: OTHER\n- Status: partial\n- NEXT: OTHER\n",
                encoding="utf-8",
            )
            (repo / "docs/AI_STATUS.md").write_text(
                "# Status\n- Current stage: OTHER\n- Status: partial\n", encoding="utf-8"
            )
            context = self.run_session_hook(repo)
            self.assertIn('"routing_status":"conflicting_stage_state"', context)
            self.assertIn('"execution_allowed":false', context)
            self.assertNotIn("## prompts/STAGES.md — selected", context)

    def test_session_hook_no_state_is_typed_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            self.create_stage_repo(repo)
            first = self.run_session_hook(repo)
            second = self.run_session_hook(repo)
            self.assertEqual(first, second)
            self.assertIn('"routing_status":"no_stage_state"', first)
            self.assertIn('"execution_allowed":false', first)
            self.assertNotIn("## prompts/STAGES.md — selected", first)

    def test_prompt_and_stages_template_collect_operational_fields(self) -> None:
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
            "templates/STAGES_TEMPLATE.md",
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
            "templates/STAGES_TEMPLATE.md",
            (
                "Status:",
                "planned | implemented | verified | partial | blocked | unavailable",
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
