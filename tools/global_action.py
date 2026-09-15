#!/usr/bin/env python3
"""Opt-in sanitized global action journal and read-only DEV script discovery.

init/record only touch an explicit ignored journal directory. lookup/validate are read-only.
No command, hook, model, external service, or project state is invoked.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "schemas" / "script-registry.json"
THRESHOLDS = ROOT / "schemas" / "repeat-detector.json"
MAX_BYTES = 65536
MAX_EVENTS = 10000
ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,95}$")
SHA = re.compile(r"^[a-f0-9]{64}$")
SECRET = re.compile(
    r"(?i)(?:api[_-]?key|password|secret|token|authorization)\s*[:=]\s*\S+"
    r"|(?:github_pat|ghp|xox[baprs]|glpat|npm_)[-_][A-Za-z0-9_-]{8,}"
    r"|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|[a-z][a-z0-9+.-]*://[^/\s:@]+:[^@\s/]+@"
    r"|eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"
)
FIELDS = {
    "schema_version", "id", "timestamp", "scope", "task_class", "intent",
    "action_type", "actor", "executor", "inputs_fingerprint",
    "resources_touched", "result", "evidence", "duration_ms", "cost",
    "repeat_signature", "redactions_applied",
}
REQUIRED = FIELDS - {"duration_ms", "cost"}
CATALOG_FIELDS = {
    "name", "path", "version", "purpose", "task_classes", "inputs", "outputs",
    "side_effects", "idempotent", "dry_run", "risk_level", "platforms",
    "dependencies", "replaces_manual_pattern", "repeat_signature",
    "created_from_events", "last_verified", "status", "fallback", "checks",
}


class ActionError(ValueError):
    pass


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ActionError("duplicate JSON key")
        result[key] = value
    return result


def _json(raw: bytes) -> Any:
    if len(raw) > MAX_BYTES:
        raise ActionError("input exceeds limit")
    try:
        return json.loads(raw, object_pairs_hook=_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ActionError("invalid UTF-8 JSON") from exc


def _identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ActionError(f"invalid {label}")
    return value


def _ref(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) > 240 or "\\" in value:
        raise ActionError(f"invalid {label}")
    path = PurePosixPath(value)
    if path.is_absolute() or not value or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ActionError(f"unsafe {label}")
    if not all(ID.fullmatch(part) for part in path.parts):
        raise ActionError(f"invalid {label}")
    return value


def validate_event(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict) or set(data) != REQUIRED | (set(data) & {"duration_ms", "cost"}):
        raise ActionError("event has missing or unknown fields")
    if data["schema_version"] != 1:
        raise ActionError("unsupported event schema")
    for field in ("id", "task_class", "intent", "executor", "repeat_signature"):
        _identifier(data[field], field)
    if data["scope"] not in {"global", "project-overlay", "task"}:
        raise ActionError("invalid scope")
    if data["action_type"] not in {"command", "tool_call", "edit", "validation", "decision", "failure", "recovery"}:
        raise ActionError("invalid action_type")
    if data["actor"] not in {"human", "agent", "subagent", "hook", "script"}:
        raise ActionError("invalid actor")
    if data["result"] not in {"success", "partial", "failed", "blocked"}:
        raise ActionError("invalid result")
    if data["redactions_applied"] is not True:
        raise ActionError("redaction assertion required")
    if not isinstance(data["timestamp"], str) or not re.fullmatch(
        r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z", data["timestamp"]
    ):
        raise ActionError("timestamp must be UTC ISO-8601")
    try:
        if datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")).utcoffset() != timezone.utc.utcoffset(None):
            raise ValueError("not UTC")
    except ValueError as exc:
        raise ActionError("invalid UTC timestamp") from exc
    if not isinstance(data["inputs_fingerprint"], str) or not SHA.fullmatch(data["inputs_fingerprint"]):
        raise ActionError("inputs_fingerprint must be SHA-256")
    for field in ("resources_touched", "evidence"):
        values = data[field]
        if not isinstance(values, list) or len(values) > 16:
            raise ActionError(f"invalid {field}")
        for value in values:
            _ref(value, field)
    if "duration_ms" in data and data["duration_ms"] is not None and (
        type(data["duration_ms"]) is not int or not 0 <= data["duration_ms"] <= 86_400_000
    ):
        raise ActionError("invalid duration_ms")
    if "cost" in data and data["cost"] is not None and (
        type(data["cost"]) not in {int, float} or not 0 <= data["cost"] <= 1_000_000
    ):
        raise ActionError("invalid cost")
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    if SECRET.search(canonical):
        raise ActionError("secret-like value rejected")
    return data


def _journal_dir(path: Path, *, must_exist: bool) -> Path:
    candidate = path.expanduser().absolute()
    if candidate.is_symlink() or (candidate.exists() and not candidate.is_dir()):
        raise ActionError("unsafe journal directory")
    if must_exist and not candidate.is_dir():
        raise ActionError("journal not initialized")
    if candidate.exists() and candidate.resolve() != candidate:
        raise ActionError("journal directory redirects")
    return candidate


def _read_events(directory: Path) -> tuple[list[dict[str, Any]], bytes]:
    path = directory / "events.jsonl"
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ActionError("unsafe events file")
    raw = path.read_bytes() if path.exists() else b""
    if len(raw) > MAX_EVENTS * MAX_BYTES or (raw and not raw.endswith(b"\n")):
        raise ActionError("journal is oversized or incomplete")
    events: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in raw.splitlines():
        event = validate_event(_json(line))
        if event["id"] in seen:
            raise ActionError("duplicate event ID in journal")
        seen.add(event["id"])
        events.append(event)
    if len(events) > MAX_EVENTS:
        raise ActionError("too many events")
    return events, raw


def _lock(directory: Path) -> Path:
    lock = directory / ".append.lock"
    deadline = time.monotonic() + 5
    while True:
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(descriptor)
            return lock
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise ActionError("journal lock unavailable")
            time.sleep(.05)


def init(directory: Path, *, dry_run: bool = False) -> dict[str, Any]:
    target = _journal_dir(directory, must_exist=False)
    if dry_run:
        if target.exists():
            _read_events(target)
        return {"status": "planned_init", "path": str(target)}
    target.mkdir(mode=0o700, parents=True, exist_ok=True)
    _read_events(target)
    return {"status": "initialized", "path": str(target)}


def record(directory: Path, event: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
    target = _journal_dir(directory, must_exist=True)
    event = validate_event(event)
    if dry_run:
        events, _ = _read_events(target)
        for prior in events:
            if prior["id"] == event["id"]:
                if prior == event:
                    return {"status": "noop", "event_id": event["id"]}
                raise ActionError("conflicting event ID")
        return {"status": "planned_record", "event_id": event["id"]}
    lock = _lock(target)
    try:
        events, _ = _read_events(target)
        encoded = (json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()
        for prior in events:
            if prior["id"] == event["id"]:
                if prior == event:
                    return {"status": "noop", "event_id": event["id"]}
                raise ActionError("conflicting event ID")
        if len(events) >= MAX_EVENTS:
            raise ActionError("journal capacity reached")
        path = target / "events.jsonl"
        if path.is_symlink():
            raise ActionError("unsafe events file")
        descriptor = os.open(path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        try:
            if os.write(descriptor, encoded) != len(encoded):
                raise ActionError("short journal write")
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        read_back, _ = _read_events(target)
        if read_back[-1] != event:
            raise ActionError("journal read-back mismatch")
        return {"status": "recorded", "event_id": event["id"], "sha256": hashlib.sha256(encoded).hexdigest()}
    finally:
        lock.unlink(missing_ok=True)


def load_catalog(path: Path = CATALOG) -> list[dict[str, Any]]:
    if path.is_symlink() or not path.is_file():
        raise ActionError("unsafe or missing Script Registry")
    data = _json(path.read_bytes())
    if not isinstance(data, dict) or set(data) != {"schema_version", "scripts"} or data["schema_version"] != 1:
        raise ActionError("unsupported Script Registry")
    scripts = data["scripts"]
    if not isinstance(scripts, list) or not 1 <= len(scripts) <= 128:
        raise ActionError("invalid Script Registry entries")
    seen: set[str] = set()
    for item in scripts:
        if not isinstance(item, dict) or set(item) != CATALOG_FIELDS:
            raise ActionError("invalid Script Registry entry")
        name = _identifier(item["name"], "script name")
        if name in seen:
            raise ActionError("duplicate script name")
        seen.add(name)
        path_ref = _ref(item["path"], "script path")
        source = ROOT / path_ref
        if source.is_symlink() or not source.is_file() or source.resolve() != source.absolute():
            raise ActionError("script path is missing or redirects")
        for field in ("version", "purpose", "inputs", "outputs", "side_effects", "fallback",
                      "replaces_manual_pattern", "repeat_signature", "last_verified"):
            if not isinstance(item[field], str) or len(item[field]) > 240 or SECRET.search(item[field]):
                raise ActionError(f"invalid {field}")
        for field in ("task_classes", "platforms", "dependencies", "created_from_events", "checks"):
            values = item[field]
            if not isinstance(values, list) or len(values) > 16 or not all(
                isinstance(value, str) and len(value) <= 120 and not SECRET.search(value) for value in values
            ):
                raise ActionError(f"invalid {field}")
        if item["status"] not in {"active", "experimental", "quarantined", "deprecated"}:
            raise ActionError("invalid script status")
        if item["risk_level"] not in {"low", "medium", "high"}:
            raise ActionError("invalid script risk")
        for field in ("idempotent", "dry_run"):
            if type(item[field]) is not bool:
                raise ActionError(f"invalid {field}")
    return scripts


def lookup(task_class: str) -> dict[str, Any]:
    _identifier(task_class, "task class")
    matched = [item for item in load_catalog() if task_class in item["task_classes"] and item["status"] == "active"]
    return {
        "status": "matched" if matched else "fallback_required",
        "task_class": task_class,
        "scripts": [{"name": item["name"], "path": item["path"], "risk_level": item["risk_level"],
                     "side_effects": item["side_effects"], "checks": item["checks"]} for item in matched],
    }


def load_thresholds(path: Path = THRESHOLDS) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ActionError("unsafe or missing repeat detector config")
    data = _json(path.read_bytes())
    if not isinstance(data, dict) or set(data) != {
        "schema_version", "exact_repeat", "equivalent_repeat", "expensive_repeat",
        "expensive_task_classes", "safety_critical_task_classes",
    } or data["schema_version"] != 1:
        raise ActionError("invalid repeat detector config")
    for field in ("exact_repeat", "equivalent_repeat", "expensive_repeat"):
        if type(data[field]) is not int or not 2 <= data[field] <= 20:
            raise ActionError(f"invalid {field} threshold")
    for field in ("expensive_task_classes", "safety_critical_task_classes"):
        values = data[field]
        if not isinstance(values, list) or len(values) > 32 or not all(isinstance(v, str) for v in values):
            raise ActionError(f"invalid {field}")
        for value in values:
            _identifier(value, field)
        if len(values) != len(set(values)):
            raise ActionError(f"duplicate {field}")
    return data


def detect(directory: Path, config_path: Path = THRESHOLDS) -> dict[str, Any]:
    """Pure candidate miner; never executes or updates the promotion engine."""
    events, _ = _read_events(_journal_dir(directory, must_exist=True))
    config = load_thresholds(config_path)
    groups: dict[tuple[str, str, str, str, str], list[dict[str, Any]]] = {}
    for event in events:
        key = (
            event["scope"], event["task_class"], event["repeat_signature"],
            event["result"], event["executor"],
        )
        groups.setdefault(key, []).append(event)
    candidates: list[dict[str, Any]] = []
    for key, rows in sorted(groups.items()):
        fingerprints = {row["inputs_fingerprint"] for row in rows}
        exact_counts: dict[str, int] = {}
        for row in rows:
            fingerprint = row["inputs_fingerprint"]
            exact_counts[fingerprint] = exact_counts.get(fingerprint, 0) + 1
        reasons: list[str] = []
        if max(exact_counts.values()) >= config["exact_repeat"]:
            reasons.append("exact_repeat")
        if len(fingerprints) >= 2 and len(rows) >= config["equivalent_repeat"]:
            reasons.append("equivalent_signature")
        if key[1] in config["expensive_task_classes"] and len(rows) >= config["expensive_repeat"]:
            reasons.append("expensive_repeat")
        if not reasons:
            continue
        signature = "|".join(key)
        candidates.append({
            "id": "AUTO-" + hashlib.sha256(signature.encode()).hexdigest()[:20],
            "fingerprint": hashlib.sha256(signature.encode()).hexdigest(),
            "scope": key[0],
            "task_class": key[1],
            "repeat_signature": key[2],
            "result": key[3],
            "executor": key[4],
            "occurrences": len(rows),
            "event_ids": [row["id"] for row in rows],
            "signals": reasons,
            "human_review_required": key[1] in config["safety_critical_task_classes"],
            "proposed_path": "spec_execution_promotion_review",
            "status": "candidate_only",
        })
    return {"status": "analyzed", "events": len(events), "candidates": candidates}


def preflight_candidates(directory: Path, config_path: Path = THRESHOLDS) -> dict[str, Any]:
    """Deduplicate only an exact named existing executor; other candidates need review."""
    analysis = detect(directory, config_path)
    scripts = load_catalog()
    decisions: list[dict[str, Any]] = []
    for candidate in analysis["candidates"]:
        exact = [
            script for script in scripts
            if script["status"] == "active"
            and candidate["task_class"] in script["task_classes"]
            and candidate["executor"] == script["name"]
        ]
        reusable = bool(exact) and not candidate["human_review_required"]
        decisions.append({
            "candidate_id": candidate["id"],
            "status": "reuse_existing" if reusable else "promotion_review_required",
            "script": exact[0]["path"] if reusable else None,
            "human_review_required": candidate["human_review_required"],
            "reason": "exact_active_executor" if reusable else "no_safe_exact_reuse",
        })
    return {"status": "preflighted", "events": analysis["events"], "decisions": decisions}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "record", "validate"):
        sub = commands.add_parser(command)
        sub.add_argument("--journal-dir", type=Path, required=True)
        if command in {"init", "record"}:
            sub.add_argument("--dry-run", action="store_true")
        if command == "record":
            sub.add_argument("--event", type=Path, required=True)
    commands.add_parser("catalog")
    lookup_command = commands.add_parser("lookup")
    lookup_command.add_argument("task_class")
    detect_command = commands.add_parser("detect")
    detect_command.add_argument("--journal-dir", type=Path, required=True)
    detect_command.add_argument("--thresholds", type=Path, default=THRESHOLDS)
    preflight_command = commands.add_parser("preflight")
    preflight_command.add_argument("--journal-dir", type=Path, required=True)
    preflight_command.add_argument("--thresholds", type=Path, default=THRESHOLDS)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = init(args.journal_dir, dry_run=args.dry_run)
        elif args.command == "record":
            if args.event.is_symlink() or not args.event.is_file():
                raise ActionError("unsafe or missing event input")
            result = record(args.journal_dir, _json(args.event.read_bytes()), dry_run=args.dry_run)
        elif args.command == "validate":
            events, _ = _read_events(_journal_dir(args.journal_dir, must_exist=True))
            result = {"status": "valid", "events": len(events)}
        elif args.command == "catalog":
            result = {"status": "valid", "scripts": len(load_catalog())}
        elif args.command == "detect":
            result = detect(args.journal_dir, args.thresholds)
        elif args.command == "preflight":
            result = preflight_candidates(args.journal_dir, args.thresholds)
        else:
            result = lookup(args.task_class)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ActionError, OSError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
