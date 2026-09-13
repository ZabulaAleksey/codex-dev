# Replaceable Module Contract

Этот файл — единственный глобальный владелец требования **Replaceability by Design**. Product
repository хранит только конкретные ports/adapters, исключения, migration debt и evidence.

## Когда граница обязательна

Явный системный port и adapter boundary обязательны, если выполняется хотя бы одно условие:

- внешний provider/SDK или vendor lock-in;
- реалистичная смена implementation/provider;
- несколько implementations либо полезный fake/emulator;
- durable state принадлежит внешней системе и требует export/import/migration;
- компоненту нужен fallback/degraded mode;
- подсистема влияет на payments, identity, storage, notifications, AI, search, queues,
  analytics, document/equation backends, RTC/video, collaboration или platform shells.

Не создавай интерфейс вокруг каждого класса. Для маленькой стабильной внутренней реализации без
внешней зависимости, альтернативы, durable migration и fallback используй YAGNI и зафиксируй
причину в architecture audit.

## Обязательная форма значимого сменного модуля

```text
Domain / Application -> system-owned Port -> Provider Adapter -> Provider
                                  \-> Fake/Test Adapter
```

Граница должна по возможности включать:

1. system-owned port/protocol, а не тип vendor SDK;
2. canonical internal DTO/model/event и anti-corruption translation;
3. provider selection в composition root/DI, без scattered conditionals;
4. normalized errors, timeouts, retries и idempotency по общей fallback policy;
5. capability declaration, если implementations отличаются;
6. общий contract test suite для каждой реализации;
7. fake/in-memory adapter только как test evidence, не как production E2E;
8. export/import/migration/rollback для vendor-owned durable state;
9. observability и security boundary без vendor secrets/types в domain layer.

Provider webhook сначала проходит authenticity/size/replay checks в infrastructure adapter, затем
становится canonical domain event. External IDs остаются metadata/correlation keys и не заменяют
внутреннюю business identity.

## Запрещённые утечки

- vendor SDK/types в domain/application/UI вне локального facade;
- прямой provider import из controller/service/component, если это не явный ingress/composition
  boundary;
- provider-specific DTO как transport/domain contract;
- business policy внутри adapter;
- provider selection, размазанный по handlers/services/components;
- durable canonical state, принадлежащий translation adapter;
- secrets/tokens вне infrastructure boundary;
- смена provider вместо локализации текущего provider в рамках обычного audit.

## Audit и score

Для каждого значимого модуля зафиксируй evidence, owner port/DTO, import sites, durable state,
tests, migration/fallback/security risk и score 0–10:

- `0–2`: provider вшит, замена требует rewrite;
- `3–4`: частичный wrapper, существенная leakage;
- `5–6`: boundary есть, contract/tests/migration неполны;
- `7–8`: swap локализован, contract tests есть;
- `9`: adapter/config/bounded migration;
- `10`: несколько implementations проходят общий suite, migration/fallback rehearsed.

P0 исправляется в текущем безопасном slice либо получает конкретный технический blocker. P1 идёт в
следующий dependency-safe slice; P2/YAGNI документирует, почему abstraction сейчас не окупается.

## Deterministic guards и evidence

Предпочитай AST/dependency tooling проекта для forbidden imports и module-boundary tests. Generic
cross-language regex gate не является достаточным evidence и не вводится, если создаёт brittle
false positives. Минимальный PASS: architecture/import check, contract tests, unit/integration и
затронутый consumer path; security-critical/provider runtime требует соответствующего real evidence.

Смена provider, data migration, production secrets, deploy, merge/push и destructive cleanup
остаются отдельными approval gates.
