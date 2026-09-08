"""Read-only, deterministic brownfield stage compatibility adapter."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import unicodedata
from pathlib import Path
from typing import Any

from hooks.stage_selector import find_stage_record, parse_stage_id


MAX_FILE_BYTES = 64_000
MAX_STAGES_BYTES = 500_000
MAX_FIELD_CHARS = 1_024
LEGACY_FILES = ("docs/AI_PLAN.md", "docs/AI_STATUS.md")
FENCE = re.compile(r"(?ms)^```stage-compatibility[ \t]*\r?\n(?P<body>.*?)^```[ \t]*$")
MASTER_FENCE = re.compile(r"(?ms)^```master-execution[ \t]*\r?\n(?P<body>.*?)^```[ \t]*$")
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
PROJECTION_FIELDS = {
    "current_stage", "master_id", "status", "next_selector", "blockers", "checkpoint", "evidence"
}
STATUSES = {
    "planned", "queued", "ready", "running", "in_progress", "blocked", "scaffolded",
    "implemented", "partial", "implemented_unverified", "completed", "verified",
    "unavailable", "unknown",
}
FIELD_LABELS = {
    "current_stage": ("Stage ID", "Current stage", "Current Stage", "Текущий этап"),
    "master_id": ("Master", "Master ID"),
    "status": ("Status", "Master status", "Lifecycle", "Статус"),
    "next_selector": ("NEXT", "Next", "Next selector", "Следующий этап"),
    "checkpoint": ("Checkpoint", "Checkpoint after", "HEAD"),
    "blockers": ("Blockers", "Blocker", "Блокеры", "Блокер"),
    "evidence": ("Evidence", "Evidence level"),
}
INCOMPLETE_LEGACY_ISSUES = {
    "missing_next_selector",
    "missing_blockers_for_blocked_status",
    "missing_checkpoint_for_terminal_status",
    "missing_evidence_for_terminal_status",
}


class CompatibilityError(ValueError):
    """A bounded state source cannot be interpreted safely."""


def _empty_projection(stage: str | None = None) -> dict[str, Any]:
    return {
        "current_stage": stage,
        "master_id": None,
        "status": None,
        "next_selector": stage,
        "blockers": [],
        "checkpoint": None,
        "evidence": [],
    }


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CompatibilityError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read(root: Path, relative: str, limit: int) -> tuple[bytes | None, str | None]:
    path = root / relative
    is_junction = getattr(path, "is_junction", lambda: False)
    if path.is_symlink() or is_junction():
        raise CompatibilityError(f"invalid state path: {relative}")
    if not path.exists():
        return None, None
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise CompatibilityError(f"state path escapes project: {relative}") from exc
    cursor = root
    for part in Path(relative).parts:
        cursor /= part
        cursor_is_junction = getattr(cursor, "is_junction", lambda: False)
        if cursor.is_symlink() or cursor_is_junction():
            raise CompatibilityError(f"invalid state path: {relative}")
    if not path.is_file():
        raise CompatibilityError(f"invalid state path: {relative}")
    try:
        if path.stat().st_size > limit:
            raise CompatibilityError(f"state file exceeds size limit: {relative}")
        with path.open("rb") as source:
            if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                raise CompatibilityError(f"invalid state path: {relative}")
            raw = source.read(limit + 1)
    except OSError as exc:
        raise CompatibilityError(f"cannot read state path: {relative}") from exc
    if len(raw) > limit:
        raise CompatibilityError(f"state file exceeds size limit: {relative}")
    try:
        raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CompatibilityError(f"unsupported encoding: {relative}") from exc
    return raw, hashlib.sha256(raw).hexdigest()


def _field_values(text: str, labels: tuple[str, ...]) -> set[str]:
    values: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip().lstrip("- ").strip()
        for label in labels:
            match = re.fullmatch(re.escape(label) + r"\s*:\s*`?([^`\r\n]+?)`?\s*", stripped, re.I)
            if match:
                value = match.group(1).strip()
                if value:
                    values.add(value)
    return values


def _normalize_status(value: str) -> str:
    normalized = value.strip().strip("`").lower()
    for status in sorted(STATUSES, key=len, reverse=True):
        if normalized == status or re.match(rf"^{re.escape(status)}(?:\s|\(|;|:)", normalized):
            return status
    return normalized


def _safe_text(value: Any) -> bool:
    return (
        type(value) is str
        and len(value) <= MAX_FIELD_CHARS
        and not any(unicodedata.category(character) in {"Cc", "Cf"} for character in value)
    )


def _projection_from_texts(
    texts: dict[str, str], *, required_stage: bool = True, required_status: bool = True,
    required_next: bool = True,
) -> tuple[dict[str, Any], list[str]]:
    collected: dict[str, set[str]] = {name: set() for name in FIELD_LABELS}
    for text in texts.values():
        for name, labels in FIELD_LABELS.items():
            values = _field_values(text, labels)
            if name == "status":
                values = {_normalize_status(value) for value in values}
            collected[name].update(values)

    issues: list[str] = []
    merged: dict[str, str | None] = {}
    for name, values in collected.items():
        if len(values) > 1:
            issues.append(f"conflicting_legacy_{name}")
            merged[name] = None
        else:
            merged[name] = next(iter(values), None)

    stage = merged["current_stage"]
    master = merged["master_id"]
    status = merged["status"]
    next_selector = merged["next_selector"]
    if required_stage and stage is None:
        issues.append("missing_current_stage")
    if required_status and status is None:
        issues.append("missing_status")
    if required_next and next_selector is None:
        issues.append("missing_next_selector")
    if stage is not None and not ID.fullmatch(stage):
        issues.append("invalid_current_stage")
    if master is not None and not ID.fullmatch(master):
        issues.append("invalid_master_id")
    if status is not None and status not in STATUSES:
        issues.append("invalid_status")
    if next_selector is not None and not ID.fullmatch(next_selector):
        issues.append("invalid_next_selector")
    for name in ("checkpoint", "blockers", "evidence"):
        value = merged[name]
        if value is not None and not _safe_text(value):
            issues.append(f"invalid_{name}")

    blockers = merged["blockers"]
    evidence = merged["evidence"]
    checkpoint = merged["checkpoint"]
    blockers_absent = blockers is None or blockers.lower() == "none"
    evidence_absent = evidence is None or evidence.lower() == "none"
    checkpoint_absent = checkpoint is None or checkpoint.lower() == "none"
    if status == "blocked" and blockers_absent:
        issues.append("missing_blockers_for_blocked_status")
    if status in {"completed", "verified"} and checkpoint_absent:
        issues.append("missing_checkpoint_for_terminal_status")
    if status in {"completed", "verified"} and evidence_absent:
        issues.append("missing_evidence_for_terminal_status")
    return {
        "current_stage": stage,
        "master_id": master,
        "status": status,
        "next_selector": next_selector,
        "blockers": [] if blockers_absent else [blockers],
        "checkpoint": None if checkpoint_absent else checkpoint,
        "evidence": [] if evidence_absent else [evidence],
    }, sorted(set(issues))


def _declared_fields(texts: dict[str, str]) -> set[str]:
    return {
        name for name, labels in FIELD_LABELS.items()
        if any(_field_values(text, labels) for text in texts.values())
    }


def _has_hard_legacy_issue(issues: list[str]) -> bool:
    return any(issue not in INCOMPLETE_LEGACY_ISSUES for issue in issues)


def _manifest(record: str) -> tuple[dict[str, Any] | None, bool]:
    matches = list(FENCE.finditer(record))
    if not matches:
        return None, False
    if len(matches) != 1:
        raise CompatibilityError("ambiguous stage-compatibility manifest")
    try:
        value = json.loads(matches[0].group("body"), object_pairs_hook=_unique)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise CompatibilityError("invalid stage-compatibility manifest") from exc
    if type(value) is not dict:
        raise CompatibilityError("invalid stage-compatibility manifest")
    return value, True


def _projection_issues(projection: Any) -> list[str]:
    if type(projection) is not dict or set(projection) != PROJECTION_FIELDS:
        return ["invalid_manifest_projection_fields"]
    issues: list[str] = []
    for name in ("current_stage", "master_id", "next_selector"):
        value = projection[name]
        if value is not None and (type(value) is not str or not ID.fullmatch(value)):
            issues.append(f"invalid_projection_{name}")
    if type(projection["current_stage"]) is not str:
        issues.append("missing_projection_current_stage")
    if type(projection["next_selector"]) is not str:
        issues.append("missing_projection_next_selector")
    if type(projection["status"]) is not str or projection["status"] not in STATUSES:
        issues.append("invalid_projection_status")
    for name in ("blockers", "evidence"):
        value = projection[name]
        if (
            type(value) is not list or len(value) > 128
            or any(not _safe_text(item) for item in value)
        ):
            issues.append(f"invalid_projection_{name}")
    if projection["checkpoint"] is not None and not _safe_text(projection["checkpoint"]):
        issues.append("invalid_projection_checkpoint")
    if projection["status"] == "blocked" and not projection["blockers"]:
        issues.append("missing_projection_blocker_for_blocked_status")
    if projection["status"] in {"completed", "verified"}:
        if projection["checkpoint"] is None:
            issues.append("missing_projection_checkpoint_for_terminal_status")
        if not projection["evidence"]:
            issues.append("missing_projection_evidence_for_terminal_status")
    return sorted(set(issues))


def _canonical_projection(record: str, stage: str) -> tuple[dict[str, Any], list[str], bool]:
    matches = list(MASTER_FENCE.finditer(record))
    if len(matches) > 1:
        return _empty_projection(stage), ["ambiguous_master_execution"], True
    if not matches:
        projection, issues = _projection_from_texts(
            {"selected_record": record}, required_stage=False, required_status=False,
            required_next=False,
        )
        if projection["current_stage"] not in (None, stage):
            issues.append("canonical_record_selector_mismatch")
        projection["current_stage"] = stage
        projection["next_selector"] = projection["next_selector"] or stage
        issues.extend(_projection_issues(projection))
        return projection, sorted(set(issues)), False

    try:
        state = json.loads(matches[0].group("body"), object_pairs_hook=_unique)
    except (json.JSONDecodeError, RecursionError):
        return _empty_projection(stage), ["invalid_master_execution"], True
    if type(state) is not dict or type(state.get("master")) is not dict:
        return _empty_projection(stage), ["invalid_master_execution"], True
    slices = state.get("slices")
    tracks = state.get("tracks")
    blockers = state.get("blockers")
    if type(slices) is not list or type(tracks) is not list or type(blockers) is not list:
        return _empty_projection(stage), ["invalid_master_execution"], True
    selected = [item for item in slices if type(item) is dict and item.get("id") == stage]
    if len(selected) != 1:
        return _empty_projection(stage), ["selected_slice_mismatch"], True
    current = selected[0]
    track_id = current.get("worktree_track")
    matching_tracks = [item for item in tracks if type(item) is dict and item.get("id") == track_id]
    if len(matching_tracks) != 1:
        return _empty_projection(stage), ["selected_track_mismatch"], True
    active_blockers = [
        item.get("id") for item in blockers
        if type(item) is dict and item.get("status") == "active" and isinstance(item.get("id"), str)
    ]
    projection = {
        "current_stage": stage,
        "master_id": state["master"].get("id"),
        "status": current.get("status"),
        "next_selector": stage,
        "blockers": active_blockers,
        "checkpoint": matching_tracks[0].get("checkpoint"),
        "evidence": current.get("evidence"),
    }
    return projection, _projection_issues(projection), True


def _validate_manifest(
    manifest: dict[str, Any], legacy: dict[str, tuple[bytes, str]], stage: str,
    canonical_projection: dict[str, Any], has_master_state: bool,
) -> list[str]:
    if set(manifest) != {"schema_version", "migration_id", "state_owner", "legacy_sources", "projection"}:
        return ["invalid_manifest_fields"]
    issues: list[str] = []
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        issues.append("invalid_manifest_schema_version")
    if type(manifest.get("migration_id")) is not str or not ID.fullmatch(manifest["migration_id"]):
        issues.append("invalid_manifest_migration_id")
    if manifest.get("state_owner") != "prompts/STAGES.md":
        issues.append("invalid_manifest_state_owner")

    sources = manifest.get("legacy_sources")
    declared: dict[str, str] = {}
    if type(sources) is not list or len(sources) > len(LEGACY_FILES):
        issues.append("invalid_manifest_sources")
    else:
        for item in sources:
            if type(item) is not dict or set(item) != {"path", "sha256", "disposition"}:
                issues.append("invalid_manifest_source")
                continue
            path = item.get("path")
            digest = item.get("sha256")
            if (
                path not in LEGACY_FILES or path in declared or type(digest) is not str
                or not SHA256.fullmatch(digest) or item.get("disposition") != "retained"
            ):
                issues.append("invalid_manifest_source")
                continue
            declared[path] = digest
    actual = {path: digest for path, (_, digest) in legacy.items()}
    if declared != actual:
        issues.append("legacy_source_set_or_digest_drift")

    projection = manifest.get("projection")
    issues.extend(_projection_issues(projection))
    if type(projection) is dict and projection.get("current_stage") != stage:
        issues.append("manifest_selector_mismatch")
    if type(projection) is dict:
        for name in PROJECTION_FIELDS:
            canonical_value = canonical_projection.get(name)
            has_canonical_fact = canonical_value is not None
            if isinstance(canonical_value, list):
                has_canonical_fact = has_master_state or bool(canonical_value)
            if has_canonical_fact and projection.get(name) != canonical_value:
                issues.append(f"manifest_canonical_{name}_mismatch")
    return sorted(set(issues))


def _conflict(issue: str) -> dict[str, Any]:
    return {
        "classification": "conflict",
        "issues": [issue],
        "legacy_sources": [],
        "manifest_present": False,
        "plan": None,
        "project": ".",
        "projection": _empty_projection(),
        "route": "migration_required",
        "runnable": False,
        "schema_version": 1,
        "stage_selector": None,
    }


def inspect_compatibility(project: str | Path) -> dict[str, Any]:
    root = Path(project).resolve()
    try:
        stages_raw, _ = _read(root, "prompts/STAGES.md", MAX_STAGES_BYTES)
        legacy: dict[str, tuple[bytes, str]] = {}
        for relative in LEGACY_FILES:
            raw, digest = _read(root, relative, MAX_FILE_BYTES)
            if raw is not None and digest is not None:
                legacy[relative] = (raw, digest)
    except CompatibilityError as exc:
        return _conflict(f"read_error:{exc}")

    legacy_texts = {path: raw.decode("utf-8-sig") for path, (raw, _) in legacy.items()}
    legacy_projection, legacy_issues = (
        _projection_from_texts(legacy_texts) if legacy_texts else (_empty_projection(), [])
    )
    legacy_declared = _declared_fields(legacy_texts)
    source_fingerprints = [
        {"path": path, "sha256": digest, "disposition": "retained"}
        for path, (_, digest) in sorted(legacy.items())
    ]
    has_legacy = bool(legacy)
    canonical_stage: str | None = None
    record: str | None = None
    canonical_issue: str | None = None
    canonical_projection = _empty_projection()
    canonical_projection_issues: list[str] = []
    canonical_declared: set[str] = set()
    has_master_state = False
    manifest: dict[str, Any] | None = None
    manifest_present = False

    if stages_raw is not None:
        stages_text = stages_raw.decode("utf-8-sig")
        selector = parse_stage_id(stages_text)
        if selector.issue_code or not selector.stage_id:
            canonical_issue = selector.issue_code or "missing-stage-id"
        else:
            canonical_stage = selector.stage_id
            selected = find_stage_record(stages_text, canonical_stage)
            if selected.issue_code or selected.record is None:
                canonical_issue = selected.issue_code or "missing-stage-record"
            else:
                record = selected.record
                canonical_projection, canonical_projection_issues, has_master_state = _canonical_projection(
                    record, canonical_stage
                )
                canonical_declared = (
                    set(PROJECTION_FIELDS) if has_master_state
                    else {"current_stage"} | _declared_fields({"selected_record": record})
                )
                try:
                    manifest, manifest_present = _manifest(record)
                except CompatibilityError as exc:
                    canonical_issue = str(exc).replace(" ", "_")
                    manifest_present = True

    classification = "none"
    route = "none"
    issues: list[str] = []
    projection = _empty_projection()

    if canonical_stage is not None and record is not None and canonical_issue is None:
        projection = canonical_projection
        if canonical_projection_issues:
            classification, route = "conflict", "migration_required"
            issues.extend(canonical_projection_issues)
        elif manifest_present and manifest is not None:
            manifest_issues = _validate_manifest(
                manifest, legacy, canonical_stage, canonical_projection, has_master_state
            )
            if manifest_issues:
                classification, route = "conflict", "migration_required"
                issues.extend(manifest_issues)
            else:
                classification, route = "migrated", "canonical"
                projection = manifest["projection"]
        elif has_legacy:
            if _has_hard_legacy_issue(legacy_issues):
                classification, route = "conflict", "migration_required"
                issues.extend(legacy_issues)
            else:
                conflicts = []
                for name in sorted(legacy_declared & canonical_declared):
                    if legacy_projection.get(name) != canonical_projection.get(name):
                        conflicts.append(f"canonical_legacy_{name}_mismatch")
                if conflicts:
                    classification, route = "conflict", "migration_required"
                    issues.extend(legacy_issues + conflicts)
                else:
                    classification, route = "mixed", "migration_required"
                    projection = legacy_projection
                    issues.extend(legacy_issues)
        else:
            classification, route = "canonical", "canonical"
    elif has_legacy:
        projection = legacy_projection
        if canonical_issue not in (None, "missing-stage-id"):
            classification, route = "conflict", "migration_required"
            issues.append(canonical_issue)
        elif _has_hard_legacy_issue(legacy_issues):
            classification, route = "conflict", "migration_required"
            issues.extend(legacy_issues)
        else:
            classification = "mixed" if stages_raw is not None else "legacy"
            route = "migration_required"
            issues.extend(legacy_issues)
    elif stages_raw is not None:
        classification, route = "conflict", "migration_required"
        issues.append(canonical_issue or "invalid_canonical_state")

    if canonical_issue is not None and classification == "conflict" and canonical_issue not in issues:
        issues.append(canonical_issue)
    issues = sorted(set(issues))

    plan = None
    if classification in {"legacy", "mixed"} and route == "migration_required" and not issues:
        plan_body = {
            "target": "prompts/STAGES.md",
            "operation": "materialize_stage_compatibility_manifest",
            "sources": source_fingerprints,
            "preserve_sources": [item["path"] for item in source_fingerprints],
            "projection": projection,
            "destructive_removals": False,
            "manual_review": [],
        }
        key = hashlib.sha256(
            json.dumps(plan_body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        plan = dict(plan_body, idempotency_key=key)

    result = {
        "schema_version": 1,
        "classification": classification,
        "route": route,
        "runnable": route == "canonical" and classification in {"canonical", "migrated"} and not issues,
        "project": ".",
        "stage_selector": canonical_stage,
        "projection": projection,
        "legacy_sources": source_fingerprints,
        "issues": issues,
        "manifest_present": manifest_present,
        "plan": plan,
    }
    return json.loads(json.dumps(result, ensure_ascii=False, sort_keys=True))


detect_compatibility = inspect_compatibility
