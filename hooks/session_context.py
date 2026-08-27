import json
import re
import sys
from pathlib import Path

MAX_CHARS = 9000
MAX_PLAN_SCAN_CHARS = 100_000
MAX_STAGE_SCAN_CHARS = 500_000
MAX_STAGE_RECORD_CHARS = 3500
FILES = [
    "docs/AI_STATUS.md",
    "specs/README.md",
    "specs/system.spec.md",
    "docs/AI_PLAN.md",
    "docs/ARCHITECTURE.md",
]

STAGE_ID_LINE = re.compile(
    r"^\s*-\s*Stage ID:\s*(?:`(?P<quoted>[^`]*)`|(?P<plain>\S+))\s*$",
    re.IGNORECASE,
)
VALID_STAGE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
MARKDOWN_HEADING = re.compile(r"^(?P<marks>#{1,6})[ \t]+(?P<title>.+?)\s*$")
MARKDOWN_FENCE = re.compile(r"^\s*(?P<fence>`{3,}|~{3,})")


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


def unfenced_lines(text: str):
    fence_char = None
    fence_size = 0
    for line in text.splitlines():
        fence = MARKDOWN_FENCE.match(line)
        if fence:
            token = fence.group("fence")
            if fence_char is None:
                fence_char = token[0]
                fence_size = len(token)
            elif token[0] == fence_char and len(token) >= fence_size:
                fence_char = None
                fence_size = 0
            continue
        if fence_char is None:
            yield line


def markdown_headings(text: str) -> list[tuple[int, int, str]]:
    headings = []
    fence_char = None
    fence_size = 0
    offset = 0
    for line_with_ending in text.splitlines(keepends=True):
        line = line_with_ending.rstrip("\r\n")
        fence = MARKDOWN_FENCE.match(line)
        if fence:
            token = fence.group("fence")
            if fence_char is None:
                fence_char = token[0]
                fence_size = len(token)
            elif token[0] == fence_char and len(token) >= fence_size:
                fence_char = None
                fence_size = 0
        elif fence_char is None:
            heading = MARKDOWN_HEADING.fullmatch(line)
            if heading:
                headings.append((offset, len(heading.group("marks")), heading.group("title")))
        offset += len(line_with_ending)
    return headings


def stage_id_from_plan(plan: str) -> tuple[str | None, str | None]:
    matches = []
    for line in unfenced_lines(plan):
        match = STAGE_ID_LINE.fullmatch(line)
        if match:
            matches.append(match)
    if not matches:
        return None, None
    if len(matches) != 1:
        return None, (
            f"AI_PLAN содержит неоднозначный Stage ID selector: строк найдено {len(matches)}. "
            "Запись stage не загружена."
        )
    match = matches[0]
    stage_id = (match.group("quoted") or match.group("plain") or "").strip()
    if not stage_id:
        return None, None
    if not VALID_STAGE_ID.fullmatch(stage_id):
        return None, (
            "AI_PLAN содержит некорректный Stage ID. Допустимы 1–64 ASCII-символа: "
            "буквы, цифры, `.`, `_`, `-`. Запись stage не загружена."
        )
    return stage_id, None


def heading_contains_stage_id(title: str, stage_id: str) -> bool:
    boundary = r"A-Za-z0-9._-"
    return re.search(
        rf"(?<![{boundary}]){re.escape(stage_id)}(?![{boundary}])",
        title,
        flags=re.IGNORECASE,
    ) is not None


def select_stage_record(catalog: str, stage_id: str) -> tuple[str | None, str | None]:
    headings = markdown_headings(catalog)
    matches = [
        (index, heading)
        for index, heading in enumerate(headings)
        if heading_contains_stage_id(heading[2], stage_id)
    ]
    if not matches:
        return None, f"Stage ID `{stage_id}` не найден в heading `prompts/STAGES.md`."
    if len(matches) != 1:
        return None, (
            f"Stage ID `{stage_id}` неоднозначен: найдено headings: {len(matches)}. "
            "Запись stage не загружена."
        )

    selected_index, selected = matches[0]
    selected_start, selected_level, _ = selected
    end = len(catalog)
    for heading in headings[selected_index + 1 :]:
        heading_start, heading_level, _ = heading
        if heading_level <= selected_level:
            end = heading_start
            break
    record = catalog[selected_start:end].strip()
    if len(record) > MAX_STAGE_RECORD_CHARS:
        record = record[:MAX_STAGE_RECORD_CHARS].rstrip()
        record += (
            "\n\n[DEGRADED: запись stage усечена hook-лимитом; "
            "откройте полный record до начала stage.]"
        )
    return record, None


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
