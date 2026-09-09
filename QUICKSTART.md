# Быстрый старт на Windows, Linux и macOS

Canonical DEV source repository и installed Codex home — разные слои:

- `~/codex-workspace/codex-dev` (или другой пользовательский path) — Git-managed source;
- `~/.codex` — installed global layer и device-local runtime state, не Git repository;
- `~/.agents/skills` — runtime materialization versioned Skills.

## Windows PowerShell

```powershell
# 1) Clone/pull canonical source
git clone <dev-remote> "$HOME\codex-workspace\codex-dev"
Set-Location "$HOME\codex-workspace\codex-dev"
git pull --ff-only

# 2) Сначала просмотреть точный install plan
Set-ExecutionPolicy -Scope Process Bypass
.\install-global.ps1 -DryRun

# 3) Установить managed layer, materialize Skills и выполнить validators
.\install-global.ps1

# 4) Проверить один full project overlay установленным validator
py -3 "$HOME\.codex\tools\validate_project_overlay.py" "$HOME\codex-workspace\<project>"
```

## Linux / macOS

```bash
git clone <dev-remote> ~/codex-workspace/codex-dev
cd ~/codex-workspace/codex-dev
git pull --ff-only

./install-global.sh --dry-run
./install-global.sh
# Если executable bit недоступен: bash ./install-global.sh

python3 -B ~/.codex/tools/validate_project_overlay.py ~/codex-workspace/<project>
```

Installer определяет source как Git root wrapper-а, использует `MANIFEST.txt` как explicit file
allowlist, сохраняет ownership ledger в `~/.codex/.dev-install-manifest.json` и не зеркалирует весь
repository. Runtime state, unknown files и active `config.toml` не перезаписываются. Различающийся
unknown collision или protected runtime path в manifest завершает install до первой записи.

`skill-sources/` остаётся только в canonical source; runtime Skills materialize-ятся существующим
`tools/sync_global_skills.py` в `~/.agents/skills`. Recommended config устанавливается как reference:

```text
~/.codex/config.ai-dev-team.recommended.toml
```

При необходимости сравни его с active `~/.codex/config.toml` вручную. Installer не заменяет и не
объединяет active config.

## Миграция старого `DEV == ~/.codex`

Если `~/.codex/.git` ещё существует, сначала сохранить Git status/remote и перенести canonical
repository в `~/codex-workspace/codex-dev`. Удаление или перенос `.git` — отдельное явно контролируемое
действие: installer fail closed и не изменяет Git metadata автоматически. После этого запусти
`-DryRun`; идентичные managed files будут приняты в ledger без перезаписи, а различающийся unknown
file потребует ручного reconcile.

## Проверка из product repository

```text
cd ~/codex-workspace/<project>
codex mcp list
codex --ask-for-approval never "Кратко изложи активные инструкции и перечисли доступных пользовательских агентов. Не изменяй файлы."
```

В интерактивном Codex открой `/agent`, `/hooks`, `/skills` и `/mcp`; доверяй automation только
после просмотра versioned source и installed ownership ledger. Для `STANDARD`/`COMPLEX` функции
прочитай затронутую SPEC.

Full staged overlay обязан иметь ровно один stable selector `- Stage ID: <id>` в
`prompts/STAGES.md` и ровно один unfenced heading с этим ID как отдельным token в том же файле.
Сначала запусти installed `validate_project_overlay.py`, затем загружай только exact selected
record. `DEGRADED` warning hook требует ручного чтения полного record и запрещает completion claim
до проверки.
