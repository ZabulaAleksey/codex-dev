"""Read-only guard/receipt verifier for rules/prompt-queue-lifecycle.md.

Inputs are trusted executor attestations, never instructions copied from a queue page.
This module has no deletion, network, credential or command-from-input capability.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LIMIT = 1024 * 1024
SOURCE_KEYS = {"backend", "queue_id", "item_id", "revision"}
RECORD_KEYS = {
    "schema_version", "source", "execution_id", "prompt_type", "retention", "state",
    "authorization_ref", "project_revision", "required_checks", "project_checks", "checks",
    "dod", "result_ref", "blockers", "durable_required", "canonical_sources",
}
SNAPSHOT_KEYS = {"backend", "queue_id", "members", "item_revision", "complete", "observed_at", "capability"}
CHECK_KEYS = {"status", "evidence_ref", "reason"}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def exact(value: Any, keys: set[str]) -> None:
    if type(value) is not dict or set(value) != keys:
        raise ValueError("invalid object fields")


def string(value: Any, *, empty: bool = False) -> None:
    if type(value) is not str or len(value) > 4096 or (not empty and not value.strip()):
        raise ValueError("invalid string")


def strings(value: Any, *, unique: bool = False) -> None:
    if type(value) is not list or len(value) > 256:
        raise ValueError("invalid list")
    for entry in value:
        string(entry)
    if unique and len(set(value)) != len(value):
        raise ValueError("duplicate identifiers")


def check_valid(value: Any) -> None:
    exact(value, CHECK_KEYS)
    for field in CHECK_KEYS:
        string(value[field], empty=True)


def passed(value: dict) -> bool:
    return bool(value["evidence_ref"].strip()) and (
        value["status"] == "pass" or
        (value["status"] == "not_applicable" and bool(value["reason"].strip()))
    )


def validate_record(record: Any) -> None:
    exact(record, RECORD_KEYS)
    if type(record["schema_version"]) is not int or record["schema_version"] != 1:
        raise ValueError("unsupported schema")
    exact(record["source"], SOURCE_KEYS)
    for value in record["source"].values():
        string(value)
    for key in ("execution_id", "prompt_type", "retention", "state", "project_revision"):
        string(record[key])
    for key in ("authorization_ref", "result_ref"):
        string(record[key], empty=True)
    for key in ("required_checks", "project_checks"):
        strings(record[key], unique=True)
    strings(record["blockers"])
    if type(record["durable_required"]) is not bool:
        raise ValueError("invalid durable flag")
    checks = record["checks"]
    if type(checks) is not dict or len(checks) > 256:
        raise ValueError("invalid checks")
    for key, value in checks.items():
        string(key)
        check_valid(value)
    check_valid(record["dod"])
    sources = record["canonical_sources"]
    if type(sources) is not list or len(sources) > 256:
        raise ValueError("invalid canonical sources")
    for source in sources:
        exact(source, {"ref", "sha256", "verification_ref"})
        for value in source.values():
            string(value, empty=True)


def members_valid(members: Any) -> None:
    if type(members) is not dict or len(members) > 2048:
        raise ValueError("invalid membership")
    for key, value in members.items():
        string(key)
        string(value)


def snapshot_valid(snapshot: Any, now: datetime) -> bool:
    exact(snapshot, SNAPSHOT_KEYS)
    string(snapshot["backend"])
    string(snapshot["queue_id"])
    string(snapshot["item_revision"], empty=True)
    string(snapshot["capability"])
    string(snapshot["observed_at"])
    if type(snapshot["complete"]) is not bool:
        raise ValueError("invalid completeness")
    members_valid(snapshot["members"])
    at = datetime.fromisoformat(snapshot["observed_at"].replace("Z", "+00:00"))
    if at.tzinfo is None:
        raise ValueError("timestamp must have timezone")
    return snapshot["complete"] and 0 <= (now - at).total_seconds() <= 300


def result(record: dict, decision: str, reason: str) -> dict:
    return {"schema_version": 1, "action": "cleanup", "decision": decision, "reason": reason,
            "source": record["source"], "execution_id": record["execution_id"],
            "record_sha256": digest(record)}


def receipt_matches(record: dict, snapshot: dict, receipt: Any) -> bool:
    exact(receipt, {"schema_version", "record_sha256", "source", "execution_id", "before",
                    "after", "verification_ref"})
    exact(receipt["source"], SOURCE_KEYS)
    members_valid(receipt["before"])
    members_valid(receipt["after"])
    string(receipt["verification_ref"])
    target = record["source"]["item_id"]
    return (
        type(receipt["schema_version"]) is int and receipt["schema_version"] == 1
        and receipt["record_sha256"] == digest(record)
        and receipt["source"] == record["source"]
        and receipt["execution_id"] == record["execution_id"]
        and target in receipt["before"] and target not in receipt["after"]
        and {k: v for k, v in receipt["before"].items() if k != target} == receipt["after"]
        and receipt["after"] == snapshot["members"]
        and snapshot["item_revision"] == ""
    )


def evaluate(record: dict, snapshot: dict, *, now: datetime | None = None,
             receipt: dict | None = None) -> dict:
    """Fail closed. Caller verifies referenced evidence and fresh adapter observations."""
    validate_record(record)
    now = now or datetime.now(timezone.utc)
    deny = lambda reason: result(record, "retain", reason)
    blocked = lambda reason: result(record, "cleanup_blocked", reason)
    if record["retention"] != "auto" or record["prompt_type"] not in {
        "one_shot", "canonicalization_candidate"
    }:
        return deny("retention_protected_or_unknown")
    if record["state"] != "completed":
        return deny("execution_incomplete")
    if not record["authorization_ref"].strip():
        return deny("authorization_missing")
    if record["blockers"] or not record["result_ref"].strip() or not passed(record["dod"]):
        return deny("completion_evidence_missing")
    required = set(record["required_checks"]) | set(record["project_checks"])
    if not record["required_checks"] or set(record["checks"]) != required:
        return deny("check_inventory_mismatch")
    if any(not passed(record["checks"][key]) for key in required):
        return deny("checks_incomplete")
    if record["durable_required"] or record["prompt_type"] == "canonicalization_candidate":
        if not record["canonical_sources"]:
            return deny("canonicalization_missing")
        for source in record["canonical_sources"]:
            sha = source["sha256"]
            if (not source["ref"].strip() or not source["verification_ref"].strip()
                    or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha)):
                return deny("canonicalization_unverified")
    if not snapshot_valid(snapshot, now):
        return blocked("observation_incomplete_or_stale")
    if (snapshot["backend"] != record["source"]["backend"]
            or snapshot["queue_id"] != record["source"]["queue_id"]):
        return blocked("queue_mismatch")
    target = record["source"]["item_id"]
    if target not in snapshot["members"]:
        if receipt is not None and receipt_matches(record, snapshot, receipt):
            return result(record, "noop", "verified_previous_cleanup")
        return blocked("source_missing_without_verified_receipt")
    if receipt is not None:
        return blocked("source_restored_or_receipt_conflict")
    if snapshot["item_revision"] != record["source"]["revision"]:
        return blocked("source_revision_changed")
    if snapshot["capability"] != "exact_item_remove":
        return blocked("adapter_unavailable")
    return result(record, "allowed", "all_gates_passed")


def verify_cleanup(record: dict, before: dict, after: dict, *, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    decision = evaluate(record, before, now=now)
    if decision["decision"] != "allowed":
        return decision
    target = record["source"]["item_id"]
    if (not snapshot_valid(after, now) or after["backend"] != before["backend"]
            or after["queue_id"] != before["queue_id"]
            or datetime.fromisoformat(after["observed_at"].replace("Z", "+00:00"))
            < datetime.fromisoformat(before["observed_at"].replace("Z", "+00:00"))
            or after["item_revision"] != "" or target in after["members"]
            or after["members"] != {k: v for k, v in before["members"].items() if k != target}):
        return result(record, "cleanup_blocked", "readback_mismatch_or_incomplete")
    verified = result(record, "cleaned", "exact_target_removed_neighbors_preserved")
    verified["receipt"] = {
        "schema_version": 1, "record_sha256": digest(record), "source": record["source"],
        "execution_id": record["execution_id"], "before": before["members"],
        "after": after["members"], "verification_ref": after["observed_at"],
    }
    return verified


def unique_object(pairs: list) -> dict:
    obj: dict = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key")
        obj[key] = value
    return obj


def read_json(path: Path) -> dict:
    if str(path).startswith(("\\\\", "//")):
        raise ValueError("network paths forbidden")
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError("input too large")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("observation", type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--after", type=Path)
    group.add_argument("--receipt", type=Path)
    parser.add_argument("--project", type=Path, required=True, help="verify current Git HEAD")
    args = parser.parse_args()
    try:
        record = read_json(args.record)
        validate_record(record)
        revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=args.project,
                                  capture_output=True, check=True, text=True).stdout.strip()
        if revision != record["project_revision"]:
            decision = result(record, "cleanup_blocked", "project_revision_changed")
        elif args.after:
            decision = verify_cleanup(record, read_json(args.observation), read_json(args.after))
        else:
            receipt = read_json(args.receipt) if args.receipt else None
            decision = evaluate(record, read_json(args.observation), receipt=receipt)
    except (ValueError, TypeError, KeyError, OSError, RecursionError, subprocess.SubprocessError):
        decision = {"schema_version": 1, "action": "cleanup", "decision": "retain",
                    "reason": "invalid_or_unreadable_input"}
    print(json.dumps(decision, ensure_ascii=True, sort_keys=True))
    return 0 if decision["decision"] in {"allowed", "cleaned", "noop"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
