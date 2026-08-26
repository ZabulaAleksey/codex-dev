# Текущее состояние ДЕВ / КАРКАС

Дата: 2026-08-26

## Статус

Completion Documentation Synchronization Gate реализован, validated и fast-forward слит
в локальную `main` feature commit `b4d8565`. Стабильный requirement принадлежит
`specs/system.spec.md`, каноническая policy — `rules/governance.md`, исполняемый workflow —
`dev-karkas/references/STATUS_WORKFLOW.md`. Runtime Skills materialized из active source;
push не выполнялся.

## Сохраняющееся подтверждённое состояние

- глобальный ДЕВ остаётся в единственном Git root `~/.codex`;
- Backend Developer Experience Policy ранее validated и слита в active `main`;
- product repositories этой задачей не изменялись;
- runtime parity всех versioned Skill sources подтверждена после merge: 9/9.

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
- `tools\sync_global_skills.py` source/runtime parity — PASS, 9 sources;
- `git diff --check` и conflict-marker scan — PASS.
- target `main` `tools\validate_global_codex.py` — `BLOCKED` только прежним
  `unmatched-browser-client-hash`; documentation/Skill drift отсутствует.

## Синхронизация документации

- Обновлены: root и `skill-sources/dev-karkas/README.md`, `docs/AI_PLAN.md`,
  `docs/AI_STATUS.md`, `docs/ROADMAP.md`, `specs/system.spec.md`, `rules/governance.md`,
  `docs/DECISIONS.md`,
  `docs/CONTEXT_COMPATIBILITY.md`, `docs/PROJECT_FRAMEWORK.md`, `docs/WORKFLOW.md`,
  `docs/TESTING.md`, `docs/LEARNING_LOG.md`, Skills, templates, validator inventory и
  contract tests.
- После merge повторно обновлены `docs/AI_PLAN.md`, `docs/AI_STATUS.md` и merge evidence
  в `docs/LEARNING_LOG.md`.
- На target `main` проверены без дополнительных изменений: root/Skill README,
  `docs/ROADMAP.md`, system SPEC, governance, decisions, compatibility,
  framework/workflow/testing, `docs/ARCHITECTURE.md`, `docs/DESIGN.md` и
  `docs/SECURITY.md`.
- Не применяются / отсутствуют: `prompts/STAGES.md`, `docs/TRACEABILITY.md`,
  `CHANGELOG.md`, `docs/DEV_LOG.md`.

## Ограничения

- Active `main` global validator остаётся `BLOCKED` прежним
  `unmatched-browser-client-hash`; изменение документационного workflow его не затрагивает.
- Gate проверяет смысл human/agent review и не заявляется как автоматический semantic validator.

## Следующее действие

Обязательных действий по этому этапу больше нет. Подтверждённые уровни: `implemented`,
`validated`, `committed`, `merged locally`, `materialized globally`. `pushed`, `released`
и `deployed` не заявляются. Browser hash repair остаётся отдельной maintenance-задачей.
