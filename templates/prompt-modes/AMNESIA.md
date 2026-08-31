# MODE: AMNESIA

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance.

## Purpose

Reduce anchoring on prior project decisions, historical agent conclusions, and accumulated narrative.

AMNESIA intentionally creates an independent solution attempt.

## Invocation

```text
MODE: AMNESIA
```

Optional:

```text
MODE: AMNESIA
MEMORY_SCOPE: minimal-runtime-state
```

## Core behavior

Use only the minimum current facts required to solve the task:
- current code/artifacts;
- explicit requirements;
- hard constraints;
- interfaces that must remain compatible.

Still load the current applicable `AGENTS.md`, explicit user requirements, accepted SPEC/ADR,
security constraints, and repository state. AMNESIA removes optional historical anchoring; it does
not erase current authority or compatibility facts.

Ignore, where safe and allowed:
- previous preferred solution;
- prior model recommendations;
- historical rationale;
- "we always do it this way";
- nonbinding roadmap assumptions.

## Never ignore

Do not ignore:
- safety constraints;
- actual production compatibility;
- explicit user requirements;
- current schemas/APIs that must be preserved;
- legal/license constraints;
- evidence of real incidents.

## Independent pass

Produce the solution before reading optional historical rationale when possible.

Then, if requested, compare:

```text
AMNESIA SOLUTION
vs
HISTORICAL SOLUTION
```

Identify:
- convergence;
- surprising divergence;
- possible anchoring;
- useful constraints that history contained;
- obsolete assumptions.

## Arena use

AMNESIA is ideal as one blind Arena candidate.

## Failure mode to avoid

Do not pretend not to know facts while still unconsciously restating the old plan. The point is an independently derived design, not theatrical forgetting.
