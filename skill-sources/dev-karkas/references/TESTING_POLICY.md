# Testing and quality policy

## Базовый принцип

SPEC/ADR являются источником требований. Accepted tests — исполняемый контракт принятого
поведения и evidence, а не препятствие, которое надо обойти и не альтернативная SPEC.

## Existing tests

- Не удаляй, не skip'ай, не ослабляй и не переписывай существующие тесты только ради прохождения CI.
- Если тест кажется устаревшим, сначала докажи конфликт со спецификацией/решением и явно сообщи его.
- Изменение существующего теста допускай только когда сама задача явно меняет соответствующий контракт и project policy это разрешает.

## New tests

Добавляй новые тесты, когда prompt/DoD требует покрыть новое поведение или когда это стандарт проекта. Не создавай бессмысленные snapshot/tests ради числа.

## Уровни

Выбирай релевантные:

- format;
- lint;
- static/type checks;
- unit;
- integration;
- component;
- E2E;
- smoke;
- build/package;
- compatibility/import/export;
- security;
- performance/load.

Continuous Master Execution нормализует evidence как `L1 static/type/lint`, `L2 unit`,
`L3 component/integration`, `L4 real backend/concurrency`, `L5 browser/UI/runtime`, `L6 external/
manual acceptance`. Required level зависит от риска slice; наличие L1/L2 не заменяет обязательный
L4/L5/L6 gate. Downstream не продолжает critical chain при missing mandatory evidence.

## E2E

Для пользовательского продукта E2E должен покрывать ключевые сценарии, а не каждую кнопку. Каждый
stage всё равно определяет concrete end-to-end scenario: для internal/docs/policy stage это
ближайший исполнимый consumer path. Если обязательный backend/внешняя зависимость ещё отсутствует,
используй `BLOCKED_BY_BACKEND`/`blocked` и не закрывай stage вместо имитации успешной проверки.

Mocks, stubs, fakes и заранее подготовленные interfaces могут подтверждать unit/integration
scaffold, но не заменяют живой user/production E2E evidence.

## Команды

Не угадывай команды. Получай их из:

- package manifests;
- Cargo/workspace config;
- Makefile/Taskfile;
- CI workflow;
- scripts;
- README/AGENTS.

## Evidence report

Для каждой существенной проверки сообщай:

```text
command / check
result: pass | fail | unavailable | not-run
scope
important caveat
```

Не используй «всё протестировано», если запускалась только часть suite.

## Failure policy

При падении проверки:

1. установи, связано ли падение с текущими изменениями;
2. исправь production code, если причина в реализации;
3. не маскируй regression изменением теста;
4. если проблема pre-existing — зафиксируй evidence и отдели её от текущей задачи.
