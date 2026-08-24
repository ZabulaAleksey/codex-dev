# Текущий план ДЕВ / КАРКАС

Статус: выполнено с сохранёнными BLOCKED-источниками
Этап: Global governance decontamination
Дата: 2026-08-24

## Текущий ограниченный срез

Закрепить global dependency-manager policy и deterministic read-only inventory/drift
checks. Не выполнять migration product repositories этим изменением global framework.

Связанная SPEC: `specs/features/dependency-manager-policy.spec.md`

## Цель

Фактически мигрировать накопленный project-specific контекст из глобального слоя, удалить только верифицированные исходники и закрепить project-agnostic boundary.

## Выполнено

1. Каждый backlog-файл полностью прочитан, дедуплицирован и перенесён в каноническую страницу идей Notion; read-back подтверждён, исходники удалены.
2. Именованные presets классифицированы. Доказанно сопоставленные и superseded копии удалены после сверки с более свежими project-local контрактами.
3. Универсальные правила научных вычислений, realtime audio и CRDT отделены от project-specific материала и обезличены.
4. Неоднозначные или конфликтующие источники сохранены без удаления со статусом `BLOCKED`.
5. `PROJECT_REGISTRY.md` очищен до schema/discovery contract без реальных project bindings.
6. Вспомогательные Markdown-документы перенесены в `docs/notes/`; активные ссылки и validators обновлены.
7. Установщик и документация project-named presets удалены из активной automation.
8. Общие формы plan/status/decisions/spec index вынесены в project-agnostic `templates/`; точные дубликаты удалены из сохранённых quarantine sources.

## Проверки

- repository manifest и context validator;
- global Codex validator;
- unit suite validators/sync/reconcile;
- отсутствие drift у runtime-проекции `dev-karkas`;
- одна локальная ветка `main` после интеграции.

## Следующее действие

Проверить policy/validator delta, синхронизировать runtime Skill и зафиксировать
evidence. Для снятия сохранённых `BLOCKED` требуется доказанный repository mapping
либо отдельное разрешение на точное внешнее архивирование исходных bundles.
