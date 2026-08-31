# AI Policy Profiling / Agent Economics

## Назначение

Эта policy применяется, когда задача вводит или оценивает дорогую AI-policy, agent route,
retrieval/reuse contour, автоматизацию, human handoff или experiment. Она не делает profiling
обязательным для каждой задачи и не заменяет SPEC, tests, review либо Stage evidence.

Канонические identifiers первой версии:

- `AEP_PASSIVE_OBSERVE_V1`;
- `AEP_BOUNDED_DISCOVERY_V1`;
- `AEP_HUMAN_HANDOFF_V1`;
- `AEP_REUSE_ECONOMICS_V1`.

## Минимальная decision model

Оптимизируй `COST_PER_VERIFIED_OUTCOME`, а не activity metrics. Если данные доступны, total
effective cost включает AI, human active, discovery, context, verification, rework, failure risk и
infrastructure overhead. Missing величины остаются `unknown`; не подставляй выдуманные числа.

Для новой policy сначала зафиксируй:

1. hypothesis;
2. comparable baseline;
3. task class;
4. experiment ID и arms;
5. outcome/quality/cost metrics;
6. sample-size caveat;
7. decision owner.

## Passive-first lifecycle

```text
Observe → Measure → Compare → Recommend
→ human-approved tuning → bounded automatic tuning
```

Текущий global profiler автоматизирует только первые четыре фазы. Policy threshold, router,
agent selection или global instruction нельзя менять автоматически по telemetry. Tuning требует
отдельного human approval и, для существенного поведения, SPEC/decision.

## Bounded discovery

До external discovery проверь по порядку existing project → local reusable catalog → internal
ecosystem → trusted upstream → bounded external search → greenfield.

Активный search имеет wall/token/cost budget и долю expected task cost. Остановись с
`STOP_DISCOVERY`, если превышен любой budget, нет strong candidate, provenance/license/
compatibility недостаточны либо adaptation estimate достиг greenfield estimate. Отсутствующий
budget для дорогого поиска означает stop/configuration required, а не unlimited loop.

## Reuse decision

Сравни expected reuse cost с expected greenfield cost. В reuse cost включай discovery, evaluation,
provenance/license, architecture intake, adaptation, integration, verification и maintenance risk.
Фиксируй `REUSE_FALSE_POSITIVE`, если выбранный reuse не дал verified outcome или actual reuse
cost не оказался ниже greenfield estimate. Не продолжай adaptation только ради соблюдения
reuse-first правила.

## Human handoff

`DELEGATE_TO_HUMAN` допустим, когда одно действие простое, быстрое, не требует специальной
экспертизы, AI tool/context overhead существенно выше и repetition/batching не оправдывает
automation. Handoff должен содержать одно действие, цель, ожидаемый ответ и DoD.

Допустимые reasons: `ECONOMIC`, `TOOL_LIMITATION`, `VISUAL_CHECK`, `PHYSICAL_ACTION`,
`SECURITY_CONFIRMATION`, `LEARNING`, `AMBIGUITY_RESOLUTION`. `LEARNING` указывается явно и не
выдаётся за economic saving. Не передавай человеку 50 повторяющихся действий по одному.

## Telemetry boundary

Opt-in project layout создаётся только явным запуском:

```text
.metrics/
  config.json
  events.jsonl
  stages.jsonl
  policies.jsonl
  experiments.jsonl
  contours.jsonl
  agents.jsonl
  reports/
```

Versioned schema принадлежит `schemas/ai-policy-profiling.schema.json`. Runtime data не является
global Git source. Не логируй prompt/user/source content, stdout/stderr, raw command arguments,
environment values, secrets или credentials. Автоматически собирай только безопасные доступные
facts; human time/handoff допускает короткое explicit observation с provenance.

## Stage integration

Если profiling включён, Stage может указать `Policy IDs`, `Experiment ID`, `Experiment arm` и
telemetry evidence. Эти поля optional и не делают `.metrics/` обязательной частью project overlay.
Telemetry report не заменяет concrete end-to-end PASS, acceptance tests или Documentation
Synchronization Gate.

## Failure and fallback

- invalid/oversized/unsupported telemetry → fail closed, no append/report overwrite;
- missing Git metadata → safe null fact, telemetry operation может продолжиться;
- missing token/model usage → `unknown`, без estimation;
- profiler unavailable → задача продолжается без profiling, если profiling не является её DoD;
- corrupt metrics required by an experiment → experiment result `UNVERIFIED`.

## Rollout and disable

Absent `.metrics/` = disabled. Existing projects не мигрируются автоматически. Включение:
explicit `init`, затем instrumented observations. Отключение: прекратить вызовы profiler; локальные
runtime data удаляет владелец проекта отдельно. Не добавляй обязательный hook или service ради
passive observation.
