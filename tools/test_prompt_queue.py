from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from tools import prompt_queue as queue
    from tools.dev_paths import BRIDGE_MARKER
except ImportError:
    import prompt_queue as queue
    from dev_paths import BRIDGE_MARKER

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 9, 7, tzinfo=timezone.utc)


def passed():
    return {"status": "pass", "evidence_ref": "test-run:recorded-result", "reason": ""}


def record():
    return {
        "schema_version": 1,
        "source": {"backend": "notion", "queue_id": "queue-1", "item_id": "delta-1", "revision": "rev-1"},
        "execution_id": "execution-1", "prompt_type": "one_shot", "retention": "auto",
        "state": "completed", "authorization_ref": "explicit user request", "project_revision": "git-head",
        "required_checks": ["tests", "review"], "project_checks": [],
        "checks": {"tests": passed(), "review": passed()}, "dod": passed(),
        "result_ref": "docs/notes/evidence.md", "blockers": [],
        "durable_required": False, "canonical_sources": [],
    }


def snapshot():
    return {"backend": "notion", "queue_id": "queue-1", "members": {"delta-1": "link-hash-1", "master-1": "link-hash-2"},
            "item_revision": "rev-1", "complete": True, "observed_at": NOW.isoformat(),
            "capability": "exact_item_remove"}


class PromptQueueTests(unittest.TestCase):
    def setUp(self):
        self.record, self.before = record(), snapshot()

    def evaluate(self, expected, reason=None):
        value = queue.evaluate(self.record, self.before, now=NOW)
        self.assertEqual(expected, value["decision"])
        if reason:
            self.assertEqual(reason, value["reason"])
        return value

    def test_one_shot_completed_evidence_project_dod(self):
        result = self.evaluate("allowed")
        self.assertEqual("cleanup", result["action"])
        self.assertEqual(self.record["source"], result["source"])

    def test_partial_blocked_and_continuations_retain(self):
        for state in ("partial", "blocked", "needs_continuation", "running", "queued", "failed", "canonicalized"):
            with self.subTest(state=state):
                self.record["state"] = state
                self.evaluate("retain", "execution_incomplete")

    def test_master_reusable_reference_unknown_and_keep_retain(self):
        for kind in ("reusable_template", "reference", "unknown", "typo"):
            with self.subTest(kind=kind):
                self.record["prompt_type"] = kind
                self.evaluate("retain")
        self.record["prompt_type"] = "one_shot"
        for retention in ("keep", "unknown"):
            self.record["retention"] = retention
            self.evaluate("retain")
        self.record["prompt_type"] = "master_prompt"
        self.record["retention"] = "keep"
        self.evaluate("retain")

    def test_completed_auto_master_reaches_exact_item_guard(self):
        self.record["prompt_type"] = "master_prompt"
        self.evaluate("allowed")

    def test_completed_auto_child_and_launcher_reach_exact_item_guard(self):
        for kind in ("child_prompt", "one_shot_launcher"):
            with self.subTest(kind=kind):
                self.record["prompt_type"] = kind
                self.evaluate("allowed")

    def test_completed_historical_master_requires_zero_orphan_attestation(self):
        self.record["prompt_type"] = "historical_execution_master"
        self.record["retention"] = "keep"
        self.record["durable_required"] = True
        self.record["canonical_sources"] = [{
            "ref": "docs/notes/dev-master-orphan-audit.md", "sha256": "a" * 64,
            "verification_ref": "review+readback:pass",
        }]
        self.evaluate("retain", "historical_master_audit_incomplete")
        for check in ("orphan_audit", "runtime_parity", "regression"):
            self.record["required_checks"].append(check)
            self.record["checks"][check] = passed()
        self.evaluate("allowed")
        self.record["checks"]["runtime_parity"] = {
            "status": "not_applicable", "evidence_ref": "policy-only", "reason": "claimed N/A"}
        self.evaluate("retain", "historical_master_checks_require_pass")
        self.record["checks"]["runtime_parity"] = passed()
        self.record["durable_required"] = False
        self.evaluate("retain", "historical_master_requires_canonicalization")

    def test_partial_historical_master_is_retained(self):
        self.record["prompt_type"] = "historical_execution_master"
        self.record["retention"] = "keep"
        self.record["state"] = "partial"
        self.evaluate("retain", "execution_incomplete")

    def test_canonicalization_required_before_cleanup(self):
        self.record["prompt_type"] = "canonicalization_candidate"
        self.evaluate("retain", "canonicalization_missing")
        self.record["canonical_sources"] = [{"ref": "rules/policy.md", "sha256": "a" * 64,
                                             "verification_ref": "readback+tests:pass"}]
        self.evaluate("allowed")
        for key in ("ref", "sha256", "verification_ref"):
            original = self.record["canonical_sources"][0][key]
            self.record["canonical_sources"][0][key] = ""
            self.evaluate("retain", "canonicalization_unverified")
            self.record["canonical_sources"][0][key] = original

    def test_one_shot_durable_content_cannot_bypass_canonicalization(self):
        self.record["durable_required"] = True
        self.evaluate("retain", "canonicalization_missing")

    def test_completion_not_boolean_claim(self):
        for key in ("authorization_ref", "result_ref"):
            with self.subTest(key=key):
                value = self.record[key]
                self.record[key] = ""
                self.evaluate("retain")
                self.record[key] = value
        self.record["blockers"] = ["missing backend"]
        self.evaluate("retain")
        self.record["blockers"] = []
        self.record["dod"]["status"] = "not_run"
        self.evaluate("retain")

    def test_required_check_inventory_and_na_reason(self):
        del self.record["checks"]["tests"]
        self.evaluate("retain", "check_inventory_mismatch")
        for state in ("skip", "not_run", "fail", "pending", "not_applicable"):
            self.record["checks"]["tests"] = dict(passed(), status=state)
            self.evaluate("retain", "checks_incomplete")
        self.record["checks"]["tests"]["reason"] = "No product backend change in policy-only delta"
        self.evaluate("allowed")

    def test_generic_inheritance_and_additive_project_delta(self):
        self.evaluate("allowed")
        self.record["project_checks"] = ["project_dod"]
        self.evaluate("retain")
        self.record["checks"]["project_dod"] = passed()
        self.evaluate("allowed")
        self.record["checks"]["tests"]["status"] = "fail"
        self.evaluate("retain")

    def test_ambiguous_missing_changed_and_wrong_source(self):
        for key, value in (("backend", "wrong"), ("queue_id", "wrong"), ("item_revision", "changed"), ("complete", False)):
            with self.subTest(key=key):
                original = self.before[key]
                self.before[key] = value
                self.evaluate("cleanup_blocked")
                self.before[key] = original
        del self.before["members"]["delta-1"]
        self.evaluate("cleanup_blocked", "source_missing_without_verified_receipt")

    def test_adapter_and_freshness(self):
        self.before["capability"] = "unavailable"
        self.evaluate("cleanup_blocked", "adapter_unavailable")
        self.before["capability"] = "exact_item_remove"
        for seconds in (-301, 1):
            self.before["observed_at"] = (NOW + timedelta(seconds=seconds)).isoformat()
            self.evaluate("cleanup_blocked", "observation_incomplete_or_stale")

    def test_exact_readback_and_idempotent_repeat(self):
        after = copy.deepcopy(self.before)
        del after["members"]["delta-1"]
        after["item_revision"] = ""
        result = queue.verify_cleanup(self.record, self.before, after, now=NOW)
        self.assertEqual("cleaned", result["decision"])
        receipt = result["receipt"]
        self.assertEqual("noop", queue.evaluate(self.record, after, now=NOW, receipt=receipt)["decision"])
        self.assertEqual("cleanup_blocked", queue.evaluate(self.record, self.before, now=NOW,
                                                           receipt=receipt)["decision"])
        self.record["execution_id"] = "another-execution"
        self.assertEqual("cleanup_blocked", queue.evaluate(self.record, after, now=NOW, receipt=receipt)["decision"])

    def test_readback_cannot_hide_collateral_or_unconfirmed_removal(self):
        for mutation in ("target_remains", "neighbor_removed", "neighbor_changed", "new_neighbor", "older_readback", "incomplete"):
            with self.subTest(mutation=mutation):
                after = copy.deepcopy(self.before)
                del after["members"]["delta-1"]
                after["item_revision"] = ""
                if mutation == "target_remains":
                    after["members"]["delta-1"] = "link-hash-1"
                elif mutation == "neighbor_removed":
                    del after["members"]["master-1"]
                elif mutation == "neighbor_changed":
                    after["members"]["master-1"] = "changed"
                elif mutation == "new_neighbor":
                    after["members"]["other-1"] = "new"
                elif mutation == "older_readback":
                    after["observed_at"] = (NOW - timedelta(seconds=1)).isoformat()
                else:
                    after["complete"] = False
                self.assertEqual("cleanup_blocked", queue.verify_cleanup(self.record, self.before, after,
                                                                         now=NOW)["decision"])

    def test_strict_schema(self):
        for key, value in (("schema_version", True), ("durable_required", "false"),
                           ("required_checks", ["tests", "tests"]), ("extra", 1)):
            with self.subTest(key=key):
                invalid = dict(self.record, **{key: value})
                with self.assertRaises(ValueError):
                    queue.evaluate(invalid, self.before, now=NOW)

    def test_routing_uses_one_canonical_owner(self):
        for path in ("AGENTS.md", "rules/governance.md"):
            self.assertIn("rules/prompt-queue-lifecycle.md", (ROOT / path).read_text(encoding="utf-8"))
        policy = (ROOT / "rules/prompt-queue-lifecycle.md").read_text(encoding="utf-8")
        for path in ("AGENTS.md", "rules/governance.md"):
            self.assertNotIn(policy, (ROOT / path).read_text(encoding="utf-8"))

    def test_cli_real_git_project_and_malformed_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "AGENTS.md").write_text(BRIDGE_MARKER + "\n", encoding="utf-8")
            marker = root / ".codex/dev-project.toml"
            marker.parent.mkdir(parents=True)
            marker.write_text(
                'schema_version = 1\n\n[dev]\nmanaged = true\nrequires_global_dev = true\n'
                'minimum_version = "2026.09.10"\nrequired_capabilities = ["prompt-queue-v1"]\n'
                'required_contract_schema = 1\n', encoding="utf-8"
            )
            subprocess.run(["git", "add", "AGENTS.md", ".codex/dev-project.toml"], cwd=root, check=True)
            subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                            "commit", "-qm", "fixture"], cwd=root, check=True)
            self.record["project_revision"] = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                                                       cwd=root, text=True).strip()
            self.before["observed_at"] = datetime.now(timezone.utc).isoformat()
            record_path, observation_path = root / "record.json", root / "observation.json"
            record_path.write_text(json.dumps(self.record), encoding="utf-8")
            observation_path.write_text(json.dumps(self.before), encoding="utf-8")
            command = [sys.executable, "-B", str(ROOT / "tools/prompt_queue.py"), str(record_path),
                       str(observation_path), "--project", str(root)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(0, run.returncode, run.stderr)
            self.assertEqual("allowed", json.loads(run.stdout)["decision"])
            for data in ('{"schema_version":1,"schema_version":1}', '[' * 2000, 'x' * (queue.LIMIT + 1)):
                record_path.write_text(data, encoding="utf-8")
                run = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(2, run.returncode)
                self.assertEqual("invalid_or_unreadable_input", json.loads(run.stdout)["reason"])
            self.record["project_revision"] = "outdated"
            record_path.write_text(json.dumps(self.record), encoding="utf-8")
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual("project_revision_changed", json.loads(run.stdout)["reason"])

    def test_cli_plain_repo_is_not_enrolled_by_filesystem_location(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                            "commit", "--allow-empty", "-qm", "fixture"], cwd=root, check=True)
            self.record["project_revision"] = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip()
            self.before["observed_at"] = datetime.now(timezone.utc).isoformat()
            record_path, observation_path = root / "record.json", root / "observation.json"
            record_path.write_text(json.dumps(self.record), encoding="utf-8")
            observation_path.write_text(json.dumps(self.before), encoding="utf-8")
            run = subprocess.run(
                [sys.executable, "-B", str(ROOT / "tools/prompt_queue.py"), str(record_path),
                 str(observation_path), "--project", str(root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(2, run.returncode)
            self.assertEqual("project_not_dev_enabled", json.loads(run.stdout)["reason"])


if __name__ == "__main__":
    unittest.main()
