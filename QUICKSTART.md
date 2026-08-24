# Быстрый старт в Windows

```powershell
# 1) Открыть PowerShell в каноническом Git repository ДЕВ
Set-Location ~/.codex
Set-ExecutionPolicy -Scope Process Bypass

# 2) Проверить глобальное ядро
.\install-global.ps1

# 2a) Проверить целостность глобального контекста
py -3 .\tools\validate_context.py

# 2b) Read-only проверка одного project overlay
py -3 .\tools\validate_project_overlay.py ~\codex-workspace\<project>

# 3) Объединить предложенную конфигурацию с существующей, если она была
notepad "$HOME\.codex\config.ai-dev-team.recommended.toml"
notepad "$HOME\.codex\config.toml"

# 4) Установить один проектный preset
.\install-project.ps1 -Preset trading-terminal -Target '~/codex-workspace/trading-terminal'

# 5) Проверить из репозитория
Set-Location ~/codex-workspace/trading-terminal
codex mcp list
codex --ask-for-approval never "Кратко изложи активные инструкции и перечисли доступных пользовательских агентов. Не изменяй файлы."
```

В интерактивном Codex открой `/hooks`, проверь определения и доверь их только после просмотра файлов. Для `STANDARD` или `COMPLEX` функции также проверь `specs/README.md` и относящуюся к задаче SPEC.
