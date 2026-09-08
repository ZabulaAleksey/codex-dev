from __future__ import annotations

import re
from dataclasses import dataclass


MAX_STAGE_RECORD_CHARS = 3500

STAGE_ID_PREFIX = re.compile(r"^\s*-\s*Stage ID\s*:", re.IGNORECASE)
STAGE_ID_LINE = re.compile(
    r"^\s*-\s*Stage ID:\s*(?:`(?P<quoted>[^`]*)`|(?P<plain>\S+))\s*$",
    re.IGNORECASE,
)
VALID_STAGE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
MARKDOWN_HEADING = re.compile(r"^(?P<marks>#{1,6})[ \t]+(?P<title>.+?)\s*$")
MARKDOWN_FENCE = re.compile(r"^\s*(?P<fence>`{3,}|~{3,})")


@dataclass(frozen=True)
class SelectorResult:
    stage_id: str | None = None
    record: str | None = None
    issue_code: str | None = None
    message: str | None = None


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


def parse_stage_id(stages: str) -> SelectorResult:
    candidates = [line for line in unfenced_lines(stages) if STAGE_ID_PREFIX.match(line)]
    if not candidates:
        return SelectorResult(
            issue_code="missing-stage-id",
            message=(
                "prompts/STAGES.md must contain exactly one unfenced "
                "`- Stage ID: <id>` selector"
            ),
        )
    if len(candidates) != 1:
        return SelectorResult(
            issue_code="ambiguous-stage-id",
            message=(
                "prompts/STAGES.md must contain exactly one unfenced Stage ID selector; "
                f"found {len(candidates)}"
            ),
        )

    match = STAGE_ID_LINE.fullmatch(candidates[0])
    if match is None:
        return SelectorResult(
            issue_code="invalid-stage-id",
            message=(
                "Stage ID must use `- Stage ID: <id>` and contain 1–64 ASCII letters, "
                "digits, `.`, `_` or `-`"
            ),
        )
    stage_id = (match.group("quoted") or match.group("plain") or "").strip()
    if not VALID_STAGE_ID.fullmatch(stage_id):
        return SelectorResult(
            issue_code="invalid-stage-id",
            message=(
                "Stage ID must contain 1–64 ASCII letters, digits, `.`, `_` or `-`, "
                "and start with a letter or digit"
            ),
        )
    return SelectorResult(stage_id=stage_id)


def stage_id_from_stages(stages: str) -> tuple[str | None, str | None]:
    result = parse_stage_id(stages)
    if result.issue_code == "missing-stage-id":
        return None, (
            "STAGES не содержит единственный Stage ID selector. "
            "Запись stage не загружена."
        )
    if result.issue_code == "ambiguous-stage-id":
        count = sum(1 for line in unfenced_lines(stages) if STAGE_ID_PREFIX.match(line))
        return None, (
            f"STAGES содержит неоднозначный Stage ID selector: строк найдено {count}. "
            "Запись stage не загружена."
        )
    if result.issue_code:
        return None, (
            "STAGES содержит некорректный Stage ID. Допустимы 1–64 ASCII-символа: "
            "буквы, цифры, `.`, `_`, `-`. Запись stage не загружена."
        )
    return result.stage_id, None


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


def heading_contains_stage_id(title: str, stage_id: str) -> bool:
    boundary = r"A-Za-z0-9._-"
    return re.search(
        rf"(?<![{boundary}]){re.escape(stage_id)}(?![{boundary}])",
        title,
        flags=re.IGNORECASE,
    ) is not None


def find_stage_record(catalog: str, stage_id: str) -> SelectorResult:
    headings = markdown_headings(catalog)
    matches = [
        (index, heading)
        for index, heading in enumerate(headings)
        if heading_contains_stage_id(heading[2], stage_id)
    ]
    if not matches:
        return SelectorResult(
            stage_id=stage_id,
            issue_code="missing-stage-heading",
            message=(
                f"prompts/STAGES.md must contain exactly one unfenced Markdown heading "
                f"with Stage ID `{stage_id}` as a separate token"
            ),
        )
    if len(matches) != 1:
        return SelectorResult(
            stage_id=stage_id,
            issue_code="ambiguous-stage-heading",
            message=(
                f"prompts/STAGES.md contains {len(matches)} headings with Stage ID "
                f"`{stage_id}`; expected exactly one"
            ),
        )

    selected_index, selected = matches[0]
    selected_start, selected_level, _ = selected
    end = len(catalog)
    for heading in headings[selected_index + 1 :]:
        heading_start, heading_level, _ = heading
        if heading_level <= selected_level:
            end = heading_start
            break
    return SelectorResult(stage_id=stage_id, record=catalog[selected_start:end].strip())


def select_stage_record(catalog: str, stage_id: str) -> tuple[str | None, str | None]:
    result = find_stage_record(catalog, stage_id)
    if result.issue_code == "missing-stage-heading":
        return None, f"Stage ID `{stage_id}` не найден в heading `prompts/STAGES.md`."
    if result.issue_code == "ambiguous-stage-heading":
        count = sum(
            1
            for _, _, title in markdown_headings(catalog)
            if heading_contains_stage_id(title, stage_id)
        )
        return None, (
            f"Stage ID `{stage_id}` неоднозначен: найдено headings: {count}. "
            "Запись stage не загружена."
        )

    record = result.record or ""
    if len(record) > MAX_STAGE_RECORD_CHARS:
        record = record[:MAX_STAGE_RECORD_CHARS].rstrip()
        record += (
            "\n\n[DEGRADED: запись stage усечена hook-лимитом; "
            "откройте полный record до начала stage.]"
        )
    return record, None
