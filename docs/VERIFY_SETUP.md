# Контрольный список проверки установки

## Целостность глобального ДЕВ

Из canonical DEV source Git root:

```powershell
py -3 .\tools\validate_context.py
.\install-global.ps1 -DryRun
.\install-global.ps1
py -3 .\tools\validate_global_codex.py --workspace . --codex-home ~/.codex
```

На Linux/macOS используй симметричный wrapper:

```bash
cd ~/codex-workspace/codex-dev
./install-global.sh --dry-run
./install-global.sh
```

Оба install wrapper проверяют exact source Git root, но не требуют его совпадения с `~/.codex`.
Они строят manifest-only plan, транзакционно materialize-ят managed layer, запускают context/global
validation, sync через `sync_global_skills.py` и повторяют validation. Active `config.toml` и
runtime namespaces не перезаписываются.

Проверка подтверждает корректность source `MANIFEST.txt`, deterministic ownership ledger,
соответствие installed managed files, отсутствие дубликатов путей без учёта регистра и Skill parity.

Legacy option `validate_global_codex.py --workspace` принимает canonical source root, то есть
`~/codex-workspace/codex-dev` или другой clone, а не installed `~/.codex`. Неверный root возвращает
структурированные
`invalid-install-policy` issues и не завершается traceback.

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
