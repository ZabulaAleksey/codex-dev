from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
import uuid
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence


SCHEMA_VERSION = 1
METRICS_DIR_NAME = ".metrics"
CONFIG_NAME = "config.json"
MAX_IDENTIFIER_LENGTH = 64
MAX_TEXT_LENGTH = 500
MAX_LINE_BYTES = 1024 * 1024
MAX_FILE_BYTES = 64 * 1024 * 1024
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
TASK_CLASSES = {
    "tiny",
    "small",
    "medium",
    "large",
    "research-heavy",
    "integration-heavy",
    "domain-heavy",
    "UI-heavy",
    "infra-heavy",
}
EVENT_FILES = {
    "command_run": "events.jsonl",
    "handoff": "events.jsonl",
    "discovery_decision": "events.jsonl",
    "reuse_outcome": "contours.jsonl",
    "stage_outcome": "stages.jsonl",
    "policy_definition": "policies.jsonl",
    "experiment_definition": "experiments.jsonl",
    "agent_outcome": "agents.jsonl",
}
DATA_FIELDS = {
    "command_run": {
        "command_class",
        "exit_code",
        "success",
        "git_revision",
        "git_branch",
        "git_dirty",
        "started_at",
        "ended_at",
    },
    "handoff": {
        "reason",
        "action",
        "expected_response",
        "completed",
        "estimated_ai_seconds",
        "estimated_human_seconds",
        "estimated_saving_seconds",
    },
    "discovery_decision": {
        "decision",
        "reason",
        "elapsed_seconds",
        "tokens_used",
        "cost_used",
        "candidate_strength",
        "estimated_adaptation_cost",
        "estimated_greenfield_cost",
    },
    "reuse_outcome": {
        "source",
        "selected",
        "success",
        "verified",
        "discovery_cost",
        "evaluation_cost",
        "adaptation_cost",
        "integration_cost",
        "verification_cost",
        "actual_reuse_cost",
        "estimated_greenfield_cost",
        "classification",
    },
    "stage_outcome": {
        "verified",
        "first_pass_dod",
        "human_interventions",
        "post_completion_defects",
        "outcome_label",
    },
    "policy_definition": {"status", "purpose", "feature_class", "verdict"},
    "experiment_definition": {"hypothesis", "baseline_arm", "variant_arm", "minimum_sample_size"},
    "agent_outcome": {"agent_id", "success", "value_added", "human_interventions"},
}
REQUIRED_DATA_FIELDS = {
    "command_run": DATA_FIELDS["command_run"],
    "handoff": DATA_FIELDS["handoff"],
    "discovery_decision": {"decision", "reason", "elapsed_seconds", "tokens_used", "cost_used", "candidate_strength"},
    "reuse_outcome": DATA_FIELDS["reuse_outcome"],
    "stage_outcome": DATA_FIELDS["stage_outcome"],
    "policy_definition": DATA_FIELDS["policy_definition"],
    "experiment_definition": DATA_FIELDS["experiment_definition"],
    "agent_outcome": DATA_FIELDS["agent_outcome"],
}
METRIC_FIELDS = {
    "wall_seconds",
    "profiler_overhead_seconds",
    "tokens_in",
    "tokens_out",
    "tokens_total",
    "context_tokens",
    "human_active_minutes",
    "rework_minutes",
    "ai_cost",
    "effective_cost",
}
TOP_LEVEL_FIELDS = {
    "schema_version",
    "timestamp",
    "event_id",
    "event_type",
    "project_id",
    "stage_id",
    "policy_ids",
    "experiment_id",
    "experiment_arm",
    "task_class",
    "metrics",
    "data",
}
HANDOFF_REASONS = {
    "ECONOMIC",
    "TOOL_LIMITATION",
    "VISUAL_CHECK",
    "PHYSICAL_ACTION",
    "SECURITY_CONFIRMATION",
    "LEARNING",
    "AMBIGUITY_RESOLUTION",
}


class ProfilingError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_identifier(value: str | None, field: str, *, optional: bool = False) -> None:
    if value is None and optional:
        return
    if not isinstance(value, str) or not IDENTIFIER_RE.fullmatch(value):
        raise ProfilingError(
            f"{field} must match {IDENTIFIER_RE.pattern} and be at most {MAX_IDENTIFIER_LENGTH} characters"
        )


def validate_text(value: object, field: str) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_TEXT_LENGTH:
        raise ProfilingError(f"{field} must be non-empty text of at most {MAX_TEXT_LENGTH} characters")
    if any(ord(char) < 32 and char not in "\t" for char in value):
        raise ProfilingError(f"{field} contains control characters")


def validate_timestamp(value: object) -> None:
    validate_text(value, "timestamp")
    assert isinstance(value, str)
    if not value.endswith("Z"):
        raise ProfilingError("timestamp must be UTC and end with Z")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ProfilingError("timestamp must be ISO-8601 UTC") from exc


def non_negative_number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProfilingError(f"{field} must be a finite non-negative number")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ProfilingError(f"{field} must be a finite non-negative number")
    return number


def resolve_project_root(root: Path) -> Path:
    resolved = root.expanduser().resolve()
    if not resolved.is_dir():
        raise ProfilingError(f"project root is not a directory: {resolved}")
    return resolved


def metrics_directory(root: Path, *, require: bool = True) -> Path:
    root = resolve_project_root(root)
    candidate = root / METRICS_DIR_NAME
    if candidate.exists():
        resolved = candidate.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ProfilingError("metrics directory escapes project root") from exc
        if resolved != candidate.absolute():
            raise ProfilingError("metrics directory must not be a symlink or junction")
        if not resolved.is_dir():
            raise ProfilingError("metrics path is not a directory")
        return resolved
    if require:
        raise ProfilingError("profiling is disabled: run init to create .metrics")
    return candidate


def contained_metrics_path(root: Path, *parts: str) -> Path:
    directory = metrics_directory(root)
    candidate = directory.joinpath(*parts)
    resolved = candidate.resolve()
    try:
        resolved.relative_to(directory)
    except ValueError as exc:
        raise ProfilingError("metrics path escapes project runtime directory") from exc
    if resolved != candidate.absolute():
        raise ProfilingError("metrics child paths must not be symlinks or junctions")
    return candidate


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


@contextmanager
def exclusive_lock(path: Path, timeout_seconds: float = 2.0) -> Iterator[None]:
    deadline = time.monotonic() + timeout_seconds
    descriptor: int | None = None
    last_permission_error: PermissionError | None = None
    while descriptor is None:
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise ProfilingError(f"telemetry stream is locked: {path.name}")
            time.sleep(0.01)
        except PermissionError as exc:
            last_permission_error = exc
            if time.monotonic() >= deadline:
                if path.exists():
                    raise ProfilingError(f"telemetry stream is locked: {path.name}") from exc
                raise last_permission_error
            time.sleep(0.01)
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode("ascii"))
        os.fsync(descriptor)
        yield
    finally:
        os.close(descriptor)
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def initialize(root: Path, project_id: str) -> Path:
    validate_identifier(project_id, "project_id")
    root = resolve_project_root(root)
    directory = metrics_directory(root, require=False)
    directory.mkdir(parents=False, exist_ok=True)
    directory = metrics_directory(root)
    contained_metrics_path(root, "reports").mkdir(exist_ok=True)
    config_path = contained_metrics_path(root, CONFIG_NAME)
    config = {"schema_version": SCHEMA_VERSION, "enabled": True, "project_id": project_id}
    if config_path.exists():
        existing = load_config(root)
        if existing["project_id"] != project_id:
            raise ProfilingError("existing metrics config uses a different project_id")
    else:
        atomic_write(config_path, json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    atomic_write(
        contained_metrics_path(root, ".gitignore"),
        "# Runtime AI Policy Profiling data; keep it local by default.\n*.jsonl\n*.lock\nreports/\nconfig.json\nREADME.md\n",
    )
    atomic_write(
        contained_metrics_path(root, "README.md"),
        "# Local AI Policy Profiling data\n\nThis directory is opt-in runtime state. Do not commit JSONL or reports.\n",
    )
    for filename in sorted(set(EVENT_FILES.values())):
        contained_metrics_path(root, filename).touch(exist_ok=True)
    return directory


def load_config(root: Path) -> dict[str, object]:
    path = contained_metrics_path(root, CONFIG_NAME)
    if not path.is_file() or path.stat().st_size > MAX_LINE_BYTES:
        raise ProfilingError("metrics config is missing or oversized")
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProfilingError("metrics config is invalid") from exc
    if not isinstance(config, dict) or set(config) != {"schema_version", "enabled", "project_id"}:
        raise ProfilingError("metrics config has unsupported fields")
    if config["schema_version"] != SCHEMA_VERSION or config["enabled"] is not True:
        raise ProfilingError("metrics config is disabled or uses an unsupported schema")
    validate_identifier(config["project_id"] if isinstance(config["project_id"], str) else None, "project_id")
    return config


def make_event(
    event_type: str,
    project_id: str,
    *,
    stage_id: str | None = None,
    policy_ids: Sequence[str] = (),
    experiment_id: str | None = None,
    experiment_arm: str | None = None,
    task_class: str | None = None,
    metrics: Mapping[str, float] | None = None,
    data: Mapping[str, object] | None = None,
) -> dict[str, object]:
    event = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": utc_now(),
        "event_id": uuid.uuid4().hex,
        "event_type": event_type,
        "project_id": project_id,
        "stage_id": stage_id,
        "policy_ids": sorted(set(policy_ids)),
        "experiment_id": experiment_id,
        "experiment_arm": experiment_arm,
        "task_class": task_class,
        "metrics": dict(metrics or {}),
        "data": dict(data or {}),
    }
    validate_event(event)
    return event


def validate_event(event: object) -> None:
    if not isinstance(event, dict) or set(event) != TOP_LEVEL_FIELDS:
        raise ProfilingError("telemetry envelope fields do not match schema v1")
    if event["schema_version"] != SCHEMA_VERSION:
        raise ProfilingError("unsupported telemetry schema version")
    validate_timestamp(event["timestamp"])
    validate_identifier(event["event_id"] if isinstance(event["event_id"], str) else None, "event_id")
    event_type = event["event_type"]
    if not isinstance(event_type, str) or event_type not in EVENT_FILES:
        raise ProfilingError("unsupported event_type")
    validate_identifier(event["project_id"] if isinstance(event["project_id"], str) else None, "project_id")
    validate_identifier(event["stage_id"] if isinstance(event["stage_id"], str) else None, "stage_id", optional=True)
    policy_ids = event["policy_ids"]
    if not isinstance(policy_ids, list) or len(policy_ids) > 16 or len(policy_ids) != len(set(policy_ids)):
        raise ProfilingError("policy_ids must be a unique list with at most 16 items")
    for policy_id in policy_ids:
        validate_identifier(policy_id if isinstance(policy_id, str) else None, "policy_id")
    experiment_id = event["experiment_id"]
    experiment_arm = event["experiment_arm"]
    validate_identifier(experiment_id if isinstance(experiment_id, str) else None, "experiment_id", optional=True)
    validate_identifier(experiment_arm if isinstance(experiment_arm, str) else None, "experiment_arm", optional=True)
    if (experiment_id is None) != (experiment_arm is None):
        raise ProfilingError("experiment_id and experiment_arm must be provided together")
    task_class = event["task_class"]
    if task_class is not None and task_class not in TASK_CLASSES:
        raise ProfilingError("unsupported task_class")
    metrics = event["metrics"]
    if not isinstance(metrics, dict) or not set(metrics).issubset(METRIC_FIELDS):
        raise ProfilingError("metrics contain unsupported fields")
    for name, value in metrics.items():
        non_negative_number(value, f"metrics.{name}")
    data = event["data"]
    if not isinstance(data, dict) or not set(data).issubset(DATA_FIELDS[event_type]):
        raise ProfilingError(f"data contains unsupported fields for {event_type}")
    missing = REQUIRED_DATA_FIELDS[event_type] - set(data)
    if missing:
        raise ProfilingError(f"data is missing required fields for {event_type}: {', '.join(sorted(missing))}")
    if event_type == "stage_outcome" and event["stage_id"] is None:
        raise ProfilingError("stage_outcome requires stage_id")
    if event_type == "policy_definition" and len(policy_ids) != 1:
        raise ProfilingError("policy_definition requires exactly one policy_id")
    if event_type == "experiment_definition" and experiment_id is None:
        raise ProfilingError("experiment_definition requires experiment_id and experiment_arm")
    _validate_event_data(event_type, data)


def _validate_event_data(event_type: str, data: Mapping[str, object]) -> None:
    text_fields = {
        "command_class",
        "git_revision",
        "git_branch",
        "started_at",
        "ended_at",
        "reason",
        "action",
        "expected_response",
        "candidate_strength",
        "decision",
        "source",
        "classification",
        "outcome_label",
        "status",
        "purpose",
        "feature_class",
        "verdict",
        "hypothesis",
        "baseline_arm",
        "variant_arm",
        "agent_id",
        "value_added",
    }
    bool_fields = {"success", "git_dirty", "completed", "selected", "verified", "first_pass_dod"}
    integer_fields = {"exit_code", "human_interventions", "post_completion_defects", "minimum_sample_size"}
    for name, value in data.items():
        if value is None and name in {"git_revision", "git_branch", "git_dirty"}:
            continue
        if name in text_fields:
            validate_text(value, f"data.{name}")
        elif name in bool_fields:
            if not isinstance(value, bool):
                raise ProfilingError(f"data.{name} must be boolean")
        elif name in integer_fields:
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                if name == "exit_code" and isinstance(value, int):
                    continue
                raise ProfilingError(f"data.{name} must be a non-negative integer")
        else:
            non_negative_number(value, f"data.{name}")
    if event_type == "command_run":
        validate_identifier(str(data["command_class"]), "data.command_class")
        validate_timestamp(data["started_at"])
        validate_timestamp(data["ended_at"])
    if event_type == "handoff" and data.get("reason") not in HANDOFF_REASONS:
        raise ProfilingError("unsupported handoff reason")
    if event_type == "handoff":
        expected_saving = max(0.0, float(data["estimated_ai_seconds"]) - float(data["estimated_human_seconds"]))
        if not math.isclose(float(data["estimated_saving_seconds"]), expected_saving, abs_tol=1e-9):
            raise ProfilingError("handoff estimated_saving_seconds is inconsistent")
    if event_type == "discovery_decision":
        if data["decision"] not in {"STOP_DISCOVERY", "CONTINUE_DISCOVERY"}:
            raise ProfilingError("unsupported discovery decision")
        if data["candidate_strength"] not in {"none", "weak", "strong"}:
            raise ProfilingError("unsupported candidate strength")
    if event_type == "reuse_outcome":
        if data["source"] not in {"project", "local", "internal", "trusted-upstream", "external"}:
            raise ProfilingError("unsupported reuse source")
        actual = sum(float(data[name]) for name in ("discovery_cost", "evaluation_cost", "adaptation_cost", "integration_cost", "verification_cost"))
        if not math.isclose(float(data["actual_reuse_cost"]), actual, abs_tol=1e-9):
            raise ProfilingError("actual_reuse_cost does not equal its components")
        expected = reuse_classification(
            selected=bool(data["selected"]),
            verified=bool(data["verified"]),
            actual_reuse_cost=actual,
            greenfield_cost=float(data["estimated_greenfield_cost"]),
        )
        if data["classification"] != expected:
            raise ProfilingError("reuse classification is inconsistent")
        if data["verified"] is True and data["success"] is not True:
            raise ProfilingError("verified reuse must also be successful")
    if event_type == "stage_outcome" and data["first_pass_dod"] is True and data["verified"] is not True:
        raise ProfilingError("first-pass DoD requires a verified stage outcome")
    if event_type == "policy_definition":
        if data["status"] not in {"experimental", "active", "disabled"}:
            raise ProfilingError("unsupported policy status")
        if data["feature_class"] not in {"immediate-optimizer", "compounding-infrastructure", "quality-insurance"}:
            raise ProfilingError("unsupported policy feature class")
        if data["verdict"] not in {"KEEP", "KEEP_WITH_LIMITS", "EXPERIMENTAL", "TUNE", "DISABLE_BY_DEFAULT", "REMOVE"}:
            raise ProfilingError("unsupported policy verdict")
    if event_type == "experiment_definition":
        validate_identifier(str(data["baseline_arm"]), "data.baseline_arm")
        validate_identifier(str(data["variant_arm"]), "data.variant_arm")
        if data["baseline_arm"] == data["variant_arm"]:
            raise ProfilingError("experiment arms must differ")
    if event_type == "agent_outcome":
        validate_identifier(str(data["agent_id"]), "data.agent_id")


def append_event(root: Path, event: dict[str, object], operation_started: float) -> Path:
    config = load_config(root)
    if event["project_id"] != config["project_id"]:
        raise ProfilingError("event project_id differs from metrics config")
    metrics = event["metrics"]
    assert isinstance(metrics, dict)
    metrics["profiler_overhead_seconds"] = max(0.0, time.perf_counter() - operation_started)
    validate_event(event)
    payload = json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"
    encoded = payload.encode("utf-8")
    if len(encoded) > MAX_LINE_BYTES:
        raise ProfilingError("telemetry line exceeds 1 MiB")
    path = contained_metrics_path(root, EVENT_FILES[str(event["event_type"])])
    size = path.stat().st_size if path.exists() else 0
    if size + len(encoded) > MAX_FILE_BYTES:
        raise ProfilingError("telemetry file exceeds 64 MiB")
    with exclusive_lock(path.with_suffix(path.suffix + ".lock")):
        current_size = path.stat().st_size if path.exists() else 0
        if current_size + len(encoded) > MAX_FILE_BYTES:
            raise ProfilingError("telemetry file exceeds 64 MiB")
        descriptor = os.open(path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        try:
            written = os.write(descriptor, encoded)
            if written != len(encoded):
                raise ProfilingError("telemetry append was incomplete")
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    return path


def git_facts(root: Path) -> dict[str, object]:
    def run(*args: str) -> str | None:
        try:
            result = subprocess.run(
                ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root), *args],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=5,
            )
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return None
        return result.stdout.strip() or None

    revision = run("rev-parse", "HEAD")
    branch = run("branch", "--show-current")
    status = run("status", "--porcelain")
    return {"git_revision": revision, "git_branch": branch, "git_dirty": bool(status) if status is not None else None}


def discovery_decision(
    *,
    elapsed_seconds: float,
    tokens_used: float,
    cost_used: float,
    wall_budget_seconds: float | None,
    token_budget: float | None,
    cost_budget: float | None,
    candidate_strength: str,
    estimated_adaptation_cost: float | None,
    estimated_greenfield_cost: float | None,
) -> dict[str, object]:
    for name, value in (("elapsed_seconds", elapsed_seconds), ("tokens_used", tokens_used), ("cost_used", cost_used)):
        non_negative_number(value, name)
    budgets = (wall_budget_seconds, token_budget, cost_budget)
    if all(value is None for value in budgets):
        return {"decision": "STOP_DISCOVERY", "reason": "BUDGET_REQUIRED"}
    checks = (
        (wall_budget_seconds, elapsed_seconds, "WALL_BUDGET_EXHAUSTED"),
        (token_budget, tokens_used, "TOKEN_BUDGET_EXHAUSTED"),
        (cost_budget, cost_used, "COST_BUDGET_EXHAUSTED"),
    )
    for budget, actual, reason in checks:
        if budget is not None:
            non_negative_number(budget, reason)
            if actual >= budget:
                return {"decision": "STOP_DISCOVERY", "reason": reason}
    if candidate_strength not in {"none", "weak", "strong"}:
        raise ProfilingError("candidate_strength must be none, weak or strong")
    if candidate_strength == "none":
        return {"decision": "STOP_DISCOVERY", "reason": "NO_CANDIDATE"}
    if estimated_adaptation_cost is not None and estimated_greenfield_cost is not None:
        adaptation = non_negative_number(estimated_adaptation_cost, "estimated_adaptation_cost")
        greenfield = non_negative_number(estimated_greenfield_cost, "estimated_greenfield_cost")
        if adaptation >= greenfield:
            return {"decision": "STOP_DISCOVERY", "reason": "GREENFIELD_BREAK_EVEN_REACHED"}
    return {"decision": "CONTINUE_DISCOVERY", "reason": "WITHIN_BUDGET"}


def handoff_decision(
    *,
    human_seconds: float,
    ai_seconds: float,
    simple: bool,
    special_expertise: bool,
    repeated_actions: int,
    reason: str,
) -> dict[str, object]:
    human = non_negative_number(human_seconds, "human_seconds")
    ai = non_negative_number(ai_seconds, "ai_seconds")
    if reason not in HANDOFF_REASONS:
        raise ProfilingError("unsupported handoff reason")
    if repeated_actions < 1:
        raise ProfilingError("repeated_actions must be at least 1")
    economic = simple and not special_expertise and repeated_actions == 1 and ai > human
    if reason == "LEARNING":
        decision = "DELEGATE_TO_HUMAN"
        decision_reason = "LEARNING"
    elif economic:
        decision = "DELEGATE_TO_HUMAN"
        decision_reason = reason
    else:
        decision = "KEEP_WITH_AI"
        decision_reason = "BATCH_OR_CAPABILITY_GUARD" if repeated_actions > 1 or special_expertise else "NO_ECONOMIC_GAIN"
    return {
        "decision": decision,
        "reason": decision_reason,
        "estimated_saving_seconds": max(0.0, ai - human) if decision == "DELEGATE_TO_HUMAN" else 0.0,
    }


def reuse_classification(*, selected: bool, verified: bool, actual_reuse_cost: float, greenfield_cost: float) -> str:
    actual = non_negative_number(actual_reuse_cost, "actual_reuse_cost")
    greenfield = non_negative_number(greenfield_cost, "greenfield_cost")
    if not selected:
        return "REUSE_NOT_SELECTED"
    if not verified or actual >= greenfield:
        return "REUSE_FALSE_POSITIVE"
    return "REUSE_SUCCESS"


def read_events(root: Path) -> list[dict[str, object]]:
    project_id = load_config(root)["project_id"]
    events: list[dict[str, object]] = []
    for filename in sorted(set(EVENT_FILES.values())):
        path = contained_metrics_path(root, filename)
        if not path.exists():
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            raise ProfilingError(f"{filename} exceeds 64 MiB")
        with path.open("rb") as stream:
            for line_number, raw in enumerate(stream, start=1):
                if len(raw) > MAX_LINE_BYTES:
                    raise ProfilingError(f"{filename}:{line_number} exceeds 1 MiB")
                if not raw.strip():
                    continue
                try:
                    event = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ProfilingError(f"{filename}:{line_number} is invalid JSON") from exc
                validate_event(event)
                if event["project_id"] != project_id:
                    raise ProfilingError(f"{filename}:{line_number} project_id differs from config")
                if EVENT_FILES[str(event["event_type"])] != filename:
                    raise ProfilingError(f"{filename}:{line_number} event_type belongs in a different stream")
                events.append(event)
    events.sort(key=lambda item: (str(item["timestamp"]), str(item["event_id"])))
    return events


def _numbers(events: Iterable[Mapping[str, object]], metric: str) -> list[float]:
    values: list[float] = []
    for event in events:
        metrics = event.get("metrics")
        if isinstance(metrics, dict) and metric in metrics:
            values.append(float(metrics[metric]))
    return values


def _median(values: Sequence[float]) -> float | None:
    return round(statistics.median(values), 6) if values else None


def _delta(variant: object, baseline: object) -> float | None:
    if isinstance(variant, (int, float)) and not isinstance(variant, bool) and isinstance(baseline, (int, float)) and not isinstance(baseline, bool):
        return round(float(variant) - float(baseline), 6)
    return None


def aggregate(events: Sequence[dict[str, object]]) -> dict[str, object]:
    by_type: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        by_type[str(event["event_type"])].append(event)
    stages = by_type["stage_outcome"]
    verified = [event for event in stages if isinstance(event["data"], dict) and event["data"].get("verified") is True]
    first_pass = [event for event in stages if isinstance(event["data"], dict) and event["data"].get("first_pass_dod") is True]
    reuse = by_type["reuse_outcome"]
    selected_reuse = [event for event in reuse if isinstance(event["data"], dict) and event["data"].get("selected") is True]
    successful_reuse = [event for event in selected_reuse if isinstance(event["data"], dict) and event["data"].get("classification") == "REUSE_SUCCESS"]
    false_reuse = [event for event in selected_reuse if isinstance(event["data"], dict) and event["data"].get("classification") == "REUSE_FALSE_POSITIVE"]
    handoffs = by_type["handoff"]
    completed_handoffs = [event for event in handoffs if isinstance(event["data"], dict) and event["data"].get("completed") is True]
    total_wall = sum(_numbers(events, "wall_seconds"))
    total_overhead = sum(_numbers(events, "profiler_overhead_seconds"))
    token_hotspots: dict[str, float] = {}
    wall_hotspots: dict[str, float] = {}
    for event_type, items in sorted(by_type.items()):
        token_hotspots[event_type] = round(sum(_numbers(items, "tokens_total")), 6)
        wall_hotspots[event_type] = round(sum(_numbers(items, "wall_seconds")), 6)

    experiment_groups: dict[tuple[str, str, str | None], list[dict[str, object]]] = defaultdict(list)
    for event in verified:
        experiment_id = event.get("experiment_id")
        arm = event.get("experiment_arm")
        if isinstance(experiment_id, str) and isinstance(arm, str):
            experiment_groups[(experiment_id, arm, event.get("task_class") if isinstance(event.get("task_class"), str) else None)].append(event)
    experiments: dict[str, object] = {}
    by_experiment: dict[str, dict[str, object]] = defaultdict(dict)
    for (experiment_id, arm, task_class), items in sorted(experiment_groups.items()):
        by_experiment[experiment_id][arm] = {
            "task_class": task_class,
            "verified_sample_size": len(items),
            "median_effective_cost": _median(_numbers(items, "effective_cost")),
            "median_wall_seconds": _median(_numbers(items, "wall_seconds")),
            "median_human_active_minutes": _median(_numbers(items, "human_active_minutes")),
            "first_pass_dod_rate": round(sum(1 for item in items if isinstance(item["data"], dict) and item["data"].get("first_pass_dod") is True) / len(items), 6),
        }
    definitions: dict[str, dict[str, object]] = {}
    for event in by_type["experiment_definition"]:
        experiment_id = event.get("experiment_id")
        if isinstance(experiment_id, str) and isinstance(event["data"], dict):
            definitions[experiment_id] = event["data"]
    for experiment_id, arms in sorted(by_experiment.items()):
        definition = definitions.get(experiment_id, {})
        baseline_arm = str(definition.get("baseline_arm", "baseline"))
        variant_arm = str(definition.get("variant_arm", "variant"))
        minimum_sample = int(definition.get("minimum_sample_size", 1))
        baseline = arms.get(baseline_arm)
        variant = arms.get(variant_arm)
        comparison: dict[str, object] | None = None
        if isinstance(baseline, dict) and isinstance(variant, dict):
            compatible = baseline["task_class"] == variant["task_class"]
            sufficient = baseline["verified_sample_size"] >= minimum_sample and variant["verified_sample_size"] >= minimum_sample
            comparison = {
                "baseline_arm": baseline_arm,
                "variant_arm": variant_arm,
                "task_class_compatible": compatible,
                "minimum_sample_size": minimum_sample,
                "sufficient_sample": sufficient,
                "median_effective_cost_delta": _delta(variant["median_effective_cost"], baseline["median_effective_cost"]),
                "median_wall_seconds_delta": _delta(variant["median_wall_seconds"], baseline["median_wall_seconds"]),
                "median_human_active_minutes_delta": _delta(variant["median_human_active_minutes"], baseline["median_human_active_minutes"]),
                "first_pass_dod_rate_delta": _delta(variant["first_pass_dod_rate"], baseline["first_pass_dod_rate"]),
            }
        experiments[experiment_id] = {
            "arms": arms,
            "comparison": comparison,
            "causality_claim": False,
            "note": "Compare only compatible task classes; medians and sample sizes are descriptive.",
        }

    reuse_efficiencies: list[float] = []
    for event in selected_reuse:
        data = event["data"]
        assert isinstance(data, dict)
        actual = float(data.get("actual_reuse_cost", 0))
        greenfield = float(data.get("estimated_greenfield_cost", 0))
        if actual > 0:
            reuse_efficiencies.append(greenfield / actual)

    policy_profiles: dict[str, dict[str, object]] = {}
    policy_events: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        for policy_id in event["policy_ids"] if isinstance(event["policy_ids"], list) else []:
            policy_events[str(policy_id)].append(event)
    for policy_id, items in sorted(policy_events.items()):
        policy_profiles[policy_id] = {
            "events": len(items),
            "verified_outcomes": sum(1 for item in items if item["event_type"] == "stage_outcome" and isinstance(item["data"], dict) and item["data"].get("verified") is True),
            "tokens_total": round(sum(_numbers(items, "tokens_total")), 6),
            "wall_seconds": round(sum(_numbers(items, "wall_seconds")), 6),
            "profiler_overhead_seconds": round(sum(_numbers(items, "profiler_overhead_seconds")), 6),
        }

    agent_profiles: dict[str, dict[str, object]] = {}
    agent_events: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in by_type["agent_outcome"]:
        data = event["data"]
        if isinstance(data, dict) and isinstance(data.get("agent_id"), str):
            agent_events[data["agent_id"]].append(event)
    for agent_id, items in sorted(agent_events.items()):
        agent_profiles[agent_id] = {
            "calls": len(items),
            "successful_tasks": sum(1 for item in items if isinstance(item["data"], dict) and item["data"].get("success") is True),
            "tokens_in": round(sum(_numbers(items, "tokens_in")), 6),
            "tokens_out": round(sum(_numbers(items, "tokens_out")), 6),
            "wall_seconds": round(sum(_numbers(items, "wall_seconds")), 6),
            "human_interventions": sum(int(item["data"].get("human_interventions", 0)) for item in items if isinstance(item["data"], dict)),
            "median_effective_cost": _median(_numbers(items, "effective_cost")),
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "events_total": len(events),
        "productivity": {
            "stage_outcomes": len(stages),
            "verified_outcomes": len(verified),
            "median_wall_seconds_per_verified_outcome": _median(_numbers(verified, "wall_seconds")),
            "median_human_active_minutes_per_verified_outcome": _median(_numbers(verified, "human_active_minutes")),
        },
        "ai_economics": {
            "median_tokens_per_verified_outcome": _median(_numbers(verified, "tokens_total")),
            "median_effective_cost_per_verified_outcome": _median(_numbers(verified, "effective_cost")),
            "profiler_overhead_seconds": round(total_overhead, 6),
            "profiler_overhead_ratio": round(total_overhead / total_wall, 6) if total_wall > 0 else None,
        },
        "quality": {
            "first_pass_dod_rate": round(len(first_pass) / len(stages), 6) if stages else None,
            "median_rework_minutes": _median(_numbers(stages, "rework_minutes")),
        },
        "reuse": {
            "attempts": len(selected_reuse),
            "successes": len(successful_reuse),
            "hit_rate": round(len(successful_reuse) / len(selected_reuse), 6) if selected_reuse else None,
            "false_positive_count": len(false_reuse),
            "false_positive_rate": round(len(false_reuse) / len(selected_reuse), 6) if selected_reuse else None,
            "median_efficiency": _median(reuse_efficiencies),
        },
        "human": {
            "handoffs": len(handoffs),
            "completed_handoffs": len(completed_handoffs),
            "estimated_saving_seconds": round(sum(float(event["data"].get("estimated_saving_seconds", 0)) for event in handoffs if isinstance(event["data"], dict)), 6),
        },
        "hotspots": {"tokens_by_event_type": token_hotspots, "wall_seconds_by_event_type": wall_hotspots},
        "policies": policy_profiles,
        "agents": agent_profiles,
        "experiments": experiments,
    }


def markdown_report(summary: Mapping[str, object]) -> str:
    productivity = summary["productivity"]
    economics = summary["ai_economics"]
    quality = summary["quality"]
    reuse = summary["reuse"]
    human = summary["human"]
    assert all(isinstance(item, dict) for item in (productivity, economics, quality, reuse, human))
    lines = [
        "# AI Policy Profiling report",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "## Productivity",
        "",
        f"- Stage outcomes: {productivity['stage_outcomes']}",
        f"- Verified outcomes: {productivity['verified_outcomes']}",
        f"- Median wall seconds / verified outcome: {productivity['median_wall_seconds_per_verified_outcome']}",
        f"- Median human active minutes / verified outcome: {productivity['median_human_active_minutes_per_verified_outcome']}",
        "",
        "## AI economics",
        "",
        f"- Median tokens / verified outcome: {economics['median_tokens_per_verified_outcome']}",
        f"- Median effective cost / verified outcome: {economics['median_effective_cost_per_verified_outcome']}",
        f"- Profiler overhead seconds: {economics['profiler_overhead_seconds']}",
        f"- Profiler overhead ratio: {economics['profiler_overhead_ratio']}",
        "",
        "## Quality and reuse",
        "",
        f"- First-pass DoD rate: {quality['first_pass_dod_rate']}",
        f"- Reuse hit rate: {reuse['hit_rate']}",
        f"- False reuse rate: {reuse['false_positive_rate']}",
        f"- Median reuse efficiency: {reuse['median_efficiency']}",
        "",
        "## Human handoffs",
        "",
        f"- Handoffs: {human['handoffs']}",
        f"- Completed: {human['completed_handoffs']}",
        f"- Estimated saving seconds: {human['estimated_saving_seconds']}",
        "",
        "## Experiments",
        "",
    ]
    experiments = summary["experiments"]
    assert isinstance(experiments, dict)
    if not experiments:
        lines.append("No comparable verified experiment outcomes.")
    for experiment_id, details in experiments.items():
        lines.extend((f"### {experiment_id}", "", "Descriptive medians only; no causality claim.", ""))
        assert isinstance(details, dict)
        arms = details["arms"]
        assert isinstance(arms, dict)
        for arm, values in arms.items():
            assert isinstance(values, dict)
            lines.append(
                f"- `{arm}`: n={values['verified_sample_size']}, task={values['task_class']}, "
                f"median cost={values['median_effective_cost']}, median wall={values['median_wall_seconds']}s, "
                f"first-pass DoD={values['first_pass_dod_rate']}"
            )
        comparison = details.get("comparison")
        if isinstance(comparison, dict):
            lines.append(
                f"- Comparison `{comparison['variant_arm']} - {comparison['baseline_arm']}`: "
                f"cost delta={comparison['median_effective_cost_delta']}, "
                f"wall delta={comparison['median_wall_seconds_delta']}s, "
                f"sample sufficient={comparison['sufficient_sample']}, "
                f"task classes compatible={comparison['task_class_compatible']}"
            )
    lines.extend(("", "## Policy profiles", ""))
    policies = summary["policies"]
    assert isinstance(policies, dict)
    if not policies:
        lines.append("No policy-linked events.")
    for policy_id, values in policies.items():
        assert isinstance(values, dict)
        lines.append(
            f"- `{policy_id}`: events={values['events']}, verified outcomes={values['verified_outcomes']}, "
            f"tokens={values['tokens_total']}, wall={values['wall_seconds']}s"
        )
    lines.extend(("", "## Agent profiles", ""))
    agents = summary["agents"]
    assert isinstance(agents, dict)
    if not agents:
        lines.append("No agent outcomes.")
    for agent_id, values in agents.items():
        assert isinstance(values, dict)
        lines.append(
            f"- `{agent_id}`: calls={values['calls']}, successes={values['successful_tasks']}, "
            f"tokens in/out={values['tokens_in']}/{values['tokens_out']}, wall={values['wall_seconds']}s"
        )
    lines.extend(("", "## Caveat", "", "Missing values remain unknown. Compare like-for-like task classes and sufficient samples before tuning policy thresholds.", ""))
    return "\n".join(lines)


def write_report(root: Path) -> tuple[Path, Path, dict[str, object]]:
    events = read_events(root)
    summary = aggregate(events)
    contained_metrics_path(root, "reports")
    json_path = contained_metrics_path(root, "reports", "latest.json")
    markdown_path = contained_metrics_path(root, "reports", "latest.md")
    json_content = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    markdown_content = markdown_report(summary)
    atomic_write(json_path, json_content)
    atomic_write(markdown_path, markdown_content)
    return json_path, markdown_path, summary


def add_common_event_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--stage-id")
    parser.add_argument("--policy-id", action="append", default=[])
    parser.add_argument("--experiment-id")
    parser.add_argument("--experiment-arm")
    parser.add_argument("--task-class", choices=sorted(TASK_CLASSES))


def optional_metrics(args: argparse.Namespace, *, wall_seconds: float | None = None) -> dict[str, float]:
    metrics: dict[str, float] = {}
    if wall_seconds is not None:
        metrics["wall_seconds"] = wall_seconds
    for field in ("tokens_in", "tokens_out", "tokens_total", "context_tokens", "human_active_minutes", "rework_minutes", "ai_cost", "effective_cost"):
        value = getattr(args, field, None)
        if value is not None:
            metrics[field] = non_negative_number(value, field)
    return metrics


def common_event(args: argparse.Namespace, event_type: str, data: Mapping[str, object], *, metrics: Mapping[str, float] | None = None) -> dict[str, object]:
    config = load_config(args.root)
    return make_event(
        event_type,
        str(config["project_id"]),
        stage_id=args.stage_id,
        policy_ids=args.policy_id,
        experiment_id=args.experiment_id,
        experiment_arm=args.experiment_arm,
        task_class=args.task_class,
        metrics=metrics,
        data=data,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Opt-in passive AI Policy Profiling / Agent Economics CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init", help="create local opt-in .metrics layout")
    init_parser.add_argument("--root", type=Path, default=Path.cwd())
    init_parser.add_argument("--project-id", required=True)

    run_parser = subparsers.add_parser("run", help="run a command and record safe automatic facts")
    add_common_event_arguments(run_parser)
    run_parser.add_argument("--command-class", required=True)
    run_parser.add_argument("command_args", nargs=argparse.REMAINDER)

    stage_parser = subparsers.add_parser("stage", help="record a stage outcome")
    add_common_event_arguments(stage_parser)
    stage_parser.add_argument("--verified", action="store_true")
    stage_parser.add_argument("--first-pass-dod", action="store_true")
    stage_parser.add_argument("--human-interventions", type=int, default=0)
    stage_parser.add_argument("--post-completion-defects", type=int, default=0)
    stage_parser.add_argument("--outcome-label", required=True)
    for field in ("wall_seconds", "tokens_total", "human_active_minutes", "rework_minutes", "effective_cost"):
        stage_parser.add_argument(f"--{field.replace('_', '-')}", dest=field, type=float)

    handoff_parser = subparsers.add_parser("handoff", help="record one bounded manual handoff")
    add_common_event_arguments(handoff_parser)
    handoff_parser.add_argument("--reason", choices=sorted(HANDOFF_REASONS), required=True)
    handoff_parser.add_argument("--action", required=True)
    handoff_parser.add_argument("--expected-response", required=True)
    handoff_parser.add_argument("--completed", action="store_true")
    handoff_parser.add_argument("--estimated-ai-seconds", type=float, required=True)
    handoff_parser.add_argument("--estimated-human-seconds", type=float, required=True)

    reuse_parser = subparsers.add_parser("reuse", help="record reusable contour economics")
    add_common_event_arguments(reuse_parser)
    reuse_parser.add_argument("--source", choices=("project", "local", "internal", "trusted-upstream", "external"), required=True)
    reuse_parser.add_argument("--selected", action="store_true")
    reuse_parser.add_argument("--success", action="store_true")
    reuse_parser.add_argument("--verified", action="store_true")
    for field in ("discovery_cost", "evaluation_cost", "adaptation_cost", "integration_cost", "verification_cost", "estimated_greenfield_cost"):
        reuse_parser.add_argument(f"--{field.replace('_', '-')}", dest=field, type=float, required=True)

    discovery_parser = subparsers.add_parser("discovery-decision", help="evaluate bounded discovery")
    discovery_parser.add_argument("--elapsed-seconds", type=float, default=0)
    discovery_parser.add_argument("--tokens-used", type=float, default=0)
    discovery_parser.add_argument("--cost-used", type=float, default=0)
    discovery_parser.add_argument("--wall-budget-seconds", type=float)
    discovery_parser.add_argument("--token-budget", type=float)
    discovery_parser.add_argument("--cost-budget", type=float)
    discovery_parser.add_argument("--candidate-strength", choices=("none", "weak", "strong"), required=True)
    discovery_parser.add_argument("--estimated-adaptation-cost", type=float)
    discovery_parser.add_argument("--estimated-greenfield-cost", type=float)

    decision_parser = subparsers.add_parser("handoff-decision", help="evaluate human-vs-AI handoff")
    decision_parser.add_argument("--human-seconds", type=float, required=True)
    decision_parser.add_argument("--ai-seconds", type=float, required=True)
    decision_parser.add_argument("--simple", action="store_true")
    decision_parser.add_argument("--special-expertise", action="store_true")
    decision_parser.add_argument("--repeated-actions", type=int, default=1)
    decision_parser.add_argument("--reason", choices=sorted(HANDOFF_REASONS), default="ECONOMIC")

    policy_parser = subparsers.add_parser("policy", help="record a policy definition")
    add_common_event_arguments(policy_parser)
    policy_parser.add_argument("--status", choices=("experimental", "active", "disabled"), required=True)
    policy_parser.add_argument("--purpose", required=True)
    policy_parser.add_argument("--feature-class", choices=("immediate-optimizer", "compounding-infrastructure", "quality-insurance"), required=True)
    policy_parser.add_argument("--verdict", choices=("KEEP", "KEEP_WITH_LIMITS", "EXPERIMENTAL", "TUNE", "DISABLE_BY_DEFAULT", "REMOVE"), required=True)

    experiment_parser = subparsers.add_parser("experiment", help="record an experiment definition")
    add_common_event_arguments(experiment_parser)
    experiment_parser.add_argument("--hypothesis", required=True)
    experiment_parser.add_argument("--baseline-arm", required=True)
    experiment_parser.add_argument("--variant-arm", required=True)
    experiment_parser.add_argument("--minimum-sample-size", type=int, required=True)

    discovery_event_parser = subparsers.add_parser("discovery", help="record a bounded discovery decision")
    add_common_event_arguments(discovery_event_parser)
    discovery_event_parser.add_argument("--elapsed-seconds", type=float, default=0)
    discovery_event_parser.add_argument("--tokens-used", type=float, default=0)
    discovery_event_parser.add_argument("--cost-used", type=float, default=0)
    discovery_event_parser.add_argument("--wall-budget-seconds", type=float)
    discovery_event_parser.add_argument("--token-budget", type=float)
    discovery_event_parser.add_argument("--cost-budget", type=float)
    discovery_event_parser.add_argument("--candidate-strength", choices=("none", "weak", "strong"), required=True)
    discovery_event_parser.add_argument("--estimated-adaptation-cost", type=float)
    discovery_event_parser.add_argument("--estimated-greenfield-cost", type=float)

    agent_parser = subparsers.add_parser("agent", help="record a bounded agent outcome")
    add_common_event_arguments(agent_parser)
    agent_parser.add_argument("--agent-id", required=True)
    agent_parser.add_argument("--success", action="store_true")
    agent_parser.add_argument("--value-added", required=True)
    agent_parser.add_argument("--human-interventions", type=int, default=0)
    for field in ("wall_seconds", "tokens_in", "tokens_out", "tokens_total", "human_active_minutes", "rework_minutes", "ai_cost", "effective_cost"):
        agent_parser.add_argument(f"--{field.replace('_', '-')}", dest=field, type=float)

    report_parser = subparsers.add_parser("report", help="validate and aggregate local telemetry")
    report_parser.add_argument("--root", type=Path, default=Path.cwd())
    report_parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    operation_started = time.perf_counter()
    try:
        if args.command == "init":
            directory = initialize(args.root, args.project_id)
            print(f"profiling enabled: {directory}")
            return 0
        if args.command == "discovery-decision":
            values = vars(args).copy()
            values.pop("command")
            decision = discovery_decision(**values)
            print(json.dumps(decision, ensure_ascii=False, sort_keys=True))
            return 0
        if args.command == "handoff-decision":
            values = vars(args).copy()
            values.pop("command")
            print(json.dumps(handoff_decision(**values), ensure_ascii=False, sort_keys=True))
            return 0
        if args.command == "report":
            json_path, markdown_path, summary = write_report(args.root)
            if args.json:
                print(json.dumps(summary, ensure_ascii=False, indent=2))
            else:
                print(f"report written: {markdown_path} ({json_path})")
            return 0
        if args.command == "run":
            command = list(args.command_args)
            if command and command[0] == "--":
                command = command[1:]
            if not command:
                raise ProfilingError("run requires a command after --")
            validate_identifier(args.command_class, "command_class")
            started_at = utc_now()
            run_started = time.perf_counter()
            completed = subprocess.run(command, cwd=resolve_project_root(args.root), check=False)
            wall_seconds = time.perf_counter() - run_started
            profiling_started = time.perf_counter()
            data = {"command_class": args.command_class, "exit_code": completed.returncode, "success": completed.returncode == 0, "started_at": started_at, "ended_at": utc_now()} | git_facts(resolve_project_root(args.root))
            event = common_event(args, "command_run", data, metrics={"wall_seconds": wall_seconds})
            append_event(args.root, event, profiling_started)
            return completed.returncode
        if args.command == "stage":
            if args.human_interventions < 0 or args.post_completion_defects < 0:
                raise ProfilingError("stage counts must be non-negative")
            data = {"verified": args.verified, "first_pass_dod": args.first_pass_dod, "human_interventions": args.human_interventions, "post_completion_defects": args.post_completion_defects, "outcome_label": args.outcome_label}
            event = common_event(args, "stage_outcome", data, metrics=optional_metrics(args, wall_seconds=args.wall_seconds))
        elif args.command == "handoff":
            ai_seconds = non_negative_number(args.estimated_ai_seconds, "estimated_ai_seconds")
            human_seconds = non_negative_number(args.estimated_human_seconds, "estimated_human_seconds")
            data = {"reason": args.reason, "action": args.action, "expected_response": args.expected_response, "completed": args.completed, "estimated_ai_seconds": ai_seconds, "estimated_human_seconds": human_seconds, "estimated_saving_seconds": max(0.0, ai_seconds - human_seconds)}
            event = common_event(args, "handoff", data)
        elif args.command == "reuse":
            components = [args.discovery_cost, args.evaluation_cost, args.adaptation_cost, args.integration_cost, args.verification_cost]
            actual = sum(non_negative_number(value, "reuse cost") for value in components)
            classification = reuse_classification(selected=args.selected, verified=args.verified, actual_reuse_cost=actual, greenfield_cost=args.estimated_greenfield_cost)
            data = {"source": args.source, "selected": args.selected, "success": args.success, "verified": args.verified, "discovery_cost": args.discovery_cost, "evaluation_cost": args.evaluation_cost, "adaptation_cost": args.adaptation_cost, "integration_cost": args.integration_cost, "verification_cost": args.verification_cost, "actual_reuse_cost": actual, "estimated_greenfield_cost": args.estimated_greenfield_cost, "classification": classification}
            event = common_event(args, "reuse_outcome", data)
        elif args.command == "policy":
            if len(args.policy_id) != 1:
                raise ProfilingError("policy command requires exactly one --policy-id")
            data = {"status": args.status, "purpose": args.purpose, "feature_class": args.feature_class, "verdict": args.verdict}
            event = common_event(args, "policy_definition", data)
        elif args.command == "experiment":
            if args.experiment_id is None or args.experiment_arm is None:
                raise ProfilingError("experiment command requires --experiment-id and --experiment-arm")
            if args.minimum_sample_size < 1:
                raise ProfilingError("minimum sample size must be positive")
            data = {"hypothesis": args.hypothesis, "baseline_arm": args.baseline_arm, "variant_arm": args.variant_arm, "minimum_sample_size": args.minimum_sample_size}
            event = common_event(args, "experiment_definition", data)
        elif args.command == "discovery":
            decision = discovery_decision(
                elapsed_seconds=args.elapsed_seconds,
                tokens_used=args.tokens_used,
                cost_used=args.cost_used,
                wall_budget_seconds=args.wall_budget_seconds,
                token_budget=args.token_budget,
                cost_budget=args.cost_budget,
                candidate_strength=args.candidate_strength,
                estimated_adaptation_cost=args.estimated_adaptation_cost,
                estimated_greenfield_cost=args.estimated_greenfield_cost,
            )
            data = {
                "decision": decision["decision"],
                "reason": decision["reason"],
                "elapsed_seconds": args.elapsed_seconds,
                "tokens_used": args.tokens_used,
                "cost_used": args.cost_used,
                "candidate_strength": args.candidate_strength,
            }
            if args.estimated_adaptation_cost is not None:
                data["estimated_adaptation_cost"] = args.estimated_adaptation_cost
            if args.estimated_greenfield_cost is not None:
                data["estimated_greenfield_cost"] = args.estimated_greenfield_cost
            event = common_event(args, "discovery_decision", data)
        elif args.command == "agent":
            validate_identifier(args.agent_id, "agent_id")
            if args.human_interventions < 0:
                raise ProfilingError("human_interventions must be non-negative")
            data = {"agent_id": args.agent_id, "success": args.success, "value_added": args.value_added, "human_interventions": args.human_interventions}
            event = common_event(args, "agent_outcome", data, metrics=optional_metrics(args, wall_seconds=args.wall_seconds))
        else:
            parser.error(f"unsupported command: {args.command}")
            return 2
        append_event(args.root, event, operation_started)
        print(json.dumps(event, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ProfilingError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
