# Status and planning workflow

## AI_STATUS.md

Отвечает на вопрос: **что подтверждённо верно сейчас?**

Храни кратко:

- последний завершённый этап;
- какие проверки реально пройдены;
- известные ограничения;
- активные blockers;
- первый ещё не начатый/не завершённый этап.

Не превращай AI_STATUS в roadmap или журнал всех commit.

## AI_PLAN.md

Отвечает на вопрос: **что делать дальше?**

Храни:

- текущую цель;
- ближайший этап;
- последовательность нескольких следующих шагов, если она устойчива;
- dependencies/blockers;
- ссылки на соответствующие stages в `prompts/STAGES.md`, SPEC и decisions.

`SPEC != AI_PLAN`: спецификация описывает требуемую систему, план — порядок работы.

## Stage lifecycle и evidence levels

Не смешивай lifecycle stage и уровень интеграционного evidence.

Lifecycle:

- `planned`, `in_progress` — работа ещё не завершена;
- `blocked` — конкретная prerequisite/инфраструктурная преграда;
- `scaffolded` — существуют interfaces/mocks/stubs/fakes, но нет реального primary path;
- `partial` — работает только часть объявленного vertical slice;
- `implemented_unverified` — production implementation существует, обязательное evidence не получено;
- `completed` — все terminal conditions канонического Stage contract выполнены.

`verified` и `DONE` — terminal completion claims и требуют того же, что `completed`. Если primary
slice или E2E зависит от future stage, допускаются только `blocked`, `scaffolded`,
`implemented_unverified` или `partial`.

Evidence/integration level:

- **implemented locally** — production code существует;
- **validated locally** — релевантные checks, включая обязательный E2E, реально прошли;
- **committed / pushed / PR opened / merged / released/deployed** — только подтверждённый уровень;
- **unknown** — evidence недостаточно.

Documentation state ведётся отдельно: запись утверждения в docs не является evidence реализации
и не повышает lifecycle либо evidence/integration level.

Requirements принадлежат SPEC/ADR. Accepted tests являются executable contract/evidence, но не
первичным source of requirements. `implemented locally` не означает `validated locally`.

## Completion Documentation Synchronization Gate

Перед `DONE`, commit handoff или заявлением о завершении всегда проверь существующие:

- `README.md`;
- `docs/AI_PLAN.md`, `docs/AI_STATUS.md`, `docs/ROADMAP.md`;
- `prompts/STAGES.md`; во время согласованной brownfield migration также проверь mapped legacy tracker;
- `docs/TRACEABILITY.md`, `CHANGELOG.md`, `docs/DEV_LOG.md`, если они используются;
- затронутые SPEC, architecture, decisions, design, security, testing, API, data,
  dependencies и fallback documents.

Проверка обязательна всегда. Меняй файл только при изменении фактов; вместо timestamp-only
правки зафиксируй в handoff `checked, still accurate`.

Ищи и устраняй stale claims:

- завершённые действия в current/future plan;
- старый указатель этапа или status `in progress`;
- уже снятые blockers и ограничения;
- старые test counts, команды и verification results;
- неподтверждённые `merged`, `released`, `deployed`;
- README-команды, возможности и ограничения, которым противоречит реализация.

Gate не пройден, если изменившийся факт остался несинхронизированным или отсутствующее evidence
заменено предположением.

Completion gate также не пройден, если prerequisite/DAG, runnable vertical slice, concrete
end-to-end PASS evidence, temporary implementation или deferred scope противоречат Stage contract
из `~/.codex/rules/governance.md`. Blocked primary gate нельзя переносить в `DONE`.

## После merge / завершения этапа

1. Проверь фактическое состояние target branch, если доступно.
2. Повтори Completion Documentation Synchronization Gate по target branch.
3. Зафиксируй выполненный stage в AI_STATUS.
4. Удали из AI_PLAN только уже неактуальные действия, не уничтожая будущий план.
5. Перенеси указатель на первый незавершённый этап.
6. Если изменились roadmap или `prompts/STAGES.md` — синхронизируй их статусы и диапазоны.
7. Если возникло новое архитектурное решение — обнови decision/design.
8. Если выяснился повторяемый lesson — обнови LEARNING.
9. В handoff перечисли обновлённые документы и проверенные документы без изменений.

## Запрет на ложную синхронизацию

Не помечай stage как merged/done только потому, что prompt выполнен локально. Отличай:

```text
implemented locally
validated locally
committed
pushed
PR opened
merged
released/deployed
```

Пиши только фактически подтверждённый уровень.
