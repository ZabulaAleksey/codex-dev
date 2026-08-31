# MODE: TIME_TRAVEL

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance.

## Purpose

Reimagine an existing product, feature, or architecture in a different technological era.

Unlike TIME_CAPSULE, which only imposes a cutoff, TIME_TRAVEL asks:

> How would this same product realistically be designed if the target year were different?

## Invocation

```text
MODE: TIME_TRAVEL
TARGET_DATE: 2015-06-01
```

Optional:

```text
SOURCE_DATE: 2026-09-01
AUTHENTICITY: HIGH
```

## Required behavior

1. Preserve the **product intent**, not the current implementation.
2. Identify which current capabilities did not exist or were impractical at the target date.
3. Replace them with period-plausible alternatives.
4. Explain what becomes harder, more expensive, less secure, less scalable, or less ergonomic.
5. Distinguish:
   - impossible in that era;
   - possible but expensive;
   - practical;
   - commonplace.

## Translation layers

For each major subsystem create:

```text
CURRENT:
TARGET-ERA EQUIVALENT:
LOST CAPABILITIES:
NEW COMPLEXITY:
PERIOD-CORRECT ALTERNATIVES:
```

Areas:
- frontend;
- backend;
- auth;
- storage;
- realtime;
- deployment;
- observability;
- CI/CD;
- ML/AI;
- payments;
- mobile;
- security.

## Historical integrity

Do not merely downgrade version numbers.

The architecture itself should reflect the target era's constraints and conventions.

## Forward travel

TIME_TRAVEL may also modernize old systems:

```text
MODE: TIME_TRAVEL
SOURCE_DATE: 2012-01-01
TARGET_DATE: 2026-09-01
```

Then identify:
- what should stay;
- what should be replaced;
- what can be wrapped;
- what migration order reduces risk.

## Deliverable

Finish with:
- target-era architecture;
- substitutions;
- capabilities lost/gained;
- migration/build strategy;
- anachronism warnings.
