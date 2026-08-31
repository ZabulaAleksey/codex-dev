# MODE: SCALE_FROM_HELL

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance.

## Purpose

Stress the architecture conceptually and experimentally under extreme growth.

Primary objective:

> Identify the order in which the system breaks as load, data, users, concurrency, or geography grows dramatically.

Conceptual analysis, capacity math, and isolated benchmarks are the default. Do not load-test
production, shared infrastructure, paid external APIs, or third-party systems without a separate
explicit instruction naming the target and resource budget.

## Invocation

```text
MODE: SCALE_FROM_HELL
MULTIPLIER: 1000x
```

Optional axes:

```text
USERS: 1000x
DATA: 100x
CONCURRENCY: 500x
REGIONS: 10
```

## Core rule

Do not preemptively rewrite everything for hyperscale.

First predict and verify bottlenecks.

## Bottleneck ladder

Produce:

```text
FAILS_FIRST:
FAILS_SECOND:
FAILS_THIRD:
SURVIVES:
UNKNOWN:
```

Analyze:
- database connections;
- hot rows/locks;
- indexes;
- queue depth;
- worker throughput;
- memory;
- file/object storage;
- network egress;
- auth provider;
- external API quotas;
- cache coherence;
- websocket/session state;
- cron/periodic jobs;
- observability volume.

## Quantitative reasoning

Use rough capacity math when exact benchmarks are unavailable.

Make assumptions explicit.

Example:
```text
100 req/s × 20 DB queries/request = 2000 qps
```

## Selective hardening

Only recommend changes that address an identified bottleneck or credible near-term threshold.

Separate:
- must change now;
- change at threshold X;
- not needed yet.

## Failure criterion

"Use microservices" is not a valid conclusion without a demonstrated boundary or bottleneck that benefits from separation.

## Completion

Return:
- bottleneck order;
- triggering thresholds;
- evidence/assumptions;
- cheapest mitigation at each threshold.
