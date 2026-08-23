# Security baseline

Применяй пропорционально поверхности атаки проекта.

## Trust boundaries

Явно определи, что нельзя считать доверенным:

- browser/client;
- user-provided files/text/URLs;
- external APIs;
- webhook/event payloads;
- model output;
- plugin/MCP/tool output;
- local network peers;
- cached/stateful data после смены permissions.

## AuthN / AuthZ

- authentication не заменяет authorization;
- проверяй ownership/role на сервере;
- не полагайся на скрытую кнопку UI;
- sensitive action должен иметь явную policy.

## Input/output

- schema validation;
- size/count/depth limits;
- safe parsing;
- path traversal protection;
- injection-aware rendering/queries;
- content-type validation;
- controlled serialization/deserialization.

## Abuse / resource exhaustion

Для публичных или multi-user функций продумай:

- per-user/per-IP rate limits;
- concurrency limits;
- quotas;
- max request/upload/document size;
- max object count/depth;
- websocket/session limits;
- timeouts;
- cancellation;
- queue backpressure;
- compute budgets;
- graceful rejection instead of process crash.

Клиентские лимиты — UX; серверные — security boundary.

## Secrets

- не коммить secrets;
- не выводи их в logs/errors;
- используй env/secret store;
- минимизируй scope/token permissions;
- предусматривай rotation/revocation.

## Privacy

Минимизируй сбор и retention. Разделяй telemetry и пользовательский content. Административный доступ не должен автоматически означать доступ к приватным документам, если продукт обещает обратное.

## Dependencies / supply chain

- pin/lock зависимости по правилам ecosystem;
- review крупных новых dependencies;
- не выполняй недоверенный generated code без sandbox;
- проверяй install/build scripts у чувствительных зависимостей.

## Logging / telemetry

Логируй достаточно для диагностики abuse и failures, но не секреты, токены и лишний приватный content.

## High-risk actions

Удаление данных, production deploy, изменение auth/security policy, destructive migration и secret rotation требуют отдельного approval согласно `AUTONOMY_POLICY.md`.
