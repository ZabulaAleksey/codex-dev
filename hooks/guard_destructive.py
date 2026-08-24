import json
import re
import sys

# Deny-list намеренно мал. Общая политика безопасности должна находиться в
# разрешениях и rules Codex, а не в хрупких регулярных выражениях.
DENY = [
    (r"\bgit(?:\.exe)?\b[^\r\n;&|]*\breset\s+--hard\b", "git reset --hard может уничтожить незакоммиченные изменения."),
    (
        r"\bgit(?:\.exe)?\b[^\r\n;&|]*\bclean\b"
        r"(?=[^\r\n;&|]*(?:\s--force(?=\s|$|[;&|])|\s-[A-Za-z]*f[A-Za-z]*(?=\s|$|[;&|])))",
        "git clean --force может необратимо удалить неотслеживаемые файлы.",
    ),
    (r"\bgit(?:\.exe)?\b[^\r\n;&|]*\bpush\b[^\r\n;&|]*(?:--force(?:-[A-Za-z-]+)?(?:=[^\s;&|]+)?|-f)(?=\s|$|[;&|])", "Force-push заблокирован глобальным hook AI-команды."),
    (r"\bdocker\s+system\s+prune\b", "docker system prune может удалить локальные ресурсы других проектов."),
    (r"\bDROP\s+DATABASE\b", "DROP DATABASE должен выполнять человек после явного решения."),
    (r"\bRemove-Item\b(?=[^\r\n;&|]*-Recurse\b)(?=[^\r\n;&|]*-Force\b)[^\r\n;&|]*(?:['\"]?[A-Za-z]:\\['\"]?|['\"]?/['\"]?)(?:\s|$)", "Рекурсивное принудительное удаление пути, похожего на корень диска, заблокировано."),
    (r"\brm\b(?=[^\r\n;&|]*(?:-[A-Za-z]*r|--recursive))(?=[^\r\n;&|]*(?:-[A-Za-z]*f|--force))[^\r\n;&|]*\s['\"]?/['\"]?(?:\s|$|\*)", "Рекурсивное удаление корня файловой системы заблокировано."),
]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") if isinstance(tool_input, dict) else ""
    if not isinstance(command, str):
        return
    for pattern, reason in DENY:
        if re.search(pattern, command, flags=re.IGNORECASE):
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason + " Используй неразрушительную альтернативу или попроси пользователя выполнить действие вручную."
                }
            }))
            return


if __name__ == "__main__":
    main()
