import json
import sys
from pathlib import Path

MAX_CHARS = 9000
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


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    payload = json.load(sys.stdin)
    cwd = Path(payload.get("cwd") or ".").expanduser()
    root = find_repo_root(cwd).resolve()
    chunks = []
    remaining = MAX_CHARS
    for rel in FILES:
        try:
            path = (root / rel).resolve(strict=True)
        except OSError:
            continue
        if not is_within_repo(root, path) or not path.is_file():
            continue
        # Сохраняем статус первым и ограничиваем каждый файл, чтобы не переполнять контекст.
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
