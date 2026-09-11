from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tools.master_execution import load_selected_state, next_execution_decision


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8-sig")


class ContinuousMasterPolicyTests(unittest.TestCase):
    def test_spec_system_and_schema_are_versioned(self) -> None:
        feature = read("specs/features/continuous-master-execution.spec.md")
        system = read("specs/system.spec.md")
        schema = json.loads(read("schemas/master-execution.schema.json"))
        for marker in ("CME-001", "CME-008", "NFR-CME-003", "AC-CME-009"):
            self.assertIn(marker, feature)
        self.assertIn("FR-012 Continuous Master Execution", system)
        self.assertIn("AC-015", system)
        self.assertEqual(schema["properties"]["schema_version"]["enum"], [1, 2])
        self.assertIn("allOf", schema)
        self.assertIn("else", schema["allOf"][0])

    def test_governance_and_router_define_continuous_stop_and_isolation_contract(self) -> None:
        governance = read("rules/governance.md")
        router = read("AGENTS.md")
        for marker in (
            "Continuous Master Execution", "Checkpoint не останавливает", "VerificationGate",
            "Continuation", "Context scope", "не выполняются controller-ом",
        ):
            self.assertIn(marker, governance)
        for marker in (
            "master-execution", "автоматически переходи", "не stop", "integration/finalization",
            "Не задавай этот вопрос после каждого внутреннего master slice",
        ):
            self.assertIn(marker, router)

    def test_existing_prompt_guard_remains_cleanup_owner(self) -> None:
        policy = read("rules/prompt-queue-lifecycle.md")
        queue_spec = read("specs/features/prompt-queue-lifecycle.spec.md")
        controller = read("tools/master_execution.py")
        self.assertIn("completed `one_shot` launcher/child", policy)
        self.assertIn("PQ-12", queue_spec)
        self.assertIn("existing_guard", controller)
        self.assertNotIn("notion_update", controller.casefold())

    def test_skills_template_workflow_and_readme_route_to_one_owner(self) -> None:
        paths = (
            "skill-sources/dev-karkas/SKILL.md",
            "skill-sources/dev-karkas/references/STATUS_WORKFLOW.md",
            "skill-sources/dev-karkas/references/GIT_WORKFLOW.md",
            "skill-sources/implement-stage/SKILL.md",
            "skill-sources/resume-project/SKILL.md",
            "templates/STAGES_TEMPLATE.md",
            "docs/WORKFLOW.md",
            "README.md",
        )
        for path in paths:
            with self.subTest(path=path):
                content = read(path)
                self.assertTrue("master" in content.casefold() or "continuous" in content.casefold())
        self.assertIn("tools\\master_execution.py", read("README.md"))
        self.assertIn("Выполнить master prompt непрерывно", read("docs/WORKFLOW.md"))

    def test_current_embedded_graph_is_selected_and_cli_is_read_only(self) -> None:
        stage_id, state = load_selected_state(ROOT)
        self.assertIn(stage_id, {item["id"] for item in state["slices"]})
        self.assertTrue(all(item["master_id"] == state["master"]["id"] for item in state["slices"]))
        decision = next_execution_decision(state)
        selected = next(item for item in state["slices"] if item["id"] == stage_id)
        if state["master"]["status"] == "completed":
            expected = "complete"
        elif selected["status"] == "running":
            expected = "await_result"
        elif selected["status"] == "ready":
            expected = "continue"
        else:
            self.fail(f"selected slice has non-routable status: {selected['status']}")
        self.assertEqual(decision.action, expected)
        if expected in {"await_result", "continue"}:
            self.assertEqual(decision.slice_id, stage_id)
        before = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, check=True,
                                capture_output=True, text=True).stdout
        completed = subprocess.run(
            [sys.executable, "-B", "tools/master_execution.py", "."], cwd=ROOT, check=True,
            capture_output=True, text=True, encoding="utf-8",
        )
        output = json.loads(completed.stdout)
        after = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, check=True,
                               capture_output=True, text=True).stdout
        self.assertTrue(output["ok"])
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
