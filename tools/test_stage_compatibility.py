import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.stage_compatibility import LEGACY_FILES, STATUSES, inspect_compatibility


ROOT = Path(__file__).resolve().parents[1]
STAGES = """- Stage ID: DEV-TEST-A

# DEV-TEST-A - fixture

- Status: partial
- Master: DEV-TEST-001
- NEXT: DEV-TEST-B
- Checkpoint: abc123
- Blockers: none
- Evidence: L1
"""
LEGACY_PLAN = """# Plan
- Stage ID: DEV-TEST-A
- Master: DEV-TEST-001
- Status: partial
- NEXT: DEV-TEST-B
- Checkpoint: abc123
- Evidence: L1
"""
LEGACY_STATUS = """# Status
- Current stage: DEV-TEST-A
- Status: partial
"""
PROJECTION = {
    "current_stage": "DEV-TEST-A",
    "master_id": "DEV-TEST-001",
    "status": "partial",
    "next_selector": "DEV-TEST-B",
    "blockers": [],
    "checkpoint": "abc123",
    "evidence": ["L1"],
}


class StageCompatibilityTests(unittest.TestCase):
    def make(self, *, stages=None, plan=None, status=None):
        root = Path(tempfile.mkdtemp())
        (root / "prompts").mkdir()
        (root / "docs").mkdir()
        if stages is not None:
            (root / "prompts" / "STAGES.md").write_text(stages, encoding="utf-8", newline="")
        if plan is not None:
            (root / "docs" / "AI_PLAN.md").write_text(plan, encoding="utf-8", newline="")
        if status is not None:
            (root / "docs" / "AI_STATUS.md").write_text(status, encoding="utf-8", newline="")
        return root

    @staticmethod
    def manifest(plan=LEGACY_PLAN, status=LEGACY_STATUS, projection=PROJECTION):
        sources = []
        for path, content in (("docs/AI_PLAN.md", plan), ("docs/AI_STATUS.md", status)):
            sources.append({
                "path": path,
                "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "disposition": "retained",
            })
        value = {
            "schema_version": 1,
            "migration_id": "MIG-001",
            "state_owner": "prompts/STAGES.md",
            "legacy_sources": sources,
            "projection": projection,
        }
        return STAGES + "\n```stage-compatibility\n" + json.dumps(value, sort_keys=True) + "\n```\n"

    def test_pure_canonical(self):
        result = inspect_compatibility(self.make(stages=STAGES))
        self.assertEqual((result["classification"], result["route"]), ("canonical", "canonical"))
        self.assertTrue(result["runnable"])
        self.assertEqual(result["projection"], PROJECTION)
        self.assertIsNone(result["plan"])

    def test_pure_legacy_has_dry_run_plan(self):
        root = self.make(plan=LEGACY_PLAN, status=LEGACY_STATUS)
        result = inspect_compatibility(root)
        self.assertEqual((result["classification"], result["route"]), ("legacy", "migration_required"))
        self.assertFalse(result["runnable"])
        self.assertEqual(result["projection"], PROJECTION)
        self.assertFalse(result["plan"]["destructive_removals"])
        self.assertEqual(result["plan"]["preserve_sources"], ["docs/AI_PLAN.md", "docs/AI_STATUS.md"])

    def test_missing_legacy_next_is_explicitly_incomplete(self):
        plan = LEGACY_PLAN.replace("- NEXT: DEV-TEST-B\n", "")
        root = self.make(plan=plan, status=LEGACY_STATUS)
        result = inspect_compatibility(root)
        self.assertEqual(result["classification"], "legacy")
        self.assertIsNone(result["projection"]["next_selector"])
        self.assertIn("missing_next_selector", result["issues"])
        self.assertIsNone(result["plan"])
        self.assertFalse(result["runnable"])

    def test_partial_migration_without_selector_is_mixed(self):
        result = inspect_compatibility(self.make(
            stages="# brownfield STAGES\n", plan=LEGACY_PLAN, status=LEGACY_STATUS
        ))
        self.assertEqual((result["classification"], result["route"]), ("mixed", "migration_required"))
        self.assertIsNotNone(result["plan"])

    def test_mixed_matching_state_is_plan(self):
        result = inspect_compatibility(self.make(stages=STAGES, plan=LEGACY_PLAN, status=LEGACY_STATUS))
        self.assertEqual(result["classification"], "mixed")
        self.assertIsNotNone(result["plan"])

    def test_conflicting_legacy_state_fails_closed(self):
        result = inspect_compatibility(self.make(
            plan=LEGACY_PLAN, status=LEGACY_STATUS.replace("partial", "blocked")
        ))
        self.assertEqual((result["classification"], result["route"]), ("conflict", "migration_required"))
        self.assertIn("conflicting_legacy_status", result["issues"])
        self.assertIsNone(result["plan"])

    def test_none_sentinel_cannot_satisfy_blocked_or_terminal_evidence(self):
        blocked = LEGACY_PLAN.replace("partial", "blocked") + "- Blockers: none\n"
        completed = (LEGACY_PLAN.replace("partial", "completed")
                     .replace("abc123", "none").replace("L1", "none"))
        cases = (
            (blocked, "blocked", "missing_blockers_for_blocked_status"),
            (completed, "completed", "missing_checkpoint_for_terminal_status"),
            (completed, "completed", "missing_evidence_for_terminal_status"),
        )
        for plan, status_value, expected_issue in cases:
            with self.subTest(expected_issue=expected_issue):
                status = LEGACY_STATUS.replace("partial", status_value)
                result = inspect_compatibility(self.make(plan=plan, status=status))
                self.assertIn(expected_issue, result["issues"])
                self.assertIsNone(result["plan"])
                self.assertFalse(result["runnable"])

    def test_canonical_legacy_selector_mismatch_fails_closed(self):
        result = inspect_compatibility(self.make(
            stages=STAGES,
            plan=LEGACY_PLAN.replace("DEV-TEST-A", "DEV-OTHER"),
            status=LEGACY_STATUS.replace("DEV-TEST-A", "DEV-OTHER"),
        ))
        self.assertEqual(result["classification"], "conflict")
        self.assertIn("canonical_legacy_current_stage_mismatch", result["issues"])
        self.assertIsNone(result["plan"])

    def test_canonical_legacy_next_checkpoint_and_evidence_mismatch_fail_closed(self):
        changed = (LEGACY_PLAN.replace("DEV-TEST-B", "DEV-TEST-C")
                   .replace("abc123", "def456").replace("L1", "L2")
                   + "- Blockers: legacy-blocker\n")
        result = inspect_compatibility(self.make(stages=STAGES, plan=changed, status=LEGACY_STATUS))
        self.assertEqual(result["classification"], "conflict")
        self.assertEqual(
            set(result["issues"]),
            {
                "canonical_legacy_checkpoint_mismatch",
                "canonical_legacy_blockers_mismatch",
                "canonical_legacy_evidence_mismatch",
                "canonical_legacy_next_selector_mismatch",
            },
        )
        self.assertIsNone(result["plan"])
        self.assertFalse(result["runnable"])

    def test_already_migrated_uses_verified_same_file_projection(self):
        root = self.make(stages=self.manifest(), plan=LEGACY_PLAN, status=LEGACY_STATUS)
        result = inspect_compatibility(root)
        self.assertEqual((result["classification"], result["route"]), ("migrated", "canonical"))
        self.assertTrue(result["manifest_present"])
        self.assertEqual(result["projection"], PROJECTION)
        self.assertIsNone(result["plan"])

    def test_migrated_digest_drift_fails_closed(self):
        root = self.make(stages=self.manifest(), plan=LEGACY_PLAN + "\nchanged\n", status=LEGACY_STATUS)
        result = inspect_compatibility(root)
        self.assertEqual(result["classification"], "conflict")
        self.assertIn("legacy_source_set_or_digest_drift", result["issues"])
        self.assertIsNone(result["plan"])

    def test_invalid_manifest_fails_closed(self):
        root = self.make(stages=STAGES + "\n```stage-compatibility\n{}\n```\n")
        result = inspect_compatibility(root)
        self.assertEqual(result["classification"], "conflict")
        self.assertTrue(result["manifest_present"])

    def test_boolean_manifest_schema_version_fails_closed(self):
        stages = self.manifest().replace('"schema_version": 1', '"schema_version": true')
        result = inspect_compatibility(self.make(
            stages=stages, plan=LEGACY_PLAN, status=LEGACY_STATUS
        ))
        self.assertEqual(result["classification"], "conflict")
        self.assertIn("invalid_manifest_schema_version", result["issues"])

    def test_utf8_bom_canonical_stages_is_supported(self):
        result = inspect_compatibility(self.make(stages="\ufeff" + STAGES))
        self.assertEqual((result["classification"], result["route"]), ("canonical", "canonical"))

    def test_unicode_format_control_is_rejected(self):
        result = inspect_compatibility(self.make(
            plan=LEGACY_PLAN.replace("abc123", "abc\u202edef"), status=LEGACY_STATUS
        ))
        self.assertEqual(result["classification"], "conflict")
        self.assertIn("invalid_checkpoint", result["issues"])

    def test_none(self):
        result = inspect_compatibility(self.make())
        self.assertEqual((result["classification"], result["route"]), ("none", "none"))

    def test_bounded_input_is_structured_conflict(self):
        result = inspect_compatibility(self.make(plan="x" * 64_001))
        self.assertEqual(result["classification"], "conflict")
        self.assertTrue(result["issues"][0].startswith("read_error:"))

    def test_reader_does_not_use_unbounded_read_bytes(self):
        root = self.make(plan=LEGACY_PLAN, status=LEGACY_STATUS)
        with patch.object(Path, "read_bytes", side_effect=AssertionError("unbounded read")):
            result = inspect_compatibility(root)
        self.assertEqual(result["classification"], "legacy")

    def test_parent_symlink_escape_is_structured_conflict(self):
        root = self.make()
        external = Path(tempfile.mkdtemp())
        (external / "AI_PLAN.md").write_text(LEGACY_PLAN, encoding="utf-8", newline="")
        (root / "docs").rmdir()
        try:
            os.symlink(external, root / "docs", target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlink unavailable: {exc}")
        result = inspect_compatibility(root)
        self.assertEqual(result["classification"], "conflict")
        self.assertTrue(result["issues"][0].startswith("read_error:"))

    def test_idempotent_repeated_routing_same_repository(self):
        root = self.make(plan=LEGACY_PLAN, status=LEGACY_STATUS)
        first = inspect_compatibility(root)
        second = inspect_compatibility(root)
        self.assertEqual(json.dumps(first, ensure_ascii=False, sort_keys=True),
                         json.dumps(second, ensure_ascii=False, sort_keys=True))

    def test_existing_cme_cli_exposes_compatibility_mode(self):
        root = self.make(plan=LEGACY_PLAN, status=LEGACY_STATUS)
        completed = subprocess.run(
            [sys.executable, "-B", str(ROOT / "tools" / "master_execution.py"), str(root),
             "--compatibility"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["compatibility"]["classification"], "legacy")
        self.assertFalse(payload["compatibility"]["runnable"])

    def test_compatibility_cli_rejects_execution_options(self):
        root = self.make(plan=LEGACY_PLAN, status=LEGACY_STATUS)
        completed = subprocess.run(
            [sys.executable, "-B", str(ROOT / "tools" / "master_execution.py"), str(root),
             "--compatibility", "--worktree-root", str(root)],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertFalse(json.loads(completed.stdout)["ok"])

    def test_schema_matches_runtime_manifest_vocabulary(self):
        schema = json.loads((ROOT / "schemas" / "stage-compatibility.schema.json").read_text(
            encoding="utf-8"
        ))
        properties = schema["properties"]
        self.assertEqual(set(properties["projection"]["properties"]["status"]["enum"]), STATUSES)
        source_properties = properties["legacy_sources"]["items"]["properties"]
        self.assertEqual(source_properties["disposition"]["const"], "retained")
        self.assertEqual(set(source_properties["path"]["enum"]), set(LEGACY_FILES))


if __name__ == "__main__":
    unittest.main()
