# MODE: ZERO_DEPENDENCY

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance.

## Purpose

Minimize or eliminate third-party runtime/build dependencies to expose what the platform can do by itself and reduce supply-chain/maintenance surface.

## Invocation

```text
MODE: ZERO_DEPENDENCY
LEVEL: STRICT
```

Levels:
- `PREFER_ZERO` — dependencies allowed only when clearly justified;
- `STRICT` — no new third-party dependencies;
- `PURE` — use only language/platform standard library where technically possible.

## Core rule

Before adding a dependency, ask:

> What exact capability are we buying, and can the platform provide enough of it directly at acceptable complexity?

## Dependency cost model

Evaluate:
- lines/API surface actually used;
- transitive dependency count;
- security exposure;
- update burden;
- bundle/runtime size;
- licensing/provenance;
- portability;
- lock-in.

## Allowed exceptions

In `PREFER_ZERO`, a dependency may be used when reimplementing it would be:
- cryptographically unsafe;
- standards-heavy;
- extremely complex;
- clearly more maintenance than value.

Document the reason.

## Never hand-roll casually

Do not reimplement cryptographic primitives, TLS, password hashing algorithms, or other high-risk security foundations just to satisfy a dependency-count aesthetic.

Use platform-provided primitives or explicitly approved mature libraries when safety requires it.

## Replacement strategy

For every removed/avoided dependency:

```text
DEPENDENCY:
CAPABILITY USED:
PLATFORM SUBSTITUTE:
TRADEOFF:
```

## Completion metric

Success is not "zero packages at any cost."

Success is the smallest dependency surface consistent with correctness, safety, and maintainability.
