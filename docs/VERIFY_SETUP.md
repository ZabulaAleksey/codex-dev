# Контрольный список проверки установки

## Целостность глобального ДЕВ

Из корня `~/.codex`:

```powershell
py -3 .\tools\validate_context.py
py -3 .\tools\sync_global_skills.py --source .\skill-sources --destination ~\.agents\skills
py -3 .\tools\validate_global_codex.py --codex-home ~/.codex
```

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

Для репозитория с `docs/AI_STATUS.md` ожидается JSON, содержащий `additionalContext`.
Если `docs/AI_PLAN.md` содержит stable `Stage ID`, а `prompts/STAGES.md` — ровно один heading с
этим ID как отдельным token, выбранная bounded запись должна идти в `additionalContext` первой.
Invalid, missing или ambiguous selector должен вернуть `Stage context — DEGRADED`, а не другую
stage-запись.

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
dirty work без provenance или stale plan/status дают `DEGRADED`/`BLOCKED`, а не ложный PASS.
