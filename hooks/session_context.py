import json
import sys
from pathlib import Path

try:
    from .stage_selector import select_stage_record, stage_id_from_plan
except ImportError:  # Script execution: hooks/ is sys.path[0].
    hook_directory = str(Path(__file__).resolve().parent)
    if hook_directory not in sys.path:
        sys.path.insert(0, hook_directory)
    from stage_selector import select_stage_record, stage_id_from_plan

MAX_CHARS = 9000
MAX_PLAN_SCAN_CHARS = 100_000
MAX_STAGE_SCAN_CHARS = 500_000
FILES = [
    "docs/AI_STATUS.md",
    "specs/README.md",
    "specs/system.spec.md",
    "docs/AI_PLAN.md",
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


def selected_stage_chunk(root: Path) -> tuple[str | None, str | None]:
    plan_path = resolve_repo_file(root, "docs/AI_PLAN.md")
    if plan_path is None:
        return None, None
    plan = read_bounded_text(plan_path, MAX_PLAN_SCAN_CHARS + 1)
    if len(plan) > MAX_PLAN_SCAN_CHARS:
        return None, (
            "`docs/AI_PLAN.md` превышает scan-limit context hook; "
            "Stage ID не выбран."
        )
    stage_id, warning = stage_id_from_plan(plan)
    if warning or stage_id is None:
        return None, warning

    stages_path = resolve_repo_file(root, "prompts/STAGES.md")
    if stages_path is None:
        return None, (
            f"AI_PLAN выбирает Stage ID `{stage_id}`, но безопасный `prompts/STAGES.md` недоступен."
        )
    catalog = read_bounded_text(stages_path, MAX_STAGE_SCAN_CHARS + 1)
    if len(catalog) > MAX_STAGE_SCAN_CHARS:
        return None, (
            "`prompts/STAGES.md` превышает scan-limit context hook; "
            "запись stage не загружена."
        )
    record, warning = select_stage_record(catalog, stage_id)
    if warning:
        return None, warning
    return f"## prompts/STAGES.md — selected `{stage_id}`\n{record}", None


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    payload = json.load(sys.stdin)
    cwd = Path(payload.get("cwd") or ".").expanduser()
    root = find_repo_root(cwd).resolve()
    chunks = []
    remaining = MAX_CHARS

    # Выбранный stage идёт первым: bounded host limit не должен отрезать task contract
    # после общего project snapshot. Ошибка явного selector остаётся видимой деградацией.
    stage_chunk, stage_warning = selected_stage_chunk(root)
    if stage_chunk:
        chunks.append(stage_chunk)
        remaining -= len(stage_chunk)
    elif stage_warning:
        warning_chunk = "## Stage context — DEGRADED\n" + stage_warning
        chunks.append(warning_chunk)
        remaining -= len(warning_chunk)

    for rel in FILES:
        path = resolve_repo_file(root, rel)
        if path is None:
            continue
        part = read_bounded_text(path, min(remaining, 3500))
        if part.strip():
            chunks.append(f"## {rel}\n{part}")
            remaining -= len(part)
        if remaining <= 0:
            break
    if not chunks:
        return
    event = payload.get("hook_event_name", "SessionStart")
    if event not in {"SessionStart", "SubagentStart"}:
        event = "SessionStart"
    out = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": "Снимок состояния и SDD-контекста проекта (только чтение):\n\n" + "\n\n".join(chunks),
        }
    }
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
