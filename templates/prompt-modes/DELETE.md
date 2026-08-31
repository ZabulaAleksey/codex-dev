# MODE: DELETE

> Optional prompt-mode only. Activate explicitly; common scope and safety boundaries are defined
> in `README.md`. It does not change DEV governance.

## Purpose

Prefer solving the problem by reducing the system rather than adding to it.

Primary question:

> What can be removed so this problem stops existing?

## Invocation

```text
MODE: DELETE
```

Optional strictness:

```text
MODE: DELETE
AGGRESSION: HIGH
```

## Search order

Before adding code, inspect whether the task can be solved by deleting:
1. obsolete feature;
2. compatibility path;
3. duplicate abstraction;
4. unused dependency;
5. unnecessary state;
6. redundant cache;
7. dead configuration;
8. wrapper layer;
9. special case;
10. entire subsystem.

## Deletion proof

For each proposed deletion establish:
- current callers/users;
- runtime reachability;
- compatibility impact;
- data impact;
- rollback path if needed.

Do not delete because something "looks unused" without evidence when the project is nontrivial.

Mode activation authorizes deletion-oriented analysis and in-scope code simplification, not broad
removal of user data, unrelated files, backups, branches, worktrees, production resources, or
accepted behavior. Protected deletion still requires an exact target, impact check, recovery path,
and any separate approval required by the environment or repository.

## Simplification metric

Prefer changes that reduce:
- executable code;
- states;
- branches;
- dependencies;
- configuration;
- deployment components;
- maintenance concepts.

## Anti-rule

Do not replace a 20-line feature with a 200-line migration framework merely to claim code was deleted.

Count total complexity, not deleted lines.

## Completion

Report:
```text
Removed:
Behavior preserved/changed:
Complexity eliminated:
Residual risk:
```
