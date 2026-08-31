# Codex Prompt Modes

This folder contains optional user-invoked prompts for testing, complicating, teaching, exploring,
or playfully changing how Codex approaches a task.

These files are **not DEV rules**, are not part of `rules/modes/`, and must not be activated or
loaded automatically by DEV routing. Merely finding a file in this folder does not activate it.

## Activation

A prompt mode activates only after an explicit user instruction.

Preferred syntax:

```text
MODE: MINIMAL
SCOPE: TASK
```

With parameters:

```text
MODE: TIME_CAPSULE
SCOPE: STAGE FS-024
CUTOFF: 2020-12-31
LEVEL: STRICT
```

Combined:

```text
MODE: MINIMAL + TIME_CAPSULE
SCOPE: PROJECT fourier-sketch
MINIMAL_LEVEL: SAFE
CUTOFF: 2020-12-31
TIME_CAPSULE_LEVEL: STRICT
```

Supported scope forms:

- `TASK` — ends when the current requested task ends;
- `STAGE <id>` — remains active for that named stage until it is completed or explicitly disabled;
- `PROJECT <name>` — remains active while working on that project until explicitly disabled;
- `UNTIL_OFF` — remains active in the current conversation until explicitly disabled.

If scope is omitted, use `TASK`. A mode declaration written by the user into a project or stage
prompt is explicit activation for that declared scope; Codex must not add such declarations on its
own.

Disable modes with:

```text
MODE OFF: MINIMAL
MODE OFF: ALL
```

## Precedence and boundaries

An explicitly activated prompt mode may override ordinary defaults such as:

- how much optional verification to run;
- whether to favor dependencies or primitives;
- whether to optimize for scale, scarcity, pedagogy, historical authenticity, or novelty;
- interaction style and optional output structure.

Prompt modes do not override:

1. system/platform safety boundaries;
2. a more specific current user instruction;
3. protection of user data, credentials, production systems, and destructive operations;
4. an accepted SPEC, test contract, or repository invariant unless the user explicitly requests
   that contract to change.

Activating a mode is not by itself permission to merge, push, deploy, access production, delete
user data, rewrite history, weaken security, or perform another separately protected action.

Prompt modes do not modify DEV governance. If a mode reduces checks or ceremony, report the actual
evidence level honestly (`NOT RUN`, `UNVERIFIED`, or an equivalent project status) instead of
claiming stronger completion.

## Combination rule

Multiple prompt modes may be active at the same time. Before work, resolve conflicts using:

1. explicit per-mode parameters supplied by the user;
2. the more specific user instruction and scope;
3. stricter safety and data-preservation constraints;
4. the narrower change;
5. if still incompatible, report the conflict and use the least destructive interpretation.

Do not silently disable one of the requested modes. Modes may be assigned to separate Arena
candidates when their optimization targets are intentionally incompatible.

## Available prompt modes

- `RED_TEAM.md` — adversarially search an authorized scope for weaknesses and abuse cases.
- `MINIMAL.md` — do only what is needed and cut optional verification and ceremony.
- `TIME_CAPSULE.md` — constrain implementation to technology available before a cutoff date.
- `TIME_TRAVEL.md` — redesign the same product for another technological era.
- `SCARCITY.md` — build under explicit compute/storage/network/resource scarcity.
- `ZERO_DEPENDENCY.md` — minimize or prohibit third-party dependencies.
- `PRIMITIVE.md` — avoid selected high-level abstractions to expose underlying mechanisms.
- `ALIEN.md` — forbid the obvious/default solution and explore a different design space.
- `DELETE.md` — prefer solving problems by removing code, features, layers, or dependencies.
- `SCALE_FROM_HELL.md` — analyze what fails under extreme growth and harden selectively.
- `BLACKOUT.md` — simulate disappearance or failure of external services and infrastructure.
- `AMNESIA.md` — produce an independent solution from minimal current facts to reduce anchoring.
- `NOVICE.md` — optimize implementation and explanation for a chosen learner level.
- `PREMORTEM.md` — assume the project failed in the future and identify likely causes now.
- `EXAMINER_MODE.md` — create one controlled bug in a disposable branch for a debugging exercise.
- `AGENT_ARENA.md` — compare independent candidates using evidence rather than voting.

## Exit

When a scope ends or the user disables a mode, stop applying its behavior. Perform only the cleanup
defined by that mode and already authorized by its activation contract. `EXAMINER_MODE` has a
special disposable-branch cleanup contract described in its own file.
