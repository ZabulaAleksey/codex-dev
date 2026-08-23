# Architecture policy

## API-first

Предпочитай ядро/application layer, которое не зависит от конкретного UI. REST/CLI/GUI/MCP/Jobs должны по возможности быть адаптерами вокруг устойчивого application/core contract, а не отдельными реализациями бизнес-логики.

```text
UI / CLI / REST / MCP / Jobs
            ↓
      Application API
            ↓
        Domain/Core
            ↓
Adapters: storage / providers / external systems
```

Не форсируй эту форму для крошечной утилиты, если она создаёт больше сложности, чем пользы.

## Contracts

Явно различай:

- domain model;
- transport DTO;
- persistence schema;
- external provider schema.

Не протаскивай случайную структуру внешнего API через всю систему.

## Adapters and backends

Для сменных backends используй единый contract и явный selection/fallback policy. Не размазывай `if provider == ...` по приложению.

## Telemetry

Для серьёзного продукта выделяй наблюдаемость как системную обязанность. TelemetryService/эквивалент может собирать:

- technical events;
- product/UX events;
- performance;
- failures/fallback usage.

Не смешивай telemetry с private document content без необходимости.

## SDK / CLI / MCP

Если сервис предполагает automation/integration, сначала стабилизируй application/API contract. SDK, CLI и MCP должны переиспользовать этот контракт, а не создавать три независимых продукта.

## Async/workflows

Используй queues/workflow engines только когда есть реальная длительная/асинхронная работа, retry, scheduling или orchestration requirement. Не добавляй RabbitMQ/Temporal/Redis «на будущее» без текущей необходимости.

## Performance acceleration

GPU/WebGPU/OpenCL/CUDA/FPGA/WASM — backends/optimization, а не источник истины. Сначала зафиксируй correctness contract и baseline implementation. Для optional acceleration определи fallback.

## Architecture decisions

При существенном выборе зафиксируй:

- context;
- decision;
- rationale;
- alternatives;
- consequences;
- migration/rollback, если требуется.
