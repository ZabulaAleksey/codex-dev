from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path

try:
    from tools import spec_execution as pipeline
    from tools import master_execution as cme
except ImportError:  # pragma: no cover
    import spec_execution as pipeline
    import master_execution as cme


class CompactIntakeTests(unittest.TestCase):
    def test_continue_existing_preserves_explicit_user_constraints(self):
        result = pipeline.normalize_intake({
            "entrypoint": "CONTINUE_EXISTING", "project": "codex-dev",
            "master_or_goal": "DEV-SEP-001", "requested_change": "Implement DEV-SEP-B",
            "explicit_constraints": ["Python standard library only", "do not change production API"],
            "explicit_non_goals": ["no merge", "no queue cleanup"],
            "write_permissions": "feature branch only", "user_decisions": ["keep master prompt"],
        })
        self.assertEqual("CONTINUE_EXISTING", result["intent"])
        self.assertEqual("ready", result["status"])
        self.assertEqual("live_repository_router", result["next_owner"])
        self.assertEqual(["Python standard library only", "do not change production API"],
                         result["explicit_constraints"])

    def test_new_project_supports_exact_four_classes(self):
        for project_class in sorted(pipeline.PROJECT_CLASSES):
            with self.subTest(project_class=project_class):
                result = pipeline.normalize_intake({
                    "entrypoint": "NEW_PROJECT", "project": "example",
                    "master_or_goal": "Build a service", "requested_change": "Create initial slice",
                    "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
                    "project_class": project_class,
                })
                self.assertEqual(project_class, result["project_class"])
                self.assertEqual("project_framework_intake", result["next_owner"])

    def test_ambiguous_new_project_class_needs_decision(self):
        result = pipeline.normalize_intake({
            "entrypoint": "NEW_PROJECT", "project": "example",
            "master_or_goal": "Adopt or compose existing code",
            "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
        })
        self.assertEqual("needs_decision", result["status"])
        self.assertEqual("project_class_required", result["reason"])

    def test_intake_bounds_fail_closed(self):
        with self.assertRaises(pipeline.SpecExecutionError):
            pipeline.normalize_intake({
                "entrypoint": "CONTINUE_EXISTING", "project": "example",
                "requested_change": "x" * (pipeline.MAX_TEXT + 1),
                "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
            })

    def test_intake_cli_returns_machine_readable_result(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "intake.json"
            path.write_text(json.dumps({
                "entrypoint": "CONTINUE_EXISTING", "project": "codex-dev",
                "explicit_constraints": [], "explicit_non_goals": [], "user_decisions": [],
            }), encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                code = pipeline.main(["intake", "--input", str(path)])
            self.assertEqual(0, code)
            self.assertTrue(json.loads(output.getvalue())["ok"])


def skill_block(skill_id: str, capability: str, trigger: str, *, status: str = "active") -> str:
    return f'''\n[[skills]]
id = "{skill_id}"
source = "skill-sources/{skill_id}/SKILL.md"
scope = "global"
status = "{status}"
capabilities = ["{capability}"]
triggers = ["{trigger}"]
inputs = ["selected_stage"]
outputs = ["verified_result"]
required_tools = []
required_context = ["selected_stage"]
stop_conditions = ["missing_contract"]
validation = ["targeted_test"]
version = "1"
maturity = "documented_skill"
executor_kind = "skill_only"
owner = "global_dev"
replacement = ""
'''


class RegistryAndRouterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        ids = ("api-contract", "backend-integration", "frontend-ui", "old-seo")
        blocks = [skill_block("api-contract", "api.contract", "api"),
                  skill_block("backend-integration", "backend.integration", "backend"),
                  skill_block("frontend-ui", "frontend.ui", "frontend"),
                  skill_block("old-seo", "seo.audit", "seo", status="retired")]
        for skill_id in ids:
            directory = self.root / "skill-sources" / skill_id
            directory.mkdir(parents=True)
            (directory / "SKILL.md").write_text(
                f"---\nname: {skill_id}\ndescription: test\n---\n", encoding="utf-8")
        self.path = self.root / "skill-sources" / "registry.toml"
        self.path.write_text("schema_version = 1\n" + "".join(blocks), encoding="utf-8")

    def registry(self):
        return pipeline.load_registry(self.path, self.root)

    def test_router_requires_known_stage_and_scope(self):
        registry = self.registry()
        with self.assertRaises(pipeline.SpecExecutionError):
            pipeline.route_skills(registry, {"scope": "global", "triggers": ["backend"]})
        with self.assertRaises(pipeline.SpecExecutionError):
            pipeline.route_skills(registry, {"stage_id": "DEV-SEP-B", "scope": "unknown"})

    def test_relevant_only_route_is_deterministic(self):
        route = pipeline.route_skills(self.registry(), {
            "stage_id": "DEV-SEP-B", "scope": "global", "triggers": ["backend"],
            "required_capabilities": ["api.contract", "backend.integration"],
        })
        self.assertEqual("ready", route["status"])
        self.assertEqual(["api-contract", "backend-integration"], route["selected_skill_ids"])
        self.assertNotIn("frontend-ui", route["selected_skill_ids"])
        self.assertNotIn("old-seo", route["selected_skill_ids"])

    def test_missing_capability_is_typed_blocked_route(self):
        route = pipeline.route_skills(self.registry(), {
            "stage_id": "DEV-SEP-B", "scope": "global",
            "required_capabilities": ["database.migration"],
        })
        self.assertEqual("blocked", route["status"])
        self.assertEqual(["missing_capability:database.migration"], route["issues"])

    def test_incompatible_capability_owner_fails_registry(self):
        directory = self.root / "skill-sources" / "other-api"
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text(
            "---\nname: other-api\ndescription: test\n---\n", encoding="utf-8")
        self.path.write_text(self.path.read_text(encoding="utf-8") +
                             skill_block("other-api", "api.contract", "other"), encoding="utf-8")
        with self.assertRaisesRegex(pipeline.SpecExecutionError, "ambiguous capability owner"):
            self.registry()

    def test_valid_critical_trace_requires_all_links_and_evidence(self):
        result = pipeline.validate_trace(self.registry(), {
            "schema_version": 1, "stage_id": "DEV-SEP-C", "stage_status": "verified",
            "requirements": [{
                "id": "SEP-005", "owner_component": "spec_execution", "stage_id": "DEV-SEP-C",
                "capability_ids": ["api.contract", "backend.integration"],
                "implementation_files": ["tools/spec_execution.py"],
                "validator_ids": ["targeted_tests"],
                "test_commands": ["python -m unittest tools.test_spec_execution"],
                "required_evidence": ["L1", "L2"], "evidence": ["L1", "L2"],
            }],
        })
        self.assertEqual("valid", result["status"])

    def test_trace_blocks_missing_capability_evidence_and_completion(self):
        result = pipeline.validate_trace(self.registry(), {
            "schema_version": 1, "stage_id": "DEV-SEP-C", "stage_status": "completed",
            "requirements": [{
                "id": "SEP-005", "owner_component": "spec_execution", "stage_id": "DEV-SEP-C",
                "capability_ids": ["missing.capability"],
                "implementation_files": ["tools/spec_execution.py"],
                "validator_ids": [], "test_commands": [],
                "required_evidence": ["L1", "L2"], "evidence": ["L1"],
            }],
        })
        self.assertEqual("blocked", result["status"])
        self.assertTrue(any(item.startswith("missing_capability:") for item in result["issues"]))
        self.assertTrue(any(item.startswith("missing_evidence:") for item in result["issues"]))
        self.assertIn("unsupported_completion:SEP-005", result["issues"])

    def test_trace_duplicate_requirement_fails_closed(self):
        row = {
            "id": "SEP-005", "owner_component": "spec_execution", "stage_id": "DEV-SEP-C",
            "capability_ids": ["api.contract"], "implementation_files": ["tools/spec_execution.py"],
            "validator_ids": ["targeted_tests"], "test_commands": [],
            "required_evidence": ["L1"], "evidence": ["L1"],
        }
        with self.assertRaisesRegex(pipeline.SpecExecutionError, "duplicate requirement"):
            pipeline.validate_trace(self.registry(), {
                "schema_version": 1, "stage_id": "DEV-SEP-C", "stage_status": "verified",
                "requirements": [row, dict(row)],
            })

    def test_placement_reuses_generic_global_capability(self):
        result = pipeline.decide_placement(["git.evidence", "context.bounded"], {
            "capability_id": "git.evidence", "semantics": "generic", "consumer_projects": 2,
            "requested_scope": "project",
        })
        self.assertEqual("reuse_global", result["action"])
        self.assertEqual("duplicate_global_capability", result["reason"])

    def test_placement_keeps_project_semantics_out_of_global(self):
        result = pipeline.decide_placement([], {
            "capability_id": "billing.invoice_format", "semantics": "project",
            "consumer_projects": 1, "requested_scope": "project",
        })
        self.assertEqual("project", result["recommended_scope"])
        self.assertEqual("ready", result["status"])

    def test_placement_selects_shared_domain_for_multiple_related_projects(self):
        result = pipeline.decide_placement([], {
            "capability_id": "payments.eu_compliance", "semantics": "domain",
            "consumer_projects": 2, "requested_scope": "domain",
        })
        self.assertEqual("domain", result["recommended_scope"])

    def test_global_duplicate_requires_explicit_adapter_delta(self):
        request = {"capability_id": "git.evidence", "semantics": "generic",
                   "consumer_projects": 2, "requested_scope": "project"}
        rejected = pipeline.decide_placement(["git.evidence"], request)
        self.assertEqual("blocked", rejected["status"])
        accepted = pipeline.decide_placement(["git.evidence"], {
            **request, "adapter_delta": True, "exception": "billing path mapping"})
        self.assertEqual("ready", accepted["status"])
        self.assertEqual("project", accepted["recommended_scope"])

    def test_unknown_semantics_needs_decision(self):
        result = pipeline.decide_placement([], {
            "capability_id": "new.behavior", "semantics": "unknown",
            "consumer_projects": 1, "requested_scope": "project"})
        self.assertEqual("needs_decision", result["status"])


class CheapestSufficientExecutorTests(unittest.TestCase):
    def test_deterministic_route_is_cheapest_sufficient(self):
        decision = pipeline.choose_executor({
            "risk": "low", "novelty": "known", "deterministic_tools": ["stage_selector"]})
        self.assertEqual("deterministic_tool", decision["route"])
        self.assertEqual("available_deterministic_tool", decision["reason"])

    def test_deterministic_failure_escalates_with_stable_reason(self):
        decision = pipeline.choose_executor({
            "risk": "low", "novelty": "bounded", "deterministic_tools": ["stage_selector"],
            "deterministic_failure": "unsupported record"})
        self.assertEqual("cheap_bounded_model", decision["route"])
        self.assertTrue(decision["reason"].endswith(":deterministic_failure"))
        self.assertTrue(decision["promotion_review_required"])

    def test_unknown_high_risk_requires_stronger_reasoning(self):
        decision = pipeline.choose_executor({"risk": "high", "novelty": "unknown"})
        self.assertEqual("high_reasoning", decision["route"])
        self.assertEqual("unknown_or_high_risk", decision["reason"])

    def test_contract_conflict_requires_user_decision(self):
        decision = pipeline.choose_executor({
            "risk": "medium", "novelty": "bounded", "contract_conflict": True})
        self.assertEqual("user_decision", decision["route"])
        self.assertFalse(decision["model_change_authorized"])


def cme_state(schema_version=1):
    source = {"backend": "test", "queue_id": "q", "item_id": "m", "revision": "r",
              "prompt_type": "master_prompt", "retention": "keep"}
    common = {"id": "DEV-SEP-B", "master_id": "DEV-SEP-001", "title": "router", "status": "running",
              "predecessors": [], "dependencies": [], "worktree_track": "track", "checkpoint_before": "x",
              "checkpoint_after": "", "required_evidence": ["L1"], "evidence": [], "context_scope": ["SEP"],
              "model_class": "MEDIUM", "reasoning_effort": "medium", "stop_after": False}
    if schema_version == 2:
        common.update(requirements=["SEP-003"], capabilities=["cap.router"])
    return {"schema_version": schema_version, "state_revision": 1,
            "master": {"id": "DEV-SEP-001", "status": "running", "source": source},
            "tracks": [{"id": "track", "repository": "~/codex-dev", "worktree": "~/work/sep",
                        "branch": "feature/sep", "checkpoint": "x", "ownership": ["router"], "status": "active"}],
            "slices": [common], "blockers": [], "decisions": ["extend-cme"],
            "context_budget": {"max_chars": 1000, "max_items": 4, "max_contours": 2,
                                "max_decisions": 2, "max_evidence_threads": 2},
            "next_action": "continue", "integration": {"required": False, "reason": ""}}


class MasterExecutionCompatibilityTests(unittest.TestCase):
    def test_v1_state_remains_valid(self):
        self.assertEqual(1, cme.validate_state(cme_state(1))["schema_version"])

    def test_v2_slice_requires_and_retains_requirements_and_capabilities(self):
        state = cme.validate_state(cme_state(2))
        self.assertEqual(["SEP-003"], state["slices"][0]["requirements"])
        self.assertEqual(["cap.router"], state["slices"][0]["capabilities"])

    def test_v2_missing_per_slice_fields_fails_closed(self):
        state = cme_state(2)
        state["slices"][0].pop("capabilities")
        with self.assertRaises(cme.MasterExecutionError):
            cme.validate_state(state)


if __name__ == "__main__":
    unittest.main()
