# Global DEV governance policy

## Prompt queue routing

Для execution/cleanup внешнего queue item применяй `rules/prompt-queue-lifecycle.md`.
Queue receipt дополняет существующее task evidence и не заменяет Stage/Completion Gate.

## Continuous Master Execution

После explicit запуска `master_prompt` selected STAGES record может содержать ровно один bounded
versioned `master-execution` JSON block. Это projection существующего Stage contract, а не второй
task/status owner. `tools/master_execution.py` детерминированно валидирует graph/track/checkpoint,
выбирает единственный ready slice, проверяет evidence/stop/context gates и строит low-context
handoff; implementation commands остаются у агента/runtime adapter и не берутся из state.

Цикл: `restore → ready slice → implement → evidence → checkpoint → master state sync → next ready`.
Checkpoint не останавливает continuous execution. Stop обязателен при ambiguous ready set,
canonical conflict, user/product decision, secret/external environment, hard blocker, destructive
или integration write, context overflow, explicit stop либо master completion. Critical dependency
без required real evidence получает узкий VerificationGate и не пропускает downstream.

Continuation того же master/track переиспользует registered worktree. Независимый parallel writer
получает отдельную branch/worktree через guarded create-only Git adapter; occupied path/branch,
dirty/unknown state и overlapping ownership fail closed либо требуют IntegrationCheckpoint.
Read-only task не создаёт isolation. Worktree не удаляется после slice; merge/push/release/cleanup
не выполняются controller-ом и остаются approval-gated finalization operations.

Context scope содержит только required router, current master summary, immediate evidence,
relevant SPEC/ADR, touched subsystem/tests и blockers. Budget overflow означает checkpoint +
durable state + compact launcher/handoff, а не silent truncation. Model/reasoning metadata является
recommendation существующему runtime router и не подменяет выбранную пользователем модель.


Этот документ — канонический общий контракт для структуры контекста, project lifecycle и evidence. Project `AGENTS.md` хранит только подтверждённую delta.

## Source of truth и независимость

1. Фактическое состояние определяют repository, текущий worktree/branch и результаты проверок.
2. Утверждённая SPEC/ADR определяет требуемый контракт; статусные документы не могут переопределять код или evidence.
3. Notion, Airtable, Eraser, Figma, презентации и чаты не переопределяют repository truth. Они
   являются derived projections, кроме узкого внешнего артефакта, которому project mapping явно
   назначил собственную роль и направление синхронизации.
4. Product repository располагается непосредственно в `~/codex-workspace/<project>` и не зависит от абсолютного пути. Scripts определяют root через Git или эквивалентный безопасный механизм.
5. Critical context должен восстанавливаться после clone/pull без старого чата и machine-local файлов.

### Матрица ответственности

| Тип информации | Канонический владелец | Допустимые projections |
|---|---|---|
| Общие правила, agents, hooks, validators и versioned Skills | Git repository `~/.codex`; Skill source — `~/.codex/skill-sources` | `~/.agents/skills` только как hash-verified runtime materialization; docs summaries |
| Product implementation и фактическое поведение | `<project>` Git repository, текущий worktree/branch, production code и migrations | build/release artifacts, GitHub views |
| Требования и acceptance contract | утверждённые `specs/system.spec.md` / `specs/features/*` и согласованные ADR | stage prompts, plans, issues, human summaries |
| Архитектурные границы и решения | `docs/ARCHITECTURE.md` и `docs/DECISIONS.md` | Eraser/другие диаграммы после подтверждённого изменения |
| Stage contracts, текущий selector/plan, lifecycle/evidence, blockers и NEXT | `prompts/STAGES.md` | selected record в session context, `ROADMAP` index, handoff |
| Назначение, setup, запуск и публичный developer workflow | `README.md` | внешняя onboarding-страница |
| Повторно полезная диагностика | `docs/LEARNING_LOG.md` | краткая ссылка/итог в соответствующем STAGES record |
| Сырая идея до approval | назначенный Notion/backlog source | `PROMPT_READY` draft; после approval контракт переносится в repository |
| Операционный реестр | Airtable или другой сервис только при явном project mapping | repository-ссылка/schema; не product requirement |
| UI contract | project `docs/DESIGN.md`, код и явный mapping design artifact | Figma после подтверждённого изменения; Figma не доказывает implementation |

Если две поверхности претендуют на одну роль, зафиксируй `CONFLICT`, выбери владельца по типу
информации и синхронизируй производную поверхность только после проверки фактического состояния.
Наличие текста в чате, Notion, Figma или диаграмме не повышает lifecycle/evidence level.

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

- `prompts/STAGES.md` одновременно описывает current/next slice и подтверждённые lifecycle/evidence;
  отдельные plan/status owners запрещены после migration.
- `ROADMAP` — короткий индекс этапов, не копия prompts.
- `DECISIONS` хранит permanent decisions/ADR; `LEARNING_LOG` — диагностику, root cause, fix и regression prevention.
- Для одной роли существует один canonical документ; legacy объединяется только после проверки уникального содержания и ссылок.

### Brownfield migration к canonical STAGES

1. Запусти read-only reconciliation и normal `tools/master_execution.py <project>`; он сам
   классифицирует canonical/legacy/mixed/conflict/none. `--compatibility` оставь для expanded
   diagnostic report, а не как обязательный скрытый pre-step.
   Compatibility adapter читает только bounded known paths `prompts/STAGES.md`,
   `docs/AI_PLAN.md`, `docs/AI_STATUS.md` и детерминированно классифицирует состояние как
   `canonical | legacy | mixed | conflict | migrated | none`. До разрешения `conflict` mutation
   и запуск product stage запрещены.
2. Семантически объедини в `prompts/STAGES.md` актуальные stages, selector, current/next work,
   lifecycle/evidence, blockers, acceptance/DoD и `NEXT`. При расхождении приоритет имеют
   проверяемое evidence и более свежий подтверждённый факт; adapter не выбирает один из
   конфликтующих legacy facts эвристически, неоднозначность остаётся blocker.
3. До любой записи получи deterministic dry-run plan с exact intended bytes, before/after SHA-256
   всех known state paths и отдельно сохрани его approved `plan_digest`. Explicit materialization
   принимает plan file только вместе с этим digest, под exclusive lock повторно сверяет repository,
   source/target bytes и path boundaries, пишет sibling temp + atomic replace, затем выполняет
   canonical parser/router read-back. Drift даёт zero-write `stale_plan`; publish/read-back failure
   восстанавливает pre-image, а unknown leftover lock требует explicit recovery. Завершённая
   migration хранит versioned `stage-compatibility` manifest в том же selected
   `prompts/STAGES.md` record; manifest projection и same-file selector обязаны совпадать.
4. Обнови router, Skills, hooks, prompts, templates, scripts и documentation, которые читали или
   создавали legacy source. Исторический журнал не превращай в current state.
5. Запусти project validator, relevant tests, reference scan и semantic content audit. Legacy file
   удаляется только после подтверждения отсутствия unique current content и stale links.
6. Reconciliation/validator лишь классифицируют `MERGE`/conflict и fail visibly; они не удаляют и
   не перезаписывают project-owned files автоматически.

Normal router, project validator и SessionStart используют один read-only stage routing result.
Только `pass_canonical` даёт `canonical_valid=true` и `execution_allowed=true`. Migration plan
availability не является canonical PASS; conflict/invalid canonical никогда не fallback-ится на
legacy. Hook остаётся exit-0 advisory host integration, но передаёт `execution_allowed=false` и не
загружает guessed record. Validator/default router возвращают non-zero для migration, conflict и
no-state; argparse/invalid invocation остаётся отдельной usage/error категорией.

## Stage contract

`prompts/STAGES.md` — единственный detailed stage и execution-state source полного project overlay.
Файл содержит ordered execution sequence и ровно один current selector `- Stage ID: <stable-id>`, а stable stage
включает status/evidence, goal, context, scope, out-of-scope, invariants, tasks, contracts,
documentation/security/performance/fallback/migration impact, DoD и handoff, а также
обязательный контракт архитектурной завершённости ниже.

Для ordinary canonical record `Status` и `NEXT` указываются явно. Blockers обязательны для
`blocked`, checkpoint/evidence — для terminal status. Невалидный canonical owner не исправляется
fallback-ом на retained legacy state.

Компактный `Status` использует vocabulary `planned | implemented | verified | partial | blocked |
unavailable` и является projection двух точных осей: `implemented` = production implementation
без terminal verification, `verified` = `completed` с требуемым evidence, `unavailable` =
`blocked` из-за недоступной prerequisite/capability. Lifecycle и evidence level всегда остаются
явными; компактный status не может повысить completion claim.

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

### Optional AI policy profiling

Если project явно включил `rules/ai-policy-profiling.md`, Stage contract дополнительно может
фиксировать `Policy IDs`, `Experiment ID`, `Experiment arm`, task class и telemetry evidence.
Поля optional: отсутствие `.metrics/` не является ошибкой existing overlay. При включённом
experiment baseline/variant сравниваются только для совместимого task class с явным sample-size
caveat.

Profiler автоматически собирает только доступные безопасные facts; missing token/human cost
остаётся `unknown`. Telemetry report не заменяет SPEC, acceptance tests, concrete end-to-end PASS,
review или Completion Documentation Synchronization Gate. Policy thresholds не меняются
автоматически: Observe → Measure → Compare → Recommend предшествуют отдельному human-approved
tuning decision.

## Completion Documentation Synchronization Gate

Перед объявлением задачи или этапа завершённым и после разрешённого merge всегда проводи
аудит существующих документов, которые отражают возможности, выполненные шаги, текущее
состояние, evidence и дальнейший план.

Обязательный минимум проверки:

- `README.md`;
- `prompts/STAGES.md`, `docs/ROADMAP.md`; во время согласованной brownfield migration также mapped legacy tracker;
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

### Триггеры обновления документации

| Событие | Обязательное действие |
|---|---|
| Изменился detailed stage contract, его DAG, scope, PASS criteria, активный slice или порядок текущей работы | обновить единственный `prompts/STAGES.md`; `ROADMAP` менять только при изменении долгосрочного порядка |
| Выполнена работа, изменился progress/evidence, появился blocker или следующий шаг | обновить lifecycle/evidence/blocker/NEXT соответствующего record и current selector в `prompts/STAGES.md` |
| Изменились назначение, setup, запуск, публичный интерфейс или user/developer workflow | обновить `README.md` |
| Принято архитектурное решение | обновить `ARCHITECTURE.md` и/или `DECISIONS.md`; STAGES — только по затронутым execution facts |
| Возникла значимая нетривиальная ошибка с повторно полезным выводом | добавить evidence-backed запись в `LEARNING_LOG.md`; в STAGES оставить краткий blocker и ссылку, если он активен |
| Ошибка исправлена и проверена | дополнить ту же learning entry полями `Verification` и `Prevention`; закрыть blocker в STAGES |
| Выполнен разрешённый merge | повторить documentation gate по target branch; не создавать формальную правку без изменения фактов |
| Изменился общий межпроектный стандарт | обновить его единственного global owner, связанные validators/tests и только затем projections; не копировать policy в проекты |

### Контракт LEARNING_LOG

Новая запись создаётся только для существенного, нетривиального и повторно полезного случая:
диагностической ошибки, неверной архитектурной гипотезы, regression/recovery, сложной миграции или
вывода, который предотвращает повторение проблемы. Обычный успешный task, список commits и
оперативный progress туда не копируются.

Новые entries используют ровно следующие смысловые поля: `Problem`, `Symptom`, `Root cause`,
`Failed attempts`, `Fix`, `Verification`, `Prevention`, `Links`. Если неудачных попыток не было,
пиши `N/A`, не выдумывай их. `Verification` содержит воспроизводимую command/check, result, scope
и caveat. Исторические записи не переписываются задним числом только ради нового формата.

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

Базовое направление: `canonical source → dependent projection`. До write определи владельца,
направление, разрешение, idempotency/read-back и поведение при недоступности. Запись во внешний
сервис не подразумевается обычным documentation update и требует действующей авторизации.

| Сервис | Когда обновлять | Что не делать |
|---|---|---|
| GitHub | только через фактические push/PR/merge/issue/release/CI операции с требуемым approval | не повышать local evidence до pushed/merged без remote evidence |
| Notion | после refinement/approval идеи, изменения межпроектного human context или подготовки human review | не превращать сырую идею в SPEC/DONE и не копировать полный governance |
| Airtable | при изменении явно назначенных operational records/registry и после проверки project mapping | не использовать как скрытый источник requirements/status |
| Eraser | после подтверждённого архитектурного изменения из repository | не обновлять после каждого локального refactor и не делать диаграмму каноном |
| Figma | после подтверждённого изменения UI/design system и сверки `DESIGN.md`/implementation | не считать mockup evidence реализованного интерфейса |
| Другой сервис | только после явного назначения ответственности и направления данных | не добавлять синхронизацию ради самой синхронизации |

Недоступность projection создаёт `pending sync` / `BLOCKED / NOT VERIFIED`, но не меняет
repository truth и не откатывает корректную локальную реализацию. После разрешённой записи нужен
read-back; без него синхронизация остаётся непроверенной.

## Переключение устройств и восстановление

Перед сменой компьютера безопасно останови работу, проверь Git status/diff, выполни применимые
checks и обнови current record/NEXT в `prompts/STAGES.md` только если иначе потеряется существенное состояние. Commit и push
выполняются лишь при явном разрешении и по Git policy; без них незакоммиченный worktree не считается
перенесённым на другое устройство, а handoff получает явный blocker.

На другом устройстве сначала восстанови/обнови Git repository глобального ДЕВ непосредственно в
`~/.codex`, выполни штатные install/validation и Skill parity checks, затем clone/pull нужного
`~/codex-workspace/<project>`. После проверки branch/status восстанови dependencies и локальные
secrets штатными механизмами проекта, прочитай context по `docs/CONTEXT_POLICY.md` и продолжай
только после согласования локального состояния с repository evidence. История чата и ручное
копирование отдельных файлов не являются recovery path.

## Классы monitoring проекта

- `active` — проверки и документация обновляются во время активной разработки;
- `event-driven` — проверки запускаются по push/PR/merge или явной команде;
- `frozen` — автоматический monitoring выключен до явного возобновления.

Класс хранится как project fact в `docs/project-context.md` либо во внешнем project mapping, но не
в global live inventory. Он задаёт частоту проверок, не разрешает внешние writes/deploy и не
заменяет status/evidence. Для `frozen` не расходуй автоматические проверки без явного события;
экспериментальный проект не становится `active` автоматически.

## Context integrity validator

Текущий read-only `validate_project_overlay.py` выявляет отсутствующие canonical docs, alternate
status, отдельные stage files, stale/machine-specific paths, exact global duplicates,
automation compatibility gaps, dependency drift, exact Stage selector/heading reference и явно
объявленный Backend DX contract. Он не исправляет repository автоматически.

Broken relative links, semantic invalid dependency DAG/Stage contract, references на отсутствующие
capabilities и истинность runtime evidence остаются обязательной human/agent проверкой, пока для
них нет versioned schema и low-false-positive parser. Exact selector PASS подтверждает только
однозначную structural ссылку; validator не имеет права объявлять stage архитектурно завершённым.
