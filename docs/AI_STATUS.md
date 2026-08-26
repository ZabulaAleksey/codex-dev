# Текущее состояние ДЕВ / КАРКАС

Дата: 2026-08-26

## Статус

Completion Documentation Synchronization Gate реализован и validated в изолированной ветке
`chore/documentation-sync-gate`. Стабильный requirement принадлежит `specs/system.spec.md`,
каноническая policy — `rules/governance.md`, исполняемый workflow —
`dev-karkas/references/STATUS_WORKFLOW.md`. Merge в `main` и runtime materialization ещё не
выполнялись.

## Сохраняющееся подтверждённое состояние

- глобальный ДЕВ остаётся в единственном Git root `~/.codex`;
- Backend Developer Experience Policy ранее validated и слита в active `main`;
- product repositories этой задачей не изменялись;
- runtime parity новых Skill sources будет проверена только после merge из active source.

## Подтверждённые инварианты

- перед `DONE` всегда проверяются существующие `README`, `AI_PLAN`, `AI_STATUS`, `ROADMAP`,
  stage tracker и другие документы, отражающие выполненные шаги или состояние;
- audit обязателен, но mutation выполняется только при изменении фактов;
- timestamp-only churn и выдуманное evidence запрещены;
- stale actions, stage pointers, blockers, test results и capability claims должны быть
  устранены или явно классифицированы;
- статус `merged`, `released` или `deployed` соответствует только подтверждённому уровню;
- после merge gate повторяется по фактическому target branch;
- итоговый handoff различает обновлённые и проверенные без изменений документы.

## Verification evidence

- `py -3 -B tools\validate_context.py` — PASS, 197 files;
- полный validator/sync/reconcile/Backend DX/documentation unit suite — PASS, 70 tests;
- `skill-sources\dev-karkas\scripts\validate.ps1` — PASS;
- `quick_validate.py` для `skill-sources/dev-karkas` и
  `skill-sources/implement-stage` через штатный `python` — PASS;
- `git diff --check` и conflict-marker scan — PASS.

## Синхронизация документации

- Обновлены: root и `skill-sources/dev-karkas/README.md`, `docs/AI_PLAN.md`,
  `docs/AI_STATUS.md`, `docs/ROADMAP.md`, `specs/system.spec.md`, `rules/governance.md`,
  `docs/DECISIONS.md`,
  `docs/CONTEXT_COMPATIBILITY.md`, `docs/PROJECT_FRAMEWORK.md`, `docs/WORKFLOW.md`,
  `docs/TESTING.md`, `docs/LEARNING_LOG.md`, Skills, templates, validator inventory и
  contract tests.
- Проверены без изменений: `docs/ARCHITECTURE.md`, `docs/DESIGN.md`,
  `docs/SECURITY.md`; их предметные факты не изменились.
- Не применяются / отсутствуют: `prompts/STAGES.md`, `docs/TRACEABILITY.md`,
  `CHANGELOG.md`, `docs/DEV_LOG.md`.

## Ограничения

- До merge active `~/.codex/AGENTS.md` и runtime Skills закономерно отличаются от feature sources;
  это не устраняется преждевременной установкой из неслитой ветки.
- Active `main` global validator остаётся `BLOCKED` прежним
  `unmatched-browser-client-hash`; изменение документационного workflow его не затрагивает.
- Gate проверяет смысл human/agent review и не заявляется как автоматический semantic validator.

## Следующее действие

После явного разрешения слить ветку в `main`, materialize изменённые runtime Skills,
повторить проверки и documentation gate по target branch. `pushed`, `released` и `deployed`
не заявляются.
