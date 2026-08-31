# План работы ИИ

## Текущая цель

<Один ограниченный проверяемый результат.>

## Связанные требования

- SPEC:
- Идентификаторы требований:

## AI policy profiling (optional)

- Profiling: `disabled | observe | experiment`
- Policy IDs:
- Experiment ID / arm:
- Task class:
- Baseline и sample-size caveat:
- Telemetry не заменяет Stage PASS/DoD evidence.

## Stage identity и dependency DAG

- Stage ID:
- Selector format: stable ASCII ID; exact unique heading token in `prompts/STAGES.md`.
- Full overlay validation: заполни ID до `validate_project_overlay.py`; пустой selector является FAIL.
- Completed / verified prerequisites:
- DAG:
- Проверка отсутствия self-reference, cycle и forward dependency:

## Входные предпосылки

| Предпосылка | Evidence доступности до старта |
|---|---|
| | |

## Самостоятельный runnable vertical slice

- Точка входа:
- Полный текущий путь:
- Наблюдаемый результат:
- Обязательная инфраструктура, входящая в этот stage:

## Concrete end-to-end scenario

1. Вход / действие consumer:
2. Реальный application/API/CLI/backend path:
3. Наблюдаемый результат:

## Область работы

### Входит

-

### Не входит

-

## Рабочие задачи

| № | Задача | Ответственный/агент | Зависит от | Выполнено |
|---|---|---|---|---|
| 1 | | | | |

## Acceptance / PASS criteria

- [ ]

## Проверка

```text
<команды>
```

| Gate | Command / check | Expected PASS | Evidence scope/environment |
|---|---|---|---|
| End-to-end | | | |

## Допустимая временная реализация

- Полностью рабочая реализация текущего slice или `none`:
- Явные границы:

## Deferred to future stages

- Только расширения/оптимизации/замены, не нужные primary path текущего stage:

## Риски и откат

-

## Документация

-

## Определение готовности

- [ ] Все prerequisites завершены; forward dependency/cycle отсутствуют.
- [ ] Primary vertical slice запускается без future stage.
- [ ] Concrete end-to-end scenario имеет PASS evidence.
- [ ] Mocks/stubs/fakes/interfaces не выданы за user/production completion.
- [ ] Критерии приёмки подтверждены.
- [ ] Релевантные проверки выполнены.
- [ ] `README`, `AI_PLAN`, `AI_STATUS`, `ROADMAP`, `prompts/STAGES.md` и другие state-bearing документы проверены.
- [ ] Изменившиеся факты синхронизированы; точные документы оставлены без churn.
- [ ] Если profiling включён, policy/experiment linkage и profiler overhead зафиксированы; automatic tuning не выполнялся.

## Условие остановки

- Остановиться и запросить решение, если реализация требует изменить SPEC, контракт или согласованные non-goals.
- Не использовать completion status, если primary path/verification зависит от future stage; выбрать `blocked`, `scaffolded`, `implemented_unverified` или `partial`.
