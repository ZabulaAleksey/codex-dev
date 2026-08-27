# Implementation Prompt Standard

Каждый prompt должен быть самодостаточным и исполнимым другим агентом без текущего чата.

## Обязательная структура

```markdown
# Stage/Feature: <short title>

## Goal
Одно ясное описание результата.

## Context
Почему работа нужна и как она связана с текущей системой.
Укажи релевантные существующие файлы/компоненты, но не выдумывай пути.

## Current state / evidence
Что подтверждено в репозитории перед началом.

## Stage identity, dependency DAG & entry preconditions
- устойчивый Stage ID;
- dependency DAG;
- только completed/verified prerequisite stages;
- обязательные входные предпосылки и evidence их доступности;
- явный запрет self-reference, cycle и forward dependency.

## Scope
Что входит в работу.

## Non-goals
Что намеренно не делаем на этом этапе.

## Requirements
Функциональные требования и наблюдаемое поведение.

## Architecture constraints
Существующие границы слоёв, API/contracts, storage/runtime ограничения.

## Runnable vertical slice
Самостоятельная точка входа, полный текущий путь и наблюдаемый результат, которые работают без
future stage. Опиши минимальную обязательную инфраструктуру текущего slice.

## Concrete end-to-end scenario
Вход/действие consumer → реальный application/API/CLI/backend path → наблюдаемый результат.
Для internal/docs/policy stage укажи ближайший исполнимый consumer path.

## Security & abuse constraints
Релевантные threat/validation/rate/permission требования.

## Fallback / failure behavior
Как система ведёт себя при недоступности optional dependency/backend/service.

## Compatibility / migration
Если меняются contracts, formats, schema или runtime requirements.

Если работа затрагивает зависимости: canonical manager, manifest/lockfile, shared
cache/store, clean restore command, migration recovery point и documented exception.

## Testing & validation
Какие существующие проверки запустить и какие новые проверки допустимы/нужны.
Не ослаблять существующие тесты для получения зелёного результата.

## Acceptance / PASS criteria
Наблюдаемые критерии завершения и точные условия `PASS` / `FAIL`.

## Required evidence
Для каждого обязательного gate: command/check, expected result, scope, environment/commit и caveat.
Mock/stub/fake/interface-only evidence помечается как scaffold и не доказывает user/production path.

## Allowed temporary implementation
Опиши полностью рабочую в текущем slice временную реализацию и её границы либо явно укажи `none`.
Замена в future stage не должна быть нужна для запуска или проверки текущего пути.

## Definition of Done
- все prerequisite stages завершены; forward dependency/cycle отсутствуют;
- runnable vertical slice и concrete end-to-end scenario имеют PASS evidence;
- код/документация согласованы;
- все обязательные проверки пройдены; unavailable primary/E2E gate оставляет stage в
  non-terminal status, а недоступность optional/deferred проверки фиксируется с evidence;
- нет известных незадокументированных regressions;
- статус обновлён только на основе evidence.

## Deferred to future stages
Функциональность, которая не входит в acceptance contract текущего stage и только расширяет либо
заменяет уже работающий slice. Она не может быть обязательной для primary path текущего stage.
```

## Правила качества prompt

1. Не пиши «улучшить архитектуру» без измеримого результата.
2. Не требуй технологию только потому, что она упомянута в brainstorm; укажи rationale или оставь decision open.
3. Не включай секреты, токены и реальные credentials.
4. Не требуй массовый refactor, если задача решается локально.
5. Не переписывай тесты под реализацию.
6. Не заявляй compatibility без evidence.
7. Если требование неизвестно, пометь `Open question` или `Needs decision`, а не угадывай.
8. Один prompt должен иметь один основной outcome.
9. Не объявляй stage самостоятельным, если его основной путь или verification зависит от future stage.
10. Не выдавай mocks/stubs/fakes/interfaces за evidence завершённого user/production path.

## Размер этапа

Разделяй этап, если одновременно меняются несколько независимых крупных областей: например auth + billing + realtime board + deployment. Объединяй мелкие изменения, если по отдельности они не дают проверяемого runnable vertical slice. После разбиения каждый новый stage обязан оставаться исполнимым и проверяемым самостоятельно.
