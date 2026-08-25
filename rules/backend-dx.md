# Backend Developer Experience Policy

Стабильный идентификатор: `AI-DEV-TEAM-BACKEND-DX-POLICY`

## Назначение и границы

Эта policy — единый глобальный контракт воспроизводимой, discoverable,
диагностируемой и безопасной разработки backend/runtime services. Она задаёт
семантику developer workflow, а не навязывает конкретный package manager, task
runner, ORM, migration framework, test runner, logger или orchestration stack.

Backend DX владеет связью «project facts → commands → evidence». Предметные
инварианты остаются у своих канонических владельцев:

- `Component Behavior & Test Contract Policy`, Test Protection, requirements,
  evidence и stage completion — test-contract sections в
  [`../AGENTS.md`](../AGENTS.md), [`governance.md`](governance.md) и
  [`../skill-sources/dev-karkas/references/TESTING_POLICY.md`](../skill-sources/dev-karkas/references/TESTING_POLICY.md);
- package manager, lockfile, cache и clean restore —
  [`dependency-management.md`](dependency-management.md);
- API и `Database Contract & Evolution` constraints —
  [`domains/api.md`](domains/api.md), data/database section в
  [`governance.md`](governance.md) и [`domains/database.md`](domains/database.md);
- security — [`../docs/SECURITY.md`](../docs/SECURITY.md) и
  [`domains/security.md`](domains/security.md);
- retry/fallback/degraded behavior — [`fallback-policy.md`](fallback-policy.md);
- procedural project audit — global Skill `backend-dx-audit`.

Project repositories наследуют policy. Они хранят только project-specific
`Backend DX Delta` в `docs/project-context.md` и короткий route в `AGENTS.md`.

## Инварианты

1. Clean checkout восстанавливается без старого чата, личной памяти и скрытых
   machine-local steps.
2. Existing stable tooling переиспользуется. Второй task runner, package manager,
   ORM, migration/test framework, logger или orchestrator без доказанного gap
   запрещён.
3. Один discoverable command surface отображает semantic operations на реальные
   команды проекта. Имена существующих стабильных команд не переименовываются ради
   унификации.
4. Local/CI gates используют общую реализацию; различия environment явны.
5. Production credentials/resources и destructive DB/resource actions
   deny-by-default. Reset/drop/truncate/mass-delete требуют local/test guard.
6. Fallback, sandbox, stub, mock и degraded mode всегда видимы; они не выдаются за
   primary/production evidence.
7. Материальное требование имеет command/test/smoke evidence либо честный статус
   `FAIL`, `BLOCKED` или `N/A — причина`.
8. Global layer остаётся project-agnostic: ports, endpoints, credentials, live
   blockers и product-specific IDs принадлежат project delta.
9. Windows/PowerShell — реальная среда. Bash/Make/POSIX-only assumptions должны
   быть либо устранены, либо явно включены в support matrix.
10. Docker, OpenAPI, database, queues, distributed tracing и observability stack
    применяются только при фактической поверхности проекта.

## Уровни применимости

### `BDX-L0 — No backend`

Backend/runtime service отсутствует. `Backend DX Delta` не создаётся. Audit только
подтверждает отсутствие ложных backend dependencies и runtime claims.

### `BDX-L1 — Basic backend`

Один runtime process и минимум инфраструктуры, возможно без persistent database.
Обязательны reproducible install, canonical dev/test/check commands, config
validation, actionable errors, quickstart, basic logs и local/CI parity.

### `BDX-L2 — Stateful/integrated backend`

Есть database, cache, filesystem, provider adapter или несколько runtime
components. Дополнительно применимы migrations, seeds/fixtures, isolated
integration resources, readiness, external-dependency strategy, structured
logs/correlation, reset/recovery и API/contract documentation.

### `BDX-L3 — Distributed/production-critical backend`

Есть workers, queues, schedulers, несколько services, сложный lifecycle либо
повышенные reliability требования. По фактической необходимости добавляются queue
inspection, retry/DLQ/replay safety, distributed tracing, dependency diagnostics,
deploy ordering, profiling, failure injection и расширенный clean-room smoke.

Уровень определяется архитектурой и риском, а не желанием установить технологию.
`BDX-L2/L3` не означает автоматически Docker, OpenAPI, OTel или конкретную БД.

## Stable requirement IDs

Используй ID только для material requirements, которые должны иметь evidence:

```text
BDX-BOOT-001  bootstrap/reproducibility
BDX-CMD-001   command surface
BDX-TOOL-001  toolchain/dependencies
BDX-CFG-001   config profiles and validation
BDX-SVC-001   service lifecycle/readiness
BDX-API-001   API contract/docs
BDX-DB-001    database lifecycle
BDX-TEST-001  test feedback/isolation
BDX-DATA-001  seeds/fixtures/factories
BDX-ERR-001   actionable diagnostics
BDX-OBS-001   logs/metrics/traces
BDX-JOB-001   workers/queues/schedulers
BDX-EXT-001   external providers/sandboxes/fallback
BDX-CI-001    local/CI parity
BDX-DOC-001   onboarding/documentation
BDX-XPLAT-001 cross-platform/monorepo paths
```

Не присваивай ID каждой команде или мелкой рекомендации.

## Семантический command contract

Project delta сопоставляет применимые операции с реальными commands. `N/A`
допустим только с причиной.

| Semantic operation | Минимальная применимость | Contract |
|---|---|---|
| `bootstrap/install` | L1 | deterministic clean install по canonical lockfile |
| `doctor` | L1 | prerequisites, versions, config и dependency diagnostics без secrets |
| `start-dev` / `stop-dev` | L1 | documented root, status и predictable shutdown |
| `check` | L1 | local CI-equivalent gate |
| `format` / `lint` / `typecheck` | по stack | отдельны либо discoverably включены в `check` |
| `test-fast` / `test-unit` | L1 | быстрый deterministic feedback |
| `test-integration` | L2 либо real boundary | isolated real boundary evidence |
| `test-contract` | API/provider contract | drift/compatibility evidence |
| `test-e2e` | live path | только реальный `client → API/CLI → backend` path |
| `build` | buildable runtime | reproducible artifact |
| `api-spec-check` | generated/API contract | canonical schema validation + drift |
| `db-status/migrate/seed/reset-local` | DB project | guarded, target-aware lifecycle |
| `logs` | L1 | local diagnostic access with redaction |
| `clean-local` | local state exists | classified, scoped, recoverable cleanup |

Command names могут отличаться. Один project-owned mechanism — package scripts,
`uv`, Cargo, dotnet, Gradle/Maven, Taskfile/just/Make, PowerShell или существующий
эквивалент — остаётся source of truth. `help` или command catalog должен быть
discoverable из документированного root. Complex pipelines хранятся в versioned
scripts, корректно возвращают exit code и объясняют failure. CI вызывает ту же
реализацию, а не скрытый параллельный pipeline.

## Bootstrap, toolchain и dependencies

- supported runtime/tool versions, manager и lockfile однозначны и проверяемы;
- hidden global dependencies запрещены либо выявляются `doctor`;
- generated files reproducible или обоснованно versioned;
- source code отделён от local data/state/cache;
- bootstrap не использует production credentials;
- prerequisite error называет missing item и безопасный recovery step;
- cache не является source of truth, cleanup не удаляет unknown/user data;
- competing lockfiles требуют documented exception;
- для Python default ДЕВ — `uv + project .venv + shared uv cache`, если upstream
  contract не требует доказанного исключения.

Полный dependency/migration contract не дублируется здесь: следуй
[`dependency-management.md`](dependency-management.md).

## Config и environment profiles

Документируй только реально используемые profiles из `local`, `test`, `ci`,
`staging`, `production`.

- `.env.example` содержит names и безопасные placeholders, не credentials;
- required config валидируется fail-fast; critical unknown/typo keys не молчат;
- precedence и safe defaults документированы;
- secret и non-secret config разделены;
- local/test target не может случайно стать production target;
- test resources изолированы;
- effective config диагностируется только с redaction;
- tokens, passwords, private keys, connection strings и sensitive payloads не
  печатаются в command output, logs, tests или docs.

`doctor/config-check` добавляется только через existing command surface.

## Local services, readiness и lifecycle

Для каждой required dependency project delta отвечает: start, readiness, stop,
status, logs, local cleanup и partial-start recovery.

- используй existing orchestration mechanism;
- health и readiness различай, когда service может быть alive, но не ready;
- startup order не строится только на sleep;
- port collision и missing dependency дают actionable diagnostics;
- service names, ports и volume/data paths принадлежат project config/delta;
- cleanup/reset не затрагивает production;
- stop не оставляет unexplained orphan processes;
- повторный запуск предсказуем, partial startup наблюдаем.

Docker Compose — допустимый вариант, но не универсальное требование.

## API Developer Experience

Для проекта с API:

- canonical request/response/error contract и его owner явны;
- OpenAPI/AsyncAPI/GraphQL schema или реальный эквивалент не создаёт второй
  source of truth;
- auth flow, examples, pagination/filtering/sorting и applicable idempotency
  discoverable;
- request/response validation и stable error model проверяются;
- correlation/request ID используется там, где нужен;
- dev docs endpoint/UI включается только безопасным profile;
- generated clients/types создаются одной командой, не редактируются вручную и
  имеют drift check;
- breaking change проходит compatibility review.

## Database DX

Database guarantees остаются в governance/database contracts. Backend DX делает
discoverable и доказуемыми connectivity, migration status/apply, clean local/test
DB, safe reset, seed, fixtures/factories, previous-schema upgrade, schema mismatch
diagnostics и critical query-plan workflow.

- schema change идёт через canonical migration mechanism;
- DB guarantee подтверждается real integration database, а не только mock;
- reset/drop/truncate/mass delete fail closed вне гарантированного local/test;
- migration command проверяет target environment;
- seed repeatable либо документирует non-idempotence;
- test DB не переиспользует личную development/production DB без изоляции;
- migration failure имеет recovery path;
- lock/backfill/large-table risks не упрощаются ради удобства.

## Tests и test data

Test DX обеспечивает быстрый feedback, отдельные/параметризованные tiers, запуск
одного test/module/suite, deterministic fixtures, isolated DB/cache/filesystem,
cleanup, readable failures и локальное воспроизведение CI.

- accepted tests/fixtures/goldens не ослабляются ради PASS;
- evidence связывается с BDX/API/DB/behavior requirements;
- hidden skip запрещён;
- flaky/quarantine требует owner, reason, expiry/issue или эквивалент;
- order dependence и uncontrolled parallelism устраняются;
- time/randomness фиксируются там, где влияют на repeatability;
- sandbox/stub явно маркируется и не считается real provider evidence.

Термины:

```text
seed              local starting data
fixture           fixed test scenario
factory           programmatic test data
demo data         presentation data
migration fixture previous-schema snapshot for migration tests
```

Production dumps запрещены без approved sanitization. Private data и production
credentials не входят в repository. Для DB project предпочтительна доказуемая
цепочка `reset local/test → migrate → seed/fixtures → tests`.

## Errors, logs и observability

Developer diagnostic отвечает: что сломалось, на каком шаге, какой resource/port/
variable/service затронут, что проверить, какая recovery command безопасна и где
найти logs/correlation ID.

- failure не возвращает success exit code и не проглатывается;
- retry bounded и observable; silent fallback запрещён;
- user-facing error, developer diagnostic, structured log и sensitive detail
  разделяются;
- logs имеют applicable timestamp/timezone, service/process, level, cause chain,
  request/job/correlation ID и redaction;
- local verbosity включается безопасным profile;
- metrics/traces добавляются только для доказанной задачи;
- L3 проверяет propagation, job IDs, dependency spans и retry/queue visibility;
  L1 не обязан иметь distributed tracing.

## Workers, queues, schedulers и external providers

Для applicable jobs workflow фиксирует separate/combined start, graceful shutdown,
health/status, pending/running/failed inspection, retry/DLQ, safe replay,
idempotency, duplicate delivery, ack/visibility semantics, test mode, local broker
and job-correlated logs. Queue не добавляется только ради policy.

Для email/SMS/payment/LLM/trading/storage/third-party API фиксируй primary path,
local path, sandbox/stub/mock, contract test, fallback/degraded behavior,
credentials source, rate limits и failure diagnostics.

- local development не выполняет реальные платежи, рассылки или trading actions;
- provider mode видим в status/logs;
- missing credentials дают explicit status;
- fallback подчиняется [`fallback-policy.md`](fallback-policy.md) и не ослабляет
  security/integrity.

## Hot reload, debugging и profiling

- watcher не создаёт duplicate workers/ports;
- schema/generated changes вызывают rebuild либо явный manual step;
- restart loops и optional-service waits диагностируются;
- fast path не обходит validation/security/contracts;
- debug mode, debugger attach, single service/worker, request/job reproduction,
  safe verbose logs, query diagnostics, CPU/memory profile и cleanup artifacts
  документируются только по применимости;
- unsafe debug endpoint не включается в production;
- startup/performance оптимизируются после измерения bottleneck.

## CI parity, cross-platform и monorepo

- local `check` эквивалентен CI semantic gate;
- runtime/manager/lockfile и generated/drift checks согласованы;
- environment differences явны, cache не скрывает missing artifacts;
- команды README указывают shell и корректно обрабатывают spaces;
- scripts resolve path от Git/project root, не hardcode machine paths, `/tmp`,
  `/usr/local` или POSIX-only syntax без abstraction;
- WSL/Linux-only support допустим только как честная documented support matrix;
- line endings/executable bits учитываются без поломки CI/Linux;
- monorepo определяет workspace root/service root, filtering и build order;
- root commands маршрутизируют, а не копируют service logic; shared contracts и
  affected tests проверяются; competing lockfiles/ports требуют решения.

## Documentation contract

README — human entrypoint, не копия policy. Для applicable backend discoverable:
purpose, prerequisites, quickstart, config, dependencies, migrations/seed,
tests/checks, API docs, logs, stop/cleanup и links на architecture/contracts/
testing/security. Commands проверяются automated fixture/smoke либо помечаются
manual с owner/reason.

## Project Backend DX Delta

Для `BDX-L1..L3` заполни
[`../templates/BACKEND_DX_DELTA_TEMPLATE.md`](../templates/BACKEND_DX_DELTA_TEMPLATE.md)
в project `docs/project-context.md`. Project `AGENTS.md` содержит только короткий
route к delta и этой policy. Для `BDX-L0` раздел не создаётся.

Матрица evidence для material requirements:

| Field | Значение |
|---|---|
| BDX ID | stable material requirement |
| Requirement | проверяемое требование |
| Applicability level | L1/L2/L3 |
| Project command/file | canonical implementation |
| Automated evidence | test/validator/smoke |
| Manual evidence | только если automation непропорциональна |
| Owner/agent | responsibility |
| Status | `PASS`, `FAIL`, `BLOCKED`, `N/A` |
| Reason for N/A | обязательно для `N/A` |
| Known limitation | residual risk |

Traceability:

```text
Backend DX requirement
→ project delta/contract
→ implementation or command
→ validator/test/smoke evidence
→ documentation
→ AI_STATUS / Definition of Done
```

## Quality gates

Каждый gate имеет один статус: `PASS`, `FAIL`, `BLOCKED`, `N/A — причина`.

1. `BDX-GATE-01 Context integrity` — instructions/canon найдены, duplicate policy и
   product contamination отсутствуют.
2. `BDX-GATE-02 Command discoverability` — catalog/root/help/exit codes доказаны.
3. `BDX-GATE-03 Clean bootstrap` — restore/toolchain/prerequisites доказаны.
4. `BDX-GATE-04 Config safety` — validation, safe `.env.example`, production
   isolation и redaction доказаны.
5. `BDX-GATE-05 Service readiness` — start/readiness/stop/partial recovery доказаны.
6. `BDX-GATE-06 API contract` — для API canonical schema, validation, drift,
   examples/auth/errors доказаны.
7. `BDX-GATE-07 Database lifecycle` — для DB status/migrate/seed/reset/test DB,
   guards и schema diagnostics доказаны.
8. `BDX-GATE-08 Test feedback` — fast/full tiers, isolation, CI reproduction и
   unchanged accepted tests доказаны.
9. `BDX-GATE-09 Diagnostics and observability` — actionable errors, logs,
   redaction/correlation и visible provider/fallback mode доказаны.
10. `BDX-GATE-10 CI parity` — implementation, versions, lockfile и drift checks
    совпадают локально/CI.
11. `BDX-GATE-11 Documentation impact` — commands/links/status актуальны.
12. `BDX-GATE-12 No overengineering` — applicability обоснована, лишний framework
    или technology отсутствуют, delta минимальна.

## Clean-room acceptance

Для существенного backend семантический scenario:

1. clean checkout;
2. prerequisites/toolchain check;
3. canonical bootstrap;
4. local config только из documented template;
5. start required local services;
6. readiness/doctor;
7. migrations;
8. minimal seed при необходимости;
9. backend/worker start;
10. smoke/API health;
11. local CI-equivalent check;
12. stop services;
13. safe local cleanup;
14. повторный start для проверки reproducibility.

Не каждый проект обязан выполнять полный scenario на каждой OS. Невыполненный
шаг получает `BLOCKED`/`N/A` с причиной. Fixture/mock доказывает framework contract,
но не production readiness конкретного backend.

## Anti-patterns и reviewer checklist

```text
Works on my machine
Hidden setup step
Secret from someone's private message
Undocumented global dependency
Competing lockfiles
Two task runners for the same commands
Command works only from an undocumented folder
Stale README command or .env.example
Silent fallback or silent mock/provider mode
Local command differs from CI without reason
Sleep-only readiness or magic port without diagnostics
Unsafe DB/resource reset
Test command touching development/production data
Generated file edited manually or contract without drift check
One slow opaque test command
Flaky test hidden by retries; skip/quarantine without control
Logs without correlation or logs containing secrets
Debug endpoint enabled in production
Docker/observability introduced without a problem to solve
New framework instead of extending the canonical one
README copied from policy
PASS claimed without command/evidence
```

## Non-goals

Policy не стандартизирует product commands, ports, API schema format, ORM,
database, queue, logger, container runtime или telemetry vendor. Она не разрешает
production access/deploy/migration и не заменяет SPEC, architecture, security,
database, testing, fallback или dependency contracts.
