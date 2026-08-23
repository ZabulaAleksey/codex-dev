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
$dev-karkas обработай новые идеи Tutor из Notion
$dev-karkas составь implementation prompt для этой идеи
$dev-karkas синхронизируй статус после завершённого этапа
```

Skill также разрешает implicit invocation через `agents/openai.yaml`.

## Что является «промптом КАРКАСА»

`SKILL.md` — orchestration-инструкция: когда и как применять КАРКАС.

`references/KARKAS.md` — канонический состав КАРКАСА.

Остальные references раскрывают отдельные policy. Такой layout не перегружает контекст Codex: основной skill остаётся компактным, а детали читаются по необходимости.

## Tutor / Notion

Пакет уже содержит `references/PROJECT_REGISTRY.md` с канонической Notion-страницей Tutor. Поэтому intake может начинать поиск сразу внутри Tutor и его дочерних заметок, а не сканировать весь workspace.
