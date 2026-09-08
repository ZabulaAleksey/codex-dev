# DEV / КАРКАС — stages и execution state

- Stage ID: `DEV-CANONICAL-STAGES-001`
- Sequence: `DEV-GLOBAL-HARDENING-001 → DEV-AI-PROFILING-001 → DEV-PROMPT-QUEUE-001 → DEV-CANONICAL-STAGES-001`
- NEXT: дождаться явного выбора следующего DEV prompt; до этого selector остаётся на последнем
  verified record `DEV-CANONICAL-STAGES-001`.

Этот файл — единственный canonical execution-state owner global DEV. Requirements принадлежат
SPEC, долговременный порядок — `docs/ROADMAP.md`, architecture/decisions — своим владельцам.

## DEV-CANONICAL-STAGES-001 — Canonical STAGES.md Policy

- Status: `verified`.
- Lifecycle: `completed`.
- Evidence level: `validated locally`; commit, merge и push не выполнялись.
- Source: Notion prompt `DEV — Astra prompt — Canonical STAGES.md Policy — 2026-09-07`;
  `https://app.notion.com/p/3d461ed8f24681059594f00e38ab3c82?pvs=204`;
  approved execution request 2026-09-08.
- Requirements: `CSP-001..007`, `AC-CSP-001..008` из
  `specs/features/canonical-stages-policy.spec.md`.

### Dependencies / entry evidence

- Base: `feature/prompt-queue-lifecycle` checkpoint `80a63b3`, clean worktree.
- Isolated branch/worktree: `feature/canonical-stages-policy` /
  `~/codex-workspace/.worktrees/dev-canonical-stages-policy`.
- Baseline: 139 unit tests PASS; context validator PASS, 234 files.
- Existing project selector, hook, validator и reconciliation seams доступны.

### Runnable slice / concrete consumer scenario

```text
temporary full overlay with one prompts/STAGES.md
  → project validator checks canonical files + single selector/heading
  → SessionStart hook loads exact selected record
  → added legacy AI plan/status fail visibly and reconcile as MERGE
  → removal restores deterministic PASS
```

### Scope / non-goals

Входит: global governance, feature/system SPEC, router/docs/Skills/templates/presets, hooks,
validators/reconciliation, tests, current global state и manifest.

Не входит: product repository rollout, unrelated project architecture, active runtime config/data,
external writes, commit, merge, push, release или deployment.

### Tasks / PASS

- [x] Exact Notion prompt fetched and scoped.
- [x] Isolated branch/worktree and pre-change baseline established.
- [x] Canonical policy and migration documentation use only `prompts/STAGES.md` as execution owner.
- [x] Hook/validator/reconciliation and templates implement the single-file contract.
- [x] Global state migrated without loss of current facts; legacy AI files removed after audit.
- [x] Targeted consumer scenario, full tests, context validator and `git diff --check` PASS.
- [x] Completion documentation synchronization and final diff review complete.

### Verification evidence

- Targeted canonical selector/validator/reconciliation/global-policy suite: 96 tests PASS.
- Full suite: `py -3 -B -m unittest discover -s tools -p "test_*.py"` — 140 tests PASS.
- Context validator: `py -3 -B tools\validate_context.py` — PASS, 233 files.
- `git diff --cached --check` — PASS; reference scan leaves only explicit legacy migration,
  forbidden-name and test-fixture mentions.
- Consumer path is exercised by accepted tests: valid single-file overlay passes and hook selects
  the exact record; legacy state files fail validation and reconcile as read-only `MERGE`.
- Manual SessionStart invocation against this worktree — PASS: additional context begins with exact
  `DEV-CANONICAL-STAGES-001`; unrelated STAGES records are not projected.

### Fallback / rollback / NEXT

Legacy documents are never auto-deleted. Brownfield migration stops on conflict or missing evidence.
Rollback before commit is isolated-worktree discard; a future commit can be reverted atomically.
NEXT: await an explicitly selected DEV prompt; no future scope is inferred from this stage.

## DEV-PROMPT-QUEUE-001 — Prompt Queue Lifecycle

- Status: `verified`.
- Lifecycle: `completed` locally; cleanup state: `cleaned` / verified.
- Evidence: global full suite 139 PASS; context validator 234 files PASS; scoped correctness/security
  review without code findings; live exact-item Notion cleanup/read-back PASS; repeat `noop`.
- Scope: global governance/tooling and minimal project delta; no product-domain work.
- Contract: `rules/prompt-queue-lifecycle.md`, `PQ-01..11`.
- Integration: checkpoint `80a63b3`; merge/push not performed.
- NEXT: none inside this completed slice; integration remains separately approval-gated.

## DEV-AI-PROFILING-001 — AI Policy Profiling Observe layer

- Status: `verified`.
- Lifecycle: `completed`; evidence level: `merged` and `pushed` to `origin/main`.
- Implementation commit: `ea1fe24`.
- Evidence: 124 tests PASS; context validator 213 files PASS; synthetic consumer path and security/
  concurrency negatives PASS. Synthetic samples do not establish real policy ROI.
- Contract: `specs/features/ai-policy-profiling.spec.md`.
- Deferred: real-project opt-in rollout and human-approved tuning after sufficient comparable data.

## DEV-GLOBAL-HARDENING-001 — Global framework hardening

- Status: `blocked`.
- Lifecycle: `implemented_unverified`.
- Evidence: reusable implementation commit `67112aa`; 110 tests and 207-file context validation
  PASS at implementation checkpoint.
- Blocker: pre-existing active-runtime `unmatched-browser-client-hash`; runtime config is outside
  repository mutation scope.
- NEXT: terminal runtime verification only after the external blocker is resolved.
