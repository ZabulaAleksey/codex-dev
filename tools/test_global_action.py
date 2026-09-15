"""Regression coverage for the explicit journal consumer path and discovery preflight."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from tools.global_action import ActionError, MAX_JOURNAL_BYTES, detect, init, load_catalog, lookup, preflight_candidates, record, _read_events


def event() -> dict:
    return {
        "schema_version": 1,
        "id": "DEV-GAJ-EVENT-001",
        "timestamp": "2026-09-15T10:00:00Z",
        "scope": "global",
        "task_class": "source-validation",
        "intent": "validate_source",
        "action_type": "validation",
        "actor": "script",
        "executor": "validate_context",
        "inputs_fingerprint": hashlib.sha256(b"source-validation-v1").hexdigest(),
        "resources_touched": ["MANIFEST.txt"],
        "result": "success",
        "evidence": ["tools/test_global_action.py"],
        "repeat_signature": "source_validation",
        "redactions_applied": True,
    }


class GlobalActionTest(unittest.TestCase):
    def test_oversized_log_and_redirected_parent_fail_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "journal"
            init(directory)
            path = directory / "events.jsonl"
            with path.open("wb") as output:
                output.truncate(MAX_JOURNAL_BYTES + 1)
            with self.assertRaises(ActionError):
                record(directory, event())
            self.assertEqual(path.stat().st_size, MAX_JOURNAL_BYTES + 1)
            link = root / "redirect"
            try:
                os.symlink(directory, link, target_is_directory=True)
            except OSError:
                return  # Windows without symlink privilege still covers the byte limit.
            with self.assertRaises(ActionError):
                init(link / "child", dry_run=True)

    def test_repeat_detector_is_configurable_pure_and_separates_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "journal"
            init(directory)
            self.assertEqual(detect(directory)["candidates"], [])
            first = event()
            second = event()
            second["id"] = "DEV-GAJ-EVENT-002"
            record(directory, first)
            record(directory, second)
            candidate = detect(directory)["candidates"][0]
            self.assertEqual(candidate["signals"], ["exact_repeat"])
            self.assertEqual(candidate["event_ids"], [first["id"], second["id"]])
            self.assertEqual(candidate["status"], "candidate_only")
            self.assertFalse(candidate["human_review_required"])
            self.assertEqual(preflight_candidates(directory)["decisions"][0]["status"], "reuse_existing")
            self.assertEqual(preflight_candidates(directory)["decisions"][0]["script"], "tools/validate_context.py")
            failed = event()
            failed["id"] = "DEV-GAJ-EVENT-003"
            failed["result"] = "failed"
            record(directory, failed)
            self.assertEqual(len(detect(directory)["candidates"]), 1)
            other_executor = event()
            other_executor["id"] = "DEV-GAJ-EVENT-005"
            other_executor["executor"] = "another_validator"
            record(directory, other_executor)
            self.assertEqual(len(detect(directory)["candidates"]), 1)
            other_repeat = copy.deepcopy(other_executor)
            other_repeat["id"] = "DEV-GAJ-EVENT-006"
            record(directory, other_repeat)
            self.assertEqual(
                sorted(decision["status"] for decision in preflight_candidates(directory)["decisions"]),
                ["promotion_review_required", "reuse_existing"],
            )
            config = Path(temporary) / "thresholds.json"
            config.write_text(json.dumps({
                "schema_version": 1, "exact_repeat": 3, "equivalent_repeat": 3,
                "expensive_repeat": 2, "expensive_task_classes": [],
                "safety_critical_task_classes": ["source-validation"],
            }), encoding="utf-8")
            self.assertEqual(detect(directory, config)["candidates"], [])
            third = event()
            third["id"] = "DEV-GAJ-EVENT-004"
            third["inputs_fingerprint"] = hashlib.sha256(b"another-safe-input").hexdigest()
            record(directory, third)
            analyzed = detect(directory, config)
            self.assertEqual(analyzed["candidates"][0]["signals"], ["equivalent_signature"])
            self.assertTrue(analyzed["candidates"][0]["human_review_required"])
            self.assertTrue(all(
                decision["status"] == "promotion_review_required"
                for decision in preflight_candidates(directory, config)["decisions"]
            ))
            config.write_text(json.dumps({
                "schema_version": 1, "exact_repeat": 1, "equivalent_repeat": 3,
                "expensive_repeat": 2, "expensive_task_classes": [],
                "safety_critical_task_classes": [],
            }), encoding="utf-8")
            with self.assertRaises(ActionError):
                detect(directory, config)

    def test_record_readback_idempotency_and_existing_tool_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "journal"
            self.assertEqual(init(directory, dry_run=True)["status"], "planned_init")
            self.assertFalse(directory.exists())
            init(directory)
            self.assertEqual(record(directory, event(), dry_run=True)["status"], "planned_record")
            self.assertEqual(_read_events(directory)[0], [])
            first = record(directory, event())
            self.assertEqual(first["status"], "recorded")
            self.assertEqual(record(directory, event())["status"], "noop")
            rows, raw = _read_events(directory)
            self.assertEqual(len(rows), 1)
            self.assertTrue(raw.endswith(b"\n"))
            choice = lookup("source-validation")
            self.assertEqual(choice["status"], "matched")
            self.assertEqual(choice["scripts"][0]["path"], "tools/validate_context.py")
            self.assertEqual(lookup("unknown-task")["status"], "fallback_required")

    def test_conflicting_id_and_corrupt_journal_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "journal"
            init(directory)
            record(directory, event())
            changed = event()
            changed["result"] = "failed"
            with self.assertRaises(ActionError):
                record(directory, changed)
            path = directory / "events.jsonl"
            before = path.read_bytes()
            self.assertEqual(path.read_bytes(), before)
            path.write_bytes(before + b'{"incomplete":')
            with self.assertRaises(ActionError):
                record(directory, event())

    def test_secret_and_unsafe_refs_never_append(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "journal"
            init(directory)
            for key, value in (
                ("intent", "password=example-value"),
                ("resources_touched", ["../config.toml"]),
                ("evidence", ["C:/private"]),
                ("redactions_applied", False),
            ):
                changed = copy.deepcopy(event())
                changed[key] = value
                with self.assertRaises(ActionError):
                    record(directory, changed)
            rows, _ = _read_events(directory)
            self.assertEqual(rows, [])

    def test_catalog_has_exact_existing_paths_and_rejects_shadow(self) -> None:
        entries = load_catalog()
        self.assertGreaterEqual(len(entries), 5)
        with tempfile.TemporaryDirectory() as temporary:
            bad = Path(temporary) / "catalog.json"
            bad.write_text(json.dumps({"schema_version": 1, "scripts": entries + [entries[0]]}), encoding="utf-8")
            with self.assertRaises(ActionError):
                load_catalog(bad)
            altered = copy.deepcopy(entries)
            altered[0]["path"] = "../config.toml"
            bad.write_text(json.dumps({"schema_version": 1, "scripts": altered}), encoding="utf-8")
            with self.assertRaises(ActionError):
                load_catalog(bad)


if __name__ == "__main__":
    unittest.main()
