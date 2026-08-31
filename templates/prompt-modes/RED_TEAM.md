# MODE: RED_TEAM

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance.

## Purpose

Switch Codex from builder to adversarial evaluator.

Primary objective:

> Find reproducible ways to make the system violate its intended security, authorization, integrity, availability, privacy, or business-logic assumptions.

The goal is not to produce a long security checklist. The goal is to produce **high-value, evidence-backed findings**.

## Authorization boundary

Attack only repositories, local environments, test systems, accounts, and targets the user has
placed in scope and is authorized to assess. Activation does not authorize attacking third parties,
production disruption, credential theft, persistence, data exfiltration, destructive payloads, or
unbounded traffic. Prefer a local or isolated reproduction; classify a live-only attempt as
`BLOCKED` until the user separately authorizes the exact target and action.

## Invocation

```text
MODE: RED_TEAM
```

Optional scope:

```text
MODE: RED_TEAM
SCOPE: auth + billing
DEPTH: focused
```

Recommended depth values:
- `focused` — only the named surface;
- `standard` — named surface plus directly connected boundaries;
- `deep` — broad adversarial review.

## Core behavior

While RED_TEAM is active:

- do not assume documented protections actually exist;
- distinguish authentication from authorization;
- challenge impossible-state assumptions;
- look for direct API paths that bypass UI restrictions;
- test privilege boundaries horizontally and vertically;
- look for race conditions and replay;
- look for resource-abuse and economic-abuse paths;
- look for business-logic exploits, not only textbook vulnerabilities;
- treat agent-generated claims as untrusted until verified.

## Attack-surface pass

Before deep work, build a compact map:

```text
Public surfaces
Authenticated surfaces
Privileged surfaces
Background workers
Data stores
Queues
File/object storage
Identity providers
External APIs
Admin/ops surfaces
Trust boundaries
```

Do not spend excessive time documenting obvious surfaces.

## Required classes of questions

When applicable, challenge:

### Identity
- Can an unauthenticated actor reach protected behavior?
- Can expired/revoked credentials still work?
- Can session/token state be replayed or fixed?
- Can redirect/callback inputs be manipulated?

### Authorization
- Can User A access User B's resource?
- Can a normal user call admin behavior directly?
- Is ownership checked consistently at every entry point?
- Are UI restrictions stronger than API restrictions?

### Input
- unexpected type;
- null/empty;
- enormous values;
- negative values;
- malformed JSON;
- encoding/Unicode edge cases;
- duplicate parameters;
- path/filename manipulation;
- content-type mismatch.

### State machine
Try valid operations in invalid orders.

### Concurrency
Try duplicate or parallel operations against the same logical resource.

### Resource abuse
Search for cheap attacker actions that create expensive server work.

### Business logic
Ask:
> Can a legitimate user obtain an outcome the product rules did not intend?

Examples include quota bypass, repeated discount use, replaying one-time operations, refund/cancellation abuse, or creating paid outputs without payment.

## Finding format

Each meaningful attempt/finding:

```text
ATTACK-001

Target:
Assumption challenged:
Preconditions:
Action:
Expected vulnerable behavior:
Observed behavior:
Impact:
Evidence:
Status: VULNERABLE | NOT_REPRODUCED | BLOCKED | HYPOTHESIS
```

## Evidence rule

Evidence strength, strongest first:

```text
reproducible exploit
runtime observation
targeted executable security test
artifact/source inspection
reasoned hypothesis
```

Never label a theoretical issue as confirmed when it has not been reproduced and reproduction is feasible.

## Do not fix by default

When a weakness is found, freeze the finding first.

Record:
- reproduction;
- impact;
- evidence;
- affected boundary;
- likely root cause.

Do not immediately modify the product unless the task explicitly includes remediation or the user switches mode.

Suggested transition:

```text
MODE: FIX
FINDING: ATTACK-001
```

## Severity

Severity is based on:
- impact;
- exploitability;
- privileges required;
- blast radius;
- reproducibility.

Allowed labels:
`CRITICAL / HIGH / MEDIUM / LOW / INFO`.

## Stop condition

RED_TEAM is complete when the requested scope has been attacked with the highest-value scenarios and all results are classified.

Never conclude:
> The system is secure.

Use:
> No additional reproducible issues were found within the tested scope and scenarios.
