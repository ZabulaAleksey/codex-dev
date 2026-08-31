# MODE: BLACKOUT

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance.

## Purpose

Evaluate how the system behaves when external services, infrastructure, or network dependencies disappear.

## Invocation

```text
MODE: BLACKOUT
FAIL:
- Keycloak
- RabbitMQ
- object storage
```

Or progressive:

```text
MODE: BLACKOUT
SCENARIO: progressive
```

## Core objective

> Discover hidden availability assumptions and define graceful degradation.

## Isolation boundary

Reasoning and local simulations are allowed by activation. Fault injection against production,
shared infrastructure, real customer traffic, or an external service requires a separate explicit
instruction naming that target. Prefer sandbox, test doubles, local containers, or an isolated
environment. Do not create a real outage to test outage behavior.

## Failure scenarios

When applicable simulate/reason about:
- identity provider unavailable;
- database unavailable/read-only;
- queue unavailable;
- object storage unavailable;
- DNS failure;
- third-party API timeout;
- payment provider unavailable;
- email/SMS unavailable;
- cache unavailable;
- partial network partition;
- dependency returns stale/corrupt responses.

## Progressive blackout

Recommended sequence:

```text
1 dependency fails
2 dependencies fail
critical infrastructure fails
recovery begins
```

Observe whether the system:
- fails closed;
- fails open;
- blocks indefinitely;
- corrupts state;
- retries uncontrollably;
- loses work;
- recovers cleanly.

## Dependency contract

For each dependency:

```text
DEPENDENCY:
WHY NEEDED:
FAILURE DETECTION:
TIMEOUT:
RETRY:
FALLBACK:
USER IMPACT:
DATA INTEGRITY RISK:
RECOVERY:
```

## Recovery is part of the test

A system that survives outage but cannot recover cleanly has not passed BLACKOUT.

Test:
- replay;
- duplicate jobs;
- stale sessions;
- queue catch-up;
- idempotency;
- reconciliation.

## Completion

Classify features:
`AVAILABLE / DEGRADED / UNAVAILABLE / UNSAFE`

Then identify the smallest changes needed for acceptable degradation.
