from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

from tools import ai_policy_profiler as profiler


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "ai_policy_profiler.py"


class AiPolicyProfilerUnitTests(unittest.TestCase):
    def test_init_is_opt_in_idempotent_and_local_data_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertFalse((root / ".metrics").exists())
            first = profiler.initialize(root, "example-project")
            second = profiler.initialize(root, "example-project")
            self.assertEqual(first, second)
            config = json.loads((first / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(config, {"schema_version": 1, "enabled": True, "project_id": "example-project"})
            ignore = (first / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("*.jsonl", ignore)
            self.assertIn("reports/", ignore)
            for filename in set(profiler.EVENT_FILES.values()):
                self.assertTrue((first / filename).is_file())

    def test_identifier_metrics_and_payload_validation_fail_closed(self) -> None:
        with self.assertRaises(profiler.ProfilingError):
            profiler.make_event("command_run", "bad project", data={})
        with self.assertRaises(profiler.ProfilingError):
            profiler.make_event("command_run", "project", metrics={"tokens_total": float("nan")}, data={})
        with self.assertRaises(profiler.ProfilingError):
            profiler.make_event("command_run", "project", data={"stdout": "secret"})
        event = profiler.make_event(
            "command_run",
            "project",
            data={
                "command_class": "unit-test",
                "exit_code": 0,
                "success": True,
                "git_revision": None,
                "git_branch": None,
                "git_dirty": None,
                "started_at": profiler.utc_now(),
                "ended_at": profiler.utc_now(),
            },
        )
        serialized = json.dumps(event)
        self.assertNotIn("stdout", serialized)
        self.assertNotIn("command_args", serialized)
        self.assertNotIn("environment", serialized)

    def test_bounded_discovery_decisions_cover_stop_and_continue(self) -> None:
        missing = profiler.discovery_decision(
            elapsed_seconds=0,
            tokens_used=0,
            cost_used=0,
            wall_budget_seconds=None,
            token_budget=None,
            cost_budget=None,
            candidate_strength="strong",
            estimated_adaptation_cost=1,
            estimated_greenfield_cost=10,
        )
        self.assertEqual(missing["reason"], "BUDGET_REQUIRED")
        exhausted = profiler.discovery_decision(
            elapsed_seconds=10,
            tokens_used=50,
            cost_used=1,
            wall_budget_seconds=10,
            token_budget=100,
            cost_budget=2,
            candidate_strength="strong",
            estimated_adaptation_cost=1,
            estimated_greenfield_cost=10,
        )
        self.assertEqual(exhausted["reason"], "WALL_BUDGET_EXHAUSTED")
        no_candidate = profiler.discovery_decision(
            elapsed_seconds=1,
            tokens_used=1,
            cost_used=0,
            wall_budget_seconds=10,
            token_budget=100,
            cost_budget=None,
            candidate_strength="none",
            estimated_adaptation_cost=None,
            estimated_greenfield_cost=None,
        )
        self.assertEqual(no_candidate["reason"], "NO_CANDIDATE")
        break_even = profiler.discovery_decision(
            elapsed_seconds=1,
            tokens_used=1,
            cost_used=0,
            wall_budget_seconds=10,
            token_budget=100,
            cost_budget=None,
            candidate_strength="strong",
            estimated_adaptation_cost=10,
            estimated_greenfield_cost=10,
        )
        self.assertEqual(break_even["reason"], "GREENFIELD_BREAK_EVEN_REACHED")
        continuing = profiler.discovery_decision(
            elapsed_seconds=1,
            tokens_used=1,
            cost_used=0,
            wall_budget_seconds=10,
            token_budget=100,
            cost_budget=None,
            candidate_strength="strong",
            estimated_adaptation_cost=2,
            estimated_greenfield_cost=10,
        )
        self.assertEqual(continuing["decision"], "CONTINUE_DISCOVERY")

    def test_handoff_decision_keeps_batch_guard_and_explicit_learning_reason(self) -> None:
        economic = profiler.handoff_decision(
            human_seconds=25,
            ai_seconds=480,
            simple=True,
            special_expertise=False,
            repeated_actions=1,
            reason="ECONOMIC",
        )
        self.assertEqual(economic["decision"], "DELEGATE_TO_HUMAN")
        batch = profiler.handoff_decision(
            human_seconds=25,
            ai_seconds=480,
            simple=True,
            special_expertise=False,
            repeated_actions=50,
            reason="ECONOMIC",
        )
        self.assertEqual(batch["decision"], "KEEP_WITH_AI")
        learning = profiler.handoff_decision(
            human_seconds=300,
            ai_seconds=10,
            simple=True,
            special_expertise=False,
            repeated_actions=1,
            reason="LEARNING",
        )
        self.assertEqual(learning["decision"], "DELEGATE_TO_HUMAN")
        self.assertEqual(learning["reason"], "LEARNING")

    def test_reuse_false_positive_and_success(self) -> None:
        self.assertEqual(
            profiler.reuse_classification(selected=True, verified=True, actual_reuse_cost=90, greenfield_cost=60),
            "REUSE_FALSE_POSITIVE",
        )
        self.assertEqual(
            profiler.reuse_classification(selected=True, verified=False, actual_reuse_cost=10, greenfield_cost=60),
            "REUSE_FALSE_POSITIVE",
        )
        self.assertEqual(
            profiler.reuse_classification(selected=True, verified=True, actual_reuse_cost=20, greenfield_cost=60),
            "REUSE_SUCCESS",
        )

    def test_aggregation_reports_experiments_hotspots_reuse_and_overhead(self) -> None:
        events = [
            profiler.make_event(
                "stage_outcome",
                "project",
                stage_id="S-1",
                experiment_id="EXP-1",
                experiment_arm="baseline",
                task_class="small",
                metrics={"wall_seconds": 100, "effective_cost": 10, "tokens_total": 1000, "profiler_overhead_seconds": 1},
                data={"verified": True, "first_pass_dod": False, "human_interventions": 1, "post_completion_defects": 0, "outcome_label": "baseline"},
            ),
            profiler.make_event(
                "stage_outcome",
                "project",
                stage_id="S-2",
                experiment_id="EXP-1",
                experiment_arm="variant",
                task_class="small",
                metrics={"wall_seconds": 80, "effective_cost": 7, "tokens_total": 800, "profiler_overhead_seconds": 1},
                data={"verified": True, "first_pass_dod": True, "human_interventions": 0, "post_completion_defects": 0, "outcome_label": "variant"},
            ),
            profiler.make_event(
                "reuse_outcome",
                "project",
                data={"source": "local", "selected": True, "success": False, "verified": False, "discovery_cost": 10, "evaluation_cost": 5, "adaptation_cost": 50, "integration_cost": 20, "verification_cost": 5, "actual_reuse_cost": 90, "estimated_greenfield_cost": 60, "classification": "REUSE_FALSE_POSITIVE"},
            ),
        ]
        summary = profiler.aggregate(events)
        self.assertEqual(summary["productivity"]["verified_outcomes"], 2)
        self.assertEqual(summary["reuse"]["false_positive_rate"], 1.0)
        self.assertGreater(summary["ai_economics"]["profiler_overhead_ratio"], 0)
        experiment = summary["experiments"]["EXP-1"]
        self.assertFalse(experiment["causality_claim"])
        self.assertEqual(experiment["arms"]["baseline"]["verified_sample_size"], 1)
        self.assertEqual(experiment["arms"]["variant"]["median_effective_cost"], 7.0)
        self.assertEqual(experiment["comparison"]["median_effective_cost_delta"], -3.0)
        self.assertTrue(experiment["comparison"]["task_class_compatible"])

    def test_corrupt_input_does_not_overwrite_last_valid_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profiler.initialize(root, "project")
            event = profiler.make_event(
                "stage_outcome",
                "project",
                stage_id="STAGE-1",
                data={"verified": True, "first_pass_dod": True, "human_interventions": 0, "post_completion_defects": 0, "outcome_label": "ok"},
            )
            profiler.append_event(root, event, profiler.time.perf_counter())
            _, markdown_path, _ = profiler.write_report(root)
            original = markdown_path.read_bytes()
            with (root / ".metrics" / "events.jsonl").open("ab") as stream:
                stream.write(b"{not-json}\n")
            with self.assertRaises(profiler.ProfilingError):
                profiler.write_report(root)
            self.assertEqual(markdown_path.read_bytes(), original)

    def test_oversized_and_wrong_stream_events_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profiler.initialize(root, "project")
            events_path = root / ".metrics" / "events.jsonl"
            events_path.write_bytes(b"12345678901")
            with mock.patch.object(profiler, "MAX_FILE_BYTES", 10):
                with self.assertRaisesRegex(profiler.ProfilingError, "exceeds"):
                    profiler.read_events(root)
            stage = profiler.make_event(
                "stage_outcome",
                "project",
                stage_id="STAGE-1",
                data={"verified": True, "first_pass_dod": True, "human_interventions": 0, "post_completion_defects": 0, "outcome_label": "wrong-stream"},
            )
            events_path.write_text(json.dumps(stage) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(profiler.ProfilingError, "different stream"):
                profiler.read_events(root)

    def test_project_id_mismatch_fails_before_append(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profiler.initialize(root, "project-a")
            event = profiler.make_event(
                "command_run",
                "project-b",
                data={
                    "command_class": "unit-test",
                    "exit_code": 0,
                    "success": True,
                    "git_revision": None,
                    "git_branch": None,
                    "git_dirty": None,
                    "started_at": profiler.utc_now(),
                    "ended_at": profiler.utc_now(),
                },
            )
            with self.assertRaisesRegex(profiler.ProfilingError, "differs"):
                profiler.append_event(root, event, profiler.time.perf_counter())
            self.assertEqual((root / ".metrics" / "events.jsonl").read_text(encoding="utf-8"), "")

    def test_stream_symlink_escape_is_rejected_when_platform_supports_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            root.mkdir()
            outside = Path(directory) / "outside.jsonl"
            outside.write_text("", encoding="utf-8")
            profiler.initialize(root, "project")
            stream = root / ".metrics" / "events.jsonl"
            stream.unlink()
            try:
                stream.symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {type(exc).__name__}")
            event = profiler.make_event(
                "command_run",
                "project",
                data={
                    "command_class": "unit-test",
                    "exit_code": 0,
                    "success": True,
                    "git_revision": None,
                    "git_branch": None,
                    "git_dirty": None,
                    "started_at": profiler.utc_now(),
                    "ended_at": profiler.utc_now(),
                },
            )
            with self.assertRaisesRegex(profiler.ProfilingError, "escapes|symlinks"):
                profiler.append_event(root, event, profiler.time.perf_counter())
            self.assertEqual(outside.read_text(encoding="utf-8"), "")

    def test_concurrent_writers_produce_complete_jsonl_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profiler.initialize(root, "project")

            def write(index: int) -> None:
                event = profiler.make_event(
                    "command_run",
                    "project",
                    data={
                        "command_class": f"writer-{index}",
                        "exit_code": 0,
                        "success": True,
                        "git_revision": None,
                        "git_branch": None,
                        "git_dirty": None,
                        "started_at": profiler.utc_now(),
                        "ended_at": profiler.utc_now(),
                    },
                )
                profiler.append_event(root, event, profiler.time.perf_counter())

            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(write, range(20)))
            events = profiler.read_events(root)
            self.assertEqual(len(events), 20)
            self.assertEqual({event["data"]["command_class"] for event in events}, {f"writer-{index}" for index in range(20)})


class AiPolicyProfilerExecutablePathTests(unittest.TestCase):
    def run_cli(self, root: Path, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, "-B", str(CLI), *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, expected, result.stderr or result.stdout)
        return result

    def test_independent_project_init_run_stage_reuse_handoff_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            self.run_cli(root, "init", "--root", str(root), "--project-id", "fixture-project")
            run = self.run_cli(
                root,
                "run",
                "--root",
                str(root),
                "--stage-id",
                "STAGE-1",
                "--policy-id",
                "AEP_PASSIVE_OBSERVE_V1",
                "--experiment-id",
                "EXP-1",
                "--experiment-arm",
                "baseline",
                "--task-class",
                "small",
                "--command-class",
                "python-check",
                "--",
                sys.executable,
                "-c",
                "print('PRIVATE_OUTPUT_SENTINEL')",
            )
            self.assertIn("PRIVATE_OUTPUT_SENTINEL", run.stdout)
            common = (
                "--root",
                str(root),
                "--policy-id",
                "AEP_PASSIVE_OBSERVE_V1",
                "--experiment-id",
                "EXP-1",
                "--task-class",
                "small",
            )
            self.run_cli(root, "stage", *common, "--stage-id", "STAGE-1", "--experiment-arm", "baseline", "--verified", "--outcome-label", "baseline", "--wall-seconds", "100", "--tokens-total", "1000", "--effective-cost", "10")
            self.run_cli(root, "stage", *common, "--stage-id", "STAGE-2", "--experiment-arm", "variant", "--verified", "--first-pass-dod", "--outcome-label", "variant", "--wall-seconds", "80", "--tokens-total", "800", "--effective-cost", "7")
            self.run_cli(root, "reuse", "--root", str(root), "--stage-id", "STAGE-2", "--policy-id", "AEP_REUSE_ECONOMICS_V1", "--source", "local", "--selected", "--discovery-cost", "10", "--evaluation-cost", "5", "--adaptation-cost", "50", "--integration-cost", "20", "--verification-cost", "5", "--estimated-greenfield-cost", "60")
            self.run_cli(root, "handoff", "--root", str(root), "--stage-id", "STAGE-2", "--policy-id", "AEP_HUMAN_HANDOFF_V1", "--reason", "VISUAL_CHECK", "--action", "Open one page", "--expected-response", "Return status and error text", "--completed", "--estimated-ai-seconds", "480", "--estimated-human-seconds", "25")
            self.run_cli(root, "discovery", "--root", str(root), "--stage-id", "STAGE-2", "--policy-id", "AEP_BOUNDED_DISCOVERY_V1", "--elapsed-seconds", "10", "--wall-budget-seconds", "10", "--candidate-strength", "strong")
            self.run_cli(root, "agent", "--root", str(root), "--stage-id", "STAGE-2", "--agent-id", "reviewer", "--success", "--value-added", "Found one regression", "--wall-seconds", "30", "--tokens-in", "400", "--tokens-out", "200", "--tokens-total", "600", "--effective-cost", "2")
            report = self.run_cli(root, "report", "--root", str(root), "--json")
            summary = json.loads(report.stdout)
            self.assertEqual(summary["productivity"]["verified_outcomes"], 2)
            self.assertEqual(summary["reuse"]["false_positive_count"], 1)
            self.assertEqual(summary["human"]["completed_handoffs"], 1)
            self.assertIn("EXP-1", summary["experiments"])
            self.assertEqual(summary["agents"]["reviewer"]["successful_tasks"], 1)
            metrics_text = "\n".join(path.read_text(encoding="utf-8") for path in (root / ".metrics").glob("*.jsonl"))
            self.assertNotIn("PRIVATE_OUTPUT_SENTINEL", metrics_text)
            self.assertNotIn("print(", metrics_text)
            command_event = json.loads((root / ".metrics" / "events.jsonl").read_text(encoding="utf-8").splitlines()[0])
            self.assertGreater(command_event["metrics"]["wall_seconds"], 0)
            self.assertGreater(command_event["metrics"]["profiler_overhead_seconds"], 0)
            self.assertIsNone(command_event["data"]["git_revision"])
            self.assertTrue((root / ".metrics" / "reports" / "latest.md").is_file())

    def test_cli_decisions_are_read_only_and_do_not_require_init(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            decision = self.run_cli(root, "discovery-decision", "--elapsed-seconds", "1", "--wall-budget-seconds", "10", "--candidate-strength", "strong")
            self.assertEqual(json.loads(decision.stdout)["decision"], "CONTINUE_DISCOVERY")
            handoff = self.run_cli(root, "handoff-decision", "--human-seconds", "25", "--ai-seconds", "480", "--simple", "--reason", "ECONOMIC")
            self.assertEqual(json.loads(handoff.stdout)["decision"], "DELEGATE_TO_HUMAN")
            self.assertFalse((root / ".metrics").exists())


class AiPolicyProfilerContractTests(unittest.TestCase):
    def test_spec_schema_policy_and_stage_routes_are_versioned(self) -> None:
        spec = (ROOT / "specs" / "features" / "ai-policy-profiling.spec.md").read_text(encoding="utf-8")
        schema = json.loads((ROOT / "schemas" / "ai-policy-profiling.schema.json").read_text(encoding="utf-8"))
        policy = (ROOT / "rules" / "ai-policy-profiling.md").read_text(encoding="utf-8")
        for marker in ("FR-AEP-001", "FR-AEP-012", "SEC-AEP-001", "AC-AEP-010"):
            self.assertIn(marker, spec)
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)
        self.assertEqual(len(schema["allOf"]), len(profiler.EVENT_FILES))
        for marker in ("AEP_PASSIVE_OBSERVE_V1", "STOP_DISCOVERY", "Absent `.metrics/` = disabled", "automatic tuning"):
            self.assertIn(marker, policy)
        self.assertIn("rules/ai-policy-profiling.md", (ROOT / "rules" / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
