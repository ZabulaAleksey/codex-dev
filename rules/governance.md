# Global DEV governance policy

Этот документ — канонический общий контракт для структуры контекста, project lifecycle и evidence. Project `AGENTS.md` хранит только подтверждённую delta.

## Source of truth и независимость

1. Фактическое состояние определяют repository, текущий worktree/branch и результаты проверок.
2. Утверждённая SPEC/ADR определяет требуемый контракт; статусные документы не могут переопределять код или evidence.
3. Notion, Airtable, Eraser, Figma, презентации и чаты — derived projections, а не repository truth.
4. Product repository располагается непосредственно в `~/codex-workspace/<project>` и не зависит от абсолютного пути. Scripts определяют root через Git или эквивалентный безопасный механизм.
5. Critical context должен восстанавливаться после clone/pull без старого чата и machine-local файлов.

## Context inheritance

```text
~/.codex/AGENTS.md
→ <repo>/AGENTS.md
→ optional subtree AGENTS.override.md
→ prompts/STAGES.md для выбранного stage
```

- Project `AGENTS.md` не копирует global Git/testing/security/fallback/tool policy.
- Project custom agents находятся в `<repo>/.codex/agents`.
- Project Skills находятся в `<repo>/.agents/skills` только при доказанном project-specific gap.
- Global agent TOML находится в `~/.codex/agents`; versioned Skill sources — в `~/.codex/skill-sources`, runtime Skills — в `~/.agents/skills`.

## Project state и документы

Для активного product repository, подключённого как полный staged ДЕВ overlay, обязательны содержательные:

- `AGENTS.md`;
- `prompts/STAGES.md`;
- `docs/AI_PLAN.md`;
- `docs/AI_STATUS.md`;
- `docs/ROADMAP.md`;
- `docs/ARCHITECTURE.md`;
- `docs/DECISIONS.md`;
- `docs/LEARNING_LOG.md`;
- `docs/project-context.md`.

Не создавай пустой placeholder. Для UI добавляй `DESIGN.md`, для security surface — `SECURITY.md`, для behavior traceability — `TRACEABILITY.md`, для отдельного test contract — `TESTING.md`.

Одноразовая утилита, vendor/upstream tree, архив или repository, который явно не подключён как
полный staged overlay, не получает этот набор механически. Классификация должна быть явной;
`validate_project_overlay.py` проверяет именно полный project overlay.

В brownfield временный legacy-путь архитектуры или ADR допустим только после canonical mapping
в `docs/CONTEXT_COMPATIBILITY.md`, semantic/link audit и подтверждения одного source of truth.
Целевой канон полного overlay — `docs/ARCHITECTURE.md` и `docs/DECISIONS.md`; параллельные
документы той же роли запрещены.

### Markdown layout

- Сначала дополняй существующий canonical document; новый файл не должен создавать вторую роль или второй source of truth.
- Непосредственно в `docs/` создаются только обязательное ядро и условные канонические контракты КАРКАСА: `DESIGN.md`, `SECURITY.md`, `TESTING.md`, `TRACEABILITY.md`, `DEPENDENCIES.md`, `API.md`, `DATA_MODEL.md`, `PRIVACY.md` и `FALLBACKS.md` при наличии соответствующей поверхности.
- Любой новый долговечный `.md`, не входящий в canonical set, размещается в `docs/notes/<topic>.md` и связывается ссылкой с ближайшим каноническим документом, если влияет на работу.
- Произвольные новые `.md` в корне repository и непосредственно в `docs/` запрещены. Временный scratch/audit output не коммитится.
- Политика действует на новые файлы; legacy layout меняется только после semantic content audit, проверки ссылок и сохранения уникального содержания.

- `AI_PLAN` описывает текущий/следующий исполнимый срез.
- `AI_STATUS` содержит только подтверждённые факты и evidence.
- `ROADMAP` — короткий индекс этапов, не копия prompts.
- `DECISIONS` хранит permanent decisions/ADR; `LEARNING_LOG` — диагностику, root cause, fix и regression prevention.
- Для одной роли существует один canonical документ; legacy объединяется только после проверки уникального содержания и ссылок.

## Stage contract

`prompts/STAGES.md` — единственный detailed stage source полного project overlay. Stable stage
включает status, goal, context, scope, out-of-scope, invariants, tasks, contracts,
documentation/security/performance/fallback/migration impact, DoD и handoff, а также
обязательный контракт архитектурной завершённости ниже.

### Архитектурно завершённый этап

До начала работы для каждого stage зафиксируй:

1. dependency DAG с устойчивыми stage IDs; каждая stage-зависимость указывает только на уже
   `completed`/`verified` prerequisite, self-reference, cycle и forward dependency запрещены;
2. обязательные входные предпосылки и evidence их доступности на старте;
3. самостоятельный runnable vertical slice с конкретной точкой входа и ожидаемым результатом;
4. конкретный end-to-end сценарий от входа пользователя/consumer до наблюдаемого результата;
5. PASS-критерии и команды/checks, которые однозначно отличают PASS от FAIL;
6. требуемое evidence: command/check, result, scope, environment/commit и существенные caveats;
7. допустимые временные реализации с явными границами; они обязаны полностью обслуживать
   заявленный текущий slice без будущего компонента;
8. функциональность, явно вынесенную в будущие stages и не требуемую текущим acceptance contract.

Для internal/docs/policy stage end-to-end означает ближайший реально исполнимый consumer path,
например `input artifact → router/template/validator → observable result`. Для user-facing stage
нужен живой путь `client → API/CLI → backend` либо эквивалентный product path. Если такой путь
невозможен из-за отсутствующей будущей инфраструктуры, stage не закрывается; используй
`blocked`/`BLOCKED_BY_BACKEND`, а не `N/A` или имитацию успеха.

Future stages могут расширять работающий slice, оптимизировать его, добавлять providers/scenarios
или заменять временную, но полностью рабочую реализацию. Они не могут задним числом:

- разблокировать основной путь предыдущего stage;
- предоставить отсутствующую обязательную инфраструктуру;
- превратить stub/mock/scaffold в реальную реализацию;
- впервые сделать возможной проверку функциональности, ранее объявленной завершённой.

Разделяй две оси состояния:

- lifecycle: `planned`, `in_progress`, `blocked`, `scaffolded`, `partial`,
  `implemented_unverified`, `completed`;
- evidence/integration: `implemented locally`, `validated locally`, `committed`, `pushed`,
  `PR opened`, `merged`, `released/deployed`.

`verified` и `DONE` являются terminal completion claims и подчиняются тем же условиям, что
`completed`. Если slice зависит от будущего компонента, E2E/PASS evidence отсутствует или путь
подтверждён только mocks/stubs/fakes/interfaces, допустимы только `blocked`, `scaffolded`,
`implemented_unverified` или `partial`. Scaffold evidence не подтверждает пользовательский или
production path.

Stage не становится `completed`, `verified` или `DONE`, пока выполнены не все обязательные gates,
не пройден Completion Documentation Synchronization Gate и не просмотрен Git diff. Заблокированный
gate допустим только для явно deferred/out-of-scope follow-up; блокировка prerequisite, primary
vertical slice, обязательной инфраструктуры, PASS-критерия или end-to-end проверки всегда
оставляет stage в нетерминальном статусе.

## Completion Documentation Synchronization Gate

Перед объявлением задачи или этапа завершённым и после разрешённого merge всегда проводи
аудит существующих документов, которые отражают возможности, выполненные шаги, текущее
состояние, evidence и дальнейший план.

Обязательный минимум проверки:

- `README.md`;
- `docs/AI_PLAN.md`, `docs/AI_STATUS.md`, `docs/ROADMAP.md`;
- `prompts/STAGES.md`; во время согласованной brownfield migration также mapped legacy tracker;
- `docs/TRACEABILITY.md`, `CHANGELOG.md` и `docs/DEV_LOG.md`, если проект их использует;
- затронутые SPEC, `ARCHITECTURE.md`, `DECISIONS.md`, `DESIGN.md`, `SECURITY.md`,
  `TESTING.md`, `API.md`, `DATA_MODEL.md`, `DEPENDENCIES.md` и `FALLBACKS.md`.

Проверка обязательна, но mutation условна: меняй только документы, факты в которых действительно
изменились. Не создавай timestamp-only churn и не переписывай точный документ ради отметки о
проверке. В handoff или final report укажи, какие источники обновлены, а какие проверены и остались
актуальными.

Во время аудита устрани или явно классифицируй:

- выполненные действия, всё ещё записанные как текущие или будущие;
- устаревшие stage ranges, указатели следующего этапа и статусы `in progress`;
- разрешённые blockers и ограничения, которые больше не действуют;
- старые test counts, команды и verification evidence;
- заявления `merged`, `released` или `deployed`, не подтверждённые target branch или внешним evidence;
- пользовательские возможности, команды запуска и ограничения README, которым уже противоречит код.

После merge повтори аудит по фактическому состоянию target branch. Предварительная синхронизация
feature branch не доказывает, что merge-level status и следующий шаг отражены корректно.

## Contract-first и testing

```text
requirement → behavior/domain contract → API/data/component contract
→ implementation → test evidence → docs/status
```

- Mandatory behavior без evidence помечается `UNVERIFIED`.
- Unit проверяет pure logic; integration — реальные границы storage/API/provider; component — rendering/actions/states/accessibility; product E2E — критические живые пути. Каждый stage дополнительно подтверждает один concrete end-to-end consumer path по Stage contract; для internal/docs/policy stage это может быть исполнимый structural consumer path.
- Accepted tests, fixtures и goldens нельзя ослаблять ради green. Contract change требует утверждённой SPEC/ADR до изменения теста.
- Для нетривиального component определи inputs, outputs, state, side effects, loading/empty/error/disabled/permission/accessibility и recovery behavior.

## Data, database и migrations

```text
domain requirement → data contract → canonical schema/model
→ migration → repository/query → integration evidence
```

Фиксируй keys, nullability, constraints, relations, indexes, timestamps/timezone, numeric precision, ownership, provenance и retention. Schema change без migration допустим только в явно disposable prototype. Destructive production operations deny-by-default и требуют backup/restore plan и отдельного approval.

## Security, fallback и observability

- Недоверенные вводы валидируются по schema, size/count/depth/path/content-type limits.
- AuthN не заменяет AuthZ; secrets не попадают в Git/logs/docs/tests.
- Critical security, money, permissions, cryptography, schema integrity и destructive paths fail closed.
- Fallback явно определяет primary, failure signal, degraded/unavailable behavior, telemetry и recovery; silent fallback/data loss/mock-as-real запрещены.
- Долгие операции имеют operation ID, state/progress, structured error, timeout, cancellation/retry и recovery без private-content logging.

## Tools, dependencies и performance

- MCP/hook/subagent/Skill добавляется только после доказанного gap, с минимальными permissions и bounded failure behavior.
- Hooks deterministic, non-destructive и repository-relative.
- Не добавляй dependency без проверки existing alternatives, maintenance, license, security, platform/runtime и lockfile impact.
- Выбор manager, manifest/lockfile, штатного shared cache/store, clean restore и
  documented exception регулирует [`dependency-management.md`](dependency-management.md).
  Не коммить dependency trees или rebuildable caches без stack-specific contract.
- Backend/runtime project классифицирует developer workflow по
  [`backend-dx.md`](backend-dx.md). `BDX-L1..L3` хранит только project delta в
  `docs/project-context.md`; `BDX-L0` не создаёт пустой section.
- Performance change требует baseline → profile → targeted optimization → correctness parity → benchmark → regression guard.
- Model routing и global reusable agents не дублируются в project overlays.

## Evidence и external projections

Используй только уровни, подтверждённые фактом: `implemented locally`, `validated locally`, `committed`, `pushed`, `PR opened`, `merged`, `released`. Для каждого gate фиксируй command/check, result, scope, commit/environment и caveat. Не запущенное обозначается `NOT RUN`, недоступное — `BLOCKED / NOT VERIFIED`.

External projection синхронизируется из Git. Недоступность внешнего сервиса создаёт pending sync, но не меняет repository truth и не откатывает корректную локальную реализацию.

## Context integrity validator

Текущий read-only `validate_project_overlay.py` выявляет отсутствующие canonical docs, alternate
status, отдельные stage files, stale/machine-specific paths, exact global duplicates,
automation compatibility gaps, dependency drift и явно объявленный Backend DX contract. Он не
исправляет repository автоматически.

Broken relative links, semantic invalid stage references/DAG, references на отсутствующие
capabilities и истинность runtime evidence остаются обязательной human/agent проверкой, пока для
них нет versioned schema и low-false-positive parser. Structural validator не имеет права
объявлять stage архитектурно завершённым.
