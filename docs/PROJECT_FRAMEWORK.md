# КАРКАС проекта и автоматизация контекста

Этот документ задаёт общую терминологию для explicit DEV-enabled repositories, разрешённых как
`${PROJECTS_ROOT}/<project>`. Path под `PROJECTS_ROOT` сам по себе не включает этот contract.

## Continuous Master Execution

Крупный approved master не превращается ни в giant diff, ни в ручную очередь микропромптов.
Selected `prompts/STAGES.md` record хранит versioned graph/track/checkpoint state; controller
выбирает единственный dependency-ready backward-complete slice, проверяет evidence/stop/context,
создаёт checkpoint и продолжает автоматически. Continuation reuse-ит worktree, independent writer
получает isolated branch/worktree. Low-context launcher восстанавливается из repository facts;
merge/push/cleanup остаются finalization operations с отдельным разрешением.

После определения live stage capability router читает metadata из
`skill-sources/registry.toml`, а не тела всех Skills. Project overlay может объявлять только
проверенный project/domain delta; он не копирует global procedures и не создаёт второй scheduler,
execution state или automation backlog. Requirement → capability → evidence trace остаётся
привязан к canonical SPEC и selected STAGES record.

## Определения

**КАРКАС проекта** — минимально достаточный living contract, который переводит идею или SPEC в состояние, пригодное для безопасной поэтапной разработки. Он связывает требования, архитектурные границы, решения, план этапов, проверки и текущее состояние.

КАРКАС не равен исходному коду, одному `AGENTS.md`, набору шаблонов или локальной копии AI Dev Team. Он является согласованным project overlay над общей инженерной инфраструктурой.

**АВТОМАТИЗАЦИЯ КОНТЕКСТА** — механизм выбора, доставки, применения и обновления минимально необходимой части КАРКАСА для текущей задачи Codex.

```text
User intent / SPEC
        ↓
Project КАРКАС
        ↓
Task-aware context routing
        ↓
Codex + inherited AI Dev Team
        ↓
Implementation → tests → state update
```

## Состав КАРКАСА

Создавай только артефакты, которые решают подтверждённую задачу проекта.

Обязательное ядро для active product repository, подключённого как полный staged overlay:

- `specs/system.spec.md` и при необходимости `specs/features/*` — стабильные требования и критерии приёмки;
- `AGENTS.md` — тонкий project overlay с локальными инвариантами и маршрутизацией контекста;
- `prompts/STAGES.md` — единственный подробный источник stages и execution state: selector,
  current plan, lifecycle/evidence, blockers и NEXT;
- `docs/ARCHITECTURE.md` — границы, зависимости, интерфейсы и потоки данных;
- `docs/DECISIONS.md` — существенные решения и их последствия;
- `docs/ROADMAP.md` — долгосрочная последовательность этапов;
- `docs/LEARNING_LOG.md` — повторно полезные инженерные выводы без копирования Git history;
- `docs/project-context.md` — устойчивые project facts и применимая Backend DX delta.

По поверхности и риску добавляются `DESIGN.md` для UI, API/data contracts, `SECURITY.md`,
test strategy, integration contracts и другие предметные документы. `DEV_LOG` создаётся только
когда подробная хронология действительно полезна; отсутствие UI не является причиной для
пустого `DESIGN.md`.

`prompts/STAGES.md` не заменяет SPEC или ROADMAP: SPEC определяет стабильные требования,
STAGES — detailed/current execution contract, ROADMAP — долгосрочный порядок.

### Backend DX profile

Во время bootstrap/audit определи, содержит ли project backend/runtime service, и
классифицируй его по `~/.codex/rules/backend-dx.md`:

- `BDX-L0` — backend отсутствует; пустой Backend DX section не создаётся;
- `BDX-L1` — basic backend;
- `BDX-L2` — stateful/integrated backend;
- `BDX-L3` — distributed/production-critical backend.

Для `BDX-L1..L3` заполни только project-specific delta из
`~/.codex/templates/BACKEND_DX_DELTA_TEMPLATE.md` в `docs/project-context.md`.
Project `AGENTS.md` маршрутизирует backend workflow к delta, global policy и Skill
`backend-dx-audit`, но не копирует их. Existing command/tooling stack остаётся
source of truth; applicability не используется как повод добавить Docker, БД,
OpenAPI, queue или tracing.

### Каталог дополнительных Markdown-файлов

До создания нового документа определи его роль. Если содержание относится к существующим SPEC, `ARCHITECTURE.md`, `DECISIONS.md`, `DESIGN.md`, `SECURITY.md`, `TESTING.md`, `prompts/STAGES.md`, `ROADMAP.md` или другому каноническому контракту, обнови этот источник вместо создания параллельного файла.

На верхнем уровне `docs/` остаются только обязательные и условные канонические документы КАРКАСА. Новый долговечный материал без канонической роли — исследовательская заметка, разбор, handoff, audit note или вспомогательное объяснение — размещается в `docs/notes/<topic>.md`. Одноразовый временный материал не входит в repository.

Это forward-only правило: существующие файлы не перемещаются механически. Их объединение или перенос требует semantic audit, проверки ссылок и подтверждения отсутствия потери уникального контента.

## Канонические роли документов

```text
SPEC                 что система обязана делать
DECISIONS            почему принято существенное решение
ARCHITECTURE/API     как соблюдаются границы и контракты
ROADMAP              в каком порядке развивается проект
STAGES               что выполняется сейчас, что подтверждено, blockers и NEXT
implementation/tests фактическое состояние и доказательства
```

При конфликте применяй каскад инструкций из `docs/CONTEXT_POLICY.md`. Не меняй требования или архитектурные границы молча: зафиксируй конфликт, решение и необходимые обновления источников истины.

## Архитектурно завершённые stages

Полный канонический контракт находится в `rules/governance.md`. Каждый stage до реализации
фиксирует DAG только из завершённых prerequisites, входные предпосылки, runnable vertical slice,
конкретный end-to-end сценарий, PASS-критерии/evidence, допустимую полностью рабочую временную
реализацию и deferred scope. `PROMPT_TEMPLATE.md` и `STAGES_TEMPLATE.md` являются операционными
проекциями этого контракта, а не отдельными владельцами требований.

Future stage может расширить или заменить работающий slice, но не может впервые сделать
предыдущий stage исполнимым или проверяемым. Mock/stub/interface-only результат остаётся
`scaffolded`; отсутствие end-to-end PASS evidence оставляет stage `blocked`, `partial` либо
`implemented_unverified`.

## Процесс bootstrap

1. Определи Git-корень, ближайшие инструкции и состояние рабочей копии.
2. Классифицируй repository как `GREENFIELD` или `BROWNFIELD`; в brownfield код и тесты являются source of truth текущего состояния.
3. Для brownfield до mutations выполни read-only reconciliation и сформируй matrix `KEEP` / `ADD` / `ADAPT` / `MERGE` / `CONFLICT` / `SUPERSEDED` / `FORBIDDEN_TO_OVERWRITE`.
4. Сними baseline тестов, отдели pre-existing failures, разреши конфликты и только затем выполняй refresh.
5. Классифицируй сложность, режим, этап SDLC, домен, стек и относящуюся SPEC.
6. Исследуй существующий проект; если КАРКАС уже есть, выполни gap analysis вместо регенерации.
7. Проверь общую AI Dev Team и `docs/CONTEXT_COMPATIBILITY.md`.
8. Для каждого предлагаемого agent, hook, MCP, Skill, config или workflow назначь статус `INHERITED`, `EXTEND`, `PROJECT_ONLY`, `CONFLICT` или `OBSOLETE`.
9. Создай только проектную delta: требования, архитектуру, решения, этапы, проверки и локальные инварианты.
10. Определи dependency ecosystem и зафиксируй canonical manager, manifest,
    lockfile, штатный cache/store, project-local materialization, cleanup, CI clean
    restore и exception rationale по `rules/dependency-management.md`.
11. Классифицируй Backend DX как `BDX-L0..L3`; для `BDX-L1..L3` добавь только delta в `docs/project-context.md`.
12. Настрой task-to-context routing в тонком `AGENTS.md` и stage prompts.
13. Для каждого stage проверь dependency DAG, completed prerequisites, runnable vertical slice,
    конкретный end-to-end сценарий, PASS/evidence, temporary implementation и deferred scope.
14. Проверь согласованность требований, контрактов, критериев приёмки, тестов и context budget.
15. После refresh выполни validator и повтор baseline-тестов; новые failures являются regression.
16. Зафиксируй текущее состояние и следующий этап.
17. Не начинай крупную реализацию продукта, если пользователь запросил только КАРКАС или автоматизацию контекста.

Готовый overlay проверяется без изменений repository:

```powershell
py -3 "$env:CODEX_HOME\tools\validate_project_overlay.py" "$env:PROJECTS_ROOT\<project>"
```

Перед изменением brownfield repository:

```powershell
py -3 "$env:CODEX_HOME\tools\reconcile_project_framework.py" "$env:PROJECTS_ROOT\<project>"
```

Для машинного чтения доступен `--json`; отдельный registry при этом не создаётся.

Default `master_execution.py <project>` и validator автоматически возвращают typed
canonical/legacy/mixed/conflict/no-state projection. Для rollout используй один повторяемый цикл:
discover → classify → report → safe plan if possible → explicit approval/materialization →
canonical validation → separately approved legacy retirement. Mass rollout и automatic legacy
deletion отсутствуют.

## Автоматизация контекста

Базовая формула:

```text
Context =
nearest instructions
+ selected mode/SDLC/domain/stack rules
+ affected SPEC requirements
+ selected record from prompts/STAGES.md when stage-bound
+ relevant architecture/decisions/security
+ target files/tests/diff
+ current/selected STAGES record
```

Не загружай автоматически все stages, roadmap, fixtures, logs и общую библиотеку. Для stage-bound
задачи укажи stable `Stage ID` в `prompts/STAGES.md` и загружай только exact unique heading record
из этого же файла. Degraded-warning selector требует ручного чтения полного record и запрещает
completion claim до проверки. Остальная маршрутизация должна быть
предметной: например изменение публичного API подтягивает API-контракт, compatibility decision и
contract tests, а изменение хранения — data model, security/retention rules и migration plan.

После этапа всегда проверяй `README.md`, `prompts/STAGES.md`, `ROADMAP` и
другие state-bearing документы по Completion Documentation Synchronization Gate из
`rules/governance.md`. Обновляй только документы, чья фактическая информация изменилась;
для остальных достаточно подтверждения `checked, still accurate` без timestamp-only churn.
После merge повторяй gate по target branch. Merge остаётся контрольной точкой синхронизации,
но не заменяет review и явное разрешение пользователя.

## Закон отсутствия дубликатов

Проект с valid `.codex/dev-project.toml` наследует общие agents, Skills, hooks, Git workflow,
review и quality practices. Exact `Global DEV bridge: enabled` в project-local `AGENTS.md` —
обязательная human-readable declaration полного overlay, но не machine-readable membership.
Repository без structured marker остаётся обычным независимым repository. Локальное расширение
допустимо только при подтверждённом пробеле и должно иметь узкую область, владельца, способ
проверки и безопасный fallback.

Отсутствие локального config, hook, MCP, Skill или subagent является нормальным результатом bootstrap.

Общая Fallback Policy наследуется из
`~/.codex/rules/fallback-policy.md`.

Если проект имеет собственные предметные цепочки деградации,
он хранит только project-specific delta в `docs/FALLBACKS.md`.

`AGENTS.md`, `SECURITY.md`, `ARCHITECTURE.md`, `DECISIONS.md` и SPEC
не должны становиться конкурирующими полными источниками fallback-правил:
они содержат только свои инварианты, решения и ссылки на канонический каталог.

## AI Policy Profiling (optional)

КАРКАС может включить project-local AI Policy Profiling для дорогих cross-task policies,
agent/retrieval/reuse contours, experiments и human handoffs. Global owner —
`rules/ai-policy-profiling.md`; runtime data остаётся ignored в `<project>/.metrics/` и не становится
каноническим status/requirements source.

Profiling включается явно, начинает с Observe и добавляет к Stage только optional Policy IDs,
Experiment ID/arm, task class и telemetry evidence. Existing project без `.metrics/` остаётся
полным валидным overlay. Report не заменяет tests/E2E/DoD, а automatic threshold tuning запрещён
до отдельного human-approved решения.

## i18n / l10n пользовательских продуктов

Каждый проект с пользовательской поверхностью наследует глобальную
[`Internationalization / Localization Policy`](../rules/i18n-l10n.md). КАРКАС проверяет её
применимость при bootstrap, архитектурном изменении и добавлении пользовательской поверхности.
Non-user-facing repository может зафиксировать обоснованное `N/A`, которое пересматривается при
изменении границы продукта.

Project `SPEC` и `DESIGN.md` не копируют глобальный стандарт. Они уточняют поддерживаемые
`language` / `locale`, fallback locale, locale-dependent product rules, UX, RTL, выбранную
реализацию, исключения и acceptance evidence. Начальный stage может иметь одну production locale,
но реальная resource/fallback infrastructure и pseudo-locale либо alternate test locale должны
доказывать расширяемость уже в этом самостоятельном slice; будущий stage добавляет переводы, а не
впервые разблокирует i18n.

Язык project context — отдельная настройка документации и не является product locale.

## Язык проектного контекста

По умолчанию человекочитаемый проектный контекст создаётся и поддерживается на русском языке. Это относится к `AGENTS.md`, SPEC, архитектуре, решениям, безопасности, тестовой стратегии, roadmap, `prompts/STAGES.md` и инструкциям проектных agents/Skills.

Не переводятся программные идентификаторы, публичные API и wire-контракты, команды, пути, имена файлов, названия технологий и машинные ключи конфигурации. Другой основной язык допустим по прямому указанию пользователя либо когда его требует внешний стандарт, аудитория или контракт проекта.

## Критерии готовности

КАРКАС готов, когда:

- требования имеют один канонический источник и проверяемые критерии;
- архитектурные границы и существенные решения явны;
- этапы архитектурно завершены: каждый имеет completed prerequisites, runnable vertical slice,
  end-to-end PASS evidence и не зависит от будущего stage для основного пути;
- один `prompts/STAGES.md` описывает текущую работу, lifecycle/evidence, blockers и NEXT;
- security и testing соответствуют рискам проекта;
- context routing использует минимально достаточный набор источников;
- нет необоснованных локальных копий глобальной AI Dev Team;
- пользователь может продолжить короткой командой вроде «Начинай этап 2».
