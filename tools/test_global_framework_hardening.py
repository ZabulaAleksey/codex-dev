from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEWED_EXPLICIT_MODELS = {
    "gpt-5.6-luna",
    "gpt-5.6-terra",
    "gpt-5.6-sol",
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class GlobalFrameworkHardeningTests(unittest.TestCase):
    def test_feature_spec_defines_stable_scope_and_acceptance(self) -> None:
        spec = read("specs/features/global-framework-hardening.spec.md")
        for marker in (
            "FR-GFH-001",
            "FR-GFH-002",
            "FR-GFH-003",
            "FR-GFH-004",
            "AC-GFH-001",
            "AC-GFH-008",
            "config.toml",
            "LEARNING_LOG",
        ):
            self.assertIn(marker, spec)

    def test_global_agents_is_a_thin_router_with_critical_invariants(self) -> None:
        path = ROOT / "AGENTS.md"
        content = path.read_text(encoding="utf-8")
        self.assertLess(path.stat().st_size, 32 * 1024)
        for marker in (
            "SIMPLE | STANDARD | COMPLEX",
            "rules/governance.md",
            "rules/model-routing.md",
            "Completion Documentation Synchronization Gate",
            "state-bearing документы обновлены",
            "проверены без изменений",
            "prompts/STAGES.md",
            "docs/LEARNING_LOG.md",
            "config.toml",
            "Да, сливай",
        ):
            self.assertIn(marker, content)

    def test_agent_model_pins_match_reviewed_allowlist_and_inheritance_is_documented(self) -> None:
        explicit_models: set[str] = set()
        unpinned = 0
        for path in sorted((ROOT / "agents").glob("*.toml")):
            data = tomllib.loads(path.read_text(encoding="utf-8"))
            model = data.get("model")
            if model is None:
                unpinned += 1
            else:
                explicit_models.add(model)
                self.assertIn(model, REVIEWED_EXPLICIT_MODELS, path.name)
        self.assertTrue(explicit_models)
        self.assertGreater(unpinned, 0)

        team = read("docs/TEAM_ARCHITECTURE.md")
        recommendation = read("config.ai-dev-team.recommended.toml")
        self.assertIn("наследуют active/default Codex model", team)
        self.assertIn("runtime/account availability probe", team)
        self.assertIn("Global default model намеренно не задаётся", recommendation)

    def test_installers_share_safe_sequence_without_config_writes(self) -> None:
        powershell = read("install-global.ps1")
        bash = read("install-global.sh")
        powershell.encode("ascii")  # Windows PowerShell 5 parses UTF-8/no-BOM as ANSI.
        for content in (powershell, bash):
            self.assertLess(content.index("validate_context.py"), content.index("sync_global_skills.py"))
            self.assertLess(content.index("sync_global_skills.py"), content.index("validate_global_codex.py"))
            self.assertIn("--workspace", content)
            self.assertIn("--codex-home", content)
        for forbidden in ("Set-Content", "Out-File", "sed -i", "config.toml >"):
            self.assertNotIn(forbidden, powershell + bash)

    def test_greenfield_router_template_uses_bootstrap_without_local_automation(self) -> None:
        template = read("templates/AGENTS_PROJECT_TEMPLATE.md")
        self.assertIn("bootstrap-project-framework", template)
        self.assertIn("docs/AI_PLAN.md", template)
        self.assertIn("docs/AI_STATUS.md", template)
        self.assertNotIn(".codex/agents", template)
        self.assertNotIn(".agents/skills", template)

    def test_ci_is_read_only_and_runs_canonical_checks(self) -> None:
        workflow = read(".github/workflows/validate.yml")
        self.assertIn("python -B tools/validate_context.py", workflow)
        self.assertIn("python -B -m unittest discover", workflow)
        self.assertIn("bash -n install-global.sh", workflow)
        self.assertNotIn("sync_global_skills.py", workflow)
        self.assertNotIn("config.toml", workflow)


if __name__ == "__main__":
    unittest.main()
