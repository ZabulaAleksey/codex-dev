# Текущий план ДЕВ / КАРКАС

Статус: выполнено
Этап: Global documentation layout hardening
Дата: 2026-08-24

## Цель

Закрепить единое место для новых дополнительных Markdown-файлов, не создавая конкурирующих источников истины и не перемещая legacy documentation без semantic audit.

## Выполнено

1. Проверен текущий canonical document set в глобальных правилах, framework и `dev-karkas`.
2. Обязательные и условные документы КАРКАСА отделены от дополнительных материалов.
3. Для новых долговечных неканонических `.md` принят путь `docs/notes/<topic>.md`.
4. Массовый перенос существующих документов явно запрещён без semantic/link audit.
5. Global framework остаётся source of truth; Eraser используется только как derived visualization.
6. Приложенный cleanup prompt проверен отдельно: project-named `presets/`, `backlog/` и `PROJECT_REGISTRY.md` отмечены как следующий decontamination scope, требующий отдельного решения о сохранении/внешней миграции.

## Проверки

- repository manifest и context validator;
- global Codex validator;
- unit suite validators/sync/reconcile;
- отсутствие drift у runtime-проекции `dev-karkas`;
- одна локальная ветка `main` после интеграции.

## Следующее действие

Применять правило к новым файлам. Существующий layout, `presets/`, `backlog/` и registry менять только отдельной подтверждённой задачей с проверкой ссылок, уникального содержания и внешней миграции.
