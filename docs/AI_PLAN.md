# Текущий план ДЕВ / КАРКАС

Статус: Completion Documentation Synchronization Gate реализован и validated в
`chore/documentation-sync-gate`; merge и runtime materialization не выполнены
Этап: обязательная синхронизация документации при task/stage/merge closeout — готов к интеграции
Дата: 2026-08-26

## Текущий ограниченный срез

Закрепить единый обязательный audit существующих `README`, `AI_PLAN`, `AI_STATUS`,
`ROADMAP`, stage tracker и других state-bearing документов. Проверка выполняется всегда,
mutation — только при изменении подтверждённых фактов; после merge gate повторяется по
target branch.

Связанная SPEC: `specs/system.spec.md`, `FR-006`, `AC-006`.

## Выполнено

1. Requirement и acceptance criterion добавлены в системную SPEC.
2. Канонический gate добавлен в `rules/governance.md` и global `AGENTS.md`.
3. Процедура встроена в `dev-karkas`, `implement-stage`, общий workflow и AI templates.
4. Gate выявляет stale current/future actions, stage pointers, blockers, test evidence,
   README capabilities и неподтверждённые merge/release/deploy claims.
5. README, roadmap, decision, compatibility, framework и learning sources синхронизированы.
6. Добавлен отдельный structural contract test без изменения принятых tests.

## Проверки

- `py -3 -B tools\validate_context.py` — PASS, 197 files;
- полный validator/sync/reconcile/Backend DX/documentation unit suite — PASS, 70 tests;
- `skill-sources\dev-karkas\scripts\validate.ps1` — PASS;
- `quick_validate.py` для `dev-karkas` и `implement-stage` через штатный `python` — PASS;
- `git diff --check` и conflict-marker scan — PASS;
- feature-worktree `validate_global_codex.py` — ожидаемо `BLOCKED` drift трёх ещё не
  materialized sources; active `main` сохраняет только прежний
  `unmatched-browser-client-hash`.

## Documentation audit

- Обновлены: root и `dev-karkas` README, `AI_PLAN`, `AI_STATUS`, `ROADMAP`, system SPEC,
  governance, decisions, compatibility, framework/workflow/testing, learning log, Skills,
  AI templates, validator inventory и contract tests.
- Проверены без изменений: `ARCHITECTURE.md`, `DESIGN.md`, `SECURITY.md`; их
  архитектурные, UI и security-факты этим этапом не изменены.
- Не используются этим repository: `prompts/STAGES.md`, `TRACEABILITY.md`, `CHANGELOG.md`,
  `DEV_LOG.md`; параллельные placeholders не создавались.

## Следующее действие

После явного разрешения пользователя слить `chore/documentation-sync-gate` в `main`,
синхронизировать runtime `dev-karkas` и `implement-stage`, повторить global validator и
Completion Documentation Synchronization Gate по target branch. Browser hash repair остаётся
отдельной maintenance-задачей.
