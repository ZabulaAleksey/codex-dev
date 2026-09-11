from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
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


def skill_block(
    skill_id: str,
    capability: str,
    trigger: str,
    *,
    status: str = "active",
    required_tools: tuple[str, ...] = (),
    validation: tuple[str, ...] = ("targeted_test",),
) -> str:
    tools = json.dumps(list(required_tools))
    validators = json.dumps(list(validation))
    return f'''\n[[skills]]
id = "{skill_id}"
source = "skill-sources/{skill_id}/SKILL.md"
scope = "global"
status = "{status}"
capabilities = ["{capability}"]
triggers = ["{trigger}"]
inputs = ["selected_stage"]
outputs = ["verified_result"]
required_tools = {tools}
required_context = ["selected_stage"]
stop_conditions = ["missing_contract"]
validation = {validators}
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
        ids = ("api-contract", "backend-integration", "database-migration", "frontend-ui", "old-seo")
        blocks = [skill_block("api-contract", "api.contract", "api"),
                  skill_block("backend-integration", "backend.integration", "backend"),
                  skill_block(
                      "database-migration", "database.migration", "migration",
                      required_tools=("migration_head", "real_database"),
                      validation=("downgrade_test", "real_database_gate", "upgrade_test"),
                  ),
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
            "required_capabilities": ["search.index"],
        })
        self.assertEqual("blocked", route["status"])
        self.assertEqual(["missing_capability:search.index"], route["issues"])

    def test_database_migration_requires_bidirectional_and_real_database_gates(self):
        route = pipeline.route_skills(self.registry(), {
            "stage_id": "DEV-SEP-F", "scope": "project", "risk": "high",
            "required_capabilities": ["database.migration"], "triggers": ["migration"],
            "available_tools": ["migration_head"],
        })
        self.assertEqual("blocked", route["status"])
        self.assertEqual(["missing_tool:real_database"], route["issues"])
        self.assertEqual(
            ["downgrade_test", "real_database_gate", "upgrade_test"], route["validators"]
        )

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


class AutomationPromotionTests(unittest.TestCase):
    def test_repeated_stable_manual_validator_qualifies_and_fingerprints(self):
        observation = {
            "procedure_id": "check_migration_head", "scope": "global", "occurrences": 3,
            "projects": ["billing", "checkout"], "stable_contract": True,
            "signals": ["expressible_manual_gate", "repeated_mechanical_sequence"],
            "disqualifiers": [], "source_kind": "task", "version": "1",
        }
        candidate = pipeline.detect_opportunity(observation)
        self.assertEqual("open", candidate["status"])
        self.assertTrue(candidate["fingerprint"])
        self.assertEqual("global", candidate["scope"])
        self.assertNotIn("procedure_id", candidate)
        self.assertFalse(candidate["write_authorized"])

    def test_one_off_unknown_unstable_or_negative_observation_is_refused(self):
        base = {"procedure_id": "investigate_defect", "scope": "global", "occurrences": 1,
                "projects": ["billing"], "stable_contract": False,
                "signals": ["repeated_instruction"], "disqualifiers": [],
                "source_kind": "review", "version": "1"}
        cases = (
            {},
            {"stable_contract": True, "occurrences": 4, "disqualifiers": ["unknown_research"]},
            {"stable_contract": True, "occurrences": 4, "disqualifiers": ["unstable_procedure"]},
            {"stable_contract": True, "occurrences": 4, "disqualifiers": ["negative_risk_benefit"]},
        )
        for extra in cases:
            with self.subTest(extra=extra):
                result = pipeline.detect_opportunity({**base, **extra})
                self.assertEqual("not_candidate", result["status"])
                self.assertEqual("keep_manual", result["action"])

    def test_same_fingerprint_deduplicates_and_closed_stays_closed(self):
        observation = {"procedure_id": "run_migration_check", "scope": "global", "occurrences": 3,
                       "projects": ["billing"], "stable_contract": True,
                       "signals": ["expressible_manual_gate"], "disqualifiers": [],
                       "source_kind": "task", "version": "1"}
        first = pipeline.detect_opportunity(observation)
        existing = {key: first[key] for key in ("id", "fingerprint", "status", "version")}
        duplicate = pipeline.detect_opportunity(observation, existing=[existing])
        self.assertEqual("reuse_candidate", duplicate["action"])
        closed = {**first, "status": "closed"}
        closed = {key: closed[key] for key in ("id", "fingerprint", "status", "version")}
        still_closed = pipeline.detect_opportunity(observation, existing=[closed])
        self.assertEqual("closed", still_closed["status"])
        reopened = pipeline.detect_opportunity({**observation, "reopen_reason": "new evidence"}, existing=[closed])
        self.assertEqual("open", reopened["status"])

    def test_promotion_selects_exact_durable_targets_and_preserves_placement(self):
        for pattern, target in pipeline.PROMOTION_TARGETS.items():
            with self.subTest(pattern=pattern):
                result = pipeline.decide_promotion(["generic.capability"], {
                    "candidate_status": "open", "pattern": pattern,
                    "capability_id": "new.generic", "semantics": "generic",
                    "consumer_projects": 2, "requested_scope": "global",
                    "stable_contract": True, "risk_acceptable": True,
                })
                self.assertEqual(target, result["target"])
                self.assertFalse(result["write_authorized"])

        project = pipeline.decide_promotion([], {
            "candidate_status": "approved", "pattern": "validation",
            "capability_id": "billing.format", "semantics": "project",
            "consumer_projects": 1, "requested_scope": "project",
            "stable_contract": True, "risk_acceptable": True})
        self.assertEqual("project", project["placement"]["recommended_scope"])

    def test_invalid_lifecycle_transition_fails_typed(self):
        with self.assertRaises(pipeline.SpecExecutionError) as caught:
            pipeline.transition_candidate({"status": "open", "fingerprint": "f"}, "closed")
        self.assertEqual("invalid_transition", caught.exception.code)

    def test_candidate_lifecycle_requires_evidence_before_verification(self):
        approved = pipeline.transition_candidate({"status": "open"}, "approved")
        implemented = pipeline.transition_candidate(approved, "implemented", "checkpoint:abc")
        verified = pipeline.transition_candidate(implemented, "verified", "tests:pass")
        closed = pipeline.transition_candidate(verified, "closed", "retention:recorded")
        self.assertEqual("closed", closed["status"])
        self.assertFalse(closed["write_authorized"])

    def test_detector_output_is_sanitized_and_never_authorizes_writes(self):
        candidate = pipeline.detect_opportunity({
            "procedure_id": "safe_identifier", "scope": "global", "occurrences": 3,
            "projects": ["billing"], "stable_contract": True,
            "signals": ["stable_io_contract"], "disqualifiers": [],
            "source_kind": "learning", "version": "1",
        })
        serialized = json.dumps(candidate, ensure_ascii=False)
        self.assertNotIn("prompt", serialized)
        self.assertNotIn("source_payload", serialized)
        self.assertFalse(candidate["write_authorized"])


class ContextEconomyAndRetirementTests(unittest.TestCase):
    def test_clean_bounded_route_is_clean(self):
        result = pipeline.analyze_context_economy({
            "context_sources": ["global_rules", "selected_stage", "SEP_SPEC"],
            "skills_loaded": ["backend_api"], "skills_used": ["backend_api"],
            "full_repo_scan": False, "full_repo_scan_reason": "",
            "full_master_load": False, "full_master_load_reason": "",
            "automation_reused": ["stage_selector"], "reasoning_fallback": "",
            "model_class": "LOW", "executor_route": "deterministic_tool",
            "live_state_source": "live_repo", "repeated_manual_procedure": False,
        })
        self.assertEqual("pass", result["status"])
        self.assertEqual([], result["issues"])

    def test_economy_reports_unused_skill_and_unjustified_scans(self):
        result = pipeline.analyze_context_economy({
            "context_sources": ["global_rules", "full_repository", "full_master"],
            "skills_loaded": ["backend_api", "frontend_ui"], "skills_used": ["backend_api"],
            "full_repo_scan": True, "full_repo_scan_reason": "",
            "full_master_load": True, "full_master_load_reason": "",
            "automation_reused": [], "reasoning_fallback": "", "model_class": "LOW",
            "executor_route": "deterministic_tool", "live_state_source": "live_repo",
            "repeated_manual_procedure": False,
        })
        self.assertIn("unused_skill:frontend_ui", result["issues"])
        self.assertIn("unjustified_full_repo_scan", result["issues"])
        self.assertIn("unjustified_full_master_load", result["issues"])

    def test_economy_reports_stale_handoff_strong_model_and_repeated_manual(self):
        result = pipeline.analyze_context_economy({
            "context_sources": ["stale_handoff", "selected_stage"],
            "skills_loaded": [], "skills_used": [], "full_repo_scan": False,
            "full_repo_scan_reason": "", "full_master_load": False,
            "full_master_load_reason": "", "automation_reused": [], "reasoning_fallback": "",
            "model_class": "FRONTIER", "executor_route": "deterministic_tool",
            "live_state_source": "handoff", "repeated_manual_procedure": True,
        })
        self.assertIn("stale_or_unverified_state_source", result["issues"])
        self.assertIn("strongest_model_for_deterministic_route", result["issues"])
        self.assertIn("repeated_manual_without_automation", result["issues"])

    def test_retirement_blocks_live_consumers_sole_capability_and_hash_drift(self):
        registry = self._retirement_registry()
        base = {"skill_id": "skill-a", "live_consumers": [],
                "required_capabilities": ["cap.one"], "replacement_id": "",
                "replacement_verified": False, "source_digest": "same", "runtime_digest": "same"}
        consumer = pipeline.retirement_preflight(registry, {**base, "live_consumers": ["route_1"]})
        self.assertIn("live_consumer:route_1", consumer["issues"])
        sole = pipeline.retirement_preflight(registry, base)
        self.assertIn("sole_required_capability_owner", sole["issues"])
        drift = pipeline.retirement_preflight(registry, {**base, "runtime_digest": "other"})
        self.assertIn("source_runtime_digest_mismatch", drift["issues"])

    def test_retirement_requires_deprecate_first_and_verified_replacement(self):
        registry = self._retirement_registry(active_target=True)
        request = {"skill_id": "skill-a", "live_consumers": [],
                   "required_capabilities": ["cap.one"], "replacement_id": "skill-b",
                   "replacement_verified": True, "source_digest": "same", "runtime_digest": "same"}
        result = pipeline.retirement_preflight(registry, request)
        self.assertEqual("blocked", result["status"])
        self.assertIn("deprecate_first", result["issues"])
        result = pipeline.retirement_preflight(self._retirement_registry(), request)
        self.assertEqual("eligible", result["status"])
        self.assertFalse(result["write_authorized"])

    def test_retirement_is_idempotent_for_already_retired_skill(self):
        registry = list(self._retirement_registry())
        registry[0] = replace(registry[0], status="retired")
        result = pipeline.retirement_preflight(registry, {
            "skill_id": "skill-a", "live_consumers": [], "required_capabilities": [],
            "replacement_id": "", "replacement_verified": False,
            "source_digest": "same", "runtime_digest": "same"})
        self.assertEqual("already_retired", result["status"])
        self.assertFalse(result["write_authorized"])

    @staticmethod
    def _retirement_registry(active_target=False):
        source = pipeline.SkillMetadata(
            id="skill-a", source="skill-sources/skill-a/SKILL.md", scope="global",
            status="active" if active_target else "deprecated", capabilities=("cap.one",),
            triggers=(), inputs=(), outputs=(), required_tools=(), required_context=(),
            stop_conditions=(), validation=(), version="1", maturity="documented_skill",
            executor_kind="skill_only", owner="global_dev", replacement="skill-b")
        replacement = replace(source, id="skill-b", source="skill-sources/skill-b/SKILL.md",
                              status="active", replacement="")
        return (source, replacement)

    def test_real_registry_loads_current_skills_when_present(self):
        path = Path(__file__).resolve().parents[1] / "skill-sources" / "registry.toml"
        if not path.exists():
            self.skipTest("repository registry is not present in this checkout")
        registry = pipeline.load_registry(path, path.parent.parent)
        self.assertGreaterEqual(len(registry), 1)
        self.assertEqual(len(registry), len({item.id for item in registry}))


if __name__ == "__main__":
    unittest.main()
