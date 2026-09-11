from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys

try:
    from tools import spec_execution as pipeline
    from tools import master_execution as cme
except ImportError:  # pragma: no cover
    import spec_execution as pipeline
    import master_execution as cme


class CompactIntakeTests(unittest.TestCase):
    def test_direct_cli_help_runs_from_repository_root(self):
        root = Path(__file__).resolve().parents[1]
        completed = subprocess.run(
            [sys.executable, "-B", "tools/spec_execution.py", "--help"],
            cwd=root, capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("Specification", completed.stdout)

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

    def test_intake_rejects_secret_like_value_without_echo(self):
        with self.assertRaises(pipeline.SpecExecutionError) as caught:
            pipeline.normalize_intake({
                "entrypoint": "CONTINUE_EXISTING", "project": "codex-dev",
                "explicit_constraints": ["api_key=synthetic-sensitive-value"],
                "explicit_non_goals": [], "user_decisions": [],
            })
        self.assertEqual("secret_like_input", caught.exception.code)
        self.assertNotIn("synthetic-sensitive-value", str(caught.exception))


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
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        implementation = self.root / "tools" / "spec_execution.py"
        implementation.parent.mkdir()
        implementation.write_text("# trace fixture\n", encoding="utf-8")
        stages = self.root / "prompts" / "STAGES.md"
        stages.parent.mkdir()
        state = cme_state(2)
        state["slices"][0]["id"] = "DEV-SEP-C"
        state["slices"][0]["requirements"] = ["SEP-005"]
        state["slices"][0]["status"] = "completed"
        state["slices"][0]["required_evidence"] = ["L1", "L2"]
        state["slices"][0]["evidence"] = ["L1", "L2"]
        stages.write_text(
            "# Stages\n\n- Stage ID: `DEV-SEP-C`\n\n## DEV-SEP-C — Trace fixture\n\n"
            f"```master-execution\n{json.dumps(state)}\n```\n",
            encoding="utf-8",
        )
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
        contract = self.root / "specs" / "trace-contract.json"
        contract.parent.mkdir()
        contract.write_text(json.dumps({
            "stage_id": "DEV-SEP-C",
            "requirement_owners": {"SEP-005": "spec_execution"},
            "known_implementation_files": ["tools/spec_execution.py"],
            "known_validator_ids": ["targeted_tests"],
            "known_test_commands": ["spec_execution_tests"],
        }), encoding="utf-8")
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.name", "Codex Test"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(
            ["git", "-C", str(self.root), "commit", "-q", "-m", "trace fixture"], check=True
        )

    def registry(self):
        return pipeline.load_registry(self.path, self.root)

    def trace_contract(self):
        return pipeline.build_trace_contract(self.root, Path("specs/trace-contract.json"))

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
        self.assertEqual(
            ["global_invariants", "project_overlay", "live_repo_state", "stage.DEV-SEP-B"],
            route["required_context"][:4],
        )

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

    def test_registry_requires_real_leading_skill_frontmatter_and_contained_path(self):
        source = self.root / "skill-sources" / "api-contract" / "SKILL.md"
        source.write_text("prose before marker\nname: api-contract\n", encoding="utf-8")
        with self.assertRaisesRegex(pipeline.SpecExecutionError, "frontmatter"):
            self.registry()
        with self.assertRaises(pipeline.SpecExecutionError) as outside:
            pipeline.load_registry(self.path, self.root / "different-root")
        self.assertEqual("unsafe_registry_path", outside.exception.code)
        with self.assertRaises(pipeline.SpecExecutionError) as network:
            pipeline.load_registry(self.path, Path("//example.invalid/share"))
        self.assertEqual("unsafe_local_path", network.exception.code)

    def test_global_and_project_registry_delta_compose_without_shadowing(self):
        global_registry = self.registry()
        project_skill = replace(
            global_registry[0], id="billing-format", scope="project",
            source=".codex/skills/billing-format/SKILL.md",
            capabilities=("billing.format",), triggers=("billing",),
        )
        combined = pipeline.compose_registries(global_registry, (project_skill,))
        route = pipeline.route_skills(combined, {
            "stage_id": "DEV-SEP-F", "scope": "project", "triggers": ["billing"],
            "required_capabilities": ["billing.format"],
        })
        self.assertEqual(["billing-format"], route["selected_skill_ids"])
        with self.assertRaises(pipeline.SpecExecutionError) as duplicate:
            pipeline.compose_registries(
                global_registry,
                (replace(project_skill, capabilities=(global_registry[0].capabilities[0],)),),
            )
        self.assertEqual("ambiguous_capability_owner", duplicate.exception.code)

    def test_valid_critical_trace_requires_all_links_and_evidence(self):
        result = pipeline.validate_trace(self.registry(), {
            "schema_version": 1,
            "stage_id": "DEV-SEP-C", "stage_status": "completed",
            "requirements": [{
                "id": "SEP-005", "owner_component": "spec_execution", "stage_id": "DEV-SEP-C",
                "capability_ids": ["api.contract", "backend.integration"],
                "implementation_files": ["tools/spec_execution.py"],
                "validator_ids": ["targeted_tests"],
                "test_commands": ["spec_execution_tests"],
                "required_evidence": ["L1", "L2"], "evidence": ["L1", "L2"],
            }],
        }, self.trace_contract())
        self.assertEqual("valid", result["status"])

    def test_trace_blocks_missing_capability_evidence_and_completion(self):
        result = pipeline.validate_trace(self.registry(), {
            "schema_version": 1,
            "stage_id": "DEV-SEP-C", "stage_status": "completed",
            "requirements": [{
                "id": "SEP-005", "owner_component": "spec_execution", "stage_id": "DEV-SEP-C",
                "capability_ids": ["missing.capability"],
                "implementation_files": ["tools/spec_execution.py"],
                "validator_ids": [], "test_commands": [],
                "required_evidence": ["L1", "L2"], "evidence": ["L1"],
            }],
        }, self.trace_contract())
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
                "schema_version": 1,
                "stage_id": "DEV-SEP-C", "stage_status": "completed",
                "requirements": [row, dict(row)],
            }, self.trace_contract())

    def test_trace_rejects_unknown_requirement_owner_file_validator_and_command(self):
        result = pipeline.validate_trace(self.registry(), {
            "schema_version": 1,
            "stage_id": "DEV-SEP-C", "stage_status": "completed",
            "requirements": [{
                "id": "NO-SUCH-REQ", "owner_component": "bogus_owner",
                "stage_id": "DEV-SEP-C", "capability_ids": ["api.contract"],
                "implementation_files": ["missing.py"], "validator_ids": ["bogus_validator"],
                "test_commands": ["bogus_command"], "required_evidence": ["L1"],
                "evidence": ["L1"],
            }],
        }, self.trace_contract())
        self.assertEqual("blocked", result["status"])
        self.assertIn("missing_stage_requirement:NO-SUCH-REQ", result["issues"])
        self.assertIn("missing_implementation_file:NO-SUCH-REQ:missing.py", result["issues"])
        self.assertIn("missing_validator_reference:NO-SUCH-REQ:bogus_validator", result["issues"])
        self.assertIn("missing_test_command_reference:NO-SUCH-REQ:bogus_command", result["issues"])
        self.assertIn("unsupported_completion:NO-SUCH-REQ", result["issues"])

    def test_trace_rejects_windows_drive_and_link_like_artifact_paths(self):
        with self.assertRaises(pipeline.SpecExecutionError) as drive_error:
            pipeline._artifact_refs(
                ["C:relative.py"], "files", repository_root=self.root
            )
        self.assertEqual("unsafe_artifact_path", drive_error.exception.code)

        outside = self.root.parent / f"{self.root.name}-outside.py"
        outside.write_text("outside\n", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        link = self.root / "tools" / "outside-link.py"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("symlink creation is unavailable")
        with self.assertRaises(pipeline.SpecExecutionError) as link_error:
            pipeline._artifact_refs(
                ["tools/outside-link.py"], "files", repository_root=self.root
            )
        self.assertEqual("unsafe_artifact_path", link_error.exception.code)

        with self.assertRaises(pipeline.SpecExecutionError):
            pipeline._artifact_refs(
                ["tools/test.py && destructive"], "files", repository_root=self.root
            )

    def test_trace_contract_must_match_canonical_slice_requirements(self):
        contract = self.root / "specs" / "trace-contract.json"
        contract.write_text(json.dumps({
            "stage_id": "DEV-SEP-C", "requirement_owners": {"FAKE-REQ": "fake_owner"},
            "known_implementation_files": ["tools/spec_execution.py"],
            "known_validator_ids": ["targeted_tests"],
            "known_test_commands": ["spec_execution_tests"],
        }), encoding="utf-8")
        subprocess.run(["git", "-C", str(self.root), "add", "specs/trace-contract.json"], check=True)
        subprocess.run(
            ["git", "-C", str(self.root), "commit", "-q", "-m", "invalid trace fixture"], check=True
        )
        with self.assertRaises(pipeline.SpecExecutionError) as mismatch:
            pipeline.build_trace_contract(self.root, Path("specs/trace-contract.json"))
        self.assertEqual("requirement_contract_mismatch", mismatch.exception.code)

    def test_trace_contract_must_be_git_tracked(self):
        untracked = self.root / "specs" / "untracked-contract.json"
        untracked.write_text((self.root / "specs" / "trace-contract.json").read_text(), encoding="utf-8")
        with self.assertRaises(pipeline.SpecExecutionError) as caught:
            pipeline.build_trace_contract(self.root, Path("specs/untracked-contract.json"))
        self.assertEqual("untracked_trace_contract", caught.exception.code)

    def test_trace_contract_must_match_committed_bytes(self):
        contract = self.root / "specs" / "trace-contract.json"
        contract.write_text(contract.read_text() + "\n", encoding="utf-8")
        with self.assertRaises(pipeline.SpecExecutionError) as caught:
            pipeline.build_trace_contract(self.root, Path("specs/trace-contract.json"))
        self.assertEqual("stale_trace_contract", caught.exception.code)

    def test_trace_requires_full_canonical_coverage_evidence_and_fresh_status(self):
        contract = self.trace_contract()
        expanded = replace(
            contract,
            requirement_owners=contract.requirement_owners + (("SEP-006", "spec_execution"),),
        )
        row = {
            "id": "SEP-005", "owner_component": "spec_execution", "stage_id": "DEV-SEP-C",
            "capability_ids": ["api.contract"],
            "implementation_files": ["tools/spec_execution.py"],
            "validator_ids": ["targeted_tests"],
            "test_commands": ["spec_execution_tests"],
            "required_evidence": ["L1"], "evidence": ["L1"],
        }
        result = pipeline.validate_trace(self.registry(), {
            "schema_version": 1, "stage_id": "DEV-SEP-C", "stage_status": "completed",
            "requirements": [row],
        }, expanded)
        self.assertIn("evidence_contract_mismatch:SEP-005", result["issues"])
        self.assertIn("missing_evidence:SEP-005:L2", result["issues"])
        self.assertIn("missing_requirement_trace:SEP-006", result["issues"])
        with self.assertRaises(pipeline.SpecExecutionError) as stale:
            pipeline.validate_trace(self.registry(), {
                "schema_version": 1, "stage_id": "DEV-SEP-C", "stage_status": "running",
                "requirements": [row],
            }, contract)
        self.assertEqual("stale_trace_claim", stale.exception.code)

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

    def test_exception_cannot_place_project_semantics_in_global_dev(self):
        result = pipeline.decide_placement([], {
            "capability_id": "billing.format", "semantics": "project",
            "consumer_projects": 1, "requested_scope": "global",
            "exception": "put product semantics globally",
        })
        self.assertEqual("blocked", result["status"])
        self.assertEqual("scope_mismatch", result["reason"])


class CheapestSufficientExecutorTests(unittest.TestCase):
    def test_deterministic_route_is_cheapest_sufficient(self):
        decision = pipeline.choose_executor({
            "risk": "low", "novelty": "known", "deterministic_tools": ["stage_selector"]})
        self.assertEqual("deterministic_tool", decision["route"])
        self.assertEqual("available_deterministic_tool", decision["reason"])

    def test_deterministic_failure_escalates_with_stable_reason(self):
        decision = pipeline.choose_executor({
            "risk": "low", "novelty": "bounded", "deterministic_tools": ["stage_selector"],
            "deterministic_failure_class": "unsupported_input"})
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

    def test_security_integrity_failure_never_falls_back_to_model(self):
        decision = pipeline.choose_executor({
            "risk": "low", "novelty": "known", "deterministic_tools": ["signature_check"],
            "deterministic_failure_class": "security_integrity",
        })
        self.assertEqual("blocked", decision["route"])
        self.assertNotIn("signature", json.dumps(decision))

    def test_unc_input_path_is_rejected_before_io(self):
        with self.assertRaises(pipeline.SpecExecutionError) as caught:
            pipeline._read_json(Path("//example.invalid/share/input.json"))
        self.assertEqual("unsafe_local_path", caught.exception.code)


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
        self.assertEqual("high", candidate["priority"])
        self.assertEqual(
            ["expressible_manual_gate", "repeated_mechanical_sequence"],
            candidate["evidence_refs"],
        )
        self.assertEqual(["billing", "checkout", "task"], candidate["provenance_refs"])
        self.assertNotIn("procedure_id", candidate)
        self.assertFalse(candidate["write_authorized"])
        transitioned = pipeline.transition_candidate(candidate, "approved")
        for key in ("occurrences", "projects", "signals", "source_kind", "priority",
                    "evidence_refs", "provenance_refs"):
            self.assertEqual(candidate[key], transitioned[key])

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
        full_duplicate = pipeline.detect_opportunity(observation, existing=[first])
        self.assertEqual("reuse_candidate", full_duplicate["action"])
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

    def test_lifecycle_rejects_unknown_payload_fields_and_emits_allowlisted_state(self):
        with self.assertRaises(pipeline.SpecExecutionError):
            pipeline.transition_candidate({"status": "open", "secret": "do-not-echo"}, "approved")
        transitioned = pipeline.transition_candidate({
            "schema_version": 1, "id": "AUTO-123", "fingerprint": "a" * 64,
            "version": "1", "scope": "global", "status": "open",
        }, "approved")
        self.assertEqual(
            {"schema_version", "id", "fingerprint", "version", "scope", "status",
             "transition_evidence", "write_authorized"},
            set(transitioned),
        )


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
                "replacement_verified": False, "source_digest": "a" * 64,
                "runtime_digest": "a" * 64}
        consumer = pipeline.retirement_preflight(registry, {**base, "live_consumers": ["route_1"]})
        self.assertIn("live_consumer:route_1", consumer["issues"])
        sole = pipeline.retirement_preflight(registry, base)
        self.assertIn("sole_required_capability_owner", sole["issues"])
        drift = pipeline.retirement_preflight(registry, {**base, "runtime_digest": "b" * 64})
        self.assertIn("source_runtime_digest_mismatch", drift["issues"])

    def test_retirement_requires_deprecate_first_and_verified_replacement(self):
        registry = self._retirement_registry(active_target=True)
        request = {"skill_id": "skill-a", "live_consumers": [],
                   "required_capabilities": ["cap.one"], "replacement_id": "skill-b",
                   "replacement_verified": True, "source_digest": "a" * 64,
                   "runtime_digest": "a" * 64}
        result = pipeline.retirement_preflight(registry, request)
        self.assertEqual("blocked", result["status"])
        self.assertIn("deprecate_first", result["issues"])
        result = pipeline.retirement_preflight(self._retirement_registry(), request)
        self.assertEqual("review_required", result["status"])
        self.assertFalse(result["attestation_trusted"])
        self.assertFalse(result["write_authorized"])

    def test_retirement_is_idempotent_for_already_retired_skill(self):
        registry = list(self._retirement_registry())
        registry[0] = replace(registry[0], status="retired")
        result = pipeline.retirement_preflight(registry, {
            "skill_id": "skill-a", "live_consumers": [], "required_capabilities": [],
            "replacement_id": "", "replacement_verified": False,
            "source_digest": "a" * 64, "runtime_digest": "a" * 64})
        self.assertEqual("already_retired", result["status"])
        self.assertFalse(result["write_authorized"])

    def test_retirement_rejects_incomplete_inventory_and_invalid_digest(self):
        request = {
            "skill_id": "skill-a", "live_consumers": [], "required_capabilities": [],
            "replacement_id": "skill-b", "replacement_verified": True,
            "source_digest": "a" * 64, "runtime_digest": "a" * 64,
        }
        result = pipeline.retirement_preflight(self._retirement_registry(), request)
        self.assertIn("capability_inventory_incomplete:cap.one", result["issues"])
        with self.assertRaises(pipeline.SpecExecutionError) as digest:
            pipeline.retirement_preflight(
                self._retirement_registry(), {**request, "source_digest": "same", "runtime_digest": "same"}
            )
        self.assertEqual("invalid_digest", digest.exception.code)

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
        route = pipeline.route_skills(registry, {
            "stage_id": "DEV-SEP-F", "scope": "global",
            "required_capabilities": ["stage.implement"],
        })
        self.assertLess(
            route["required_context"].index("selected_spec"),
            route["required_context"].index("architecture_boundary"),
        )
        self.assertNotIn("selected_stage", route["required_context"])


if __name__ == "__main__":
    unittest.main()
