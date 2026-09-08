# Спецификация Backend Developer Experience Policy

Статус: APPROVED
Версия: 1.0
Дата: 2026-08-25
Стабильный идентификатор: `AI-DEV-TEAM-BACKEND-DX-POLICY`

## 1. Назначение

Встроить в глобальный ДЕВ один адаптивный контракт Backend DX, который делает
backend-разработку воспроизводимой, диагностируемой, безопасной и проверяемой
одинаковыми семантическими gates локально и в CI.

## 2. Область

- canonical Backend DX Policy и её routing;
- applicability model `BDX-L0..L3`;
- project-specific Backend DX delta в КАРКАСЕ;
- procedural audit/implementation Skill;
- обязанности существующих backend/database/test/review/security/devops agents;
- read-only project-overlay validation с нейтральными fixtures;
- evidence, traceability, clean-room acceptance и documentation lifecycle.

## 3. Вне области

- массовое изменение product repositories;
- добавление package manager, task runner, ORM, migration/test framework,
  container orchestration или observability stack;
- физический clean-room запуск реального пользовательского backend;
- production access, deployment, миграции данных и destructive resource actions;
- новый hook/validator framework или отдельная devops/platform role.

## 4. Функциональные требования

### FR-001 Один канонический контракт

Полная нормативная Backend DX Policy хранится в одном global rules-файле.
Глобальный `AGENTS.md`, framework docs и Skills содержат только routing,
project-specific delta либо procedural workflow и не копируют policy целиком.

### FR-002 Адаптивная применимость

Policy определяет уровни `BDX-L0` (backend отсутствует), `BDX-L1` (basic),
`BDX-L2` (stateful/integrated) и `BDX-L3` (distributed/production-critical).
Требования и gates применяются только по фактической поверхности проекта;
Docker, OpenAPI, БД, queues и tracing не требуются без соответствующего use case.

### FR-003 Нормативный Backend DX contract

Policy определяет semantic command contract и применимые требования к bootstrap,
toolchain/dependencies, config profiles, local service lifecycle, API, database,
test data, test tiers/isolation, diagnostics, logs/metrics/traces, workers/queues,
external providers, hot reload, debugging/profiling, CI parity, cross-platform,
monorepo и onboarding documentation.

### FR-004 Project overlay и КАРКАС

Backend-enabled project хранит только собственную delta: applicability level,
support matrix, working root, toolchain/lockfile, command map, config/services,
API/DB/test/logs/workers/providers, clean-room smoke, gates, limitations и явные
deviations. `BDX-L0` не создаёт пустой раздел. Каноническое место project facts —
`docs/project-context.md`; project `AGENTS.md` только маршрутизирует к нему.

### FR-005 Skill и роли

Versioned `backend-dx-audit` Skill выполняет discovery, classification, baseline,
gap matrix, minimal change plan, implementation через existing tooling,
clean-room validation, evidence, documentation impact и handoff. Existing agents
получают узкие Backend DX обязанности без создания дублирующих ролей.

### FR-006 Read-only automation

Существующий project-overlay validator проверяет явно объявленную `BDX-L1..L3`
delta, обязательные поля/commands, policy routing, conservative secret patterns в
`.env.example`, guard destructive reset и generated-contract drift declaration.
Он не пытается эвристически объявить любой Python/Node project backend-проектом и
не изменяет target repository.

### FR-007 Gates, IDs и evidence

Policy определяет stable material IDs `BDX-*`, gates `BDX-GATE-01..12`, статусы
`PASS | FAIL | BLOCKED | N/A` с обязательной причиной для `N/A` и traceability
`requirement → delta → command/implementation → evidence → docs/status`.
Существенный backend имеет clean-room scenario; интеграция ДЕВ подтверждается
нейтральным automated fixture test.

### FR-008 Source/runtime Skill parity

Skill создаётся в `skill-sources/` и материализуется в `~/.agents/skills` только
штатным `tools/sync_global_skills.py` с hash parity и recoverable backup behavior.

## 5. Нефункциональные требования

### NFR-001 Безопасность данных и секретов

Production access и destructive DB/resource operations deny-by-default. Config,
logs, diagnostics, docs и fixtures не раскрывают secrets или private data; local
и test profiles не могут молча использовать production targets.

### NFR-002 Совместимость и простота

Existing manager/task runner/test runner/ORM/migration/orchestration mechanisms
переиспользуются. Stable commands сохраняются; новый тяжёлый stack не добавляется
ради соответствия checklist.

### NFR-003 Переносимость

Policy и automation используют portable paths от `~`, учитывают PowerShell/Windows,
не предполагают Bash/Make и не содержат machine-specific project facts.

### NFR-004 Детерминизм и false positives

Validators возвращают стабильный sorted result, работают read-only и применяют
Backend DX checks только к явной delta. High-confidence security checks должны
иметь positive и negative fixtures.

## 6. Безопасность и fallback

- Canonical security invariants остаются в `docs/SECURITY.md`,
  `rules/governance.md` и dev-karkas `SECURITY_BASELINE.md`.
- Canonical retry/degraded behavior остаётся в `rules/fallback-policy.md`.
- Schema/integrity/auth failures fail closed; mock/sandbox не считается real
  provider evidence; partial side effect требует reconciliation до retry.

## 7. Критерии приёмки

- AC-001 Один `rules/backend-dx.md` содержит complete policy, levels, anti-patterns,
  IDs, gates, delta/evidence и clean-room contract.
- AC-002 Global routers ссылаются на реальный policy/Skill без копирования policy.
- AC-003 `backend-dx-audit` проходит Skill validation и source/runtime parity.
- AC-004 Existing six roles содержат bounded Backend DX responsibilities.
- AC-005 КАРКАС и reusable template фиксируют только project delta и пропускают L0.
- AC-006 Project validator принимает полный neutral BDX fixture и диагностирует
  missing fields, unsafe reset, high-confidence secret и missing drift command.
- AC-007 Existing unit/context/global validators не ослаблены; новые failures
  отделены от pre-existing runtime issues.
- AC-008 Architecture, decisions, testing, commands, STAGES execution state, manifest и
  learning evidence синхронизированы с фактическими результатами.
- AC-009 Product repositories, hooks, dependencies и production systems не изменены.
- AC-010 `git diff --check` и итоговый review не находят blocking defects.

## 8. Связь с тестами

| Требование | Evidence |
|---|---|
| FR-006, NFR-004 | `tools.test_validate_project_overlay` |
| FR-008 | `tools.test_sync_global_skills`, `tools/sync_global_skills.py` |
| FR-001, AC-008 | `tools/validate_context.py`, `tools.test_validate_global_codex` |
| FR-004, FR-007 | neutral Backend DX fixture tests + policy/Skill structural checks |

## 9. Открытые вопросы

Нет. Product-specific command names, ports, profiles and providers определяются
отдельно в project delta при применении policy.

## 10. История изменений

- 2026-08-25 — требования предоставленного implementation prompt зафиксированы
  как APPROVED feature contract до реализации.
