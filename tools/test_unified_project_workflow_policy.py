from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from tools.validate_global_codex import validate_global_codex


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class UnifiedProjectWorkflowPolicyTests(unittest.TestCase):
    def test_system_spec_owns_stable_requirements(self) -> None:
        spec = read("specs/system.spec.md")
        for marker in ("FR-008", "FR-009", "AC-009", "AC-010", "AC-011", "AC-012"):
            self.assertIn(marker, spec)
        self.assertIn("`~/.codex`", spec)
        self.assertIn("`~/.agents/skills`", spec)

    def test_governance_owns_responsibility_and_sync_contracts(self) -> None:
        governance = read("rules/governance.md")
        for heading in (
            "### Матрица ответственности",
            "### Триггеры обновления документации",
            "### Контракт LEARNING_LOG",
            "## Переключение устройств и восстановление",
            "## Классы monitoring проекта",
        ):
            self.assertIn(heading, governance)
        for service in ("GitHub", "Notion", "Airtable", "Eraser", "Figma"):
            self.assertIn(service, governance)
        for monitoring_class in ("`active`", "`event-driven`", "`frozen`"):
            self.assertIn(monitoring_class, governance)
        for field in (
            "`Problem`",
            "`Symptom`",
            "`Root cause`",
            "`Failed attempts`",
            "`Fix`",
            "`Verification`",
            "`Prevention`",
            "`Links`",
        ):
            self.assertIn(field, governance)

    def test_workflow_has_eight_copy_ready_lifecycle_requests(self) -> None:
        workflow = read("docs/WORKFLOW.md")
        headings = (
            "### Начать работу с проектом",
            "### Выполнить stage",
            "### Завершить stage",
            "### Провести архитектурное изменение",
            "### Проверить перед merge",
            "### Поставить проект на паузу",
            "### Возобновить проект",
            "### Обработать новую идею",
        )
        for heading in headings:
            self.assertEqual(1, workflow.count(heading), heading)
        self.assertIn("## K. Компьютер ↔ ноутбук", workflow)
        self.assertIn("rules/governance.md", workflow)
        for evidence_marker in (
            "product/user-facing stage",
            "internal/docs/policy stage",
            "structural consumer path",
            "`BLOCKED_BY_BACKEND`",
            "`client → API/CLI → backend`",
        ):
            self.assertIn(evidence_marker, workflow)

    def test_learning_template_has_one_new_entry_shape(self) -> None:
        template = read("templates/LEARNING_LOG_TEMPLATE.md")
        headings = re.findall(r"^### (.+)$", template, flags=re.MULTILINE)
        self.assertEqual(
            [
                "Problem",
                "Symptom",
                "Root cause",
                "Failed attempts",
                "Fix",
                "Verification",
                "Prevention",
                "Links",
            ],
            headings,
        )
        self.assertIn("не дублируй Git history", template)

    def test_actual_global_root_is_explicit_and_competing_root_is_rejected(self) -> None:
        architecture = read("docs/ARCHITECTURE.md")
        compatibility = read("docs/CONTEXT_COMPATIBILITY.md")
        self.assertIn("`~/.codex`", architecture)
        self.assertIn("`~/codex-workspace/global/codex` не является source root", architecture)
        self.assertIn("`CONFLICT` → `INHERITED`", compatibility)
        self.assertIn("Skills этой задачей не затронуты", compatibility)


class GlobalSourceRootFailureTests(unittest.TestCase):
    def test_missing_canonical_root_returns_issues_without_exception(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            wrong_source = base / "codex-workspace"
            wrong_source.mkdir()
            codex_home = base / ".codex"
            codex_home.mkdir()
            (codex_home / "config.toml").write_text(
                "[shell_environment_policy]\nignore_default_excludes = false\n",
                encoding="utf-8",
            )

            issues = validate_global_codex(wrong_source, codex_home)
            codes = {issue.code for issue in issues}

            self.assertIn("missing-canonical-source", codes)
            self.assertIn("missing-document-layout-policy", codes)
            self.assertIn("missing-source-root", codes)


if __name__ == "__main__":
    unittest.main()
