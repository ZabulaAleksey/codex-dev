from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.master_execution import (
    GitWorktreeAdapter,
    ContextItem,
    FailureObservation,
    IntegrationSignals,
    MasterExecutionError,
    RouteRequest,
    StopSignals,
    WorktreeFact,
    apply_slice_result,
    build_handoff,
    classify_failure,
    evidence_decision,
    extract_master_state,
    next_execution_decision,
    integration_decision,
    required_evidence_for,
    render_launcher,
    resolve_context,
    route_worktree,
    validate_handoff,
    validate_state,
)


def state() -> dict:
    return {
        "schema_version": 1,
        "state_revision": 1,
        "master": {"id": "MASTER-1", "status": "partial", "source": {
            "backend": "notion", "queue_id": "queue-1", "item_id": "item-1",
            "revision": "rev-1", "prompt_type": "master_prompt", "retention": "keep",
        }},
        "tracks": [{
            "id": "track-a", "repository": "/repo", "worktree": "/worktrees/a",
            "branch": "feature/a", "checkpoint": "abc123", "ownership": ["rules/stages"],
            "status": "active",
        }],
        "slices": [{
            "id": "SLICE-A", "master_id": "MASTER-1", "title": "A", "status": "completed",
            "predecessors": [], "dependencies": [], "worktree_track": "track-a",
            "checkpoint_before": "", "checkpoint_after": "abc123", "required_evidence": ["L1"],
            "evidence": ["L1"], "context_scope": ["spec"], "model_class": "HIGH",
            "reasoning_effort": "high", "stop_after": False,
        }],
        "blockers": [], "decisions": [],
        "context_budget": {"max_chars": 6000, "max_items": 12, "max_contours": 4,
                           "max_decisions": 4, "max_evidence_threads": 6},
        "next_action": "continue", "integration": {"required": False, "reason": ""},
    }


class StateContractTests(unittest.TestCase):
    def test_embedded_state_parses(self) -> None:
        raw = "## MASTER\n\n```master-execution\n" + json.dumps(state()) + "\n```\n"
        self.assertEqual(extract_master_state(raw)["master"]["id"], "MASTER-1")

    def test_duplicate_json_key_fails_closed(self) -> None:
        raw = '```master-execution\n{"schema_version":1,"schema_version":1}\n```'
        with self.assertRaisesRegex(MasterExecutionError, "duplicate JSON key"):
            extract_master_state(raw)

    def test_duplicate_track_or_unknown_slice_track_fails_closed(self) -> None:
        duplicate = state()
        duplicate["tracks"].append(dict(duplicate["tracks"][0]))
        with self.assertRaises(MasterExecutionError):
            validate_state(duplicate)
        unknown = state()
        unknown["slices"][0]["worktree_track"] = "missing"
        with self.assertRaises(MasterExecutionError):
            validate_state(unknown)

    def test_cycle_fails_closed(self) -> None:
        cyclic = state()
        cyclic["slices"][0]["predecessors"] = ["SLICE-B"]
        second = dict(cyclic["slices"][0])
        second.update(id="SLICE-B", predecessors=["SLICE-A"])
        cyclic["slices"].append(second)
        with self.assertRaisesRegex(MasterExecutionError, "cyclic"):
            validate_state(cyclic)


class ExecutionControllerTests(unittest.TestCase):
    def chain(self) -> dict:
        value = state()
        value["slices"][0]["status"] = "completed"
        second = dict(value["slices"][0])
        second.update(id="SLICE-B", title="B", status="queued", predecessors=["SLICE-A"],
                      checkpoint_before="abc123", checkpoint_after="", evidence=[])
        third = dict(second)
        third.update(id="SLICE-C", title="C", predecessors=["SLICE-B"])
        value["slices"].extend([second, third])
        return value

    def test_two_slices_auto_advance_without_user_prompt(self) -> None:
        value = self.chain()
        first = next_execution_decision(value)
        self.assertEqual((first.action, first.slice_id), ("continue", "SLICE-B"))
        value["slices"][1]["status"] = "running"
        value = apply_slice_result(value, "SLICE-B", "completed", "def456", ["L1"])
        second = next_execution_decision(value)
        self.assertEqual((second.action, second.slice_id), ("continue", "SLICE-C"))

    def test_unverified_dependency_inserts_verification_gate(self) -> None:
        value = self.chain()
        value["slices"][0]["required_evidence"] = ["L2"]
        decision = next_execution_decision(value)
        self.assertEqual((decision.action, decision.slice_id), ("verification_gate", "SLICE-A"))

    def test_ambiguous_ready_set_stops(self) -> None:
        value = self.chain()
        value["slices"][2]["predecessors"] = ["SLICE-A"]
        decision = next_execution_decision(value)
        self.assertEqual(decision.action, "user_decision")

    def test_hard_blocker_and_stop_signals_stop_auto_continue(self) -> None:
        value = self.chain()
        value["blockers"] = [{"id": "B-1", "class": "pre_existing", "status": "active",
                              "blocking": True, "owner": "environment", "evidence": "check-1"}]
        self.assertEqual(next_execution_decision(value).action, "blocked")
        value["blockers"][0]["blocking"] = False
        self.assertEqual(next_execution_decision(value, StopSignals(context_overflow=True)).action, "handoff")
        self.assertEqual(next_execution_decision(value, StopSignals(integration_write_required=True)).action,
                         "integration_checkpoint")

    def test_terminal_result_without_evidence_downgrades(self) -> None:
        value = self.chain()
        value["slices"][1]["status"] = "running"
        value["slices"][1]["required_evidence"] = ["L1", "L2"]
        updated = apply_slice_result(value, "SLICE-B", "completed", "def456", ["L1"])
        self.assertEqual(updated["slices"][1]["status"], "implemented_unverified")


class LowContextTests(unittest.TestCase):
    def current(self) -> dict:
        value = state()
        value["slices"][0]["status"] = "running"
        value["slices"][0]["context_scope"] = ["routing", "SPEC:CME-005", "tests"]
        return value

    def items(self) -> list[ContextItem]:
        return [
            ContextItem("unrelated", "ignore", "other"),
            ContextItem("tests", "targeted tests", "tests", "thread-1"),
            ContextItem("routing", "nearest AGENTS", "governance"),
            ContextItem("SPEC:CME-005", "relevant requirement", "spec"),
        ]

    def test_resolver_preserves_declared_order_and_ignores_unrelated(self) -> None:
        result = resolve_context(self.current(), "SLICE-A", self.items())
        self.assertFalse(result.overflow)
        self.assertEqual([item.ref for item in result.items], ["routing", "SPEC:CME-005", "tests"])

    def test_missing_required_context_fails_closed(self) -> None:
        with self.assertRaisesRegex(MasterExecutionError, "missing context refs"):
            resolve_context(self.current(), "SLICE-A", self.items()[:-1])

    def test_budget_overflow_builds_complete_compact_launcher(self) -> None:
        value = self.current()
        value["context_budget"]["max_chars"] = 5
        result = resolve_context(value, "SLICE-A", self.items())
        self.assertTrue(result.overflow)
        self.assertEqual(result.items, ())
        for marker in ("MASTER-1", "feature/a", "/worktrees/a", "abc123", "current_slice"):
            self.assertIn(marker, result.launcher)

    def test_handoff_staleness_is_rejected(self) -> None:
        value = self.current()
        handoff = build_handoff(value, "SLICE-A")
        validate_handoff(handoff, value, "abc123")
        stale = dict(handoff)
        stale["state_revision"] = 0
        with self.assertRaisesRegex(MasterExecutionError, "state_revision"):
            validate_handoff(stale, value, "abc123")
        with self.assertRaisesRegex(MasterExecutionError, "Git checkpoint"):
            validate_handoff(handoff, value, "different")
        self.assertLess(len(render_launcher(handoff)), value["context_budget"]["max_chars"])


class EvidenceAndIntegrationTests(unittest.TestCase):
    def test_risk_classes_require_real_higher_evidence(self) -> None:
        self.assertEqual(required_evidence_for("static"), ("L1",))
        self.assertEqual(required_evidence_for("backend_concurrency")[-1], "L4")
        self.assertEqual(required_evidence_for("browser_runtime")[-1], "L5")
        self.assertEqual(required_evidence_for("external_manual")[-1], "L6")
        with self.assertRaises(MasterExecutionError):
            required_evidence_for("synthetic-is-real")

    def test_evidence_gate_does_not_inflate_partial_proof(self) -> None:
        item = state()["slices"][0]
        item["required_evidence"] = list(required_evidence_for("component_integration"))
        item["evidence"] = ["L1", "L2"]
        decision = evidence_decision(item)
        self.assertEqual(decision.action, "verification_gate")
        self.assertIn("L3", decision.reason)
        item["evidence"].append("L3")
        self.assertEqual(evidence_decision(item).action, "pass")

    def test_failure_classes_are_separated(self) -> None:
        self.assertEqual(classify_failure(FailureObservation(False, True, True)), "regression")
        self.assertEqual(classify_failure(FailureObservation(True, True, True)), "pre_existing")
        self.assertEqual(classify_failure(FailureObservation(False, False, True)), "unrelated_debt")
        self.assertEqual(classify_failure(FailureObservation(False, True, False)), "environment_unavailable")

    def test_integration_is_checkpoint_only_at_real_boundary(self) -> None:
        self.assertEqual(integration_decision(IntegrationSignals()).action, "defer_integration")
        decision = integration_decision(IntegrationSignals(dependent_track=True, divergence_risk=True))
        self.assertEqual(decision.action, "integration_checkpoint")
        self.assertNotIn("merge", decision.action)


class WorktreeRoutingTests(unittest.TestCase):
    def request(self, **overrides) -> RouteRequest:
        values = dict(master_id="MASTER-1", track_id="track-a", task_kind="continuation",
                      repository="/repo", branch="feature/a", worktree="/worktrees/a",
                      checkpoint="abc123", ownership=("rules/stages",))
        values.update(overrides)
        return RouteRequest(**values)

    def test_read_only_does_not_create_isolation(self) -> None:
        decision = route_worktree(state(), self.request(task_kind="read_only"))
        self.assertEqual(decision.action, "read_only")

    def test_same_track_continuation_reuses_registered_worktree(self) -> None:
        facts = [WorktreeFact("/worktrees/a", "abc123", "feature/a")]
        decision = route_worktree(state(), self.request(), facts)
        self.assertEqual(decision.action, "reuse")

    def test_changed_continuation_branch_fails_closed(self) -> None:
        facts = [WorktreeFact("/worktrees/a", "abc123", "feature/other")]
        with self.assertRaisesRegex(MasterExecutionError, "unavailable or changed"):
            route_worktree(state(), self.request(), facts)

    def test_independent_parallel_track_is_created_only_without_overlap(self) -> None:
        decision = route_worktree(state(), self.request(
            task_kind="parallel", track_id="track-b", branch="feature/b", worktree="/worktrees/b",
            ownership=("tools/master_execution.py",)))
        self.assertEqual(decision.action, "create")
        overlap = route_worktree(state(), self.request(
            task_kind="parallel", track_id="track-b", branch="feature/b", worktree="/worktrees/b"))
        self.assertEqual(overlap.action, "integration_checkpoint")

    def test_occupied_parallel_target_fails_closed(self) -> None:
        with self.assertRaisesRegex(MasterExecutionError, "occupied"):
            route_worktree(state(), self.request(
                task_kind="parallel", track_id="track-b", branch="feature/b", worktree="/worktrees/b",
                ownership=("tools/new.py",)), [WorktreeFact("/worktrees/b", "abc", "other")])


class RealGitWorktreeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "Test"], check=True)
        (self.repo / "tracked.txt").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "tracked.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "base"], check=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_adapter_creates_and_reads_back_isolated_worktree(self) -> None:
        worktrees = self.root / "worktrees"
        worktrees.mkdir()
        target = worktrees / "track-b"
        head = subprocess.run(["git", "-C", str(self.repo), "rev-parse", "HEAD"], check=True,
                              capture_output=True, text=True).stdout.strip()
        adapter = GitWorktreeAdapter(self.repo, worktrees)
        decision = route_worktree(state(), RouteRequest(
            master_id="MASTER-1", track_id="track-b", task_kind="parallel",
            repository=str(self.repo), branch="feature/track-b", worktree=str(target),
            checkpoint=head, ownership=("tools/new.py",)), adapter.snapshot())
        created = adapter.ensure(decision)
        self.assertEqual(created.branch, "feature/track-b")
        self.assertEqual(Path(created.path).resolve(), target.resolve())
        self.assertTrue((target / "tracked.txt").is_file())

    def test_adapter_rejects_target_outside_allowed_root(self) -> None:
        worktrees = self.root / "worktrees"
        worktrees.mkdir()
        adapter = GitWorktreeAdapter(self.repo, worktrees)
        from tools.master_execution import RouteDecision
        decision = RouteDecision("create", "test", "x", str(self.repo), "feature/x",
                                 str(self.root / "outside"), "HEAD")
        with self.assertRaisesRegex(MasterExecutionError, "escapes"):
            adapter.ensure(decision)


if __name__ == "__main__":
    unittest.main()
