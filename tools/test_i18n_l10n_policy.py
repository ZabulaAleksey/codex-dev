from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class I18nL10nPolicyTests(unittest.TestCase):
    def test_canonical_policy_owns_terms_and_scope(self) -> None:
        policy = read("rules/i18n-l10n.md")
        for marker in (
            "Internationalization (`i18n`)",
            "Localization (`l10n`)",
            "`language`",
            "`locale`",
            "`en-US`",
            "`en-GB`",
            "всех продуктов с пользовательской",
            "Полный контракт принадлежит только этому файлу",
        ):
            self.assertIn(marker, policy)
        self.assertIn("Язык проектной документации", policy)

    def test_policy_covers_resources_and_locale_dependent_data(self) -> None:
        policy = read("rules/i18n-l10n.md")
        for marker in (
            't("...")',
            "даты и время",
            "числа",
            "валюты",
            "единицы измерения",
            "plural rules",
            "сортировку и collation",
            "адреса и телефонные номера",
            "часовые пояса",
        ):
            self.assertIn(marker, policy)
        self.assertIn("presentation boundary", policy)

    def test_fallback_layout_and_stage_contract_are_self_contained(self) -> None:
        policy = read("rules/i18n-l10n.md")
        for marker in (
            "fallback locale",
            "missing key",
            "rules/fallback-policy.md",
            "text expansion",
            "RTL",
            "pseudo-locale",
            "alternate test locale",
            "без будущего компонента",
            "implemented_unverified",
        ):
            self.assertIn(marker, policy)
        self.assertIn("structural test", policy)

    def test_global_routers_point_to_one_policy_and_project_delta(self) -> None:
        routes = {
            "AGENTS.md": "~/.codex/rules/i18n-l10n.md",
            "rules/README.md": "rules/i18n-l10n.md",
            "docs/PROJECT_FRAMEWORK.md": "../rules/i18n-l10n.md",
            "docs/ARCHITECTURE.md": "rules/i18n-l10n.md",
            "README.md": "rules/i18n-l10n.md",
        }
        for relative, marker in routes.items():
            self.assertIn(marker, read(relative), relative)

        framework = read("docs/PROJECT_FRAMEWORK.md")
        self.assertIn("Project `SPEC` и `DESIGN.md` не копируют", framework)
        self.assertIn("Язык project context", framework)

    def test_canonical_rules_owner_is_unique_and_routers_remain_thin(self) -> None:
        owner_signature = (
            "Internationalization (`i18n`)",
            "Localization (`l10n`)",
            't("...")',
            "fallback locale",
            "text expansion",
            "Project-specific delta",
            "## PASS evidence",
        )
        owners = []
        for candidate in (ROOT / "rules").rglob("*.md"):
            content = candidate.read_text(encoding="utf-8")
            if all(marker in content for marker in owner_signature):
                owners.append(candidate.relative_to(ROOT).as_posix())
        self.assertEqual(["rules/i18n-l10n.md"], sorted(owners))

        normative_headings = (
            "### Пользовательские строки",
            "### Locale-dependent данные",
            "### Выбор locale и fallback",
            "## PASS evidence",
        )
        for relative in ("AGENTS.md", "rules/README.md", "docs/PROJECT_FRAMEWORK.md"):
            content = read(relative)
            for heading in normative_headings:
                self.assertNotIn(heading, content, f"{relative} copies {heading}")

    def test_system_spec_owns_stable_requirement_and_acceptance(self) -> None:
        spec = read("specs/system.spec.md")
        for marker in (
            "Версия: 1.9",
            "FR-010",
            "AC-013",
            "internationalization (`i18n`)",
            "localization (`l10n`)",
            "pseudo-locale",
        ):
            self.assertIn(marker, spec)

    def test_context_validator_requires_policy_and_contract_test(self) -> None:
        validator = read("tools/validate_context.py")
        self.assertIn('"rules/i18n-l10n.md"', validator)
        self.assertIn('"tools/test_i18n_l10n_policy.py"', validator)


if __name__ == "__main__":
    unittest.main()
