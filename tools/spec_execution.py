#!/usr/bin/env python3
"""Bounded, side-effect-free decisions for the Specification → Execution Pipeline.

The module consumes explicit structured facts.  It never executes registry commands, changes Git,
loads an unselected Skill body, mutates a project, or writes external state.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
import tomllib
from typing import Any, Iterable, Mapping, Sequence


MAX_INPUT_BYTES = 512 * 1024
MAX_REGISTRY_BYTES = 512 * 1024
MAX_ITEMS = 128
MAX_LIST_ITEMS = 32
MAX_TEXT = 4096
MAX_OBSERVATION = 2048
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SKILL_NAME = re.compile(r"^name:\s*([^\r\n]+)\s*$", re.MULTILINE)

ENTRYPOINTS = {"CONTINUE_EXISTING", "NEW_PROJECT"}
PROJECT_CLASSES = {
    "GREENFIELD",
    "COMPOSITION",
    "FORK_EXTERNAL_REPOSITORY",
    "MIGRATION_ADOPTION_EXISTING_CODEBASE",
}
SCOPES = {"global", "domain", "project"}
SKILL_STATUSES = {"active", "deprecated", "retired"}
MATURITY = {
    "documented_skill",
    "deterministic_script",
    "shared_library",
    "validator",
    "automatic_gate",
}
EXECUTOR_KINDS = {
    "skill_only",
    "skill_with_tool",
    "deterministic_tool",
    "validator",
}
FULL_SCAN_REASONS = {
    "unknown_ownership",
    "architecture_drift",
    "contract_conflict",
    "final_audit",
    "unknown_regression",
    "explicit_user_request",
    "targeted_path_failed",
}

SKILL_KEYS = {
    "id",
    "source",
    "scope",
    "status",
    "capabilities",
    "triggers",
    "inputs",
    "outputs",
    "required_tools",
    "required_context",
    "stop_conditions",
    "validation",
    "version",
    "maturity",
    "executor_kind",
    "owner",
    "replacement",
}


class SpecExecutionError(ValueError):
    """Fail-closed structured-input or registry error."""

    def __init__(self, message: str, code: str = "invalid_input") -> None:
        super().__init__(message)
        self.code = code


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SpecExecutionError(f"duplicate JSON key: {key}", "duplicate_json_key")
        result[key] = value
    return result


@dataclass(frozen=True)
class SkillMetadata:
    id: str
    source: str
    scope: str
    status: str
    capabilities: tuple[str, ...]
    triggers: tuple[str, ...]
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    required_tools: tuple[str, ...]
    required_context: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    validation: tuple[str, ...]
    version: str
    maturity: str
    executor_kind: str
    owner: str
    replacement: str


def _mapping(value: Any, label: str, *, allowed: set[str], required: set[str] = frozenset()) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SpecExecutionError(f"{label} must be an object")
    keys = set(value)
    unknown = sorted(keys - allowed)
    missing = sorted(required - keys)
    if unknown:
        raise SpecExecutionError(f"{label} has unknown fields: {','.join(unknown)}")
    if missing:
        raise SpecExecutionError(f"{label} is missing fields: {','.join(missing)}")
    return value


def _text(value: Any, label: str, *, required: bool = True, limit: int = MAX_TEXT) -> str:
    if not isinstance(value, str):
        raise SpecExecutionError(f"{label} must be a string")
    if len(value) > limit:
        raise SpecExecutionError(f"{label} is oversized")
    if required and not value.strip():
        raise SpecExecutionError(f"{label} must not be empty")
    return value


def _identifier(value: Any, label: str) -> str:
    value = _text(value, label, limit=128)
    if not IDENTIFIER.fullmatch(value):
        raise SpecExecutionError(f"{label} is invalid")
    return value


def _string_list(
    value: Any,
    label: str,
    *,
    identifiers: bool = False,
    required: bool = False,
    preserve: bool = False,
) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) > MAX_LIST_ITEMS:
        raise SpecExecutionError(f"{label} must be a bounded list")
    if required and not value:
        raise SpecExecutionError(f"{label} must not be empty")
    result: list[str] = []
    for index, item in enumerate(value):
        parsed = _identifier(item, f"{label}[{index}]") if identifiers else _text(
            item, f"{label}[{index}]", limit=MAX_OBSERVATION
        )
        if parsed in result:
            raise SpecExecutionError(f"{label} contains duplicates")
        result.append(parsed)
    return tuple(result if preserve else sorted(result))


def _contained(root: Path, relative: str, label: str) -> Path:
    path = Path(_text(relative, label, limit=512))
    if path.is_absolute() or ".." in path.parts:
        raise SpecExecutionError(f"{label} must be a contained relative path")
    target = (root / path).resolve(strict=False)
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise SpecExecutionError(f"{label} escapes source root") from exc
    return target


def _skill_name(path: Path) -> str:
    if not path.is_file() or path.stat().st_size > MAX_REGISTRY_BYTES:
        raise SpecExecutionError(f"Skill source is missing or oversized: {path}")
    text = path.read_text(encoding="utf-8")
    match = SKILL_NAME.search(text[:8192])
    if not match:
        raise SpecExecutionError(f"Skill source has no frontmatter name: {path}")
    return match.group(1).strip().strip('"\'')


def load_registry(path: Path, source_root: Path | None = None) -> tuple[SkillMetadata, ...]:
    """Load and validate metadata without loading Skill procedure bodies into the route output."""
    path = path.resolve()
    if not path.is_file() or path.stat().st_size > MAX_REGISTRY_BYTES:
        raise SpecExecutionError("registry is missing or oversized")
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise SpecExecutionError("registry is unreadable or invalid") from exc
    data = _mapping(raw, "registry", allowed={"schema_version", "skills"}, required={"schema_version", "skills"})
    if data["schema_version"] != 1:
        raise SpecExecutionError("unsupported registry schema_version")
    items = data["skills"]
    if not isinstance(items, list) or not items or len(items) > MAX_ITEMS:
        raise SpecExecutionError("registry skills must be a non-empty bounded list")
    root = (source_root or path.parent.parent).resolve()
    parsed: list[SkillMetadata] = []
    ids: set[str] = set()
    capability_owners: dict[str, str] = {}
    for index, raw_item in enumerate(items):
        item = _mapping(
            raw_item,
            f"skills[{index}]",
            allowed=SKILL_KEYS,
            required=SKILL_KEYS,
        )
        skill_id = _identifier(item["id"], f"skills[{index}].id")
        if skill_id in ids:
            raise SpecExecutionError(f"duplicate Skill id: {skill_id}")
        ids.add(skill_id)
        scope = _text(item["scope"], f"skills[{index}].scope", limit=16)
        status = _text(item["status"], f"skills[{index}].status", limit=16)
        maturity = _text(item["maturity"], f"skills[{index}].maturity", limit=32)
        executor_kind = _text(item["executor_kind"], f"skills[{index}].executor_kind", limit=32)
        if scope not in SCOPES or status not in SKILL_STATUSES or maturity not in MATURITY or executor_kind not in EXECUTOR_KINDS:
            raise SpecExecutionError(f"skills[{index}] has unsupported routing enum")
        source = _text(item["source"], f"skills[{index}].source", limit=512)
        source_path = _contained(root, source, f"skills[{index}].source")
        if _skill_name(source_path) != skill_id:
            raise SpecExecutionError(f"Skill source name mismatch: {skill_id}")
        capabilities = _string_list(
            item["capabilities"], f"skills[{index}].capabilities", identifiers=True, required=True
        )
        for capability in capabilities:
            previous = capability_owners.get(capability)
            if previous is not None:
                raise SpecExecutionError(
                    f"ambiguous capability owner: {capability}:{previous},{skill_id}",
                    "ambiguous_capability_owner",
                )
            capability_owners[capability] = skill_id
        replacement = _text(
            item["replacement"], f"skills[{index}].replacement", required=False, limit=128
        )
        if replacement:
            _identifier(replacement, f"skills[{index}].replacement")
        parsed.append(
            SkillMetadata(
                id=skill_id,
                source=source,
                scope=scope,
                status=status,
                capabilities=capabilities,
                triggers=_string_list(item["triggers"], f"skills[{index}].triggers", identifiers=True),
                inputs=_string_list(item["inputs"], f"skills[{index}].inputs", identifiers=True),
                outputs=_string_list(item["outputs"], f"skills[{index}].outputs", identifiers=True),
                required_tools=_string_list(
                    item["required_tools"], f"skills[{index}].required_tools", identifiers=True
                ),
                required_context=_string_list(
                    item["required_context"], f"skills[{index}].required_context", identifiers=True
                ),
                stop_conditions=_string_list(
                    item["stop_conditions"], f"skills[{index}].stop_conditions", identifiers=True
                ),
                validation=_string_list(
                    item["validation"], f"skills[{index}].validation", identifiers=True
                ),
                version=_text(item["version"], f"skills[{index}].version", limit=64),
                maturity=maturity,
                executor_kind=executor_kind,
                owner=_identifier(item["owner"], f"skills[{index}].owner"),
                replacement=replacement,
            )
        )
    for skill in parsed:
        if skill.replacement and skill.replacement not in ids:
            raise SpecExecutionError(f"unknown Skill replacement: {skill.id}:{skill.replacement}")
    return tuple(sorted(parsed, key=lambda candidate: candidate.id))


def normalize_intake(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Compile explicit intake facts without guessing repository or project class."""
    allowed = {
        "entrypoint",
        "project",
        "master_or_goal",
        "requested_change",
        "explicit_constraints",
        "explicit_non_goals",
        "write_permissions",
        "user_decisions",
        "project_class",
    }
    data = _mapping(
        raw,
        "intake",
        allowed=allowed,
        required={"entrypoint", "project", "explicit_constraints", "explicit_non_goals", "user_decisions"},
    )
    entrypoint = _text(data["entrypoint"], "entrypoint", limit=32)
    if entrypoint not in ENTRYPOINTS:
        raise SpecExecutionError("unsupported entrypoint", "unknown_entrypoint")
    project = _text(data["project"], "project", limit=256)
    master_or_goal = _text(data.get("master_or_goal", ""), "master_or_goal", required=False)
    requested_change = _text(data.get("requested_change", ""), "requested_change", required=False)
    write_permissions = _text(data.get("write_permissions", "unspecified"), "write_permissions", limit=256)
    constraints = _string_list(
        data["explicit_constraints"], "explicit_constraints", preserve=True
    )
    non_goals = _string_list(data["explicit_non_goals"], "explicit_non_goals", preserve=True)
    decisions = _string_list(data["user_decisions"], "user_decisions", preserve=True)
    project_class = _text(data.get("project_class", ""), "project_class", required=False, limit=64)
    status = "ready"
    reason = "resolve_live_state"
    if entrypoint == "CONTINUE_EXISTING":
        if project_class:
            raise SpecExecutionError("CONTINUE_EXISTING must not declare a new-project class")
    else:
        reason = "project_intake"
        if not master_or_goal.strip():
            raise SpecExecutionError("NEW_PROJECT requires master_or_goal")
        if not project_class:
            status = "needs_decision"
            reason = "project_class_required"
        elif project_class not in PROJECT_CLASSES:
            raise SpecExecutionError("unsupported project_class")
    return {
        "schema_version": 1,
        "status": status,
        "reason": reason,
        "intent": entrypoint,
        "project": project,
        "master_or_goal": master_or_goal,
        "requested_change": requested_change,
        "explicit_constraints": list(constraints),
        "explicit_non_goals": list(non_goals),
        "write_permissions": write_permissions,
        "user_decisions": list(decisions),
        "project_class": project_class or None,
        "next_owner": "live_repository_router" if entrypoint == "CONTINUE_EXISTING" else "project_framework_intake",
    }


def _scope_eligible(skill_scope: str, request_scope: str) -> bool:
    if request_scope == "global":
        return skill_scope == "global"
    if request_scope == "domain":
        return skill_scope in {"global", "domain"}
    return skill_scope in SCOPES


def route_skills(registry: Sequence[SkillMetadata], raw: Mapping[str, Any]) -> dict[str, Any]:
    """Select only metadata-matching Skills after stage and scope are known."""
    allowed = {
        "stage_id",
        "scope",
        "intent",
        "requirement_ids",
        "components",
        "change_types",
        "risk",
        "required_capabilities",
        "triggers",
        "available_tools",
        "full_scan_reason",
    }
    if "stage_id" not in raw:
        raise SpecExecutionError("route requires selected stage_id", "stage_required")
    data = _mapping(raw, "route", allowed=allowed, required={"stage_id", "scope"})
    stage_id = _identifier(data["stage_id"], "stage_id")
    scope = _text(data["scope"], "scope", limit=16)
    if scope not in SCOPES:
        raise SpecExecutionError("unsupported route scope", "unknown_scope")
    intent = _text(data.get("intent", ""), "intent", required=False)
    requirement_ids = _string_list(
        data.get("requirement_ids", []), "requirement_ids", identifiers=True
    )
    components = _string_list(data.get("components", []), "components", identifiers=True)
    change_types = _string_list(data.get("change_types", []), "change_types", identifiers=True)
    risk = _text(data.get("risk", "medium"), "risk", limit=16)
    if risk not in {"low", "medium", "high", "critical"}:
        raise SpecExecutionError("unsupported route risk", "unknown_risk")
    required = _string_list(
        data.get("required_capabilities", []), "required_capabilities", identifiers=True
    )
    triggers = _string_list(data.get("triggers", []), "triggers", identifiers=True)
    available_tools = set(_string_list(data.get("available_tools", []), "available_tools", identifiers=True))
    full_scan_reason = _text(
        data.get("full_scan_reason", ""), "full_scan_reason", required=False, limit=64
    )
    if full_scan_reason and full_scan_reason not in FULL_SCAN_REASONS:
        raise SpecExecutionError("unsupported full_scan_reason")

    active = [
        item for item in registry
        if item.status == "active" and _scope_eligible(item.scope, scope)
    ]
    selected: list[SkillMetadata] = []
    required_set = set(required)
    trigger_set = set(triggers) | set(components) | set(change_types)
    for item in active:
        if required_set.intersection(item.capabilities) or trigger_set.intersection(item.triggers):
            selected.append(item)

    provided = {capability for item in selected for capability in item.capabilities}
    missing_capabilities = sorted(required_set - provided)
    missing_tools = sorted({tool for item in selected for tool in item.required_tools} - available_tools)
    issues = [f"missing_capability:{value}" for value in missing_capabilities]
    issues.extend(f"missing_tool:{value}" for value in missing_tools)
    status = "blocked" if issues else "ready"
    selected.sort(key=lambda item: item.id)
    contexts = {
        "global_invariants",
        "project_overlay",
        "live_repo_state",
        f"stage.{stage_id}",
    }
    contexts.update(value for item in selected for value in item.required_context)
    return {
        "schema_version": 1,
        "status": status,
        "reason": "route_gaps" if issues else "relevant_capabilities_selected",
        "stage_id": stage_id,
        "scope": scope,
        "intent": intent,
        "requirement_ids": list(requirement_ids),
        "components": list(components),
        "change_types": list(change_types),
        "risk": risk,
        "selected_skill_ids": [item.id for item in selected],
        "selected_skill_sources": [item.source for item in selected],
        "selected_capabilities": sorted(provided),
        "required_tools": sorted({tool for item in selected for tool in item.required_tools}),
        "required_context": sorted(contexts),
        "validators": sorted({value for item in selected for value in item.validation}),
        "stop_conditions": sorted({value for item in selected for value in item.stop_conditions}),
        "issues": issues,
        "full_repo_scan": bool(full_scan_reason),
        "full_repo_scan_reason": full_scan_reason or None,
    }


def choose_executor(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Recommend the cheapest sufficient route without changing the active model."""
    allowed = {
        "deterministic_tools",
        "validators",
        "skill_executor",
        "mechanical",
        "novelty",
        "risk",
        "deterministic_failure",
        "contract_conflict",
        "prior_high_reasoning_failed",
    }
    data = _mapping(raw, "executor", allowed=allowed, required={"novelty", "risk"})
    tools = _string_list(data.get("deterministic_tools", []), "deterministic_tools", identifiers=True)
    validators = _string_list(data.get("validators", []), "validators", identifiers=True)
    for key in ("skill_executor", "mechanical", "contract_conflict", "prior_high_reasoning_failed"):
        if key in data and not isinstance(data[key], bool):
            raise SpecExecutionError(f"{key} must be boolean")
    novelty = _text(data["novelty"], "novelty", limit=16)
    risk = _text(data["risk"], "risk", limit=16)
    if novelty not in {"known", "bounded", "unknown"} or risk not in {"low", "medium", "high", "critical"}:
        raise SpecExecutionError("unsupported executor novelty/risk")
    failure = _text(
        data.get("deterministic_failure", ""), "deterministic_failure", required=False, limit=MAX_OBSERVATION
    )
    conflict = bool(data.get("contract_conflict", False))
    if conflict:
        route, reason = "user_decision", "contract_conflict"
    elif tools and not failure:
        route, reason = "deterministic_tool", "available_deterministic_tool"
    elif validators and bool(data.get("mechanical", False)) and not failure:
        route, reason = "deterministic_validator", "mechanical_validation_path"
    elif bool(data.get("skill_executor", False)) and not failure:
        route, reason = "skill_with_deterministic_executor", "selected_skill_executor"
    elif novelty == "unknown" and risk == "critical" and bool(data.get("prior_high_reasoning_failed", False)):
        route, reason = "frontier_reasoning", "critical_unknown_after_high_reasoning_failure"
    elif novelty == "unknown" or risk in {"high", "critical"}:
        route, reason = "high_reasoning", "unknown_or_high_risk"
    elif risk == "medium":
        route, reason = "normal_implementation", "accepted_bounded_contract"
    else:
        route, reason = "cheap_bounded_model", "low_risk_bounded_transformation"
    if failure:
        reason += ":deterministic_failure"
    return {
        "schema_version": 1,
        "route": route,
        "reason": reason,
        "deterministic_failure": failure or None,
        "promotion_review_required": bool(failure) or (bool(data.get("mechanical", False)) and not tools),
        "model_change_authorized": False,
    }


def _read_json(path: Path) -> Mapping[str, Any]:
    if not path.is_file() or path.stat().st_size > MAX_INPUT_BYTES:
        raise SpecExecutionError("input is missing or oversized")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise SpecExecutionError("input is unreadable or invalid JSON") from exc
    return _mapping(raw, "input", allowed=set(raw) if isinstance(raw, Mapping) else set())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pure Specification → Execution decisions")
    commands = parser.add_subparsers(dest="command", required=True)
    intake = commands.add_parser("intake", help="normalize explicit compact intake")
    intake.add_argument("--input", type=Path, required=True)
    route = commands.add_parser("route", help="select relevant Skill metadata")
    route.add_argument("--registry", type=Path, required=True)
    route.add_argument("--source-root", type=Path)
    route.add_argument("--input", type=Path, required=True)
    executor = commands.add_parser("executor", help="choose cheapest sufficient executor class")
    executor.add_argument("--input", type=Path, required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "intake":
            output = normalize_intake(_read_json(args.input))
        elif args.command == "route":
            output = route_skills(
                load_registry(args.registry, args.source_root),
                _read_json(args.input),
            )
        else:
            output = choose_executor(_read_json(args.input))
    except SpecExecutionError as exc:
        print(json.dumps({"ok": False, "error": str(exc), "error_code": exc.code},
                         sort_keys=True, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": output}, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
