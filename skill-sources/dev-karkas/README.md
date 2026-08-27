# dev-karkas

Глобальный Codex skill для ДЕВ / КАРКАС.

## Установка на Windows

Положи папку `dev-karkas` сюда:

```text
%USERPROFILE%\.agents\skills\dev-karkas\
```

Или из PowerShell, находясь в распакованной папке:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

Скрипт не перезапишет существующую установку без `-Force`; с `-Force` сначала сделает backup.

## Проверка пакета

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate.ps1
```

## Вызов

Примеры:

```text
$dev-karkas bootstrap this repository
$dev-karkas audit this repository
$dev-karkas обработай новые идеи выбранного проекта из Notion
$dev-karkas составь implementation prompt для этой идеи
$dev-karkas синхронизируй статус после завершённого этапа
```

Skill также разрешает implicit invocation через `agents/openai.yaml`.

При построении или выполнении stage Skill применяет канонический Stage contract из
`~/.codex/rules/governance.md`: completed prerequisites/DAG, runnable vertical slice, concrete
end-to-end PASS evidence, fully working temporary implementation и deferred scope. Future stage
не может впервые сделать предыдущий stage исполнимым или проверяемым; mock-only результат остаётся
`scaffolded`.

При завершении задачи или этапа Skill всегда проверяет `README`, `AI_PLAN`,
`AI_STATUS`, `ROADMAP`, `prompts/STAGES.md` и другие state-bearing документы по
`references/STATUS_WORKFLOW.md`. Изменившиеся факты обновляются; точные документы
остаются без timestamp-only churn. После merge gate повторяется по target branch.

## Что является «промптом КАРКАСА»

`SKILL.md` — orchestration-инструкция: когда и как применять КАРКАС.

`references/KARKAS.md` — канонический состав КАРКАСА.

Остальные references раскрывают отдельные policy. Такой layout не перегружает контекст Codex: основной skill остаётся компактным, а детали читаются по необходимости.

## Notion

`references/PROJECT_REGISTRY.md` содержит только schema и discovery policy. Actual project bindings ищутся во внешнем project-aware слое и подтверждаются fetch/read-back; реальные project names, IDs и абсолютные paths не сохраняются в global Skill.
