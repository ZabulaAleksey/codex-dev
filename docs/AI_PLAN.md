# Текущий план ДЕВ / КАРКАС

Статус: Completion Documentation Synchronization Gate fast-forward слит в локальную `main`,
runtime Skills синхронизированы; push не выполнен
Этап: обязательная синхронизация документации при task/stage/merge closeout — завершён
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
7. Feature commit `b4d8565` fast-forward слит в локальную `main`.
8. Runtime Skills `dev-karkas` и `implement-stage` materialized из active `main`;
   source/runtime parity — PASS, 9 sources.

## Проверки

- `py -3 -B tools\validate_context.py` — PASS, 197 files;
- полный validator/sync/reconcile/Backend DX/documentation unit suite — PASS, 70 tests;
- `skill-sources\dev-karkas\scripts\validate.ps1` — PASS;
- `quick_validate.py` для `dev-karkas` и `implement-stage` через штатный `python` — PASS;
- `git diff --check` и conflict-marker scan — PASS;
- target `main` source/runtime parity — PASS, 9 sources;
- target `main` `validate_global_codex.py` — `BLOCKED` только прежним
  `unmatched-browser-client-hash`; documentation/Skill drift отсутствует.

## Documentation audit

- Обновлены: root и `dev-karkas` README, `AI_PLAN`, `AI_STATUS`, `ROADMAP`, system SPEC,
  governance, decisions, compatibility, framework/workflow/testing, learning log, Skills,
  AI templates, validator inventory и contract tests.
- После merge повторно обновлены `AI_PLAN`, `AI_STATUS` и merge evidence в learning log.
- На target `main` проверены без дополнительных изменений: root/Skill README, `ROADMAP`,
  system SPEC, governance, decisions, compatibility, framework/workflow/testing,
  `ARCHITECTURE.md`, `DESIGN.md` и `SECURITY.md`.
- Не используются этим repository: `prompts/STAGES.md`, `TRACEABILITY.md`, `CHANGELOG.md`,
  `DEV_LOG.md`; параллельные placeholders не создавались.

## Следующее действие

Обязательных действий по Completion Documentation Synchronization Gate больше нет.
Следующая возможная задача — отдельный repair `unmatched-browser-client-hash` runtime Browser.
