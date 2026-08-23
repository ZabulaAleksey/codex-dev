# Testing and quality policy

## Базовый принцип

Тесты — источник требований и evidence, а не препятствие, которое надо обойти.

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

## E2E

Для пользовательского продукта E2E должен покрывать ключевые сценарии, а не каждую кнопку. Если backend/внешняя зависимость ещё отсутствует, фиксируй readiness и невозможность полного E2E вместо имитации успешной проверки.

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
