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
- ссылки на соответствующие PROMPTS/spec/decisions.

`SPEC != AI_PLAN`: спецификация описывает требуемую систему, план — порядок работы.

## Evidence levels

Используй строгую лексику:

- **implemented** — код существует;
- **validated** — релевантные проверки действительно выполнены;
- **documented** — утверждение записано в docs;
- **planned** — только план;
- **idea** — brainstorm;
- **blocked** — есть конкретное препятствие;
- **unknown** — evidence недостаточно.

`implemented` не означает автоматически `validated`.

## Completion Documentation Synchronization Gate

Перед `DONE`, commit handoff или заявлением о завершении всегда проверь существующие:

- `README.md`;
- `docs/AI_PLAN.md`, `docs/AI_STATUS.md`, `docs/ROADMAP.md`;
- `prompts/STAGES.md` или принятый stage tracker;
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

## После merge / завершения этапа

1. Проверь фактическое состояние target branch, если доступно.
2. Повтори Completion Documentation Synchronization Gate по target branch.
3. Зафиксируй выполненный stage в AI_STATUS.
4. Удали из AI_PLAN только уже неактуальные действия, не уничтожая будущий план.
5. Перенеси указатель на первый незавершённый этап.
6. Если изменились roadmap или stage tracker — синхронизируй их статусы и диапазоны.
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
