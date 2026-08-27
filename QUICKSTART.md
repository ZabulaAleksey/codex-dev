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

# 4) Проверить из выбранного независимого project repository
Set-Location ~/codex-workspace/<project>
codex mcp list
codex --ask-for-approval never "Кратко изложи активные инструкции и перечисли доступных пользовательских агентов. Не изменяй файлы."
```

В интерактивном Codex открой `/hooks`, проверь определения и доверь их только после просмотра файлов. Для `STANDARD` или `COMPLEX` функции также проверь `specs/README.md` и относящуюся к задаче SPEC. Для stage-bound задачи укажи stable `Stage ID` в `docs/AI_PLAN.md`, загрузи только exact unique heading record из `prompts/STAGES.md` и до кода проверь его dependency DAG, runnable vertical slice и end-to-end PASS contract. `DEGRADED` warning hook требует ручного чтения полного record и не разрешает completion claim.
