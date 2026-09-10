from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.validate_project_overlay import (
    BACKEND_DX_COMMAND_FIELDS,
    BACKEND_DX_REQUIRED_FIELDS,
    _markdown_bullet_fields,
    validate_project,
)


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_CONTENT = {
    "AGENTS.md": (
        "# Project router\n\nGlobal DEV bridge: enabled\n\n"
        "Backend workflow: read ~/.codex/rules/backend-dx.md and "
        "docs/project-context.md.\n"
    ),
    "prompts/STAGES.md": (
        "# Stages\n\n- Stage ID: `STAGE-001`\n\n"
        "## STAGE-001 — backend slice\n\n- Lifecycle: `planned`\n- NEXT: `STAGE-001`\n"
    ),
    "docs/ARCHITECTURE.md": "# Architecture\n",
    "docs/DECISIONS.md": "# Decisions\n",
    "docs/LEARNING_LOG.md": "# Learning log\n",
    "docs/ROADMAP.md": "# Roadmap\n",
}

COMPLETE_DELTA = """# Project context

## Backend DX Delta

- Applicability level: `BDX-L2`
- Supported local environments: Windows PowerShell and CI Linux
- Canonical working directory: repository root
- Toolchain/runtime versions: Python 3.13
- Package manager and lockfile: uv with uv.lock
- Canonical commands:
  - bootstrap: `pwsh scripts/dev.ps1 bootstrap`
  - doctor: `pwsh scripts/dev.ps1 doctor`
  - dev: `pwsh scripts/dev.ps1 start`
  - stop: `pwsh scripts/dev.ps1 stop`
  - check: `pwsh scripts/dev.ps1 check`
  - test-fast: `pwsh scripts/dev.ps1 test-fast`
  - test-integration: `pwsh scripts/dev.ps1 test-integration`
  - build: `N/A — this runtime is not packaged`
  - logs: `pwsh scripts/dev.ps1 logs`
- Required local services: isolated PostgreSQL test service
- Readiness/status command: `pwsh scripts/dev.ps1 doctor`
- Ports and collision policy: configurable local port with preflight collision check
- Config source, profiles and required variables: `.env.example`; local/test/ci
- Secret redaction/effective-config diagnostics: doctor prints names and redacted values
- API docs/spec and generated-contract drift command: `pwsh scripts/dev.ps1 api-spec-check`
- DB migration/status/seed/reset-local commands: `db-status`; `db-migrate`; `db-seed`; `db-reset-local`
- Destructive command guard: APP_ENV must be local or test; production is refused
- Worker/scheduler commands: `N/A — this project has no worker or scheduler`
- External sandbox/stub/fallback modes: `N/A — this project has no external provider`
- Clean-room smoke command or documented manual scenario: `pwsh scripts/dev.ps1 smoke-clean`
- Project-specific quality gates: `BDX-GATE-01..12` recorded in `prompts/STAGES.md`
- Known limitations: clean-room fixture covers Windows and CI Linux only
- Explicit deviations from global Backend DX Policy: none
"""


class BackendDxPolicyValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "workspace"
        policy = self.workspace / "rules/backend-dx.md"
        policy.parent.mkdir(parents=True)
        policy.write_text("# Backend Developer Experience Policy\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def make_project(self) -> Path:
        project = self.root / "project"
        project.mkdir()
        for relative, content in REQUIRED_CONTENT.items():
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        context = project / "docs/project-context.md"
        context.write_text(COMPLETE_DELTA, encoding="utf-8")
        subprocess.run(["git", "init", "--quiet", str(project)], check=True, capture_output=True)
        return project

    def issues(self, project: Path):
        return validate_project(project, self.workspace).issues

    def issue_codes(self, project: Path) -> set[str]:
        return {issue.code for issue in self.issues(project)}

    def test_neutral_bdx_l2_clean_room_fixture_passes(self) -> None:
        project = self.make_project()
        (project / ".env.example").write_text(
            "DATABASE_URL=postgresql://example:example@localhost/example\n"
            "API_TOKEN=<local-example-token>\n",
            encoding="utf-8",
        )
        result = validate_project(project, self.workspace)
        self.assertTrue(result.ok, result.issues)

    def test_ambiguous_level_and_missing_field_are_reported(self) -> None:
        project = self.make_project()
        context = project / "docs/project-context.md"
        content = context.read_text(encoding="utf-8")
        content = content.replace("`BDX-L2`", "`BDX-L1 | BDX-L2`")
        content = content.replace("- Supported local environments: Windows PowerShell and CI Linux\n", "")
        context.write_text(content, encoding="utf-8")
        codes = self.issue_codes(project)
        self.assertIn("invalid-backend-dx-level", codes)
        self.assertIn("missing-backend-dx-field", codes)

    def test_core_command_cannot_be_unexplained_na(self) -> None:
        project = self.make_project()
        context = project / "docs/project-context.md"
        content = context.read_text(encoding="utf-8").replace(
            "- doctor: `pwsh scripts/dev.ps1 doctor`",
            "- doctor: `N/A — reason`",
        )
        context.write_text(content, encoding="utf-8")
        codes = self.issue_codes(project)
        self.assertIn("missing-backend-dx-command", codes)
        self.assertIn("unexplained-backend-dx-na", codes)

    def test_reset_requires_enforced_local_or_test_guard(self) -> None:
        project = self.make_project()
        context = project / "docs/project-context.md"
        content = context.read_text(encoding="utf-8").replace(
            "APP_ENV must be local or test; production is refused",
            "operator checks the environment",
        )
        context.write_text(content, encoding="utf-8")
        self.assertIn("unsafe-backend-dx-reset", self.issue_codes(project))

    def test_generated_contract_requires_drift_check_command(self) -> None:
        project = self.make_project()
        context = project / "docs/project-context.md"
        content = context.read_text(encoding="utf-8").replace(
            "`pwsh scripts/dev.ps1 api-spec-check`",
            "OpenAPI generated from source",
        )
        context.write_text(content, encoding="utf-8")
        self.assertIn("missing-generated-contract-drift-check", self.issue_codes(project))

    def test_env_example_rejects_credential_like_value_without_echoing_it(self) -> None:
        project = self.make_project()
        secret = "opaque-credential-value-123456"
        (project / ".env.example").write_text(f"API_TOKEN={secret}\n", encoding="utf-8")
        issues = self.issues(project)
        self.assertIn("env-example-secret", {issue.code for issue in issues})
        self.assertTrue(all(secret not in issue.message for issue in issues))

    def test_bdx_l0_does_not_accept_delta_section(self) -> None:
        project = self.make_project()
        context = project / "docs/project-context.md"
        context.write_text(
            context.read_text(encoding="utf-8").replace("BDX-L2", "BDX-L0"),
            encoding="utf-8",
        )
        self.assertIn("backend-dx-l0-has-delta", self.issue_codes(project))

    def test_minimal_bdx_l0_delta_reports_only_root_cause(self) -> None:
        project = self.make_project()
        (project / "docs/project-context.md").write_text(
            "# Project context\n\n## Backend DX Delta\n\n"
            "- Applicability level: `BDX-L0`\n",
            encoding="utf-8",
        )
        self.assertEqual({"backend-dx-l0-has-delta"}, self.issue_codes(project))

    def test_delta_requires_thin_agents_route(self) -> None:
        project = self.make_project()
        (project / "AGENTS.md").write_text("# Project router\n", encoding="utf-8")
        self.assertIn("missing-backend-dx-route", self.issue_codes(project))

    def test_delta_in_another_document_is_rejected(self) -> None:
        project = self.make_project()
        (project / "docs/project-context.md").write_text("# Project context\n", encoding="utf-8")
        (project / "docs/ARCHITECTURE.md").write_text(COMPLETE_DELTA, encoding="utf-8")
        self.assertIn("misplaced-backend-dx-delta", self.issue_codes(project))

    def test_duplicate_heading_in_canonical_document_is_rejected(self) -> None:
        project = self.make_project()
        context = project / "docs/project-context.md"
        context.write_text(
            context.read_text(encoding="utf-8") + "\n## Backend DX Delta\n",
            encoding="utf-8",
        )
        self.assertIn("duplicate-backend-dx-delta", self.issue_codes(project))

    def test_embedded_global_policy_copy_is_rejected(self) -> None:
        project = self.make_project()
        context = project / "docs/project-context.md"
        context.write_text(
            context.read_text(encoding="utf-8")
            + "\nЭта policy — единый глобальный контракт воспроизводимой, discoverable, "
            "диагностируемой и безопасной разработки backend/runtime services.\n",
            encoding="utf-8",
        )
        self.assertIn("backend-dx-policy-copy", self.issue_codes(project))


class GlobalBackendDxContractTests(unittest.TestCase):
    def test_template_and_validator_contract_are_aligned(self) -> None:
        template = (ROOT / "templates/BACKEND_DX_DELTA_TEMPLATE.md").read_text(encoding="utf-8")
        fields = _markdown_bullet_fields(template)
        self.assertTrue(set(BACKEND_DX_REQUIRED_FIELDS).issubset(fields))
        self.assertTrue(set(BACKEND_DX_COMMAND_FIELDS).issubset(fields))

    def test_policy_routing_and_skill_source_are_connected(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        router = (ROOT / "rules/README.md").read_text(encoding="utf-8")
        skill = (ROOT / "skill-sources/backend-dx-audit/SKILL.md").read_text(encoding="utf-8")
        for content in (agents, router, skill):
            self.assertIn("rules/backend-dx.md", content)
        self.assertIn("AI-DEV-TEAM-BACKEND-DX-POLICY", agents)
        self.assertIn("backend-dx-audit", agents)

    def test_policy_declares_stable_ids_and_all_quality_gates(self) -> None:
        policy = (ROOT / "rules/backend-dx.md").read_text(encoding="utf-8")
        for identifier in (
            "BDX-BOOT-001", "BDX-CMD-001", "BDX-TOOL-001", "BDX-CFG-001",
            "BDX-SVC-001", "BDX-API-001", "BDX-DB-001", "BDX-TEST-001",
            "BDX-DATA-001", "BDX-ERR-001", "BDX-OBS-001", "BDX-JOB-001",
            "BDX-EXT-001", "BDX-CI-001", "BDX-DOC-001", "BDX-XPLAT-001",
        ):
            self.assertIn(identifier, policy)
        for gate in range(1, 13):
            self.assertIn(f"BDX-GATE-{gate:02d}", policy)

    def test_policy_relative_markdown_links_resolve(self) -> None:
        policy_path = ROOT / "rules/backend-dx.md"
        policy = policy_path.read_text(encoding="utf-8")
        targets = re.findall(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)", policy)
        self.assertTrue(targets)
        for target in targets:
            self.assertTrue((policy_path.parent / target).resolve().is_file(), target)

    def test_existing_roles_cover_backend_dx_without_new_role(self) -> None:
        roles = (
            "backend_engineer.toml",
            "database_engineer.toml",
            "test_engineer.toml",
            "reviewer.toml",
            "security_reviewer.toml",
            "devops_engineer.toml",
        )
        for filename in roles:
            content = (ROOT / "agents" / filename).read_text(encoding="utf-8")
            self.assertIn("Backend DX", content, filename)


if __name__ == "__main__":
    unittest.main()
