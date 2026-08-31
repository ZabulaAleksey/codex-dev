# MODE: NOVICE

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance.

## Purpose

Optimize implementation and explanation so a developer at a chosen level can genuinely understand and maintain it.

## Invocation

```text
MODE: NOVICE
LEVEL: junior
```

Possible levels:
- `beginner`;
- `junior`;
- `intermediate`.

Optional:
```text
TEACHING_DEPTH: high
```

## Core objective

> Reduce cognitive complexity without unnecessarily reducing engineering quality.

## Prefer

- explicit control flow;
- descriptive names;
- small functions;
- standard language features;
- visible data transformations;
- conventional folder structure;
- comments that explain *why*, not syntax;
- straightforward error paths.

## Avoid when alternatives are reasonable

- clever metaprogramming;
- dense functional chains;
- implicit magic;
- deep inheritance;
- hidden global state;
- excessive generic abstractions;
- framework tricks;
- premature design patterns;
- terse one-liners that obscure behavior.

## Learning boundary

Do not dumb down the system into bad practices.

If a professional mechanism is important, keep it and explain it.

## Explain hidden machinery

For important abstractions:

```text
WHAT YOU WRITE:
WHAT ACTUALLY HAPPENS:
WHY THIS ABSTRACTION EXISTS:
WHERE TO DEBUG IT:
```

## Human checkpoints

When useful, leave a bounded manual task:

```text
HUMAN CHECKPOINT
Task:
Why:
Steps:
DoD:
```

Use this only where it improves understanding.

## Completion

A novice should be able to answer:
- where execution starts;
- where data goes;
- where errors go;
- what component owns each responsibility;
- how to test the changed behavior.
