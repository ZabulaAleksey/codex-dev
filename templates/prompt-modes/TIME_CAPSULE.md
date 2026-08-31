# MODE: TIME_CAPSULE

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance.

## Purpose

Constrain implementation to the technological world that existed before a specified date.

Example:

```text
MODE: TIME_CAPSULE
CUTOFF: 2020-12-31
LEVEL: STRICT
```

Interpretation:

> The implementation may use only languages, versions, libraries, APIs, standards, dependencies, tooling and platform capabilities available by the cutoff.

## Scope of the cutoff

Apply to:
- language version and syntax;
- compiler/runtime;
- framework version;
- direct dependencies;
- transitive dependencies when strict;
- database versions/features;
- browser APIs;
- protocols/standards;
- build tools;
- package managers;
- CI/CD tooling;
- cloud/platform APIs;
- testing frameworks;
- cryptographic primitives/standards;
- deployment assumptions.

## Version-ceiling rule

For each material technology establish:

```text
technology
latest_allowed_version
release_date
```

A technology name existing before the cutoff does not permit later APIs.

Example:
- Python existed before 2020;
- Python 3.12 syntax is still forbidden for a 2020 cutoff.

## Levels

### COMPATIBLE
Modern development tools may be used around the project, but the produced artifact must run on an era-compatible stack.

### STRICT
The software stack, versions, dependencies and APIs must all fit the cutoff. Modern Codex itself remains allowed as the development assistant.

### AUTHENTIC
Aim for historically authentic tooling and deployment as well, where practical.

## Dependency rule

Required:

```text
release_date <= cutoff
```

Also verify the used API existed in that allowed release.

### Transitive future leak

In STRICT/AUTHENTIC, a pre-cutoff direct dependency must not silently pull post-cutoff transitive packages.

## Modern knowledge rule

Modern engineering knowledge may be used to avoid mistakes.

Future implementation technology may not.

Current safety boundaries still apply. Historical authenticity never requires deploying known-
unsafe cryptography, authentication, dependency, or data-handling behavior. If no period-correct
safe option satisfies the real use case, keep the result isolated or report `TEMPORAL_BLOCKED`.

It is valid to know in 2026 that an old pattern was risky and choose a better **period-correct** alternative.

## Unknown dates

If a material feature/version cannot be dated confidently, mark:

```text
TEMPORAL_UNKNOWN
```

Do not silently treat it as allowed.

Prefer:
1. verify;
2. substitute a clearly period-correct option;
3. otherwise disclose uncertainty.

## Future-leak audit

Before completion check:

```text
[ ] language syntax
[ ] compiler/runtime
[ ] direct dependencies
[ ] transitive dependencies
[ ] framework APIs
[ ] browser APIs
[ ] database features
[ ] protocols
[ ] build tooling
[ ] deployment tooling
[ ] generated config
```

## Anachronism ledger

For nontrivial work record:

```text
Cutoff:
Allowed stack:
Rejected as too new:
Historical substitutions:
Temporal unknowns:
```

## Non-goal

TIME_CAPSULE does not require deliberately bad historical coding practices.

Use good architecture and testing when the mechanisms themselves are period-correct.
