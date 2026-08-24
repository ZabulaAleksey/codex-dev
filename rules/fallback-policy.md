# Fallback Policy — каноническая политика деградации и отказов

## Назначение

Этот документ является общим каноническим контрактом AI Dev Team для операций,
которые могут завершиться ошибкой, потребовать retry, перейти на альтернативный
backend/tool/model/data source или вернуть деградированный результат.

Проекты наследуют эту политику и не копируют её полностью.
Project-specific цепочки хранятся только как локальная delta.

## Базовая модель

Для операции, допускающей деградацию, явно определи:

Primary → Retry → Fallback → Degraded mode → Fail closed

Не каждая операция обязана использовать все стадии.

Для security-sensitive операций нормальной цепочкой может быть:

Primary → Fail closed

## Обязательный контракт fallback-цепочки

Для каждой значимой цепочки определи:

1. Primary — предпочтительный путь.
2. Trigger — точное условие перехода.
3. Retryable errors — какие ошибки можно повторять.
4. Non-retryable errors — какие повторять запрещено.
5. Retry budget — attempts, timeout и backoff.
6. Ordered fallback — заранее разрешённые альтернативы в фиксированном порядке.
7. Capability check — способен ли fallback выполнить требуемую операцию.
8. Semantic equivalence — какие гарантии сохраняются или теряются.
9. Degraded result — как обозначается частичный или пониженный результат.
10. Provenance — какой путь фактически использовался.
11. Side-effect policy — идемпотентность, reconciliation и rollback.
12. Stop condition — явная точка fail closed.
13. Observability — какие безопасные события и метрики фиксируются.
14. Tests — как проверяется сама fallback-цепочка.

## Retry Policy

Retry разрешён только для ошибок, которые действительно могут исчезнуть при повторе.

Типичные retryable причины:

- transient network failure;
- временная недоступность storage/provider;
- временная недоступность worker;
- timeout при известной безопасной повторяемости;
- 429/503 при документированной политике backoff.

Типичные non-retryable причины:

- invalid input;
- corrupted input;
- unsupported version;
- authorization failure;
- authentication failure, требующий повторного входа;
- integrity/signature failure;
- security policy violation;
- hard quota;
- resource/security limit;
- deterministic parser error;
- incompatible schema.

Бизнес-ошибка не превращается автоматически в технический retry.

Бесконечные retry запрещены.

## Ordered Fallback

Fallback не выбирается агентом произвольно.

Разрешённые альтернативы должны быть:

- заранее определены;
- упорядочены;
- проверены на capability;
- совместимы с security policy;
- наблюдаемы.

Случайно найденная библиотека, package, model, API или CLI не является допустимым fallback.

## Semantic Equivalence

Fallback нельзя считать эквивалентным primary только потому, что он вернул какой-либо результат.

Если теряются:

- точность;
- функциональность;
- структура;
- редактируемость;
- свежесть;
- доказательная сила;
- provenance;
- security guarantee,

результат помечается degraded, partial, stale или unverified.

Silent fallback запрещён.

## Security Invariants

Fallback никогда не может обходить:

- authentication;
- authorization;
- permissions;
- sandbox;
- validation;
- security gates;
- approval requirements;
- integrity checks;
- signature verification;
- crypto requirements;
- resource/security limits.

Запрещены, в частности:

crypto failure → plaintext

authorization failure → anonymous access

signature failure → trust payload anyway

validator failure → disable validation

sandbox failure → execute directly on host

security reviewer unavailable → считать security review пройденным

Для auth, authorization, crypto, integrity и security validation
по умолчанию применяется fail closed.

## Side Effects и идемпотентность

Перед retry операции с побочным эффектом нужно определить,
могла ли предыдущая попытка фактически завершиться.

Если состояние неизвестно:

unknown side effect → reconcile → retry/fallback

а не:

unknown side effect → повторить операцию

Используй stable operation ID или idempotency key там, где это возможно.

Нельзя создавать повторно:

- job;
- payment;
- resource;
- deployment;
- merge;
- commit;
- message;
- webhook side effect,

если неизвестно состояние предыдущей попытки.

## Rollback и recovery

Для мутаций заранее определи:

- нужен ли rollback;
- нужен ли reconciliation;
- какие изменения reversible;
- какие требуют отдельной compensating action.

Fallback не должен запускаться поверх неизвестного частичного состояния.

## Evidence Policy

Понижение уровня проверки допустимо только как явно более слабое evidence:

E2E
→ integration
→ component/smoke
→ static validation
→ NOT RUN / UNVERIFIED

Smoke-test нельзя называть E2E.

Fixture/mock нельзя выдавать за production evidence.

Cache нельзя выдавать за live data.

Локальный domain review не заменяет обязательный global security/reviewer gate.

Если обязательный gate недоступен, его итог:

UNVERIFIED

## Типовые цепочки

### Models

preferred model
→ approved alternate model
→ limited/local model
→ fail closed, если capability недостаточна

### Tools

preferred MCP/tool
→ approved CLI/API/SDK
→ ограниченный manual path
→ fail closed

Permissions при переходе не ослабляются.

### Data

live source
→ canonical database
→ timestamped cache
→ fixture/mock только в dev/test
→ unavailable

### Tests

E2E
→ integration
→ component/smoke
→ static validation
→ UNVERIFIED

### Implementation

preferred backend/library
→ проверенная совместимая альтернатива
→ минимальная собственная реализация только при приемлемом риске
→ stop/escalate

## Observability

Для существенного fallback фиксируй без чувствительных данных:

- primary path;
- класс failure;
- retry count;
- выбранный fallback;
- degraded mode;
- итоговый статус;
- correlation/operation ID.

Нельзя логировать секреты или пользовательский payload только ради диагностики fallback.

## Budget Limits

Для retries/fallbacks задавай суммарные лимиты:

- времени;
- количества попыток;
- стоимости;
- токенов;
- network requests;
- compute;
- внешних API расходов.

## Обязательные тесты

Для значимых цепочек проверяй:

1. primary success;
2. transient failure + retry success;
3. exhausted retry;
4. fallback success;
5. degraded result;
6. fallback capability insufficient;
7. fail closed;
8. partial side effect + reconciliation;
9. отсутствие повторного side effect;
10. security policy не ослабляется fallback'ом.

## Project overlay

Проекты наследуют этот файл как INHERITED.

Если проект имеет предметные fallback-сценарии, он может создать:

docs/FALLBACKS.md

Этот файл содержит только project-specific delta:

- конкретные цепочки;
- product semantics;
- конкретные fail-closed решения;
- ссылки на SPEC/ADR/tests.

Глобальную Fallback Policy туда не копировать.

AGENTS.md должен только маршрутизировать контекст к этому документу.

## Dependency manager migration

Dependency-manager migration follows
[`dependency-management.md`](dependency-management.md). Incompatibility is not a
reason to silently switch manager: retain the current working state, document an
exception and stop. A graph change, failed verification, dirty worktree, unavailable
dependency or unknown directory prohibits deletion of the previous lockfile or
materialized dependencies until recovery/clean-restore proof is complete.
