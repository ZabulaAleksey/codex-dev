# Быстрый старт на Windows, Linux и macOS

## Windows PowerShell

```powershell
# 1) Открыть канонический Git repository ДЕВ
Set-Location ~/.codex
Set-ExecutionPolicy -Scope Process Bypass

# 2) Проверить context, materialize Skills и проверить active layer
.\install-global.ps1

# 3) Read-only проверка одного full project overlay
py -3 .\tools\validate_project_overlay.py ~\codex-workspace\<project>

# 4) При необходимости вручную объединить recommendation с active config
notepad "$HOME\.codex\config.ai-dev-team.recommended.toml"
notepad "$HOME\.codex\config.toml"
```

## Linux / macOS

```bash
# 1) Открыть канонический Git repository ДЕВ
cd ~/.codex

# 2) Проверить context, materialize Skills и проверить active layer
./install-global.sh
# Если executable bit недоступен: bash ./install-global.sh

# 3) Read-only проверка одного full project overlay
python3 -B ./tools/validate_project_overlay.py ~/codex-workspace/<project>

# 4) При необходимости вручную сравнить recommendation с active config
${EDITOR:-vi} ~/.codex/config.ai-dev-team.recommended.toml ~/.codex/config.toml
```

Install wrappers проверяют, что их directory и Git root совпадают с canonical `~/.codex`,
запускают read-only `validate_context.py` до Skill sync и не перезаписывают `config.toml`.

## Проверка из product repository

```text
cd ~/codex-workspace/<project>
codex mcp list
codex --ask-for-approval never "Кратко изложи активные инструкции и перечисли доступных пользовательских агентов. Не изменяй файлы."
```

В интерактивном Codex открой `/agent`, `/hooks`, `/skills` и `/mcp`; доверяй automation только
после просмотра versioned files. Для `STANDARD`/`COMPLEX` функции прочитай затронутую SPEC.

Full staged overlay обязан иметь ровно один stable selector `- Stage ID: <id>` в
`docs/AI_PLAN.md` и ровно один unfenced heading с этим ID как отдельным token в
`prompts/STAGES.md`. Сначала запусти `validate_project_overlay.py`, затем загружай только exact
selected record. `DEGRADED` warning hook требует ручного чтения полного record и запрещает
completion claim до проверки.
