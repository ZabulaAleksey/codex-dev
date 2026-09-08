from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.master_execution import (
    GitWorktreeAdapter,
    MasterExecutionError,
    RouteRequest,
    WorktreeFact,
    extract_master_state,
    route_worktree,
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
