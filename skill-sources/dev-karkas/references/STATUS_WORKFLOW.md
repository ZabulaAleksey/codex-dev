# Canonical STAGES.md workflow

## Единственный execution-state owner

Active full staged overlay использует `prompts/STAGES.md` одновременно для:

- единственного current selector `- Stage ID: <stable-id>`;
- current/next plan;
- lifecycle и evidence level каждого stage;
- prerequisites, blockers, runnable path и deferred scope;
- последних существенных проверок и конкретного NEXT.

Не создавай `AI_PLAN.md`, `AI_STATUS.md`, `PLAN.md`, `STATUS.md`, `PROGRESS.md` или другой
конкурирующий project-state owner. Requirements принадлежат SPEC/ADR, `ROADMAP` хранит
долгосрочный порядок, а история — Git/CHANGELOG/DEV_LOG только при отдельной необходимости.

## Stage lifecycle и evidence levels

Не смешивай lifecycle stage и уровень интеграционного evidence.

Каждый record имеет компактный `Status: planned | implemented | verified | partial | blocked |
unavailable`. Это projection, а не третья независимая шкала: `implemented` соответствует
production implementation без terminal verification, `verified` — `completed` со всем требуемым
evidence, `unavailable` — `blocked` из-за недоступной prerequisite/capability.

Lifecycle:

- `planned`, `in_progress` — работа ещё не завершена;
- `blocked` — конкретная prerequisite/инфраструктурная преграда;
- `scaffolded` — существуют interfaces/mocks/stubs/fakes, но нет реального primary path;
- `partial` — работает только часть объявленного vertical slice;
- `implemented_unverified` — production implementation существует, обязательное evidence не получено;
- `completed` — все terminal conditions канонического Stage contract выполнены.

Evidence/integration level:

- **implemented locally** — production code существует;
- **validated locally** — релевантные checks, включая обязательный E2E, реально прошли;
- **committed / pushed / PR opened / merged / released/deployed** — только подтверждённый уровень;
- **unknown** — evidence недостаточно.

`verified` и `DONE` — terminal completion claims и требуют того же, что `completed`. Если primary
slice или E2E зависит от future stage, допускаются только `blocked`, `scaffolded`,
`implemented_unverified` или `partial`. Requirements принадлежат SPEC/ADR; accepted tests являются
executable contract/evidence, но не первичным source of requirements.

## Обновление текущего состояния

После изменения фактического состояния до handoff обнови только соответствующий stage record:

1. compact Status, lifecycle и evidence level;
2. выполненные acceptance/PASS gates с command, result, scope, environment/commit и caveat;
3. активные blockers и полностью рабочую temporary implementation;
4. deferred scope;
5. ровно один конкретный NEXT и, если текущий stage завершён, selector следующего допустимого stage;
   если утверждённого следующего stage нет, оставь selector на последнем verified record и явно
   укажи ожидание нового выбора вместо создания placeholder stage.

Не превращай `STAGES.md` в журнал действий. Устаревшие подробности удаляй из current record только
после сохранения нужной истории в Git/CHANGELOG/DEV_LOG; не теряй активные facts или evidence.

## Brownfield migration

Если существуют legacy plan/status files:

1. Запусти read-only `tools/reconcile_project_framework.py` и зафиксируй compatibility matrix.
2. Прочитай canonical/legacy `STAGES.md`, `AI_PLAN.md`, `AI_STATUS.md`, `PLAN.md`, `STATUS.md`,
   `PROGRESS.md` и mapped equivalents.
3. Сопоставь current selector, stages, facts, blockers, evidence и NEXT. При конфликте предпочитай
   repository/test evidence, затем более свежее подтверждённое состояние; не угадывай.
4. Создай или дополни один `prompts/STAGES.md`, сохрани stable IDs и уникальное актуальное содержание.
5. Обнови routes в `AGENTS.md`, README, Skills, hooks, prompts, scripts и документации.
6. Запусти project validator и baseline/regression checks.
7. Только после semantic/content/link audit удали legacy files. Reconciler/validator сами ничего
   не удаляют и не пишут в product repository.

Unresolved conflict оставляет migration `BLOCKED`; competing files не объявляются безопасно
удаляемыми только по имени.

## Completion Documentation Synchronization Gate

Перед `DONE`, commit handoff и после разрешённого merge всегда проверь существующие:

- `README.md`;
- `prompts/STAGES.md`, `docs/ROADMAP.md`;
- `docs/TRACEABILITY.md`, `CHANGELOG.md`, `docs/DEV_LOG.md`, если они используются;
- затронутые SPEC, architecture, decisions, design, security, testing, API, data,
  dependencies и fallback documents.

Проверка обязательна всегда. Меняй файл только при изменении фактов; вместо timestamp-only
правки зафиксируй в handoff `checked, still accurate`.

Ищи и устраняй stale claims: завершённые действия в current/future plan, старый selector,
разрешённые blockers, старые test counts, неподтверждённые integration levels и README-команды,
которым противоречит реализация. Blocked primary gate нельзя переносить в `DONE`.

## После merge / завершения этапа

1. Проверь фактическое состояние target branch.
2. Повтори Completion Documentation Synchronization Gate.
3. Обнови lifecycle/evidence текущего record только до подтверждённого уровня.
4. Перенеси selector/NEXT на первый допустимый незавершённый stage.
5. Синхронизируй `ROADMAP`, decisions/design/learning только при изменившихся фактах.
6. В handoff перечисли обновлённые документы и проверенные документы без изменений.

Не повышай local evidence до pushed/merged/released без соответствующего факта.
