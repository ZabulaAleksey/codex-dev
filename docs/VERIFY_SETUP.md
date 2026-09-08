# Контрольный список проверки установки

## Целостность глобального ДЕВ

Из корня `~/.codex`:

```powershell
py -3 .\tools\validate_context.py
py -3 .\tools\sync_global_skills.py --source .\skill-sources --destination ~\.agents\skills
py -3 .\tools\validate_global_codex.py --codex-home ~/.codex
```

На Linux/macOS используй симметричный wrapper:

```bash
cd ~/.codex
./install-global.sh
```

Оба install wrapper проверяют canonical directory/Git root, выполняют `validate_context.py` до
materialization, sync через `sync_global_skills.py`, повторную context/global validation и не
перезаписывают `config.toml`.

Проверка подтверждает наличие обязательных документов, корректность `MANIFEST.txt`, отсутствие дубликатов путей без учёта регистра и соответствие manifest фактическим отслеживаемым/неигнорируемым файлам.

Legacy option `validate_global_codex.py --workspace` принимает canonical source root, то есть
`~/.codex`, а не `~/codex-workspace`. Неверный root должен вернуть структурированные
`missing-canonical-source` issues и не завершаться traceback.

## Глобальная конфигурация

```powershell
codex mcp list
codex --ask-for-approval never "Кратко изложи текущие глобальные и проектные инструкции."
```

В TUI:

```text
/agent
/hooks
/skills
/mcp
```

## Правила

Пример проверки:

```powershell
codex execpolicy check --pretty --rules "$HOME\.codex\rules\ai-dev-team.rules" -- git push --force origin main
```

Ожидаемый результат: действие запрещено.

## Пробный запуск hook

```powershell
'{"cwd":"~/codex-workspace/<project>","hook_event_name":"SessionStart","source":"startup"}' | py -3 "$HOME\.codex\hooks\session_context.py"
```

Для canonical/migrated repository ожидается selected record без compatibility noise. Для
legacy/mixed ожидается bounded `migration_required`, plan availability и
`execution_allowed=false`; conflict/no-state также fail closed. Hook не запускает materialization.
`validate_project_overlay.py`: full overlay обязан иметь ровно один валидный
unfenced selector и ровно один unfenced heading с ID как отдельным token. Если selector отсутствует,
validator возвращает `missing-stage-id`; multiple/invalid selector и missing/ambiguous heading
имеют отдельные issue codes.

Validator exit `0` означает canonical-ready; successful brownfield inspection с migration required
возвращает typed JSON и exit `1`. Argparse usage остаётся exit `2`. Hook при этих состояниях
возвращает advisory JSON/exit `0`, но не загружает guessed stage или общие docs.

## Проект

```powershell
git status --short
codex --ask-for-approval never "Перечисли пользовательских агентов проекта и укажи, кто из них должен обрабатывать следующий этап дорожной карты. Не изменяй файлы."
```

Для read-only восстановления без старого чата выполни также:

```powershell
py -3 "$HOME\.codex\tools\reconcile_project_framework.py" ~\codex-workspace\<project> --json
py -3 "$HOME\.codex\tools\validate_project_overlay.py" ~\codex-workspace\<project> --json
```

Затем используй copy-ready запрос «Возобновить проект» из `docs/WORKFLOW.md`. Broken links,
dirty work без provenance или stale STAGES execution state дают `DEGRADED`/`BLOCKED`, а не ложный PASS.
