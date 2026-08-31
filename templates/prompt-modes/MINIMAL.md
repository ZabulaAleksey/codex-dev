# MODE: MINIMAL

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance.

## Purpose

Use MINIMAL when the user wants the requested change **without the normal Codex ceremony**.

Primary objective:

> Make the smallest useful change with the smallest useful verification cost.

MINIMAL is intentionally allowed to trade verification depth for speed and scope control.

## Invocation

```text
MODE: MINIMAL
```

Recommended levels:

```text
MODE: MINIMAL
LEVEL: SAFE
```

Values:
- `STRICT` — almost literal patch-only behavior;
- `SAFE` — minimal diff plus one or two cheap targeted checks;
- `EXPERIMENTAL` — rapid proof-of-concept, no production guarantee.

Default: `SAFE`.

## Normal workflow override

Ordinary workflow may look like:

```text
inspect
change
full tests
lint
typecheck
security scan
docs
regressions
status updates
```

MINIMAL should instead aim for:

```text
requested change
cheapest meaningful sanity check
done
```

If even the sanity check has no meaningful value, it may be omitted.

## Disabled by default

Unless necessary or explicitly requested, skip:
- full test suite;
- unrelated tests;
- repository-wide lint;
- repository-wide formatting;
- repository-wide typecheck;
- dependency audit;
- security scan;
- architecture review;
- browser E2E;
- Docker rebuild;
- comprehensive CI reproduction;
- benchmarks;
- broad documentation regeneration;
- opportunistic refactoring;
- unrelated cleanup;
- dependency modernization;
- speculative improvements.

## Never disabled

MINIMAL does not override:
- direct user requirements;
- hard safety constraints;
- destructive-operation protections;
- checks required to know whether the requested artifact is syntactically valid;
- checks required to avoid obvious data corruption;
- accepted tests or explicit Definition of Done gates for the requested task;
- evidence honesty: skipped checks remain `NOT RUN`/`UNVERIFIED` and cannot support a stronger
  completion claim.

## Minimal-diff law

> Touch as little as possible.

Do not:
- rename neighboring symbols for style;
- refactor surrounding code because it is ugly;
- add abstractions "for later";
- upgrade dependencies opportunistically;
- fix unrelated TODOs.

Ban the phrase/behavior:
> While I'm here...

## Verification budget

Concept:

```text
VERIFICATION_BUDGET: LOW
```

Choose the cheapest check that catches the most likely mistake introduced by this exact edit.

Examples:
- JSON edit → parse JSON;
- one function → targeted unit test if cheap;
- CSS copy change → inspect selector/render only if needed;
- README typo → no tests;
- config edit → parse/load config, not full monorepo CI.

## Reporting

Keep completion report short:

```text
Changed:
Checked:
Not run because MINIMAL is active:
```

Do not compensate for reduced verification with a giant warning.

## Escalation

If the task turns out to be unsafe to modify minimally:

```text
MINIMAL BLOCKER:
<reason>
```

Then perform only the minimum additional inspection needed to establish a safe path.

Do not silently transform MINIMAL into a full-quality workflow.

## STRICT

`LEVEL: STRICT`

Rules:
- no new files unless required;
- no unrelated changes;
- no docs unless requested or an in-scope changed fact would otherwise leave existing state-bearing
  documentation false;
- no dependency updates unless required;
- no tests except absolutely necessary sanity checks;
- no refactoring.

## SAFE

`LEVEL: SAFE`

Allow:
- one or a few targeted tests;
- syntax/type check of changed scope;
- cheap regression check.

This is the recommended default.

## EXPERIMENTAL

`LEVEL: EXPERIMENTAL`

Allow a deliberately provisional implementation.

Mark artifacts that are not production-ready.

## Completion test

If Codex did significantly more work than the user requested without a concrete necessity, MINIMAL failed.
