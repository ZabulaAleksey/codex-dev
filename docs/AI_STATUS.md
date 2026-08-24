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

## Verification evidence

После изменения глобального контекста обязательны `validate_context.py`, `validate_global_codex.py`, unit suite и проверка runtime Skill parity. Фактические команды и результаты фиксируются в handoff текущей задачи.

## Известные ограничения

- forward-only правило `docs/notes/` не переносит legacy files автоматически;
- semantic classification существующего документа требует отдельного content/link audit;
- внешняя визуализация может отставать от Git и должна обновляться как derived projection.
- tracked `presets/`, `backlog/` и `skill-sources/dev-karkas/references/PROJECT_REGISTRY.md` остаются предметом отдельного decontamination audit из нового prompt; они не являются автоматически загружаемым active governance, но пока не соответствуют его целевой repository boundary.

## Следующее действие

Сохранять project-agnostic boundary и применять новый Markdown layout при создании будущего контекста.
