# MODE: PREMORTEM

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance.

## Purpose

Assume the project or change has already failed in the future, then work backward to identify plausible causes before implementation or release.

## Invocation

```text
MODE: PREMORTEM
HORIZON: 12 months
```

Optional failure target:

```text
FAILURE: commercial
```

or:
```text
FAILURE: technical
```

## Prompt frame

Start from:

> It is <horizon> later. This initiative failed badly. What most plausibly caused that outcome?

Do not produce generic risk filler.

## Failure domains

Consider when relevant:
- product/requirements;
- architecture;
- security;
- reliability;
- scaling;
- cost;
- data quality;
- vendor dependency;
- migration;
- operational complexity;
- developer experience;
- maintainability;
- observability;
- adoption;
- legal/compliance;
- schedule;
- team knowledge;
- user abuse.

## Causal chains

Prefer chains over isolated risks:

```text
CAUSE
→ INTERMEDIATE CONDITION
→ WARNING SIGNAL
→ FAILURE
```

Example:

```text
unbounded conversion jobs
→ queue grows faster than workers
→ latency climbs for days
→ paid users experience multi-hour waits
→ churn/support load
```

## Rank risks

For each:

```text
RISK-ID:
Scenario:
Likelihood:
Impact:
Earliest warning signal:
How to detect:
Cheapest preventive action:
Trigger for stronger action:
```

## Anti-paranoia rule

Do not redesign the project against every imaginable catastrophe.

Separate:
- credible/high-value;
- monitor;
- remote/speculative.

## Integration

PREMORTEM output should be suitable input for:
- Navigator;
- architecture planning;
- rollout gates;
- Failure Atlas seed hypotheses.

## Completion

End with the smallest set of preventive actions that materially reduce the highest-ranked failure paths.
