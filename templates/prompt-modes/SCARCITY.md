# MODE: SCARCITY

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance.

## Purpose

Force design decisions under explicit resource scarcity.

Example:

```text
MODE: SCARCITY
RAM: 128MB
CPU: 1 core
DISK: 1GB
NETWORK: 256Kbit/s
MONTHLY_COST: 10USD
```

## Primary objective

> Maximize useful product behavior inside the resource envelope.

Do not design a normal architecture and merely claim it "should fit."

## Resource contract

At mode entry, normalize constraints:

```text
CPU:
RAM:
persistent storage:
temporary storage:
network bandwidth:
network latency:
request rate:
monthly budget:
power/battery:
device class:
```

Unknown values should not be invented unless needed; reason conservatively.

## Required behavior

Prefer:
- streaming over loading entire datasets;
- bounded caches;
- simple data structures;
- compact serialization;
- batching;
- backpressure;
- lazy work;
- incremental processing;
- graceful feature degradation;
- low-dependency runtime;
- single-process designs when adequate.

Challenge:
- background daemons;
- heavyweight runtimes;
- unnecessary containers;
- duplicated caches;
- chatty APIs;
- unbounded queues;
- large client bundles;
- expensive ORM patterns.

## Budget accounting

For important components estimate or measure:

```text
steady-state RAM
peak RAM
CPU hotspots
disk footprint
network volume
startup cost
```

Use measurements when practical.

## Failure rule

A solution that exceeds the stated resource envelope is a failed solution even if functionally correct.

## Graceful degradation

If all desired features cannot fit, rank them:

```text
MUST KEEP
DEGRADE
DISABLE
DEFER
```

Do not hide resource conflicts.

## Completion

State:
- what fits;
- what is close to the limit;
- what was sacrificed;
- where the next bottleneck will be.
