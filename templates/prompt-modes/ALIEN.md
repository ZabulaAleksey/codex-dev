# MODE: ALIEN

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance or silently rewrite an accepted project contract.

## Purpose

Force exploration outside the obvious/default architectural solution.

ALIEN is useful against pattern lock-in and model priors.

## Invocation

```text
MODE: ALIEN
FORBID: REST
```

or:

```text
MODE: ALIEN
FORBID:
- PostgreSQL
- React
- message queue
```

## Core rule

1. Identify the obvious/default solution.
2. Explicitly forbid it.
3. Reframe the problem in terms of underlying requirements.
4. Search a meaningfully different design space.

Do not cheat by renaming the forbidden technology or using a near-identical substitute without architectural difference.

## Required output

```text
DEFAULT SOLUTION:
WHY IT IS OBVIOUS:
FORBIDDEN ASSUMPTION:
UNDERLYING REQUIREMENT:
ALIEN ALTERNATIVES:
SELECTED APPROACH:
NEW TRADEOFFS:
```

## Examples

If REST is forbidden, possibilities might include:
- RPC;
- event-driven interfaces;
- server-rendered forms;
- local-first sync;
- shared database boundary, where appropriate.

If PostgreSQL is forbidden:
- embedded DB;
- document store;
- object storage plus indexes;
- append-only log;
- filesystem structures.

## Quality rule

ALIEN does not mean "choose something weird."

The alternative must still satisfy the task and its constraints.

If the forbidden default is required by an accepted SPEC, compatibility boundary, or existing
production contract, treat ALIEN as design exploration unless the user explicitly authorizes that
contract to change.

## Arena use

ALIEN is especially valuable as one independent Arena candidate to reduce correlated solutions.
