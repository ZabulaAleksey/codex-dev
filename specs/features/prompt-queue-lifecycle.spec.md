# Prompt Queue Lifecycle — feature SPEC

Статус: approved requirement из явно запущенного DEV + Current Project DELTA.
Класс: COMPLEX, production governance, SDLC implementation/verification, Python stdlib + existing
Notion adapter. Нормативный owner — `rules/prompt-queue-lifecycle.md`; SPEC задаёт traceability,
а процедуры и guard ссылаются на этот owner без второго lifecycle engine.

## Исходное состояние и scope

До изменения есть governance Stage/Completion Gate, Skill intake/state references, context validators,
opt-in profiler и session hooks. Prompt retention/cleanup guard и queue metadata contract отсутствуют.
Текстовая политика внешней очереди сама по себе не исполняемый guard.
Не менять product implementation, host config/credentials/hooks activation, telemetry schema;
не создавать сервис, scheduler, global queue inventory или новый Skill.

## Requirements / acceptance

| ID | Требование / обязательное evidence |
|---|---|
| PQ-01 | Exact source/backend/queue/revision + execution/authorization evidence; missing/ambiguous/mismatched/unavailable source retains |
| PQ-02 | Eligible one_shot completed + result + required checks + project DoD разрешает только exact-item cleanup |
| PQ-03 | Partial/blocked/needs_continuation/running/queued и unknown retention/type сохраняются |
| PQ-04 | Master/reusable/reference/keep сохраняются даже при completed |
| PQ-05 | Candidate или durable content без verified canonical refs/digests retains; с evidence разрешён |
| PQ-06 | Cleanup requires fresh complete observation + adapter capability; отсутствие capability — cleanup_blocked |
| PQ-07 | Before/after read-back удаляет только exact target, сохраняет всех соседей; mismatch/error — cleanup_blocked |
| PQ-08 | Verified receipt + same source/execution + fresh absence даёт noop; no receipt/restore/changed source не позволяет blind retry |
| PQ-09 | Generic project наследует без копии; additive project checks не могут ослабить global checks |
| PQ-10 | Strict bounded JSON, duplicate keys/malformed/unknown fields fail closed; no command execution or credential access |
| PQ-11 | Current project inherits canonical routing; master partial сохранён; self-test удаляет лишь запущенный one_shot после DoD либо фиксирует cleanup_blocked |
| PQ-12 | Completed auto child/launcher проходит exact-item guard независимо от partial parent; parent master сохраняет собственные status/retention/overall DoD gates |

## Архитектура и безопасность

Read-only guard принимает executor attestation record и свежий adapter observation; output JSON
содержит deterministic reason, fingerprint входного record и exact target. Внешний write выполняет
существующий connector, после нового fetch и guard. Semantic correctness evidence остаётся
responsibility executor/reviewer, поля JSON не делают непроверенное заявление истинным.
CLI ограничивает input size, не загружает network paths и не исполняет evidence strings.
Receipt связывается с exact record fingerprint, source и before/after snapshots. Отсутствие source
без verified receipt не успех. Unknown outcome reconciled до retry. Rollback: восстановить
конкретный archived item штатным backend recovery; локальный code rollback обычным Git revert,
без reset/clean runtime state.

## Verification и rollout

Новые unit/CLI/adapter-receipt tests реализуют PQ-01..10 и hierarchical eligibility PQ-12; current project structural test и реальная
Notion операция/read-back — PQ-11. Tests с fixtures не объявляются real Notion evidence.
Global context/unittest + project validator и targeted project tests обязательны.
Full overlay validator используется как read-only baseline comparison: существующие unrelated
issues фиксируются отдельно; lifecycle delta не должна добавлять новые issues.
Существующие принятые tests не ослабляются. Нет optional product E2E для policy-only delta;
live consumer path — executor → guard CLI → Notion exact-item operation → read-back verifier.
При недоступном adapter local implementation может быть validated locally, live cleanup остаётся
cleanup_blocked; полный self-cleanup не заявляется. Merge/push только по отдельному user request.
