# Текущее состояние ДЕВ / КАРКАС

Дата: 2026-08-24

## Статус

Глобальный ДЕВ хранится в единственном Git root `~/.codex`. Active instruction/rules layer предоставляет project-agnostic правила, agents, hooks, Skills, templates, validators и framework documentation. Product repositories наследуют глобальный `~/.codex/AGENTS.md` и хранят только локальную delta.

## Подтверждённые инварианты

- active global instruction source — `~/.codex/AGENTS.md`;
- runtime state, credentials, sessions, caches, downloaded plugins и machine-local config не входят в tracked global context;
- versioned custom Skill sources находятся в `skill-sources/`, runtime projection — в `~/.agents/skills`;
- project root определяется независимо, а глобальный framework не ведёт live inventory потребителей;
- `docs/AI_STATUS.md` — единственный текущий status source; `docs/AI_PLAN.md` — единственный текущий plan source;
- новые дополнительные долговечные `.md` размещаются в `docs/notes/`, если содержание нельзя включить в существующий canonical document;
- external Notion/Eraser/Figma projections не заменяют Git source of truth.
- global `rules/dependency-management.md` задаёт preferred matrix, exception
  contract, штатные shared caches/stores и clean-restore requirements; validators
  дают только read-only inventory/drift evidence и не мигрируют product repositories.

## Verification evidence

После изменения глобального контекста обязательны `validate_context.py`, `validate_global_codex.py`, unit suite и проверка runtime Skill parity. Фактические команды и результаты фиксируются в handoff текущей задачи.

## Результат decontamination

- backlog мигрирован в каноническую Notion-страницу с read-back verification; локальные исходники удалены;
- доказанно сопоставленные project presets удалены после сверки с более свежими repositories;
- registry содержит только schema/discovery policy, без actual inventory;
- вспомогательные Markdown-файлы находятся в `docs/notes/`;
- активная документация и automation больше не предлагают установку project-named presets;
- неоднозначные project-specific источники сохранены со статусом `BLOCKED` и не считаются active governance.

## Следующее действие

Поддерживать dependency contract в project overlays и выполнять actual project
migration только в отдельной repository-scoped работе с recovery point, clean restore
и проверками.
