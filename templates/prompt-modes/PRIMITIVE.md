# MODE: PRIMITIVE

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance or silently rewrite an accepted project contract.

## Purpose

Expose underlying mechanisms by deliberately avoiding selected high-level abstractions.

This is primarily an engineering-learning and architecture-clarity mode.

## Invocation

```text
MODE: PRIMITIVE
NO_ORM: true
NO_DI_CONTAINER: true
NO_CODEGEN: true
```

Or:

```text
MODE: PRIMITIVE
LAYER: HTTP
```

## Core principle

> Replace convenience abstractions with the lowest reasonable primitives that still produce a correct, comprehensible system.

## Possible restrictions

- no ORM;
- no web framework;
- no DI container;
- no code generation;
- no schema generator;
- no state-management framework;
- no queue abstraction;
- no RPC framework;
- no reactive wrapper;
- no metaprogramming.

## Required behavior

When removing an abstraction, explicitly expose:
- what work the abstraction normally performs;
- what state it manages;
- what protocol/data flow exists underneath;
- which responsibilities now become manual.

Example without ORM:
- SQL;
- connection lifecycle;
- transactions;
- mapping;
- migrations;
- error handling.

## Safety boundary

Do not go below safe primitives merely for purity.

Examples:
- do not write custom crypto;
- do not bypass memory safety when unnecessary;
- do not manually parse dangerous formats if a safe standard parser is available.

## Learning artifact

For each removed abstraction:

```text
ABSTRACTION REMOVED:
UNDERLYING PRIMITIVES:
MANUAL RESPONSIBILITIES:
WHAT THIS TEACHES:
WHAT WOULD BE RESTORED IN PRODUCTION:
```

## Completion

The result should be intentionally more explicit, not intentionally worse.

If an accepted project contract requires the abstraction, use PRIMITIVE as an explanatory or
isolated experimental pass unless the user explicitly requests the contract change.
