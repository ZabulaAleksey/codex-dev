#!/usr/bin/env python3
"""Bounded decisions and read-only launcher resolution for Specification → Execution.

The pure core consumes explicit structured facts; the launcher adapter reads only the exact
project and selected stage through canonical resolvers.  The module never executes registry
commands, changes Git, loads an unselected Skill body, mutates a project, or writes external state.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import subprocess
import sys
import threading
import tomllib
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hooks.stage_selector import find_stage_record, parse_stage_id
from tools.dev_paths import (
    DevLayout,
    PathResolutionError,
    is_exact_git_root,
    inspect_project,
    resolve_layout,
    resolve_project_reference,
)
from tools.master_execution import (
    GitWorktreeAdapter,
    MasterExecutionError,
    MasterExecutionResourceLimit,
    RecoveryFacts,
    extract_master_state,
    next_execution_decision,
    recover_execution,
)
from tools.stage_compatibility import CompatibilityError, stage_routing_snapshot


MAX_INPUT_BYTES = 512 * 1024
MAX_REGISTRY_BYTES = 512 * 1024
MAX_ITEMS = 128
MAX_LIST_ITEMS = 32
MAX_TEXT = 4096
MAX_OBSERVATION = 2048
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
ARTIFACT_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,511}$")
SKILL_NAME = re.compile(r"^name:\s*([^\r\n]+)\s*$", re.MULTILINE)
SKILL_FRONTMATTER = re.compile(r"\A---\r?\n(?P<body>.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SECRET_LIKE = re.compile(
    r"(?i)(?:api[_-]?key|password|secret|token)\s*[:=]\s*\S+"
    r"|authorization\s*:\s*\S+"
    r"|(?:github_pat|ghp|xox[baprs])[-_][A-Za-z0-9_-]{8,}"
    r"|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|[a-z][a-z0-9+.-]*://[^/\s:@]+:[^@\s/]+@"
    r"|eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"
    r"|(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{8,}|sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{12,}"
    r"|glpat-[A-Za-z0-9_-]{8,}|npm_[A-Za-z0-9]{8,}|AIza[0-9A-Za-z_-]{20,}"
)

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
CONTEXT_PRECEDENCE = (
    "current_slice", "selected_spec", "affected_spec", "architecture_boundary",
    "architecture_decisions", "changed_files", "dependency_files", "targeted_tests",
    "predecessor_evidence", "failure_path", "diff",
)
TRACE_STATUSES = {"planned", "running", "implemented_unverified", "verified", "completed"}
EVIDENCE_LEVELS = {"L1", "L2", "L3", "L4", "L5", "L6"}
OPPORTUNITY_SIGNALS = {
    "repeated_instruction", "repeated_mechanical_sequence", "repeated_user_reminder",
    "repeated_reasoning_cost", "repeated_review_defect", "expressible_manual_gate",
    "stable_mapping", "stable_io_contract",
}
OPPORTUNITY_DISQUALIFIERS = {
    "one_off_product_decision", "unknown_research", "unstable_procedure", "negative_risk_benefit",
}
CANDIDATE_STATUSES = {"open", "approved", "rejected", "implemented", "verified", "blocked", "closed"}
PROMOTION_TARGETS = {
    "repeated_explanation": "documentation_contract",
    "repeated_procedure": "skill_recipe",
    "mechanical_sequence": "script_tool",
    "stable_transformation": "library_module",
    "routing_decision": "router_rule_table",
    "validation": "validator_test",
    "invariant": "hook_ci_gate",
}
DETERMINISTIC_FAILURE_CLASSES = {
    "unsupported_input", "tool_unavailable", "unknown_result", "security_integrity",
    "authorization", "resource_limit", "contract_validation",
}
FAIL_CLOSED_FAILURE_CLASSES = {
    "security_integrity", "authorization", "resource_limit", "contract_validation",
}
CANDIDATE_KEYS = {
    "schema_version", "id", "fingerprint", "version", "scope", "status", "action",
    "reason", "qualified", "occurrences", "projects", "signals", "disqualifiers",
    "source_kind", "priority", "evidence_refs", "provenance_refs", "write_authorized",
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


@dataclass(frozen=True)
class TraceContract:
    repository_root: Path
    stage_id: str
    stage_status: str
    requirement_owners: tuple[tuple[str, str], ...]
    known_implementation_files: tuple[str, ...]
    known_validator_ids: tuple[str, ...]
    known_test_commands: tuple[str, ...]
    required_evidence: tuple[str, ...]


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


def _reject_secret_like(values: Iterable[str], label: str) -> None:
    if any(SECRET_LIKE.search(value) for value in values):
        raise SpecExecutionError(f"{label} contains secret-like input", "secret_like_input")


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
    lexical = root / path
    current = root
    for part in path.parts:
        current = current / part
        if current.exists() and _is_link_like(current):
            raise SpecExecutionError(f"{label} contains link-like path", "unsafe_source_path")
    target = lexical.resolve(strict=False)
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise SpecExecutionError(f"{label} escapes source root") from exc
    return target


def _is_link_like(path: Path) -> bool:
    is_junction = getattr(os.path, "isjunction", None)
    if path.is_symlink() or bool(is_junction and is_junction(path)):
        return True
    try:
        attributes = getattr(path.stat(follow_symlinks=False), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _local_path(value: str | os.PathLike[str], label: str) -> Path:
    raw = str(value)
    windows = raw.replace("/", "\\")
    if windows.startswith(("\\\\", "\\?\\", "\\.\\")):
        raise SpecExecutionError(f"{label} must be a local non-device path", "unsafe_local_path")
    return Path(raw).expanduser()


def _reject_link_like_components(path: Path, label: str) -> None:
    candidate = path.expanduser()
    if not candidate.is_absolute():
        return
    current = Path(candidate.anchor)
    for part in candidate.parts[1:]:
        current = current / part
        if current.exists() and _is_link_like(current):
            raise SpecExecutionError(f"{label} contains link-like path", "unsafe_local_path")


def _path_identity(path: Path) -> str:
    return os.path.normcase(str(path.resolve(strict=False)))


def _run_bounded(
    command: Sequence[str], *, environment: Mapping[str, str], timeout: int = 15,
    limit: int = MAX_INPUT_BYTES,
) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        list(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=dict(environment),
    )
    chunks: list[bytes] = []
    observed = 0
    overflow = False

    def drain() -> None:
        nonlocal observed, overflow
        assert process.stdout is not None
        while True:
            chunk = process.stdout.read(min(64 * 1024, limit + 1 - observed))
            if not chunk:
                return
            chunks.append(chunk)
            observed += len(chunk)
            if observed > limit:
                overflow = True
                process.kill()
                return

    reader = threading.Thread(target=drain, daemon=True)
    reader.start()
    try:
        returncode = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        process.kill()
        process.wait()
        reader.join(timeout=1)
        if process.stdout is not None:
            process.stdout.close()
        raise SpecExecutionError("Git recovery timed out", "git_recovery_failed") from exc
    reader.join(timeout=1)
    if process.stdout is not None:
        process.stdout.close()
    output = b"".join(chunks).decode("utf-8", errors="replace")
    if overflow:
        raise SpecExecutionError("Git recovery output exceeded bounded limit", "resource_limit")
    return subprocess.CompletedProcess(list(command), returncode, output, "")


def _skill_name(path: Path) -> str:
    if _is_link_like(path) or not path.is_file() or path.stat().st_size > MAX_REGISTRY_BYTES:
        raise SpecExecutionError(f"Skill source is missing or oversized: {path}")
    text = path.read_text(encoding="utf-8")[:8192].lstrip("\ufeff")
    frontmatter = SKILL_FRONTMATTER.match(text)
    match = SKILL_NAME.search(frontmatter.group("body")) if frontmatter else None
    if not match:
        raise SpecExecutionError(f"Skill source has no frontmatter name: {path}")
    return match.group(1).strip().strip('"\'')


def load_registry(path: Path, source_root: Path | None = None) -> tuple[SkillMetadata, ...]:
    """Load and validate metadata without loading Skill procedure bodies into the route output."""
    raw_path = _local_path(path, "registry").absolute()
    root = _local_path(
        source_root if source_root is not None else raw_path.parent.parent,
        "source_root",
    ).resolve()
    if _is_link_like(raw_path):
        raise SpecExecutionError("registry must not be link-like", "unsafe_registry_path")
    path = raw_path.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise SpecExecutionError("registry escapes source root", "unsafe_registry_path") from exc
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


def compose_registries(
    global_registry: Sequence[SkillMetadata],
    delta_registry: Sequence[SkillMetadata] = (),
) -> tuple[SkillMetadata, ...]:
    """Compose a global registry with a project/domain-only delta, rejecting shadow owners."""
    combined: list[SkillMetadata] = []
    ids: set[str] = set()
    capability_owners: dict[str, str] = {}
    for source_name, items in (("global", global_registry), ("delta", delta_registry)):
        for item in items:
            if source_name == "global" and item.scope != "global":
                raise SpecExecutionError("global registry contains non-global Skill", "invalid_registry_scope")
            if source_name == "delta" and item.scope not in {"domain", "project"}:
                raise SpecExecutionError("registry delta must be domain or project scoped", "invalid_registry_scope")
            if item.id in ids:
                raise SpecExecutionError(f"duplicate composed Skill id: {item.id}", "duplicate_skill_id")
            ids.add(item.id)
            for capability in item.capabilities:
                previous = capability_owners.get(capability)
                if previous is not None:
                    raise SpecExecutionError(
                        f"ambiguous composed capability owner: {capability}:{previous},{item.id}",
                        "ambiguous_capability_owner",
                    )
                capability_owners[capability] = item.id
            combined.append(item)
    return tuple(sorted(combined, key=lambda item: item.id))


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
    _reject_secret_like(
        [project, master_or_goal, requested_change, write_permissions, *constraints, *non_goals, *decisions],
        "intake",
    )
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


def _git_recovery_facts(
    project_root: Path,
    master_state: Mapping[str, Any],
    track: Mapping[str, Any],
    *,
    source_revision: str,
    queue_item_present: bool,
) -> RecoveryFacts:
    repository_path = _local_path(track["repository"], "track repository")
    worktree_path = _local_path(track["worktree"], "track worktree")
    if not repository_path.is_absolute() or not worktree_path.is_absolute():
        raise SpecExecutionError("track paths must be absolute", "invalid_track_path")
    _reject_link_like_components(repository_path, "track repository")
    _reject_link_like_components(worktree_path, "track worktree")
    repository = repository_path.resolve(strict=False)
    worktree = worktree_path.resolve(strict=False)
    if _path_identity(repository) != _path_identity(project_root):
        raise SpecExecutionError("track repository does not match resolved project", "track_repository_mismatch")
    if not is_exact_git_root(repository):
        raise SpecExecutionError("track repository is not an exact Git root", "invalid_track_repository")

    try:
        inventory = GitWorktreeAdapter(repository, worktree.parent).snapshot()
    except MasterExecutionResourceLimit as exc:
        raise SpecExecutionError(str(exc), "resource_limit") from exc
    except (MasterExecutionError, OSError, subprocess.SubprocessError) as exc:
        raise SpecExecutionError(str(exc), "git_recovery_failed") from exc
    worktree_key = _path_identity(worktree)
    branch = track["branch"]
    worktree_fact = next(
        (item for item in inventory if _path_identity(Path(item.path)) == worktree_key),
        None,
    )
    if worktree_fact is not None and worktree_fact.branch != branch:
        raise SpecExecutionError(
            "track worktree is checked out on a different branch",
            "worktree_branch_mismatch",
        )
    worktree_exists = worktree_fact is not None

    def git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
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
        return _run_bounded(
            [
                "git", "-c", f"safe.directory={root}",
                "-c", "core.fsmonitor=false", "-c", f"core.hooksPath={os.devnull}",
                "-c", "submodule.recurse=false", "-C", str(root), *arguments,
            ],
            environment=environment,
        )

    branch_exists = git(
        repository, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"
    ).returncode == 0

    dirty = False
    if worktree_exists:
        status = git(
            worktree,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "--ignore-submodules=all",
            "--no-renames",
            "--no-ahead-behind",
        )
        if status.returncode != 0:
            raise SpecExecutionError("worktree status is unavailable", "git_recovery_failed")
        dirty = bool(status.stdout.strip())
    checkpoint = track["checkpoint"]
    checkpoint_reachable = False
    if worktree_fact is not None:
        checkpoint_check = git(
            repository,
            "merge-base",
            "--is-ancestor",
            checkpoint,
            worktree_fact.head,
        )
        checkpoint_reachable = checkpoint_check.returncode == 0
    state_at_head = False
    if worktree_exists:
        state_diff = git(
            worktree, "diff", "--quiet", "--no-ext-diff", "--no-textconv",
            "HEAD", "--", "prompts/STAGES.md",
        )
        head_state_file: subprocess.CompletedProcess[str] | None = None
        if state_diff.returncode == 0:
            head_state_size = git(worktree, "cat-file", "-s", "HEAD:prompts/STAGES.md")
            try:
                size = int(head_state_size.stdout.strip()) if head_state_size.returncode == 0 else -1
            except ValueError:
                size = -1
            if 0 <= size <= MAX_INPUT_BYTES:
                head_state_file = git(worktree, "cat-file", "-p", "HEAD:prompts/STAGES.md")
        if head_state_file is not None and head_state_file.returncode == 0:
            try:
                head_selector = parse_stage_id(head_state_file.stdout)
                if head_selector.issue_code or head_selector.stage_id is None:
                    raise ValueError("invalid Stage ID at HEAD")
                head_record = find_stage_record(head_state_file.stdout, head_selector.stage_id)
                if head_record.issue_code or head_record.record is None:
                    raise ValueError("selected stage record is invalid at HEAD")
                head_state = extract_master_state(head_record.record)
                head_track = next(
                    (item for item in head_state["tracks"] if item["id"] == track["id"]),
                    None,
                )
                state_at_head = bool(
                    head_state["master"]["id"] == master_state["master"]["id"]
                    and head_state["state_revision"] == master_state["state_revision"]
                    and head_track is not None
                    and head_track["checkpoint"] == track["checkpoint"]
                )
            except (ValueError, MasterExecutionError):
                state_at_head = False
    return RecoveryFacts(
        source_revision=source_revision,
        worktree_exists=worktree_exists,
        branch_exists=branch_exists,
        dirty=dirty,
        queue_item_present=queue_item_present,
        git_head=worktree_fact.head if worktree_fact else "",
        checkpoint_reachable=checkpoint_reachable,
        state_revision_at_head=state_at_head,
        overlapping_contract_merged=False,
        launcher_state_revision=master_state["state_revision"],
        launcher_checkpoint=track["checkpoint"],
        context_compacted=False,
    )


def _launcher_status(action: str, capability_route: Mapping[str, Any] | None) -> str:
    action_status = {
        "complete": "completed",
        "blocked": "blocked",
        "stopped": "blocked",
        "user_decision": "needs_decision",
        "integration_checkpoint": "needs_decision",
        "handoff": "needs_continuation",
        "reconcile_status": "needs_reconciliation",
        "route_worktree": "needs_reconciliation",
        "verification_gate": "verification_required",
        "await_result": "in_progress",
        "continue": "ready",
        "canonical_stage": "ready",
    }
    status = action_status.get(action, "blocked")
    if capability_route is not None and capability_route["status"] != "ready":
        return "blocked"
    return status


def resolve_user_launcher(
    raw: Mapping[str, Any],
    registry: Sequence[SkillMetadata],
    *,
    layout: DevLayout | None = None,
    available_tools: Sequence[str] = (),
    source_revision: str | None = None,
    queue_item_present: bool | None = None,
) -> dict[str, Any]:
    """Resolve a minimal user entrypoint without mutating project or global state.

    ``NEW_PROJECT`` remains an explicit handoff to the existing project-framework intake.
    ``CONTINUE_EXISTING`` composes the canonical path, bridge, selected-stage and CME
    adapters before routing only the capabilities declared by the next live slice.
    """
    intake = normalize_intake(raw)
    if intake["intent"] == "NEW_PROJECT":
        return {
            "schema_version": 1,
            "status": intake["status"],
            "reason": intake["reason"],
            "phase": "project_framework_intake",
            "intake": intake,
            "global_mutation_authorized": False,
        }

    try:
        active_layout = layout or resolve_layout()
        project_reference = intake["project"]
        project_lexical = _local_path(project_reference, "project")
        if (
            project_reference not in {".", "..", "~"}
            and "/" not in project_reference
            and "\\" not in project_reference
        ):
            project_lexical = active_layout.projects_root / project_reference
        elif not project_lexical.is_absolute():
            project_lexical = Path.cwd() / project_lexical
        _reject_link_like_components(project_lexical, "project")
        project_root = resolve_project_reference(intake["project"], active_layout)
        _reject_link_like_components(project_root, "project")
        project = inspect_project(project_root, active_layout)
        if project.dev_integration != "enabled" or not project.git_repo:
            raise SpecExecutionError("project is not an exact DEV-enabled Git root", "invalid_dev_bridge")
        stage_state, selected_record = stage_routing_snapshot(project_root)
    except PathResolutionError as exc:
        raise SpecExecutionError(str(exc), "invalid_project") from exc
    except (CompatibilityError, OSError, subprocess.SubprocessError) as exc:
        raise SpecExecutionError(str(exc), "invalid_stage_state") from exc

    if stage_state.get("execution_allowed") is not True or selected_record is None:
        return {
            "schema_version": 1,
            "status": "blocked",
            "reason": "stage_execution_not_allowed",
            "phase": "live_repository_router",
            "intake": intake,
            "project": asdict(project),
            "stage_state": stage_state,
            "global_mutation_authorized": False,
        }

    stage_id = stage_state.get("stage_selector")
    if not isinstance(stage_id, str) or not stage_id:
        raise SpecExecutionError("selected stage is missing", "invalid_stage_state")

    capability_route: dict[str, Any] | None = None
    recovery: dict[str, Any] | None = None
    try:
        master_state = extract_master_state(selected_record)
    except MasterExecutionError as exc:
        if str(exc) != "selected record must contain exactly one master-execution block":
            raise SpecExecutionError(str(exc), "invalid_master_state") from exc
        if intake["master_or_goal"] and intake["master_or_goal"] != stage_id:
            raise SpecExecutionError(
                "requested stage does not match selected live state",
                "master_selector_mismatch",
            )
        controller = {"action": "canonical_stage", "reason": "no_master_execution_state", "slice_id": ""}
    else:
        requested_master = intake["master_or_goal"]
        valid_targets = {
            stage_id,
            master_state["master"]["id"],
        }
        if requested_master and requested_master not in valid_targets:
            raise SpecExecutionError(
                "requested master does not match selected live state",
                "master_selector_mismatch",
            )
        decision = next_execution_decision(master_state)
        if decision.action not in {"complete", "blocked", "user_decision", "integration_checkpoint"}:
            if source_revision is None or queue_item_present is None:
                return {
                    "schema_version": 1,
                    "status": "needs_reconciliation",
                    "reason": "source_observation_required",
                    "phase": "live_repository_router",
                    "intake": intake,
                    "project": asdict(project),
                    "stage_state": stage_state,
                    "controller": asdict(decision),
                    "capability_route": None,
                    "global_mutation_authorized": False,
                }
            if type(queue_item_present) is not bool:
                raise SpecExecutionError(
                    "queue_item_present must be a boolean", "invalid_source_observation"
                )
            selected_slice = next(
                (item for item in master_state["slices"] if item["id"] == decision.slice_id),
                None,
            )
            track_id = selected_slice["worktree_track"] if selected_slice else ""
            track = next(
                (item for item in master_state["tracks"] if item["id"] == track_id),
                None,
            )
            if track is None:
                raise SpecExecutionError("controller track is missing", "invalid_master_state")
            facts = _git_recovery_facts(
                project_root,
                master_state,
                track,
                source_revision=_text(source_revision, "source_revision", limit=512),
                queue_item_present=queue_item_present,
            )
            recovery_decision = recover_execution(master_state, facts, track_id=track["id"])
            recovery = asdict(recovery_decision)
            if recovery_decision.action != "resume":
                decision = recovery_decision
        controller = asdict(decision)
        if decision.slice_id:
            selected_slice = next(
                (item for item in master_state["slices"] if item["id"] == decision.slice_id),
                None,
            )
            if selected_slice is None:
                raise SpecExecutionError("controller selected an unknown slice", "invalid_master_state")
            capabilities = selected_slice.get("capabilities", [])
            if capabilities:
                risk = "high" if selected_slice.get("model_class") in {"HIGH", "FRONTIER"} else "medium"
                capability_route = route_skills(
                    registry,
                    {
                        "stage_id": stage_id,
                        "scope": "global" if project.bridge == "dev_source" else "project",
                        "intent": intake["intent"],
                        "risk": risk,
                        "required_capabilities": capabilities,
                        "available_tools": list(available_tools),
                    },
                )

    status = _launcher_status(controller["action"], capability_route)
    return {
        "schema_version": 1,
        "status": status,
        "reason": controller["reason"],
        "phase": "live_repository_router",
        "intake": intake,
        "project": asdict(project),
        "stage_state": stage_state,
        "controller": controller,
        "recovery": recovery,
        "capability_route": capability_route,
        "global_mutation_authorized": False,
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
    contexts = [
        "global_invariants",
        "project_overlay",
        "live_repo_state",
        f"stage.{stage_id}",
    ]
    context_aliases = {"selected_stage", "live_repo_state", "global_invariants", "project_overlay"}
    extras = {
        value for item in selected for value in item.required_context
        if value not in context_aliases
    }
    precedence = {value: index for index, value in enumerate(CONTEXT_PRECEDENCE)}
    ordered_extras = sorted(extras, key=lambda value: (precedence.get(value, len(precedence)), value))
    contexts.extend(ordered_extras)
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
        "required_context": contexts,
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
        "deterministic_failure_class",
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
        data.get("deterministic_failure_class", ""),
        "deterministic_failure_class", required=False, limit=32,
    )
    if failure and failure not in DETERMINISTIC_FAILURE_CLASSES:
        raise SpecExecutionError("unsupported deterministic failure class")
    conflict = bool(data.get("contract_conflict", False))
    if failure in FAIL_CLOSED_FAILURE_CLASSES:
        route, reason = "blocked", f"fail_closed_{failure}"
    elif conflict:
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
        "deterministic_failure_class": failure or None,
        "promotion_review_required": bool(failure) or (bool(data.get("mechanical", False)) and not tools),
        "model_change_authorized": False,
    }


def _repository_root(value: Any) -> Path:
    raw = str(value) if isinstance(value, os.PathLike) else _text(
        value, "trace.repository_root", limit=1024
    )
    root = _local_path(raw, "trace.repository_root").resolve()
    if not root.is_dir() or not (root / ".git").exists():
        raise SpecExecutionError("trace repository_root is not an exact Git root", "invalid_repository_root")
    return root


def _artifact_refs(
    value: Any,
    label: str,
    *,
    repository_root: Path | None = None,
    require_existing: bool = False,
) -> tuple[str, ...]:
    refs = _string_list(value, label, required=True)
    for ref in refs:
        path = Path(ref)
        windows = PureWindowsPath(ref)
        posix = PurePosixPath(ref)
        if (
            path.is_absolute() or windows.is_absolute() or bool(windows.drive)
            or posix.is_absolute() or ".." in windows.parts or ".." in posix.parts
            or ref.startswith(("~", "/", "\\")) or ":" in ref or "\\" in ref
            or not ARTIFACT_REF.fullmatch(ref)
        ):
            raise SpecExecutionError(f"{label} contains unsafe path", "unsafe_artifact_path")
        if repository_root is not None:
            lexical = repository_root.joinpath(*posix.parts)
            current = repository_root
            for part in posix.parts:
                current = current / part
                if current.exists() and _is_link_like(current):
                    raise SpecExecutionError(f"{label} contains link-like path", "unsafe_artifact_path")
            resolved = lexical.resolve(strict=False)
            try:
                resolved.relative_to(repository_root)
            except ValueError as exc:
                raise SpecExecutionError(f"{label} escapes repository root", "unsafe_artifact_path") from exc
            if require_existing and not resolved.is_file():
                raise SpecExecutionError(f"{label} references a missing file", "missing_known_artifact")
    return refs


def build_trace_contract(repository_root: Path, contract_path: Path) -> TraceContract:
    """Build trusted trace facts after verifying the live repository selector and file inventory."""
    root = _repository_root(repository_root)
    canonical_contract = str(contract_path).replace("\\", "/")
    _artifact_refs(
        [canonical_contract], "trace.contract_path", repository_root=root, require_existing=True
    )
    try:
        tracked = subprocess.run(
            [
                "git", "-c", f"safe.directory={root}", "-C", str(root),
                "ls-files", "--error-unmatch", "--", canonical_contract,
            ],
            check=False, capture_output=True, text=True, encoding="utf-8",
        )
    except OSError as exc:
        raise SpecExecutionError("cannot verify trace contract tracking", "invalid_trace_contract") from exc
    if tracked.returncode != 0:
        raise SpecExecutionError("trace contract must be Git-tracked", "untracked_trace_contract")
    contract_file = root.joinpath(*PurePosixPath(canonical_contract).parts)
    committed = subprocess.run(
        [
            "git", "-c", f"safe.directory={root}", "-C", str(root),
            "show", f"HEAD:{canonical_contract}",
        ],
        check=False, capture_output=True,
    )
    if committed.returncode != 0 or committed.stdout != contract_file.read_bytes():
        raise SpecExecutionError(
            "trace contract must match its committed Git version", "stale_trace_contract"
        )
    raw = _read_json(contract_file)
    data = _mapping(
        raw,
        "trace_contract",
        allowed={
            "stage_id", "requirement_owners", "known_implementation_files",
            "known_validator_ids", "known_test_commands",
        },
        required={
            "stage_id", "requirement_owners", "known_implementation_files",
            "known_validator_ids", "known_test_commands",
        },
    )
    stage_id = _identifier(data["stage_id"], "trace_contract.stage_id")
    stages_path = root / "prompts" / "STAGES.md"
    if not stages_path.is_file() or stages_path.stat().st_size > MAX_INPUT_BYTES:
        raise SpecExecutionError("canonical STAGES is missing or oversized", "invalid_stage_contract")
    try:
        stages_text = stages_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise SpecExecutionError("canonical STAGES is unreadable", "invalid_stage_contract") from exc
    selector = parse_stage_id(stages_text)
    if selector.stage_id != stage_id or selector.issue_code:
        raise SpecExecutionError("trace contract does not match live stage selector", "stale_stage_contract")
    record = find_stage_record(stages_text, stage_id)
    if record.issue_code:
        raise SpecExecutionError("trace contract stage record is missing or ambiguous", "invalid_stage_contract")
    try:
        master_state = extract_master_state(record.record or "")
    except MasterExecutionError as exc:
        raise SpecExecutionError(
            "trace contract requires canonical master-execution state", "invalid_stage_contract"
        ) from exc
    if master_state.get("schema_version") != 2:
        raise SpecExecutionError("trace contract requires CME schema v2", "invalid_stage_contract")
    selected_slices = [item for item in master_state["slices"] if item["id"] == stage_id]
    if len(selected_slices) != 1:
        raise SpecExecutionError("trace contract selected slice is missing", "invalid_stage_contract")
    canonical_requirements = set(selected_slices[0]["requirements"])
    canonical_evidence = tuple(selected_slices[0]["required_evidence"])
    raw_owners = data["requirement_owners"]
    if not isinstance(raw_owners, Mapping) or not raw_owners or len(raw_owners) > MAX_ITEMS:
        raise SpecExecutionError("trace contract owners must be a bounded mapping")
    owners: list[tuple[str, str]] = []
    for requirement_id, owner in raw_owners.items():
        owners.append((
            _identifier(requirement_id, "trace_contract.requirement_id"),
            _identifier(owner, f"trace_contract.requirement_owners.{requirement_id}"),
        ))
    if len({item[0] for item in owners}) != len(owners):
        raise SpecExecutionError("trace contract has duplicate requirement owners")
    if {item[0] for item in owners} != canonical_requirements:
        raise SpecExecutionError(
            "trace contract owners must exactly cover selected slice requirements",
            "requirement_contract_mismatch",
        )
    return TraceContract(
        repository_root=root,
        stage_id=stage_id,
        stage_status=selected_slices[0]["status"],
        requirement_owners=tuple(sorted(owners)),
        known_implementation_files=_artifact_refs(
            data["known_implementation_files"], "trace_contract.known_implementation_files",
            repository_root=root, require_existing=True,
        ),
        known_validator_ids=_string_list(
            data["known_validator_ids"], "trace_contract.known_validator_ids",
            identifiers=True, required=True,
        ),
        known_test_commands=_string_list(
            data["known_test_commands"], "trace_contract.known_test_commands",
            identifiers=True, required=True,
        ),
        required_evidence=canonical_evidence,
    )


def validate_trace(
    registry: Sequence[SkillMetadata], raw: Mapping[str, Any], contract: TraceContract
) -> dict[str, Any]:
    """Validate compact requirement→capability→artifact→evidence links without running checks."""
    data = _mapping(
        raw,
        "trace",
        allowed={"schema_version", "stage_id", "stage_status", "requirements"},
        required={"schema_version", "stage_id", "stage_status", "requirements"},
    )
    if data["schema_version"] != 1:
        raise SpecExecutionError("unsupported trace schema_version")
    stage_id = _identifier(data["stage_id"], "trace.stage_id")
    if stage_id != contract.stage_id:
        raise SpecExecutionError("trace claim does not match trusted stage contract", "stale_trace_claim")
    stage_status = _text(data["stage_status"], "trace.stage_status", limit=32)
    if stage_status not in TRACE_STATUSES:
        raise SpecExecutionError("unsupported trace stage_status")
    if stage_status != contract.stage_status:
        raise SpecExecutionError("trace status does not match trusted stage contract", "stale_trace_claim")
    requirement_owners = dict(contract.requirement_owners)
    stage_requirements = set(requirement_owners)
    known_files = set(contract.known_implementation_files)
    known_validators = set(contract.known_validator_ids)
    known_commands = set(contract.known_test_commands)
    rows = data["requirements"]
    if not isinstance(rows, list) or not rows or len(rows) > MAX_ITEMS:
        raise SpecExecutionError("trace requirements must be a non-empty bounded list")
    capability_ids = {
        capability
        for item in registry
        if item.status == "active"
        for capability in item.capabilities
    }
    seen: set[str] = set()
    issues: list[str] = []
    normalized: list[dict[str, Any]] = []
    row_keys = {
        "id", "owner_component", "stage_id", "capability_ids", "implementation_files",
        "validator_ids", "test_commands", "required_evidence", "evidence",
    }
    for index, raw_row in enumerate(rows):
        row = _mapping(raw_row, f"requirements[{index}]", allowed=row_keys, required=row_keys)
        requirement_id = _identifier(row["id"], f"requirements[{index}].id")
        if requirement_id in seen:
            raise SpecExecutionError(f"duplicate requirement id: {requirement_id}", "duplicate_requirement")
        seen.add(requirement_id)
        owner = _identifier(row["owner_component"], f"requirements[{index}].owner_component")
        row_stage = _identifier(row["stage_id"], f"requirements[{index}].stage_id")
        capabilities = _string_list(
            row["capability_ids"], f"requirements[{index}].capability_ids", identifiers=True, required=True
        )
        files = _artifact_refs(
            row["implementation_files"], f"requirements[{index}].implementation_files",
            repository_root=contract.repository_root,
        )
        validators = _string_list(
            row["validator_ids"], f"requirements[{index}].validator_ids", identifiers=True
        )
        commands = _string_list(
            row["test_commands"], f"requirements[{index}].test_commands", identifiers=True
        )
        required_evidence = _string_list(
            row["required_evidence"], f"requirements[{index}].required_evidence", required=True
        )
        evidence = _string_list(row["evidence"], f"requirements[{index}].evidence")
        if any(level not in EVIDENCE_LEVELS for level in required_evidence + evidence):
            raise SpecExecutionError("unsupported trace evidence level")
        if set(required_evidence) != set(contract.required_evidence):
            issues.append(f"evidence_contract_mismatch:{requirement_id}")
        if row_stage != stage_id:
            issues.append(f"stage_mismatch:{requirement_id}")
        if requirement_id not in stage_requirements:
            issues.append(f"missing_stage_requirement:{requirement_id}")
        elif requirement_owners[requirement_id] != owner:
            issues.append(f"owner_mismatch:{requirement_id}")
        for capability in sorted(set(capabilities) - capability_ids):
            issues.append(f"missing_capability:{requirement_id}:{capability}")
        for file_ref in sorted(set(files) - known_files):
            issues.append(f"missing_implementation_file:{requirement_id}:{file_ref}")
        for validator in sorted(set(validators) - known_validators):
            issues.append(f"missing_validator_reference:{requirement_id}:{validator}")
        for command in sorted(set(commands) - known_commands):
            issues.append(f"missing_test_command_reference:{requirement_id}:{command}")
        if not validators and not commands:
            issues.append(f"missing_validator_or_test:{requirement_id}")
        missing_evidence = sorted(set(contract.required_evidence) - set(evidence))
        if missing_evidence:
            issues.append(f"missing_evidence:{requirement_id}:{','.join(missing_evidence)}")
        if stage_status in {"verified", "completed"} and any(
            issue.split(":")[1] == requirement_id for issue in issues if ":" in issue
        ):
            issues.append(f"unsupported_completion:{requirement_id}")
        normalized.append({
            "id": requirement_id,
            "owner_component": owner,
            "stage_id": row_stage,
            "capability_ids": list(capabilities),
            "implementation_files": list(files),
            "validator_ids": list(validators),
            "test_commands": list(commands),
            "required_evidence": list(contract.required_evidence),
            "evidence": list(evidence),
        })
    for requirement_id in sorted(stage_requirements - seen):
        issues.append(f"missing_requirement_trace:{requirement_id}")
        if stage_status in {"verified", "completed"}:
            issues.append(f"unsupported_completion:{requirement_id}")
    return {
        "schema_version": 1,
        "status": "blocked" if issues else "valid",
        "stage_id": stage_id,
        "stage_status": stage_status,
        "requirements": normalized,
        "coverage_count": len(normalized),
        "issues": sorted(set(issues)),
        "commands_executed": False,
    }


def decide_placement(global_capabilities: Sequence[str], raw: Mapping[str, Any]) -> dict[str, Any]:
    """Return a placement/reuse decision; never materialize the capability."""
    data = _mapping(
        raw,
        "placement",
        allowed={
            "capability_id", "semantics", "consumer_projects", "requested_scope",
            "equivalent_global", "adapter_delta", "exception",
        },
        required={"capability_id", "semantics", "consumer_projects", "requested_scope"},
    )
    capability_id = _identifier(data["capability_id"], "placement.capability_id")
    semantics = _text(data["semantics"], "placement.semantics", limit=16)
    requested_scope = _text(data["requested_scope"], "placement.requested_scope", limit=16)
    consumers = data["consumer_projects"]
    if type(consumers) is not int or consumers < 1 or consumers > MAX_ITEMS:
        raise SpecExecutionError("consumer_projects must be a bounded positive integer")
    if requested_scope not in SCOPES:
        raise SpecExecutionError("unsupported placement scope", "unknown_scope")
    if semantics not in {"generic", "domain", "project", "unknown"}:
        raise SpecExecutionError("unsupported capability semantics")
    equivalent_global = _text(
        data.get("equivalent_global", ""), "placement.equivalent_global", required=False, limit=128
    )
    adapter_delta = data.get("adapter_delta", False)
    if not isinstance(adapter_delta, bool):
        raise SpecExecutionError("adapter_delta must be boolean")
    exception = _text(data.get("exception", ""), "placement.exception", required=False, limit=MAX_OBSERVATION)
    known_global = {_identifier(value, "global_capability") for value in global_capabilities}
    if equivalent_global:
        _identifier(equivalent_global, "placement.equivalent_global")
    duplicate = bool(equivalent_global) or (capability_id in known_global and requested_scope != "global")
    if duplicate and not (adapter_delta and exception):
        return {
            "status": "blocked", "action": "reuse_global", "reason": "duplicate_global_capability",
            "capability_id": capability_id, "recommended_scope": "global",
            "equivalent_global": equivalent_global or capability_id, "write_authorized": False,
        }
    if semantics == "unknown":
        return {
            "status": "needs_decision", "action": "user_decision", "reason": "unknown_semantics",
            "capability_id": capability_id, "recommended_scope": None,
            "equivalent_global": equivalent_global or None, "write_authorized": False,
        }
    if duplicate and adapter_delta and exception:
        recommended = requested_scope
    elif semantics == "generic" and consumers >= 2:
        recommended = "global"
    elif semantics == "domain" and consumers >= 2:
        recommended = "domain"
    else:
        recommended = "project"
    if requested_scope != recommended:
        status, action, reason = "blocked", "change_scope", "scope_mismatch"
    else:
        status, action = "ready", "place"
        reason = "explicit_adapter_delta" if duplicate else "scope_matches_semantics"
    return {
        "status": status,
        "action": action,
        "reason": reason,
        "capability_id": capability_id,
        "recommended_scope": recommended,
        "equivalent_global": equivalent_global or None,
        "write_authorized": False,
    }


def detect_opportunity(
    raw: Mapping[str, Any], existing: Sequence[Mapping[str, Any]] = ()
) -> dict[str, Any]:
    """Classify one sanitized observation and deduplicate it by stable structural identity."""
    data = _mapping(
        raw,
        "opportunity",
        allowed={
            "procedure_id", "scope", "occurrences", "projects", "stable_contract", "signals",
            "disqualifiers", "source_kind", "version", "reopen_reason", "priority",
            "evidence_refs", "provenance_refs",
        },
        required={
            "procedure_id", "scope", "occurrences", "projects", "stable_contract", "signals",
            "disqualifiers", "source_kind", "version",
        },
    )
    procedure_id = _identifier(data["procedure_id"], "opportunity.procedure_id")
    scope = _text(data["scope"], "opportunity.scope", limit=16)
    if scope not in SCOPES:
        raise SpecExecutionError("unsupported opportunity scope", "unknown_scope")
    occurrences = data["occurrences"]
    if type(occurrences) is not int or occurrences < 1 or occurrences > 1_000_000:
        raise SpecExecutionError("opportunity occurrences must be a bounded positive integer")
    projects = _string_list(data["projects"], "opportunity.projects", identifiers=True)
    if not isinstance(data["stable_contract"], bool):
        raise SpecExecutionError("stable_contract must be boolean")
    signals = _string_list(data["signals"], "opportunity.signals", identifiers=True)
    disqualifiers = _string_list(data["disqualifiers"], "opportunity.disqualifiers", identifiers=True)
    if any(value not in OPPORTUNITY_SIGNALS for value in signals):
        raise SpecExecutionError("unsupported opportunity signal")
    if any(value not in OPPORTUNITY_DISQUALIFIERS for value in disqualifiers):
        raise SpecExecutionError("unsupported opportunity disqualifier")
    source_kind = _text(data["source_kind"], "opportunity.source_kind", limit=16)
    if source_kind not in {"task", "review", "learning", "profiler"}:
        raise SpecExecutionError("unsupported opportunity source_kind")
    version = _identifier(data["version"], "opportunity.version")
    priority = _text(data.get("priority", ""), "opportunity.priority", required=False, limit=16)
    if priority and priority not in {"low", "medium", "high", "critical"}:
        raise SpecExecutionError("unsupported opportunity priority")
    evidence_refs = _string_list(
        data.get("evidence_refs", list(signals)), "opportunity.evidence_refs", identifiers=True
    )
    provenance_refs = _string_list(
        data.get("provenance_refs", [source_kind, *projects]),
        "opportunity.provenance_refs", identifiers=True,
    )
    reopen_reason = _text(
        data.get("reopen_reason", ""), "opportunity.reopen_reason", required=False, limit=MAX_OBSERVATION
    )
    fingerprint_source = json.dumps(
        {"procedure_id": procedure_id, "scope": scope, "projects": list(projects), "version": version},
        ensure_ascii=True, sort_keys=True, separators=(",", ":"),
    )
    fingerprint = hashlib.sha256(fingerprint_source.encode("utf-8")).hexdigest()
    candidate_id = f"AUTO-{fingerprint[:12].upper()}"
    qualified = bool(signals) and not disqualifiers and (
        occurrences >= 2
        or bool(set(signals).intersection({"expressible_manual_gate", "stable_mapping", "stable_io_contract"}))
    ) and bool(data["stable_contract"])
    if not priority:
        priority = "high" if qualified and occurrences >= 3 else ("medium" if qualified else "low")
    reason = "qualified_repeatable_procedure" if qualified else "not_a_stable_automation_candidate"
    status = "open" if qualified else "not_candidate"
    action = "create_candidate" if qualified else "keep_manual"
    for index, raw_item in enumerate(existing):
        item = _mapping(
            raw_item, f"existing[{index}]",
            allowed=CANDIDATE_KEYS | {"transition_evidence"},
            required={"id", "fingerprint", "status", "version"},
        )
        existing_fingerprint = _text(item["fingerprint"], f"existing[{index}].fingerprint", limit=64)
        existing_status = _text(item["status"], f"existing[{index}].status", limit=24)
        if existing_status not in CANDIDATE_STATUSES:
            raise SpecExecutionError("unsupported existing candidate status")
        if existing_fingerprint != fingerprint:
            continue
        candidate_id = _identifier(item["id"], f"existing[{index}].id")
        if existing_status in {"verified", "closed", "rejected"} and not reopen_reason:
            status, action, reason = existing_status, "closed_duplicate", "terminal_candidate_already_exists"
        elif existing_status in {"verified", "closed", "rejected"}:
            status, action, reason = "open", "reopen_candidate", "explicit_reopen_reason"
        else:
            status, action, reason = existing_status, "reuse_candidate", "open_candidate_already_exists"
        break
    return {
        "schema_version": 1,
        "id": candidate_id,
        "fingerprint": fingerprint,
        "version": version,
        "scope": scope,
        "status": status,
        "action": action,
        "reason": reason,
        "qualified": qualified,
        "occurrences": occurrences,
        "projects": list(projects),
        "signals": list(signals),
        "disqualifiers": list(disqualifiers),
        "source_kind": source_kind,
        "priority": priority,
        "evidence_refs": list(evidence_refs),
        "provenance_refs": list(provenance_refs),
        "write_authorized": False,
    }


def decide_promotion(global_capabilities: Sequence[str], raw: Mapping[str, Any]) -> dict[str, Any]:
    """Choose one durable target and placement for a qualified candidate, without applying it."""
    data = _mapping(
        raw,
        "promotion",
        allowed={
            "candidate_status", "pattern", "capability_id", "semantics", "consumer_projects",
            "requested_scope", "equivalent_global", "adapter_delta", "exception",
            "stable_contract", "risk_acceptable",
        },
        required={
            "candidate_status", "pattern", "capability_id", "semantics", "consumer_projects",
            "requested_scope", "stable_contract", "risk_acceptable",
        },
    )
    candidate_status = _text(data["candidate_status"], "promotion.candidate_status", limit=24)
    if candidate_status not in CANDIDATE_STATUSES | {"not_candidate"}:
        raise SpecExecutionError("unsupported candidate_status")
    pattern = _text(data["pattern"], "promotion.pattern", limit=32)
    if pattern not in PROMOTION_TARGETS:
        raise SpecExecutionError("unsupported promotion pattern")
    if not isinstance(data["stable_contract"], bool) or not isinstance(data["risk_acceptable"], bool):
        raise SpecExecutionError("promotion stability/risk flags must be boolean")
    if candidate_status not in {"open", "approved"} or not data["stable_contract"] or not data["risk_acceptable"]:
        return {
            "status": "no_promotion", "reason": "candidate_not_eligible",
            "target": None, "placement": None, "write_authorized": False,
        }
    placement = decide_placement(global_capabilities, {
        "capability_id": data["capability_id"],
        "semantics": data["semantics"],
        "consumer_projects": data["consumer_projects"],
        "requested_scope": data["requested_scope"],
        "equivalent_global": data.get("equivalent_global", ""),
        "adapter_delta": data.get("adapter_delta", False),
        "exception": data.get("exception", ""),
    })
    return {
        "status": "ready" if placement["status"] == "ready" else placement["status"],
        "reason": "promotion_target_selected" if placement["status"] == "ready" else placement["reason"],
        "target": PROMOTION_TARGETS[pattern],
        "placement": placement,
        "write_authorized": False,
    }


def transition_candidate(
    candidate: Mapping[str, Any], target_status: str, evidence: str = ""
) -> dict[str, Any]:
    """Apply a pure candidate lifecycle transition; terminal states never reopen implicitly."""
    data = _mapping(
        candidate,
        "candidate",
        allowed=CANDIDATE_KEYS | {"transition_evidence"},
        required={"status"},
    )
    current = _text(data["status"], "candidate.status", limit=24)
    target = _text(target_status, "candidate.target_status", limit=24)
    transitions = {
        "open": {"approved", "rejected", "blocked"},
        "approved": {"implemented", "blocked", "rejected"},
        "implemented": {"verified", "blocked"},
        "verified": {"closed"},
        "blocked": {"open", "rejected"},
        "closed": set(),
        "rejected": set(),
    }
    if current not in transitions or target not in transitions[current]:
        raise SpecExecutionError(f"invalid candidate transition: {current}->{target}", "invalid_transition")
    evidence = _text(evidence, "candidate.evidence", required=False, limit=MAX_OBSERVATION)
    _reject_secret_like([evidence], "candidate.evidence")
    if target in {"implemented", "verified", "closed"} and not evidence:
        raise SpecExecutionError("candidate transition requires evidence", "evidence_required")
    result: dict[str, Any] = {"status": target}
    if "schema_version" in data:
        if data["schema_version"] != 1:
            raise SpecExecutionError("unsupported candidate schema_version")
        result["schema_version"] = 1
    if "id" in data:
        result["id"] = _identifier(data["id"], "candidate.id")
    if "fingerprint" in data:
        fingerprint = _text(data["fingerprint"], "candidate.fingerprint", limit=64)
        if not SHA256.fullmatch(fingerprint):
            raise SpecExecutionError("candidate fingerprint must be SHA-256")
        result["fingerprint"] = fingerprint
    if "version" in data:
        result["version"] = _identifier(data["version"], "candidate.version")
    if "scope" in data:
        scope = _text(data["scope"], "candidate.scope", limit=16)
        if scope not in SCOPES:
            raise SpecExecutionError("unsupported candidate scope")
        result["scope"] = scope
    for key in ("action", "reason"):
        if key in data:
            result[key] = _identifier(data[key], f"candidate.{key}")
    if "qualified" in data:
        if not isinstance(data["qualified"], bool):
            raise SpecExecutionError("candidate.qualified must be boolean")
        result["qualified"] = data["qualified"]
    if "occurrences" in data:
        occurrences = data["occurrences"]
        if type(occurrences) is not int or occurrences < 1 or occurrences > 1_000_000:
            raise SpecExecutionError("candidate.occurrences must be bounded")
        result["occurrences"] = occurrences
    for key in ("projects", "signals", "disqualifiers", "evidence_refs", "provenance_refs"):
        if key in data:
            result[key] = list(_string_list(data[key], f"candidate.{key}", identifiers=True))
    if "source_kind" in data:
        source_kind = _text(data["source_kind"], "candidate.source_kind", limit=16)
        if source_kind not in {"task", "review", "learning", "profiler"}:
            raise SpecExecutionError("unsupported candidate source_kind")
        result["source_kind"] = source_kind
    if "priority" in data:
        priority = _text(data["priority"], "candidate.priority", limit=16)
        if priority not in {"low", "medium", "high", "critical"}:
            raise SpecExecutionError("unsupported candidate priority")
        result["priority"] = priority
    result["transition_evidence"] = evidence or None
    result["write_authorized"] = False
    return result


def analyze_context_economy(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Diagnose a bounded slice summary without collecting prompts, code, or token estimates."""
    keys = {
        "context_sources", "skills_loaded", "skills_used", "full_repo_scan",
        "full_repo_scan_reason", "full_master_load", "full_master_load_reason",
        "automation_reused", "reasoning_fallback", "model_class", "executor_route",
        "live_state_source", "repeated_manual_procedure",
    }
    data = _mapping(raw, "context_economy", allowed=keys, required=keys)
    sources = _string_list(data["context_sources"], "context_sources", identifiers=True)
    loaded = _string_list(data["skills_loaded"], "skills_loaded", identifiers=True)
    used = _string_list(data["skills_used"], "skills_used", identifiers=True)
    automation = _string_list(data["automation_reused"], "automation_reused", identifiers=True)
    if not set(used).issubset(loaded):
        raise SpecExecutionError("used Skill was not loaded", "invalid_skill_usage")
    for name in ("full_repo_scan", "full_master_load", "repeated_manual_procedure"):
        if not isinstance(data[name], bool):
            raise SpecExecutionError(f"{name} must be boolean")
    repo_reason = _text(data["full_repo_scan_reason"], "full_repo_scan_reason", required=False, limit=64)
    master_reason = _text(data["full_master_load_reason"], "full_master_load_reason", required=False, limit=64)
    if repo_reason and repo_reason not in FULL_SCAN_REASONS:
        raise SpecExecutionError("unsupported full_repo_scan_reason")
    if master_reason and master_reason not in FULL_SCAN_REASONS:
        raise SpecExecutionError("unsupported full_master_load_reason")
    fallback = _text(data["reasoning_fallback"], "reasoning_fallback", required=False, limit=MAX_OBSERVATION)
    model_class = _text(data["model_class"], "model_class", limit=16)
    if model_class not in {"LOW", "MEDIUM", "HIGH", "FRONTIER"}:
        raise SpecExecutionError("unsupported model_class")
    executor_route = _identifier(data["executor_route"], "executor_route")
    live_state_source = _text(data["live_state_source"], "live_state_source", limit=16)
    if live_state_source not in {"live_repo", "handoff", "chat", "unknown"}:
        raise SpecExecutionError("unsupported live_state_source")
    issues = [f"unused_skill:{skill}" for skill in sorted(set(loaded) - set(used))]
    if data["full_repo_scan"] and not repo_reason:
        issues.append("unjustified_full_repo_scan")
    if data["full_master_load"] and not master_reason:
        issues.append("unjustified_full_master_load")
    if live_state_source != "live_repo":
        issues.append("stale_or_unverified_state_source")
    if model_class == "FRONTIER" and executor_route in {
        "deterministic_tool", "deterministic_validator", "skill_with_deterministic_executor"
    }:
        issues.append("strongest_model_for_deterministic_route")
    if data["repeated_manual_procedure"] and not automation:
        issues.append("repeated_manual_without_automation")
    return {
        "schema_version": 1,
        "status": "review" if issues else "pass",
        "context_source_count": len(sources),
        "skills_loaded": list(loaded),
        "skills_used": list(used),
        "automation_reused": list(automation),
        "reasoning_fallback_used": bool(fallback),
        "model_class": model_class,
        "executor_route": executor_route,
        "issues": sorted(issues),
        "raw_content_recorded": False,
    }


def retirement_preflight(registry: Sequence[SkillMetadata], raw: Mapping[str, Any]) -> dict[str, Any]:
    """Recommend a safe two-phase retirement; never delete source or runtime materialization."""
    data = _mapping(
        raw,
        "retirement",
        allowed={
            "skill_id", "live_consumers", "required_capabilities", "replacement_id",
            "replacement_verified", "source_digest", "runtime_digest",
        },
        required={
            "skill_id", "live_consumers", "required_capabilities", "replacement_id",
            "replacement_verified", "source_digest", "runtime_digest",
        },
    )
    skill_id = _identifier(data["skill_id"], "retirement.skill_id")
    by_id = {item.id: item for item in registry}
    skill = by_id.get(skill_id)
    if skill is None:
        raise SpecExecutionError("unknown retirement Skill", "unknown_skill")
    consumers = _string_list(data["live_consumers"], "retirement.live_consumers", identifiers=True)
    required = _string_list(
        data["required_capabilities"], "retirement.required_capabilities", identifiers=True
    )
    replacement_id = _text(
        data["replacement_id"], "retirement.replacement_id", required=False, limit=128
    )
    replacement = None
    if replacement_id:
        replacement = by_id.get(_identifier(replacement_id, "retirement.replacement_id"))
        if replacement is None:
            raise SpecExecutionError("unknown retirement replacement", "unknown_replacement")
    if not isinstance(data["replacement_verified"], bool):
        raise SpecExecutionError("replacement_verified must be boolean")
    source_digest = _text(data["source_digest"], "retirement.source_digest", limit=128)
    runtime_digest = _text(data["runtime_digest"], "retirement.runtime_digest", limit=128)
    if not SHA256.fullmatch(source_digest) or not SHA256.fullmatch(runtime_digest):
        raise SpecExecutionError("retirement digests must be lowercase SHA-256", "invalid_digest")
    issues: list[str] = []
    action = "retirement_candidate"
    if skill.status == "retired":
        action = "already_retired"
    elif skill.status == "active":
        issues.append("deprecate_first")
        action = "deprecate_first"
    if consumers:
        issues.extend(f"live_consumer:{consumer}" for consumer in consumers)
    if source_digest != runtime_digest:
        issues.append("source_runtime_digest_mismatch")
    if skill.status != "retired":
        issues.extend(
            f"capability_inventory_incomplete:{capability}"
            for capability in sorted(set(skill.capabilities) - set(required))
        )
    relevant = set() if skill.status == "retired" else set(skill.capabilities)
    if relevant:
        if replacement is None:
            issues.append("sole_required_capability_owner")
        elif replacement.status != "active" or not data["replacement_verified"]:
            issues.append("replacement_not_verified")
        elif not relevant.issubset(set(replacement.capabilities)):
            issues.append("replacement_missing_capability")
    status = "already_retired" if action == "already_retired" and not issues else (
        "review_required" if not issues else "blocked"
    )
    return {
        "schema_version": 1,
        "status": status,
        "action": action,
        "skill_id": skill_id,
        "replacement_id": replacement_id or None,
        "issues": sorted(issues),
        "attestation_trusted": False,
        "write_authorized": False,
        "deletion_authorized": False,
    }


def _read_json(path: Path) -> Mapping[str, Any]:
    path = _local_path(path, "input")
    if not path.is_file() or path.stat().st_size > MAX_INPUT_BYTES:
        raise SpecExecutionError("input is missing or oversized")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise SpecExecutionError("input is unreadable or invalid JSON") from exc
    return _mapping(raw, "input", allowed=set(raw) if isinstance(raw, Mapping) else set())


def _add_registry_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--registry", type=Path, required=True)
    command.add_argument("--source-root", type=Path)
    command.add_argument("--delta-registry", type=Path)
    command.add_argument("--delta-source-root", type=Path)


def _load_composed_registry(args: argparse.Namespace) -> tuple[SkillMetadata, ...]:
    global_registry = load_registry(args.registry, args.source_root)
    if args.delta_registry is None:
        return compose_registries(global_registry)
    return compose_registries(
        global_registry,
        load_registry(args.delta_registry, args.delta_source_root),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Specification-to-Execution decisions and read-only launcher resolution"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    intake = commands.add_parser("intake", help="normalize explicit compact intake")
    intake.add_argument("--input", type=Path, required=True)
    launcher = commands.add_parser(
        "launcher", help="resolve a minimal user entrypoint through live DEV state"
    )
    _add_registry_arguments(launcher)
    launcher.add_argument("--input", type=Path, required=True)
    launcher.add_argument("--available-tool", action="append", default=[])
    launcher.add_argument("--source-revision")
    launcher.add_argument(
        "--queue-item-present",
        action=argparse.BooleanOptionalAction,
        default=None,
    )
    route = commands.add_parser("route", help="select relevant Skill metadata")
    _add_registry_arguments(route)
    route.add_argument("--input", type=Path, required=True)
    executor = commands.add_parser("executor", help="choose cheapest sufficient executor class")
    executor.add_argument("--input", type=Path, required=True)
    trace = commands.add_parser("trace", help="validate requirement/capability/evidence links")
    _add_registry_arguments(trace)
    trace.add_argument("--contract", type=Path, required=True)
    trace.add_argument("--repository-root", type=Path, required=True)
    trace.add_argument("--input", type=Path, required=True)
    placement = commands.add_parser("placement", help="decide global/domain/project placement")
    _add_registry_arguments(placement)
    placement.add_argument("--input", type=Path, required=True)
    opportunity = commands.add_parser("opportunity", help="detect a repeatable automation candidate")
    opportunity.add_argument("--input", type=Path, required=True)
    promotion = commands.add_parser("promotion", help="choose a promotion target and placement")
    _add_registry_arguments(promotion)
    promotion.add_argument("--input", type=Path, required=True)
    context = commands.add_parser("context-diagnostics", help="check lightweight context economy signals")
    context.add_argument("--input", type=Path, required=True)
    retirement = commands.add_parser("retirement", help="preflight a two-phase Skill retirement")
    _add_registry_arguments(retirement)
    retirement.add_argument("--input", type=Path, required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "intake":
            output = normalize_intake(_read_json(args.input))
        elif args.command == "launcher":
            output = resolve_user_launcher(
                _read_json(args.input),
                _load_composed_registry(args),
                available_tools=args.available_tool,
                source_revision=args.source_revision,
                queue_item_present=args.queue_item_present,
            )
        elif args.command == "route":
            output = route_skills(
                _load_composed_registry(args),
                _read_json(args.input),
            )
        elif args.command == "executor":
            output = choose_executor(_read_json(args.input))
        elif args.command == "trace":
            output = validate_trace(
                _load_composed_registry(args),
                _read_json(args.input),
                build_trace_contract(args.repository_root, args.contract),
            )
        elif args.command == "placement":
            registry = _load_composed_registry(args)
            global_capabilities = sorted({
                capability for item in registry if item.scope == "global"
                for capability in item.capabilities
            })
            output = decide_placement(global_capabilities, _read_json(args.input))
        elif args.command == "opportunity":
            output = detect_opportunity(_read_json(args.input))
        elif args.command == "promotion":
            registry = _load_composed_registry(args)
            global_capabilities = sorted({
                capability for item in registry if item.scope == "global"
                for capability in item.capabilities
            })
            output = decide_promotion(global_capabilities, _read_json(args.input))
        elif args.command == "context-diagnostics":
            output = analyze_context_economy(_read_json(args.input))
        else:
            output = retirement_preflight(
                _load_composed_registry(args), _read_json(args.input)
            )
    except SpecExecutionError as exc:
        print(json.dumps({"ok": False, "error": str(exc), "error_code": exc.code},
                         sort_keys=True, ensure_ascii=True))
        return 2
    print(json.dumps({"ok": True, "result": output}, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
