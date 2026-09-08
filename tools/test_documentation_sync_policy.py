from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class DocumentationSyncPolicyTests(unittest.TestCase):
    def assert_markers(self, relative: str, markers: tuple[str, ...]) -> None:
        content = read(relative)
        for marker in markers:
            with self.subTest(path=relative, marker=marker):
                self.assertIn(marker, content)

    def test_system_spec_defines_requirement_and_acceptance_criterion(self) -> None:
        self.assert_markers(
            "specs/system.spec.md",
            ("FR-006", "AC-006", "Completion Documentation Synchronization Gate"),
        )

    def test_governance_defines_required_state_sources_and_post_merge_audit(self) -> None:
        self.assert_markers(
            "rules/governance.md",
            (
                "Completion Documentation Synchronization Gate",
                "`README.md`",
                "`prompts/STAGES.md`",
                "`docs/ROADMAP.md`",
                "После merge повтори аудит",
            ),
        )

    def test_global_router_requires_gate_before_completion(self) -> None:
        self.assert_markers(
            "AGENTS.md",
            (
                "Completion Documentation Synchronization Gate",
                "state-bearing документы обновлены",
                "проверены без изменений",
            ),
        )

    def test_stage_skills_route_to_canonical_workflow(self) -> None:
        self.assert_markers(
            "skill-sources/dev-karkas/SKILL.md",
            ("references/STATUS_WORKFLOW.md", "После merge повтори gate"),
        )
        self.assert_markers(
            "skill-sources/implement-stage/SKILL.md",
            ("Completion Documentation Synchronization Gate", "target branch"),
        )
        self.assert_markers(
            "skill-sources/dev-karkas/references/STATUS_WORKFLOW.md",
            ("checked, still accurate", "README-команды", "После merge / завершения этапа"),
        )

    def test_templates_and_readme_expose_the_gate(self) -> None:
        self.assert_markers(
            "templates/STAGES_TEMPLATE.md",
            ("`README`", "`prompts/STAGES.md`", "`ROADMAP`", "Проверены без изменений"),
        )
        self.assert_markers(
            "README.md",
            ("Completion Documentation Synchronization Gate", "target branch"),
        )


if __name__ == "__main__":
    unittest.main()
