from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class ReplaceableModulePolicyTests(unittest.TestCase):
    def test_single_policy_owns_complete_contract(self) -> None:
        policy = read("rules/replaceable-modules.md")
        for marker in (
            "Replaceable Module Contract",
            "system-owned port/protocol",
            "anti-corruption",
            "composition root",
            "contract test suite",
            "export/import/migration/rollback",
            "YAGNI",
            "0–2",
            "9",
            "10",
        ):
            self.assertIn(marker, policy)

        owners = []
        signature = ("Replaceable Module Contract", "0–2", "contract test suite", "YAGNI")
        for candidate in (ROOT / "rules").rglob("*.md"):
            content = candidate.read_text(encoding="utf-8")
            if all(marker in content for marker in signature):
                owners.append(candidate.relative_to(ROOT).as_posix())
        self.assertEqual(["rules/replaceable-modules.md"], owners)

    def test_routes_point_to_policy_without_copying_it(self) -> None:
        routes = (
            "AGENTS.md",
            "rules/README.md",
            "README.md",
            "docs/PROJECT_FRAMEWORK.md",
            "skill-sources/dev-karkas/references/ARCHITECTURE_POLICY.md",
        )
        for relative in routes:
            self.assertIn("rules/replaceable-modules.md", read(relative), relative)

    def test_spec_owns_requirement_and_acceptance(self) -> None:
        spec = read("specs/system.spec.md")
        for marker in ("Версия: 1.9", "FR-015", "AC-018", "Replaceability by Design"):
            self.assertIn(marker, spec)

    def test_global_structural_guard_is_not_product_evidence(self) -> None:
        policy = read("rules/replaceable-modules.md")
        self.assertIn("Generic\ncross-language regex gate", policy)
        self.assertIn("не является достаточным evidence", policy)


if __name__ == "__main__":
    unittest.main()
