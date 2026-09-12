"""Deterministic primitives for Continuous Master Execution.

The canonical state is an embedded ``master-execution`` JSON block in the selected
``prompts/STAGES.md`` record. This module never executes commands from that state and never
performs merge, push, release, prompt cleanup, or worktree deletion.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hooks.stage_selector import find_stage_record, parse_stage_id
from tools.stage_compatibility import inspect_compatibility, materialize_plan, stage_routing_snapshot


MAX_STAGES_CHARS = 500_000
MAX_STATE_CHARS = 64_000
MAX_ITEMS = 128
MAX_GIT_OUTPUT_BYTES = 512 * 1024
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
BRANCH = re.compile(r"^(?![./])(?!.*(?:\.\.|//|@\{|\\|\s))[A-Za-z0-9._/-]{1,160}(?<![./])$")
STATE_FENCE = re.compile(
    r"(?ms)^```master-execution[ \t]*\r?\n(?P<body>.*?)^```[ \t]*\r?$"
)

TOP_KEYS = {
    "schema_version", "state_revision", "master", "tracks", "slices", "blockers",
    "decisions", "context_budget", "next_action", "integration",
}
MASTER_KEYS = {"id", "status", "source"}
SOURCE_KEYS = {"backend", "queue_id", "item_id", "revision", "prompt_type", "retention"}
TRACK_KEYS = {"id", "repository", "worktree", "branch", "checkpoint", "ownership", "status"}
SLICE_KEYS_V1 = {
    "id", "master_id", "title", "status", "predecessors", "dependencies", "worktree_track",
    "checkpoint_before", "checkpoint_after", "required_evidence", "evidence", "context_scope",
    "model_class", "reasoning_effort", "stop_after",
}
SLICE_KEYS_V2 = SLICE_KEYS_V1 | {"requirements", "capabilities"}
BLOCKER_KEYS = {"id", "class", "status", "blocking", "owner", "evidence"}
BUDGET_KEYS = {"max_chars", "max_items", "max_contours", "max_decisions", "max_evidence_threads"}
INTEGRATION_KEYS = {"required", "reason"}
MASTER_STATUS = {"running", "partial", "blocked", "needs_continuation", "completed"}
TRACK_STATUS = {"active", "integration_required", "integrated", "closed"}
SLICE_STATUS = {"queued", "ready", "running", "implemented_unverified", "verified", "blocked", "completed"}
EVIDENCE = {"L1", "L2", "L3", "L4", "L5", "L6"}
MODEL_CLASS = {"LOW", "MEDIUM", "HIGH", "FRONTIER"}
REASONING = {"low", "medium", "high", "xhigh", "max"}
BLOCKER_CLASS = {"regression", "pre_existing", "unrelated_debt", "environment_unavailable"}
TERMINAL_SLICE = {"verified", "completed"}
EVIDENCE_RANK = {level: index for index, level in enumerate(("L1", "L2", "L3", "L4", "L5", "L6"), 1)}


class MasterExecutionError(ValueError):
    """A fail-closed state, route, or adapter error."""


class MasterExecutionResourceLimit(MasterExecutionError):
    """A bounded adapter observation exceeded its declared resource limit."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise MasterExecutionError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _exact(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise MasterExecutionError(f"invalid {label} fields")
    return value


def _string(value: Any, label: str, *, empty: bool = False, limit: int = 4096) -> str:
    if type(value) is not str or len(value) > limit or (not empty and not value.strip()):
        raise MasterExecutionError(f"invalid {label}")
    return value


def _identifier(value: Any, label: str) -> str:
    value = _string(value, label, limit=64)
    if not ID.fullmatch(value):
        raise MasterExecutionError(f"invalid {label}")
    return value


def _strings(value: Any, label: str, *, allowed: set[str] | None = None) -> list[str]:
    if type(value) is not list or len(value) > MAX_ITEMS:
        raise MasterExecutionError(f"invalid {label}")
    result = [_string(item, label) for item in value]
    if len(set(result)) != len(result):
        raise MasterExecutionError(f"duplicate {label}")
    if allowed is not None and any(item not in allowed for item in result):
        raise MasterExecutionError(f"unsupported {label}")
    return result


def _expand_portable(path: str) -> Path:
    value = _string(path, "path")
    if value == "~":
        return Path.home().resolve()
    if value.startswith("~/") or value.startswith("~\\"):
        return (Path.home() / value[2:]).resolve()
    return Path(value).resolve()


def _path_key(path: str | Path) -> str:
    return os.path.normcase(str(_expand_portable(str(path))))


def _lexical_path_key(path: str | Path) -> str:
    """Normalize untrusted state paths without filesystem or network resolution."""
    value = _string(str(path), "path")
    if value == "~":
        value = str(Path.home())
    elif value.startswith("~/") or value.startswith("~\\"):
        value = os.path.join(str(Path.home()), value[2:])
    return os.path.normcase(os.path.normpath(value))


def validate_state(state: Any) -> dict[str, Any]:
    state = _exact(state, TOP_KEYS, "state")
    if type(state["schema_version"]) is not int or state["schema_version"] not in {1, 2}:
        raise MasterExecutionError("unsupported schema_version")
    if type(state["state_revision"]) is not int or state["state_revision"] < 1:
        raise MasterExecutionError("invalid state_revision")

    master = _exact(state["master"], MASTER_KEYS, "master")
    master_id = _identifier(master["id"], "master id")
    if master["status"] not in MASTER_STATUS:
        raise MasterExecutionError("invalid master status")
    source = _exact(master["source"], SOURCE_KEYS, "source")
    for key, value in source.items():
        _string(value, f"source {key}")

    tracks = state["tracks"]
    if type(tracks) is not list or not tracks or len(tracks) > 64:
        raise MasterExecutionError("invalid tracks")
    track_ids: set[str] = set()
    worktrees: set[str] = set()
    branches: set[str] = set()
    for raw in tracks:
        track = _exact(raw, TRACK_KEYS, "track")
        track_id = _identifier(track["id"], "track id")
        if track_id in track_ids:
            raise MasterExecutionError("duplicate track id")
        track_ids.add(track_id)
        _string(track["repository"], "track repository")
        worktree = _string(track["worktree"], "track worktree")
        branch = _string(track["branch"], "track branch")
        if not BRANCH.fullmatch(branch):
            raise MasterExecutionError("invalid track branch")
        worktree_key = _lexical_path_key(worktree)
        if worktree_key in worktrees or branch.casefold() in branches:
            raise MasterExecutionError("duplicate track worktree or branch")
        worktrees.add(worktree_key)
        branches.add(branch.casefold())
        _string(track["checkpoint"], "track checkpoint")
        _strings(track["ownership"], "track ownership")
        if track["status"] not in TRACK_STATUS:
            raise MasterExecutionError("invalid track status")

    slices = state["slices"]
    if type(slices) is not list or not slices or len(slices) > MAX_ITEMS:
        raise MasterExecutionError("invalid slices")
    slice_ids: set[str] = set()
    for raw in slices:
        item = _exact(raw, SLICE_KEYS_V2 if state["schema_version"] == 2 else SLICE_KEYS_V1, "slice")
        slice_id = _identifier(item["id"], "slice id")
        if slice_id in slice_ids:
            raise MasterExecutionError("duplicate slice id")
        slice_ids.add(slice_id)
        if _identifier(item["master_id"], "slice master id") != master_id:
            raise MasterExecutionError("slice master mismatch")
        _string(item["title"], "slice title")
        if item["status"] not in SLICE_STATUS:
            raise MasterExecutionError("invalid slice status")
        _strings(item["predecessors"], "slice predecessors")
        _strings(item["dependencies"], "slice dependencies")
        if _identifier(item["worktree_track"], "slice track") not in track_ids:
            raise MasterExecutionError("unknown slice track")
        _string(item["checkpoint_before"], "checkpoint_before", empty=True)
        _string(item["checkpoint_after"], "checkpoint_after", empty=True)
        _strings(item["required_evidence"], "required evidence", allowed=EVIDENCE)
        _strings(item["evidence"], "evidence", allowed=EVIDENCE)
        _strings(item["context_scope"], "context scope")
        if state["schema_version"] == 2:
            _strings(item["requirements"], "slice requirements")
            _strings(item["capabilities"], "slice capabilities")
        if item["model_class"] not in MODEL_CLASS or item["reasoning_effort"] not in REASONING:
            raise MasterExecutionError("invalid model routing")
        if type(item["stop_after"]) is not bool:
            raise MasterExecutionError("invalid stop_after")

    for item in slices:
        refs = item["predecessors"] + item["dependencies"]
        if item["id"] in refs or any(ref not in slice_ids for ref in refs):
            raise MasterExecutionError("invalid slice dependency reference")

    graph = {item["id"]: item["predecessors"] + item["dependencies"] for item in slices}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise MasterExecutionError("cyclic slice dependency")
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph[node]:
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)

    blockers = state["blockers"]
    if type(blockers) is not list or len(blockers) > MAX_ITEMS:
        raise MasterExecutionError("invalid blockers")
    blocker_ids: set[str] = set()
    for raw in blockers:
        blocker = _exact(raw, BLOCKER_KEYS, "blocker")
        blocker_id = _identifier(blocker["id"], "blocker id")
        if blocker_id in blocker_ids:
            raise MasterExecutionError("duplicate blocker id")
        blocker_ids.add(blocker_id)
        if blocker["class"] not in BLOCKER_CLASS or blocker["status"] not in {"active", "resolved"}:
            raise MasterExecutionError("invalid blocker classification")
        if type(blocker["blocking"]) is not bool:
            raise MasterExecutionError("invalid blocker blocking flag")
        _string(blocker["owner"], "blocker owner")
        _string(blocker["evidence"], "blocker evidence")

    _strings(state["decisions"], "decisions")
    budget = _exact(state["context_budget"], BUDGET_KEYS, "context budget")
    for key, value in budget.items():
        if type(value) is not int or value < 1:
            raise MasterExecutionError(f"invalid context budget {key}")
    _string(state["next_action"], "next action")
    integration = _exact(state["integration"], INTEGRATION_KEYS, "integration")
    if type(integration["required"]) is not bool:
        raise MasterExecutionError("invalid integration flag")
    _string(integration["reason"], "integration reason", empty=True)
    return state


def extract_master_state(record: str) -> dict[str, Any]:
    matches = list(STATE_FENCE.finditer(record))
    if len(matches) != 1:
        raise MasterExecutionError("selected record must contain exactly one master-execution block")
    body = matches[0].group("body")
    if len(body) > MAX_STATE_CHARS:
        raise MasterExecutionError("master-execution block exceeds size limit")
    try:
        state = json.loads(body, object_pairs_hook=_unique_object)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise MasterExecutionError("invalid master-execution JSON") from exc
    return validate_state(state)


def load_selected_state(project: Path) -> tuple[str, dict[str, Any]]:
    root = project.resolve()
    stages_path = (root / "prompts" / "STAGES.md").resolve()
    try:
        stages_path.relative_to(root)
    except ValueError as exc:
        raise MasterExecutionError("STAGES path escapes project") from exc
    with stages_path.open("r", encoding="utf-8") as stream:
        raw = stream.read(MAX_STAGES_CHARS + 1)
    if len(raw) > MAX_STAGES_CHARS:
        raise MasterExecutionError("STAGES exceeds scan limit")
    selector = parse_stage_id(raw)
    if selector.issue_code or not selector.stage_id:
        raise MasterExecutionError(selector.issue_code or "invalid selector")
    selected = find_stage_record(raw, selector.stage_id)
    if selected.issue_code or selected.record is None:
        raise MasterExecutionError(selected.issue_code or "invalid selected record")
    return selector.stage_id, extract_master_state(selected.record)


@dataclass(frozen=True)
class RouteRequest:
    master_id: str
    track_id: str
    task_kind: str
    repository: str
    branch: str
    worktree: str
    checkpoint: str
    ownership: tuple[str, ...] = ()


@dataclass(frozen=True)
class RouteDecision:
    action: str
    reason: str
    track_id: str
    repository: str
    branch: str
    worktree: str
    checkpoint: str


@dataclass(frozen=True)
class WorktreeFact:
    path: str
    head: str
    branch: str
    detached: bool = False
    bare: bool = False


@dataclass(frozen=True)
class StopSignals:
    explicit_stop: bool = False
    user_decision_required: bool = False
    external_input_required: bool = False
    destructive_action_required: bool = False
    integration_write_required: bool = False
    canonical_conflict: bool = False
    context_overflow: bool = False


@dataclass(frozen=True)
class ExecutionDecision:
    action: str
    reason: str
    slice_id: str = ""
    model_class: str = ""
    reasoning_effort: str = ""


@dataclass(frozen=True)
class ContextItem:
    ref: str
    content: str
    contour: str
    evidence_thread: str = ""


@dataclass(frozen=True)
class ContextResolution:
    overflow: bool
    reason: str
    items: tuple[ContextItem, ...]
    chars: int
    launcher: str = ""


@dataclass(frozen=True)
class FailureObservation:
    failed_before: bool
    in_changed_scope: bool
    environment_available: bool


@dataclass(frozen=True)
class IntegrationSignals:
    coherent_boundary: bool = False
    dependent_track: bool = False
    divergence_risk: bool = False
    release_gate: bool = False
    master_complete: bool = False


@dataclass(frozen=True)
class CleanupEligibility:
    action: str
    reason: str


@dataclass(frozen=True)
class RecoveryFacts:
    git_head: str
    worktree_exists: bool
    branch_exists: bool
    dirty: bool
    source_revision: str
    queue_item_present: bool
    launcher_state_revision: int
    launcher_checkpoint: str
    checkpoint_reachable: bool = True
    state_revision_at_head: bool = True
    overlapping_contract_merged: bool = False
    context_compacted: bool = False


def _evidence_satisfies(item: dict[str, Any]) -> bool:
    available = set(item["evidence"])
    return set(item["required_evidence"]).issubset(available)


def required_evidence_for(risk: str) -> tuple[str, ...]:
    levels = {
        "static": ("L1",),
        "logic": ("L1", "L2"),
        "component_integration": ("L1", "L2", "L3"),
        "backend_concurrency": ("L1", "L2", "L3", "L4"),
        "browser_runtime": ("L1", "L2", "L3", "L4", "L5"),
        "external_manual": ("L1", "L2", "L3", "L4", "L5", "L6"),
    }
    try:
        return levels[risk]
    except KeyError as exc:
        raise MasterExecutionError("unknown evidence risk class") from exc


def evidence_decision(item: dict[str, Any]) -> ExecutionDecision:
    if set(item) == SLICE_KEYS_V1:
        _exact(item, SLICE_KEYS_V1, "slice")
    else:
        _exact(item, SLICE_KEYS_V2, "slice")
    if _evidence_satisfies(item):
        return ExecutionDecision("pass", "required_evidence_present", item["id"])
    missing = sorted(set(item["required_evidence"]) - set(item["evidence"]),
                     key=EVIDENCE_RANK.__getitem__)
    return ExecutionDecision("verification_gate", "missing_evidence:" + ",".join(missing), item["id"])


def classify_failure(observation: FailureObservation) -> str:
    if not observation.environment_available:
        return "environment_unavailable"
    if observation.failed_before:
        return "pre_existing"
    if not observation.in_changed_scope:
        return "unrelated_debt"
    return "regression"


def integration_decision(signals: IntegrationSignals) -> ExecutionDecision:
    reasons = [name for name, enabled in (
        ("coherent_boundary", signals.coherent_boundary),
        ("dependent_track", signals.dependent_track),
        ("divergence_risk", signals.divergence_risk),
        ("release_gate", signals.release_gate),
        ("master_complete", signals.master_complete),
    ) if enabled]
    if not reasons:
        return ExecutionDecision("defer_integration", "no_integration_boundary")
    return ExecutionDecision("integration_checkpoint", "+".join(reasons))


def cleanup_eligibility(prompt_type: str, item_status: str, retention: str, *,
                        parent_master_status: str = "", overall_dod: bool = False) -> CleanupEligibility:
    """Classify hierarchy before delegating any eligible exact item to prompt_queue.py."""
    if prompt_type not in {"one_shot", "one_shot_launcher", "child_prompt", "master_prompt"}:
        return CleanupEligibility("retain", "unknown_prompt_type")
    if item_status != "completed":
        return CleanupEligibility("retain", "item_incomplete")
    if prompt_type == "master_prompt":
        if retention != "auto":
            return CleanupEligibility("retain", "master_retention_protected")
        if not overall_dod:
            return CleanupEligibility("retain", "master_overall_dod_missing")
        return CleanupEligibility("existing_guard", "completed_auto_master_requires_exact_item_guard")
    if retention != "auto":
        return CleanupEligibility("retain", "item_retention_protected")
    reason = "completed_child_independent_of_partial_parent"
    if parent_master_status and parent_master_status not in MASTER_STATUS:
        return CleanupEligibility("retain", "unknown_parent_master_status")
    return CleanupEligibility("existing_guard", reason)


def recover_execution(
    state: dict[str, Any], facts: RecoveryFacts, *, track_id: str = ""
) -> ExecutionDecision:
    """Reconcile durable state with bounded Git/prompt/session observations."""
    validate_state(state)
    if track_id:
        selected_track = _identifier(track_id, "recovery track id")
        track = next(
            (
                item for item in state["tracks"]
                if item["id"] == selected_track
                and item["status"] in {"active", "integration_required"}
            ),
            None,
        )
    else:
        track = next(
            (
                item for item in state["tracks"]
                if item["status"] in {"active", "integration_required"}
            ),
            None,
        )
    if track is None:
        reason = "selected_active_track_missing" if track_id else "active_track_missing"
        return ExecutionDecision("blocked", reason)
    if facts.source_revision != state["master"]["source"]["revision"]:
        return ExecutionDecision("blocked", "master_source_revision_changed")
    if not facts.queue_item_present:
        return ExecutionDecision("blocked", "queue_item_missing_requires_receipt_reconciliation")
    if facts.worktree_exists and not facts.branch_exists:
        return ExecutionDecision("blocked", "worktree_exists_but_branch_missing")
    if facts.branch_exists and not facts.worktree_exists:
        return ExecutionDecision("route_worktree", "branch_exists_but_worktree_missing")
    if not facts.branch_exists and not facts.worktree_exists:
        return ExecutionDecision("blocked", "track_branch_and_worktree_missing")
    if facts.dirty:
        return ExecutionDecision("blocked", "user_or_unknown_dirty_changes_between_slices")
    if facts.overlapping_contract_merged:
        return ExecutionDecision("integration_checkpoint", "parallel_track_merged_overlapping_contract")
    if (facts.launcher_state_revision != state["state_revision"]
            or facts.launcher_checkpoint != track["checkpoint"]):
        return ExecutionDecision("handoff", "stale_launcher_requires_fresh_state")
    running = [
        item for item in state["slices"]
        if item["status"] == "running" and item["worktree_track"] == track["id"]
    ]
    if facts.git_head != track["checkpoint"]:
        if not facts.checkpoint_reachable:
            return ExecutionDecision("blocked", "status_checkpoint_not_present_in_git")
        if facts.state_revision_at_head:
            pass
        elif running and not running[0]["checkpoint_after"]:
            return ExecutionDecision("reconcile_status", "commit_created_before_status_update", running[0]["id"])
        else:
            return ExecutionDecision("blocked", "durable_state_not_present_at_git_head")
    if facts.context_compacted:
        target = running[0]["id"] if running else ""
        return ExecutionDecision("handoff", "context_compacted_resume_from_durable_state", target)
    return ExecutionDecision("resume", "git_state_prompt_and_launcher_consistent",
                             running[0]["id"] if running else "")


def next_execution_decision(state: dict[str, Any], signals: StopSignals | None = None) -> ExecutionDecision:
    """Return the next deterministic lifecycle decision without executing a slice."""
    validate_state(state)
    signals = signals or StopSignals()
    stops = (
        (signals.explicit_stop, "stopped", "explicit_user_stop"),
        (signals.canonical_conflict, "blocked", "canonical_contract_conflict"),
        (signals.destructive_action_required, "user_decision", "destructive_or_irreversible_action"),
        (signals.integration_write_required, "integration_checkpoint", "integration_write_requires_approval"),
        (signals.user_decision_required, "user_decision", "product_or_architecture_decision_required"),
        (signals.external_input_required, "blocked", "external_input_or_environment_required"),
        (signals.context_overflow, "handoff", "context_budget_exceeded"),
    )
    for active, action, reason in stops:
        if active:
            return ExecutionDecision(action, reason)
    if state["master"]["status"] == "completed":
        return ExecutionDecision("complete", "master_already_completed")
    if state["integration"]["required"]:
        return ExecutionDecision("integration_checkpoint", state["integration"]["reason"] or "integration_required")
    blocking = sorted(item["id"] for item in state["blockers"]
                      if item["status"] == "active" and item["blocking"])
    if blocking:
        return ExecutionDecision("blocked", "active_blockers:" + ",".join(blocking))

    running = [item for item in state["slices"] if item["status"] == "running"]
    if len(running) > 1:
        return ExecutionDecision("blocked", "multiple_running_slices")
    if running:
        item = running[0]
        return ExecutionDecision("await_result", "slice_already_running", item["id"],
                                 item["model_class"], item["reasoning_effort"])

    by_id = {item["id"]: item for item in state["slices"]}
    verification_needed: set[str] = set()
    candidates: list[dict[str, Any]] = []
    for item in state["slices"]:
        if item["status"] not in {"queued", "ready"}:
            continue
        dependencies = [by_id[ref] for ref in item["predecessors"] + item["dependencies"]]
        for dependency in dependencies:
            if dependency["status"] in TERMINAL_SLICE and not _evidence_satisfies(dependency):
                verification_needed.add(dependency["id"])
        if all(dependency["status"] in TERMINAL_SLICE and _evidence_satisfies(dependency)
               for dependency in dependencies):
            candidates.append(item)
    if verification_needed:
        target = sorted(verification_needed)[0]
        return ExecutionDecision("verification_gate", "mandatory_evidence_missing", target)
    if len(candidates) > 1:
        return ExecutionDecision("user_decision", "ambiguous_ready_slices:" + ",".join(
            sorted(item["id"] for item in candidates)))
    if len(candidates) == 1:
        item = candidates[0]
        return ExecutionDecision("continue", "single_dependency_ready_slice", item["id"],
                                 item["model_class"], item["reasoning_effort"])
    if all(item["status"] in TERMINAL_SLICE for item in state["slices"]):
        return ExecutionDecision("complete", "all_slices_terminal_pending_master_sync")
    return ExecutionDecision("blocked", "no_dependency_ready_slice")


def apply_slice_result(state: dict[str, Any], slice_id: str, status: str, checkpoint: str,
                       evidence: Sequence[str]) -> dict[str, Any]:
    """Return a validated copy with one running slice result reconciled."""
    validate_state(state)
    if status not in {"implemented_unverified", "verified", "completed", "blocked"}:
        raise MasterExecutionError("unsupported slice result status")
    levels = _strings(list(evidence), "result evidence", allowed=EVIDENCE)
    updated = copy.deepcopy(state)
    item = next((candidate for candidate in updated["slices"] if candidate["id"] == slice_id), None)
    if item is None or item["status"] != "running":
        raise MasterExecutionError("slice result does not match one running slice")
    if status in TERMINAL_SLICE and not checkpoint.strip():
        raise MasterExecutionError("terminal slice result requires checkpoint")
    item["evidence"] = sorted(levels, key=EVIDENCE_RANK.__getitem__)
    if status in TERMINAL_SLICE and not _evidence_satisfies(item):
        item["status"] = "implemented_unverified"
        item["checkpoint_after"] = checkpoint
        updated["next_action"] = f"verify {slice_id}"
    else:
        item["status"] = status
        item["checkpoint_after"] = checkpoint
        updated["next_action"] = "select next ready slice"
    if checkpoint:
        track = next(track for track in updated["tracks"] if track["id"] == item["worktree_track"])
        track["checkpoint"] = checkpoint
    updated["state_revision"] += 1
    return validate_state(updated)


def _slice(state: dict[str, Any], slice_id: str) -> dict[str, Any]:
    item = next((candidate for candidate in state["slices"] if candidate["id"] == slice_id), None)
    if item is None:
        raise MasterExecutionError("unknown slice")
    return item


def build_handoff(state: dict[str, Any], slice_id: str) -> dict[str, Any]:
    """Build the durable minimum needed by a fresh session; no separate file is implied."""
    validate_state(state)
    item = _slice(state, slice_id)
    track = next(track for track in state["tracks"] if track["id"] == item["worktree_track"])
    verified = [candidate["id"] for candidate in state["slices"]
                if candidate["status"] in TERMINAL_SLICE and _evidence_satisfies(candidate)]
    active_blockers = [
        {key: blocker[key] for key in ("id", "class", "blocking", "owner", "evidence")}
        for blocker in state["blockers"] if blocker["status"] == "active"
    ]
    return {
        "schema_version": 1,
        "master_id": state["master"]["id"],
        "master_status": state["master"]["status"],
        "state_revision": state["state_revision"],
        "track_id": track["id"],
        "repository": track["repository"],
        "worktree": track["worktree"],
        "branch": track["branch"],
        "checkpoint": track["checkpoint"],
        "verified_chain": verified,
        "current_slice": item["id"],
        "next_action": state["next_action"],
        "blockers": active_blockers,
        "stop_conditions": [
            "user_decision", "external_input", "hard_blocker", "destructive_action",
            "integration_write", "context_overflow", "canonical_conflict", "master_complete",
        ],
        "merge_push": "not_authorized",
        "prompt_cleanup": (
            "retain_parent_master" if state["master"]["status"] != "completed"
            or state["master"]["source"]["retention"] == "keep" else "existing_guard_only"
        ),
    }


def render_launcher(handoff: dict[str, Any]) -> str:
    required = {
        "schema_version", "master_id", "master_status", "state_revision", "track_id",
        "repository", "worktree", "branch", "checkpoint", "verified_chain", "current_slice",
        "next_action", "blockers", "stop_conditions", "merge_push", "prompt_cleanup",
    }
    if type(handoff) is not dict or set(handoff) != required:
        raise MasterExecutionError("invalid handoff fields")
    lines = [
        "CONTINUE MASTER (low-context)",
        f"master/track: {handoff['master_id']} / {handoff['track_id']}",
        f"worktree: {handoff['worktree']}",
        f"branch: {handoff['branch']}",
        f"checkpoint: {handoff['checkpoint']}",
        f"state_revision: {handoff['state_revision']}",
        "verified_chain: " + ", ".join(handoff["verified_chain"]),
        f"current_slice: {handoff['current_slice']}",
        f"next_action: {handoff['next_action']}",
        "blockers: " + (json.dumps(handoff["blockers"], ensure_ascii=False, sort_keys=True)
                         if handoff["blockers"] else "none"),
        "stop_conditions: " + ", ".join(handoff["stop_conditions"]),
        f"merge/push: {handoff['merge_push']}",
        f"prompt_cleanup: {handoff['prompt_cleanup']}",
    ]
    return "\n".join(lines)


def validate_handoff(handoff: dict[str, Any], state: dict[str, Any], git_checkpoint: str) -> None:
    validate_state(state)
    current = build_handoff(state, handoff.get("current_slice", ""))
    for field in ("master_id", "track_id", "worktree", "branch", "state_revision", "checkpoint"):
        if handoff.get(field) != current[field]:
            raise MasterExecutionError(f"stale handoff {field}")
    if git_checkpoint != current["checkpoint"]:
        raise MasterExecutionError("stale handoff Git checkpoint")


def resolve_context(state: dict[str, Any], slice_id: str,
                    available: Sequence[ContextItem]) -> ContextResolution:
    """Select only current-slice refs and produce a handoff when the declared budget is exceeded."""
    validate_state(state)
    item = _slice(state, slice_id)
    by_ref: dict[str, ContextItem] = {}
    for candidate in available:
        for value, label in ((candidate.ref, "context ref"), (candidate.content, "context content"),
                             (candidate.contour, "context contour"),
                             (candidate.evidence_thread, "context evidence thread")):
            _string(value, label, empty=label == "context evidence thread", limit=MAX_STATE_CHARS)
        if candidate.ref in by_ref:
            raise MasterExecutionError("duplicate context ref")
        by_ref[candidate.ref] = candidate
    missing = [ref for ref in item["context_scope"] if ref not in by_ref]
    if missing:
        raise MasterExecutionError("missing context refs:" + ",".join(missing))
    selected = tuple(by_ref[ref] for ref in item["context_scope"])
    budget = state["context_budget"]
    chars = sum(len(candidate.content) for candidate in selected)
    contours = {candidate.contour for candidate in selected}
    threads = {candidate.evidence_thread for candidate in selected if candidate.evidence_thread}
    exceeded = []
    if chars > budget["max_chars"]:
        exceeded.append("chars")
    if len(selected) > budget["max_items"]:
        exceeded.append("items")
    if len(contours) > budget["max_contours"]:
        exceeded.append("contours")
    if len(state["decisions"]) > budget["max_decisions"]:
        exceeded.append("decisions")
    if len(threads) > budget["max_evidence_threads"]:
        exceeded.append("evidence_threads")
    if exceeded:
        launcher = render_launcher(build_handoff(state, slice_id))
        return ContextResolution(True, "context_budget_exceeded:" + ",".join(exceeded), (), chars, launcher)
    return ContextResolution(False, "within_budget", selected, chars)


def _active_tracks(state: dict[str, Any]) -> Iterable[dict[str, Any]]:
    return (track for track in state["tracks"] if track["status"] in {"active", "integration_required"})


def route_worktree(state: dict[str, Any], request: RouteRequest,
                   facts: Sequence[WorktreeFact] = ()) -> RouteDecision:
    validate_state(state)
    if request.master_id != state["master"]["id"]:
        raise MasterExecutionError("route master mismatch")
    if request.task_kind not in {"read_only", "continuation", "parallel"}:
        raise MasterExecutionError("invalid task_kind")
    _identifier(request.track_id, "route track id")
    if not BRANCH.fullmatch(request.branch):
        raise MasterExecutionError("invalid route branch")
    for value, label in ((request.repository, "route repository"), (request.worktree, "route worktree"),
                         (request.checkpoint, "route checkpoint")):
        _string(value, label)
    if len(set(request.ownership)) != len(request.ownership):
        raise MasterExecutionError("duplicate route ownership")
    repositories = {track["repository"] for track in state["tracks"]}
    if request.repository not in repositories:
        raise MasterExecutionError("route repository is outside the registered master")

    tracks = {track["id"]: track for track in state["tracks"]}
    existing = tracks.get(request.track_id)
    by_path = {_path_key(fact.path): fact for fact in facts}
    by_branch = {fact.branch.casefold(): fact for fact in facts if fact.branch}

    if request.task_kind == "read_only":
        return RouteDecision("read_only", "read_only_task_needs_no_isolation", request.track_id,
                             request.repository, request.branch, request.worktree, request.checkpoint)

    if request.task_kind == "continuation":
        if existing is None or existing["status"] not in {"active", "integration_required"}:
            raise MasterExecutionError("continuation track is not active")
        for field in ("repository", "branch", "worktree"):
            if (field == "worktree" and _path_key(existing[field]) != _path_key(getattr(request, field))) or (
                    field != "worktree" and existing[field] != getattr(request, field)):
                raise MasterExecutionError(f"continuation {field} mismatch")
        fact = by_path.get(_path_key(existing["worktree"]))
        if facts and (fact is None or fact.branch.casefold() != existing["branch"].casefold()):
            raise MasterExecutionError("registered continuation worktree is unavailable or changed")
        return RouteDecision("reuse", "same_master_track_continuation", request.track_id,
                             existing["repository"], existing["branch"], existing["worktree"],
                             existing["checkpoint"])

    if existing is not None:
        raise MasterExecutionError("parallel track id already exists")
    if any(_path_key(track["worktree"]) == _path_key(request.worktree) for track in state["tracks"]):
        raise MasterExecutionError("parallel worktree already registered")
    if any(track["branch"].casefold() == request.branch.casefold() for track in state["tracks"]):
        raise MasterExecutionError("parallel branch already registered")
    if _path_key(request.worktree) in by_path or request.branch.casefold() in by_branch:
        raise MasterExecutionError("parallel worktree or branch is occupied")
    requested_owners = set(request.ownership)
    overlaps = sorted({owner for track in _active_tracks(state)
                       for owner in track["ownership"] if owner in requested_owners})
    if overlaps:
        return RouteDecision("integration_checkpoint", "ownership_overlap:" + ",".join(overlaps),
                             request.track_id, request.repository, request.branch, request.worktree,
                             request.checkpoint)
    return RouteDecision("create", "independent_parallel_write_track", request.track_id,
                         request.repository, request.branch, request.worktree, request.checkpoint)


class GitWorktreeAdapter:
    """Narrow Git adapter: inventory and explicit create-only ensure operation."""

    def __init__(self, repository: Path, worktree_root: Path, *, timeout: int = 30) -> None:
        self.repository = repository.resolve()
        self.worktree_root = worktree_root.resolve()
        self.timeout = timeout

    def _git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        environment = {
            key: value for key, value in os.environ.items()
            if not key.upper().startswith("GIT_")
        }
        environment.update({
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_PAGER": "cat",
            "GIT_NO_LAZY_FETCH": "1",
        })
        command = [
            "git",
            "-c", f"safe.directory={self.repository}",
            "-c", "core.fsmonitor=false",
            "-c", f"core.hooksPath={os.devnull}",
            "-c", "submodule.recurse=false",
            "-C", str(self.repository),
            *args,
        ]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=environment,
        )
        chunks: list[bytes] = []
        observed = 0
        overflow = False

        def drain() -> None:
            nonlocal observed, overflow
            assert process.stdout is not None
            while True:
                chunk = process.stdout.read(min(64 * 1024, MAX_GIT_OUTPUT_BYTES + 1 - observed))
                if not chunk:
                    return
                chunks.append(chunk)
                observed += len(chunk)
                if observed > MAX_GIT_OUTPUT_BYTES:
                    overflow = True
                    process.kill()
                    return

        reader = threading.Thread(target=drain, daemon=True)
        reader.start()
        try:
            returncode = process.wait(timeout=self.timeout)
        except subprocess.TimeoutExpired as exc:
            process.kill()
            process.wait()
            reader.join(timeout=1)
            if process.stdout is not None:
                process.stdout.close()
            raise MasterExecutionError("git adapter timed out") from exc
        reader.join(timeout=1)
        if process.stdout is not None:
            process.stdout.close()
        output = b"".join(chunks).decode("utf-8", errors="replace")
        if overflow:
            raise MasterExecutionResourceLimit("git adapter output exceeded bounded limit")
        completed = subprocess.CompletedProcess(command, returncode, output, "")
        if check and completed.returncode != 0:
            detail = (completed.stderr or completed.stdout)[-2000:].strip()
            raise MasterExecutionError(f"git adapter failed: {detail}")
        return completed

    def snapshot(self) -> tuple[WorktreeFact, ...]:
        output = self._git("worktree", "list", "--porcelain").stdout
        facts: list[WorktreeFact] = []
        current: dict[str, str | bool] = {}
        for line in [*output.splitlines(), ""]:
            if not line:
                if current:
                    if len(facts) >= MAX_ITEMS:
                        raise MasterExecutionResourceLimit(
                            "git worktree inventory exceeds item limit"
                        )
                    facts.append(WorktreeFact(
                        path=str(current.get("worktree", "")), head=str(current.get("HEAD", "")),
                        branch=str(current.get("branch", "")).removeprefix("refs/heads/"),
                        detached=bool(current.get("detached", False)), bare=bool(current.get("bare", False)),
                    ))
                    current = {}
                continue
            key, _, value = line.partition(" ")
            current[key] = value if value else True
        return tuple(facts)

    def ensure(self, decision: RouteDecision) -> WorktreeFact:
        if _path_key(decision.repository) != _path_key(self.repository):
            raise MasterExecutionError("route decision repository mismatch")
        if decision.action in {"reuse", "read_only"}:
            fact = next((item for item in self.snapshot()
                         if _path_key(item.path) == _path_key(decision.worktree)), None)
            if decision.action == "reuse" and (fact is None or fact.branch.casefold() != decision.branch.casefold()):
                raise MasterExecutionError("reuse target changed before adapter operation")
            return fact or WorktreeFact(decision.worktree, decision.checkpoint, decision.branch)
        if decision.action != "create":
            raise MasterExecutionError("route decision does not authorize worktree creation")
        target = _expand_portable(decision.worktree)
        try:
            target.relative_to(self.worktree_root)
        except ValueError as exc:
            raise MasterExecutionError("worktree target escapes allowed root") from exc
        if target == self.worktree_root or target.exists():
            raise MasterExecutionError("worktree target is occupied")
        self._git("check-ref-format", "--branch", decision.branch)
        before = self.snapshot()
        if any(item.branch.casefold() == decision.branch.casefold() for item in before):
            raise MasterExecutionError("branch is already checked out")
        branch_exists = self._git("show-ref", "--verify", "--quiet", f"refs/heads/{decision.branch}", check=False)
        if branch_exists.returncode == 0:
            raise MasterExecutionError("branch already exists; automatic reuse is not proven")
        try:
            self._git("worktree", "add", "-b", decision.branch, str(target), decision.checkpoint)
        except (MasterExecutionError, subprocess.TimeoutExpired) as exc:
            reconciled = next((item for item in self.snapshot()
                               if _path_key(item.path) == _path_key(target)), None)
            if reconciled and reconciled.branch.casefold() == decision.branch.casefold():
                return reconciled
            raise MasterExecutionError("worktree create outcome is not reconciled") from exc
        created = next((item for item in self.snapshot() if _path_key(item.path) == _path_key(target)), None)
        if created is None or created.branch.casefold() != decision.branch.casefold():
            raise MasterExecutionError("worktree create read-back mismatch")
        return created


def _request_from_json(raw: Any) -> RouteRequest:
    keys = {"master_id", "track_id", "task_kind", "repository", "branch", "worktree", "checkpoint", "ownership"}
    data = _exact(raw, keys, "route request")
    ownership = tuple(_strings(data["ownership"], "route ownership"))
    return RouteRequest(**{key: data[key] for key in keys if key != "ownership"}, ownership=ownership)


def _read_json(path: Path) -> Any:
    if str(path).startswith(("\\\\", "//")):
        raise MasterExecutionError("network JSON paths are forbidden")
    with path.open("rb") as stream:
        raw = stream.read(MAX_STATE_CHARS + 1)
    if len(raw) > MAX_STATE_CHARS:
        raise MasterExecutionError("JSON input exceeds size limit")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)


def _context_from_json(raw: Any) -> tuple[ContextItem, ...]:
    if type(raw) is not list or len(raw) > MAX_ITEMS:
        raise MasterExecutionError("invalid context input")
    result = []
    for item in raw:
        data = _exact(item, {"ref", "content", "contour", "evidence_thread"}, "context item")
        result.append(ContextItem(**data))
    return tuple(result)


def _recovery_from_json(raw: Any) -> RecoveryFacts:
    keys = {
        "git_head", "worktree_exists", "branch_exists", "dirty", "source_revision",
        "queue_item_present", "launcher_state_revision", "launcher_checkpoint",
        "checkpoint_reachable", "state_revision_at_head", "overlapping_contract_merged",
        "context_compacted",
    }
    data = _exact(raw, keys, "recovery facts")
    for key in ("git_head", "source_revision", "launcher_checkpoint"):
        _string(data[key], f"recovery {key}")
    for key in ("worktree_exists", "branch_exists", "dirty", "queue_item_present",
                "checkpoint_reachable", "state_revision_at_head", "overlapping_contract_merged",
                "context_compacted"):
        if type(data[key]) is not bool:
            raise MasterExecutionError(f"invalid recovery {key}")
    if type(data["launcher_state_revision"]) is not int or data["launcher_state_revision"] < 1:
        raise MasterExecutionError("invalid recovery launcher_state_revision")
    return RecoveryFacts(**data)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--context", type=Path)
    parser.add_argument("--recovery", type=Path)
    parser.add_argument("--worktree-root", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--compatibility", action="store_true")
    parser.add_argument(
        "--materialize-compatibility", "--materialize-plan", "--plan-file",
        dest="materialize_plan", type=Path,
        metavar="PLAN",
        help="apply one explicit digest-matched stage compatibility plan",
    )
    parser.add_argument("--expected-plan-digest", dest="expected_plan_digest")
    args = parser.parse_args(argv)
    try:
        if args.compatibility:
            if args.request or args.context or args.recovery or args.worktree_root or args.apply or args.materialize_plan or args.expected_plan_digest:
                raise MasterExecutionError("--compatibility cannot be combined with execution options")
            print(json.dumps({"ok": True, "compatibility": inspect_compatibility(args.project)}, ensure_ascii=False, sort_keys=True))
            return 0
        if args.materialize_plan is not None:
            if args.request or args.context or args.recovery or args.worktree_root or args.apply:
                raise MasterExecutionError("--materialize-plan cannot be combined with execution options")
            result = materialize_plan(
                args.project, args.materialize_plan,
                expected_plan_digest=args.expected_plan_digest,
            )
            print(json.dumps({"ok": result["status"] in {"materialized", "already_materialized"},
                              "materialization": result}, ensure_ascii=False, sort_keys=True))
            return 0 if result["status"] in {"materialized", "already_materialized"} else 2
        if args.expected_plan_digest:
            raise MasterExecutionError("--expected-plan-digest requires --materialize-plan")
        routing, selected_record = stage_routing_snapshot(args.project)
        if routing["execution_allowed"] is not True:
            print(json.dumps({
                "ok": False,
                "inspection_ok": routing["inspection_ok"],
                "canonical_valid": False,
                "execution_allowed": False,
                "stage_state": routing,
            }, ensure_ascii=False, sort_keys=True))
            return 1
        try:
            if selected_record is None or type(routing.get("stage_selector")) is not str:
                raise MasterExecutionError("canonical routing snapshot is incomplete")
            stage_id = routing["stage_selector"]
            state = extract_master_state(selected_record)
        except MasterExecutionError as exc:
            if str(exc) != "selected record must contain exactly one master-execution block":
                raise
            if args.request or args.context or args.recovery or args.worktree_root or args.apply:
                raise MasterExecutionError("ordinary canonical stage does not support CME execution options") from exc
            print(json.dumps({
                "ok": True,
                "stage_id": routing["stage_selector"],
                "stage_state": routing,
                "decision": {"action": "canonical_stage", "reason": "no_master_execution_state"},
            }, ensure_ascii=False, sort_keys=True))
            return 0
        output: dict[str, Any] = {"ok": True, "stage_id": stage_id,
                                  "master_id": state["master"]["id"], "state_revision": state["state_revision"],
                                  "stage_state": routing}
        output["decision"] = asdict(next_execution_decision(state))
        if args.recovery:
            output["recovery"] = asdict(recover_execution(state, _recovery_from_json(
                _read_json(args.recovery))))
        if args.context:
            decision = next_execution_decision(state)
            target = decision.slice_id or next((item["id"] for item in state["slices"]
                                                if item["status"] == "running"), "")
            if not target:
                raise MasterExecutionError("no current slice for context resolution")
            output["context"] = asdict(resolve_context(state, target, _context_from_json(
                _read_json(args.context))))
        if args.request:
            request = _request_from_json(_read_json(args.request))
            if args.worktree_root is None:
                raise MasterExecutionError("--worktree-root is required with --request")
            adapter = GitWorktreeAdapter(_expand_portable(request.repository), args.worktree_root)
            decision = route_worktree(state, request, adapter.snapshot())
            output["route"] = asdict(decision)
            if args.apply:
                output["worktree"] = asdict(adapter.ensure(decision))
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 0
    except (MasterExecutionError, OSError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)[:2000]}, ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
