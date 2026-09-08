import json
import sys
from pathlib import Path

try:
    from tools.stage_compatibility import render_stage_routing_context, stage_routing_snapshot
except ImportError:  # Direct script execution from the repository root.
    project_root = str(Path(__file__).resolve().parents[1])
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    try:
        from tools.stage_compatibility import render_stage_routing_context, stage_routing_snapshot
    except ImportError:  # Bootstrap fallback remains advisory and fail-closed.
        render_stage_routing_context = None
        stage_routing_snapshot = None

MAX_CHARS = 9000
MAX_STAGE_RECORD_CHARS = 6_000
MAX_ROUTING_CONTEXT_CHARS = 3_000
FILES = [
    "specs/README.md",
    "specs/system.spec.md",
    "docs/ARCHITECTURE.md",
]


def find_repo_root(start: Path) -> Path:
    p = start.resolve()
    for candidate in [p, *p.parents]:
        if (candidate / ".git").exists():
            return candidate
    return p


def is_within_repo(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def read_bounded_text(path: Path, limit: int) -> str:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return handle.read(limit)


def resolve_repo_file(root: Path, relative: str) -> Path | None:
    try:
        path = (root / relative).resolve(strict=True)
    except OSError:
        return None
    if not is_within_repo(root, path) or not path.is_file():
        return None
    return path


def _safe_routing_context(routing: dict) -> str | None:
    if render_stage_routing_context is None:
        return "routing helper unavailable; execution is degraded"
    try:
        rendered = render_stage_routing_context(routing)
    except Exception:  # Advisory hook: never block the host process.
        return "routing_render_failed_closed"
    if rendered is None:
        return None
    clean = "".join(
        character for character in str(rendered)
        if character in "\n\r\t" or ord(character) >= 0x20
    )
    return clean[:MAX_ROUTING_CONTEXT_CHARS]


def _routing(root: Path) -> tuple[dict, str | None]:
    if stage_routing_snapshot is None:
        return ({
            "status": "degraded", "inspection_ok": False,
            "canonical_valid": False, "execution_allowed": False,
            "classification": "unknown", "route": "migration_required",
            "projection": {}, "issue_codes": ["routing_helper_unavailable"],
            "outcome": "conflict", "materialization": {"state": "plan_unavailable"},
        }, None)
    try:
        value, record = stage_routing_snapshot(root)
        if isinstance(value, dict) and (record is None or isinstance(record, str)):
            return value, record
        raise ValueError("invalid_routing_result")
    except Exception:  # Advisory hook: fail closed and exit zero.
        return ({
            "status": "degraded", "inspection_ok": False,
            "canonical_valid": False, "execution_allowed": False,
            "classification": "conflict", "route": "migration_required",
            "projection": {}, "issue_codes": ["routing_error"],
            "outcome": "conflict", "materialization": {"state": "plan_unavailable"},
        }, None)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, TypeError):
        return
    cwd = Path(payload.get("cwd") or ".").expanduser()
    root = find_repo_root(cwd).resolve()
    chunks = []
    remaining = MAX_CHARS

    routing, selected_record = _routing(root)
    routing_context = _safe_routing_context(routing)
    if routing_context:
        header = "## Stage compatibility\n"
        chunks.append(header + routing_context)
        remaining -= len(header) + len(routing_context)

    # Only the pure router may authorize selected-record injection. Legacy or
    # conflicting state receives the compatibility block, never guessed prose.
    if routing.get("execution_allowed") is True and remaining > 0:
        if selected_record is not None and type(routing.get("stage_selector")) is str:
            if len(selected_record) > MAX_STAGE_RECORD_CHARS:
                selected_record = selected_record[:MAX_STAGE_RECORD_CHARS].rstrip()
                selected_record += (
                    "\n\n[DEGRADED: selected record truncated by hook limit; "
                    "open the full record before stage execution.]"
                )
            stage_chunk = (
                f"## prompts/STAGES.md — selected `{routing['stage_selector']}`\n"
                + selected_record
            )
            chunks.append(stage_chunk)
            remaining -= len(stage_chunk)
        else:
            warning_chunk = "## Stage context — DEGRADED\nrouting snapshot missing selected record"
            chunks.append(warning_chunk)
            remaining -= len(warning_chunk)

    # A noncanonical route is already a complete low-context stop result. General
    # docs cannot authorize a guessed stage and would only obscure the exact issue.
    if routing.get("execution_allowed") is True:
        for rel in FILES:
            if remaining <= 0:
                break
            path = resolve_repo_file(root, rel)
            if path is None:
                continue
            part = read_bounded_text(path, min(remaining, 3500))
            if part.strip():
                chunks.append(f"## {rel}\n{part}")
                remaining -= len(part)
    if not chunks:
        return
    event = payload.get("hook_event_name", "SessionStart")
    if event not in {"SessionStart", "SubagentStart"}:
        event = "SessionStart"
    out = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": "Project snapshot (read-only):\n\n" + "\n\n".join(chunks),
        }
    }
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
