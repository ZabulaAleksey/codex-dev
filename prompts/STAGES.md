# DEV / КАРКАС — stages и execution state

- Stage ID: `DEV-CME-F`
- Sequence: `DEV-CANONICAL-STAGES-001 → DEV-CME-A → DEV-CME-B → DEV-CME-C → DEV-CME-D → DEV-CME-E → DEV-CME-F`
- NEXT: master complete; integration/finalization requires explicit merge approval.

Этот файл — единственный canonical execution-state owner global DEV. Requirements принадлежат
SPEC, долговременный порядок — `docs/ROADMAP.md`, architecture/decisions — своим владельцам.

## DEV-CME-A — Audit + Canonical Contract

- Status: `verified`; Lifecycle: `completed`; Evidence level: `validated locally`.
- Master: `DEV-CME-001`; master status: `partial`; track: `canonical-stages-policy`.
- Worktree/branch: `~/codex-workspace/.worktrees/dev-canonical-stages-policy` /
  `feature/canonical-stages-policy`; checkpoint before: `72197b2`.
- Source: Notion master `3d461ed8-f246-812d-b41c-da2510a70dd3`, revision
  `2026-09-07T18:46:55.040Z`, type `master_prompt`, retention `keep`; explicit execution 2026-09-08.
- Requirements: `CME-001..008`, `NFR-CME-001..003`, `AC-CME-001..009`.

### Dependencies / runnable slice / PASS

Prerequisite `DEV-CANONICAL-STAGES-001` is completed and committed as `72197b2`. This docs/policy
slice maps existing owners and establishes approved SPEC + ADR before executable implementation.
PASS: feature/system SPEC, gap map, architecture decision, roadmap/current record and repository
state agree; targeted policy checks and `git diff --check` pass.

### Execution graph / scope / stop conditions

Ready chain: `A(contract) → B(track router) → C(graph/auto-continue) → D(context/handoff) →
E(evidence/integration) → F(lifecycle/recovery/final validation)`. Each successor requires verified
predecessor evidence. No external input, destructive action or integration write is needed through
F. Merge/push/worktree cleanup are finalization boundaries and remain prohibited without approval.

Scope: global DEV/KARKAS only; no product rollout, runtime config, external mutation or new
scheduler. Fallback: invalid/ambiguous state or missing evidence stops fail closed. Rollback:
revert/discard isolated checkpoint. Evidence: 44 targeted policy/validator tests PASS, context
validator PASS (234 files), SessionStart selected only `DEV-CME-A`, `git diff --check` PASS.
NEXT: `DEV-CME-B` selected automatically.

## DEV-CME-B — Track Registry + Worktree Router

- Status: `verified`; Lifecycle: `completed`; Evidence level: `validated locally`.
- Master: `DEV-CME-001`; master status: `partial`; predecessor: `DEV-CME-A` verified.
- Track/worktree/branch: continuation of `canonical-stages-policy` in current isolated worktree;
  checkpoint before will be the Phase A commit.
- Requirements: `CME-002`, `CME-003`, `NFR-CME-001..003`; acceptance `AC-CME-001`, `AC-CME-003`.

### Runnable slice / PASS / boundaries

Add one versioned embedded state contract and stdlib Git adapter that classifies read-only,
same-track continuation and independent parallel write. Real temporary Git integration proves
continuation reuse and collision-safe isolated creation; no branch switch in an occupied worktree,
merge/push/delete or product mutation. Invalid paths/duplicate registry entries fail closed.

NEXT after PASS: checkpoint and select `DEV-CME-C` automatically. Blockers: none.

Evidence: strict state/schema and validator checks PASS; 48 targeted tests PASS, including real
temporary Git worktree creation/read-back; context validator PASS (237 files); SessionStart emits
the complete selected record without degradation; `git diff --check` PASS. Checkpoint: `5401b65`.

## DEV-CME-C — Execution Graph + Auto-Continue

- Status: `verified`; Lifecycle: `completed`; Evidence level: `validated locally`.
- Master: `DEV-CME-001`; master status: `partial`; predecessor `DEV-CME-B` verified.
- Track/worktree/branch: same continuation track; checkpoint before `5401b65`.
- Requirements: `CME-001`, `CME-004`; acceptance `AC-CME-002`.

### Runnable slice / PASS / boundaries

Extend the same controller with cycle-safe dependency readiness, mandatory evidence gates,
normalized stop conditions and immutable result transitions. A deterministic scenario advances
two ready slices without a user prompt; ambiguous ready sets, hard blockers and unverified
predecessors stop fail closed. The controller returns decisions and never executes task commands.

NEXT after PASS: checkpoint and select `DEV-CME-D` automatically. Blockers: none.

Evidence: 16 controller tests and 40 policy tests PASS; CLI reports the running slice without
executing it; context validator and `git diff --check` PASS. Checkpoint: `2f140c5`.

## DEV-CME-D — Low-Context Scope + Handoff

- Status: `verified`; Lifecycle: `completed`; Evidence level: `validated locally`.
- Master: `DEV-CME-001`; master status: `partial`; predecessor `DEV-CME-C` verified.
- Same continuation track; checkpoint before `2f140c5`.
- Requirements: `CME-005`, `NFR-CME-001`; acceptance `AC-CME-004`.

### Runnable slice / PASS / boundaries

Resolve only ordered context items named by the current slice, enforce char/item/contour/decision/
evidence-thread budgets, and build a compact launcher/handoff on overflow. Handoff contains master,
track, worktree, branch, state revision, checkpoint, verified chain, next action, blockers and
integration/cleanup rules. Stale checkpoint/revision fails closed. No separate status file.

NEXT after PASS: checkpoint and select `DEV-CME-E` automatically. Blockers: none.

Evidence: 20 master/controller/context tests PASS; targeted scope ordering, complete overflow
launcher and stale checkpoint/revision rejection verified; CLI, SessionStart, context validator
and `git diff --check` PASS. Checkpoint: `53138d5`.

## DEV-CME-E — Evidence + Integration Gates

- Status: `verified`; Lifecycle: `completed`; Evidence level: `validated locally`.
- Master: `DEV-CME-001`; master status: `partial`; predecessor `DEV-CME-D` verified.
- Same continuation track; checkpoint before `53138d5`.
- Requirements: `CME-006`; acceptance `AC-CME-005`.

### Runnable slice / PASS / boundaries

Normalize risk-to-evidence levels, classify failures as regression/pre-existing/unrelated/environment,
and decide coherent/dependent/divergent/final integration checkpoints without executing merge.
Critical downstream remains blocked until required real evidence is present. Unit scenarios prove
classification and no evidence inflation.

NEXT after PASS: checkpoint and select `DEV-CME-F` automatically. Blockers: none.

Evidence: 24 master tests and 24 governance/documentation tests PASS; risk levels L1-L6,
verification gate, four failure classes and checkpoint-only integration verified. CLI/context/
diff PASS. Checkpoint: `252e935`.

## DEV-CME-F — Hierarchical Lifecycle + Recovery + Final Gates

- Status: `verified`; Lifecycle: `completed`; Evidence level: `committed` at `c81ee81`.
- Master: `DEV-CME-001`; master status: `completed`; predecessor `DEV-CME-E` verified.
- Same continuation track; checkpoint before `252e935`.
- Requirements: `CME-007..008`, `NFR-CME-002..003`; acceptance `AC-CME-006..009`.

```master-execution
{"schema_version":1,"state_revision":7,"master":{"id":"DEV-CME-001","status":"completed","source":{"backend":"notion","queue_id":"3d061ed8-f246-8163-b502-d1829668063c","item_id":"3d461ed8-f246-812d-b41c-da2510a70dd3","revision":"2026-09-07T18:46:55.040Z","prompt_type":"master_prompt","retention":"keep"}},"tracks":[{"id":"canonical-stages-policy","repository":"~/.codex","worktree":"~/codex-workspace/.worktrees/dev-canonical-stages-policy","branch":"feature/canonical-stages-policy","checkpoint":"c81ee81d5722cca3db8fbbe1b91fc4055dd1a837","ownership":["global-orchestration-contract"],"status":"integration_required"}],"slices":[{"id":"DEV-CME-A","master_id":"DEV-CME-001","title":"Contract","status":"completed","predecessors":[],"dependencies":[],"worktree_track":"canonical-stages-policy","checkpoint_before":"72197b268e5e0525d19cbee712535d68346062f4","checkpoint_after":"d4f711ec43964125dcd3a4658ef87d14cfca6c4a","required_evidence":["L1"],"evidence":["L1"],"context_scope":[],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-CME-B","master_id":"DEV-CME-001","title":"Routing","status":"completed","predecessors":["DEV-CME-A"],"dependencies":[],"worktree_track":"canonical-stages-policy","checkpoint_before":"d4f711ec43964125dcd3a4658ef87d14cfca6c4a","checkpoint_after":"5401b65a925bce28af7c2d2b619781e2a4d0f392","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":[],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-CME-C","master_id":"DEV-CME-001","title":"Graph","status":"completed","predecessors":["DEV-CME-B"],"dependencies":[],"worktree_track":"canonical-stages-policy","checkpoint_before":"5401b65a925bce28af7c2d2b619781e2a4d0f392","checkpoint_after":"2f140c528d29f3af4a62ce7f3c48bc1e52ea25d9","required_evidence":["L1","L2"],"evidence":["L1","L2"],"context_scope":[],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-CME-D","master_id":"DEV-CME-001","title":"Handoff","status":"completed","predecessors":["DEV-CME-C"],"dependencies":[],"worktree_track":"canonical-stages-policy","checkpoint_before":"2f140c528d29f3af4a62ce7f3c48bc1e52ea25d9","checkpoint_after":"53138d5379458a1adaaf8c7c4e353ade045f9081","required_evidence":["L1","L2"],"evidence":["L1","L2"],"context_scope":[],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-CME-E","master_id":"DEV-CME-001","title":"Evidence","status":"completed","predecessors":["DEV-CME-D"],"dependencies":[],"worktree_track":"canonical-stages-policy","checkpoint_before":"53138d5379458a1adaaf8c7c4e353ade045f9081","checkpoint_after":"252e935d75fca284edc07bf48cb8ec8439c9b115","required_evidence":["L1","L2"],"evidence":["L1","L2"],"context_scope":[],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-CME-F","master_id":"DEV-CME-001","title":"Recovery","status":"completed","predecessors":["DEV-CME-E"],"dependencies":[],"worktree_track":"canonical-stages-policy","checkpoint_before":"252e935d75fca284edc07bf48cb8ec8439c9b115","checkpoint_after":"c81ee81d5722cca3db8fbbe1b91fc4055dd1a837","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":[],"model_class":"HIGH","reasoning_effort":"high","stop_after":true}],"blockers":[{"id":"CME-ROLLOUT-ET","class":"pre_existing","status":"active","blocking":false,"owner":"electro-tutor brownfield migration stage","evidence":"legacy AI_PLAN/AI_STATUS and missing same-file selector"}],"decisions":["keep-parent-master","no-integration-write"],"context_budget":{"max_chars":6000,"max_items":12,"max_contours":4,"max_decisions":4,"max_evidence_threads":6},"next_action":"integration finalization requires explicit merge approval","integration":{"required":true,"reason":"master_complete"}}
```


### Runnable slice / PASS / boundaries

Hierarchical cleanup eligibility delegates completed children to the existing guard and retains this
master because source retention is `keep`. Recovery covers commit/status ordering, missing branch/
worktree, stale launcher/source, dirty edits, overlapping integration, missing queue item and
compaction. Router/rules/Skills/templates/docs are synchronized.

Evidence: full 181 tests PASS; master-policy 40, queue 15 and existing governance 36 targeted tests
PASS; context validator PASS (238 files); Python and PowerShell syntax PASS; exact SessionStart
record PASS; real temporary Git worktree create/read-back supplies L3. Bash syntax is
`UNAVAILABLE` because local WSL returned `E_ACCESSDENIED`; unchanged script had prior evidence.
Read-only `electro-tutor` validation classified a pre-existing brownfield gap (legacy
`AI_PLAN/AI_STATUS`, missing same-file selector); no product mutation or regression.

Stop: master complete. Merge/push/worktree cleanup were not performed. Prompt cleanup: `retain`
because this is a `master_prompt` with retention `keep`.

## DEV-CANONICAL-STAGES-001 — Canonical STAGES.md Policy

- Status: `verified`.
- Lifecycle: `completed`.
- Evidence level: `committed` at `72197b2`; merge и push не выполнялись.
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
