# DEV completed master prompts — durable orphan audit

Дата аудита: 2026-09-12. Scope: Notion items
`3d461ed8-f246-812d-b41c-da2510a70dd3` (CME) и
`3d561ed8-f246-81c0-b8c6-d06c1819bb4a` (SEP). Оба источника прочитаны полностью; live
repository/runtime, code, tests и canonical rules имеют приоритет над текстом prompts.

Baseline: source `~/codex-dev`, starting local-main HEAD
`47b6c223534c1a8f6e7d67ddfa506be6809d819d`, remote main
`89539840725ad57655a1f6e6ffe45ced874ce055`, runtime `~/.codex`, audit branch
`fix/completed-master-cleanup`. Unrelated worktree `fix/dev-launcher-evidence` не изменялся.

Initial result: один orphan — completed historical execution master с исходным
`retention=keep` не мог пройти deterministic cleanup guard. Этот bounded gap канонизирован в
PQ-13, `rules/prompt-queue-lifecycle.md`, `prompt_queue.py`, `master_execution.py` и regression
tests. Runtime Skill drift обнаружен отдельно и не является requirement orphan; cleanup остаётся
заблокирован до восстановления и повторной проверки parity. Восемь drifted runtime Skills затем
синхронизированы штатным `sync_global_skills.py` с recoverable backup; повторные
`validate_global_codex.py` и Skill parity вернули PASS для global layer и 10 источников.

## Requirement → canonical owner matrix

`RUNTIME_ACTIVE=yes` означает, что поведение требуется в materialized runtime; `source` —
долговечный repository owner, который проверяется installer/validator, но не вызывается runtime
напрямую.

| REQ_ID | SOURCE_MASTER | REQUIREMENT | CLASS | CANONICAL_OWNER | OWNER_PATH | IMPLEMENTATION_OR_RULE | VALIDATOR_OR_TEST | RUNTIME_ACTIVE | STATUS |
|---|---|---|---|---|---|---|---|---|---|
| CME-01 | CME | Live state/code/evidence precede prompt text | STAGE_STATE_RULE | Governance | `rules/governance.md`, `prompts/STAGES.md` | selected-record state contract | context + CME policy suites | yes | CANONICALIZED |
| CME-02 | CME | Automatically select next dependency-safe backward-complete slice | ROUTER_RULE | CME engine | `tools/master_execution.py` | `select_next_slice` | `tools/test_master_execution.py` | yes | CANONICALIZED |
| CME-03 | CME | Checkpoint is not a stop; stop only on canonical conditions | GLOBAL_RULE | Governance + CME SPEC | `rules/governance.md`, `specs/features/continuous-master-execution.spec.md` | execution/stop decisions | CME policy tests | yes | CANONICALIZED |
| CME-04 | CME | Structured graph, bounded slices and dependency validation | STAGE_STATE_RULE | CME schema/engine | `schemas/master-execution.schema.json`, `tools/master_execution.py` | strict graph validation | master execution tests | yes | CANONICALIZED |
| CME-05 | CME | Same master/track continuation reuses worktree | WORKTREE_RULE | CME router | `tools/master_execution.py` | `route_worktree` | reuse/changed-branch tests | yes | CANONICALIZED |
| CME-06 | CME | Independent parallel writer gets isolated branch/worktree | WORKTREE_RULE | Git policy + CME router | `AGENTS.md`, `tools/master_execution.py` | overlap-aware routing | parallel/collision/real Git tests | yes | CANONICALIZED |
| CME-07 | CME | No per-slice merge or worktree deletion; use integration checkpoints | WORKTREE_RULE | Governance + CME engine | `rules/governance.md`, `tools/master_execution.py` | `integration_decision` | integration boundary tests | yes | CANONICALIZED |
| CME-08 | CME | Minimal context package; full scan only for stable reason | CONTEXT_RULE | CME resolver | `tools/master_execution.py`, `docs/ARCHITECTURE.md` | budgeted context selection | context budget/reason tests | yes | CANONICALIZED |
| CME-09 | CME | Launcher/handoff is derived from canonical state, not old chat | CONTEXT_RULE | CME launcher | `tools/master_execution.py`, `hooks/session_context.py` | state/checkpoint handoff | launcher/context tests | yes | CANONICALIZED |
| CME-10 | CME | Recover new session, compaction, model switch, crash and missing relation | RECOVERY_RULE | CME recovery | `tools/master_execution.py`, `rules/fallback-policy.md` | `recover_execution` | recovery matrix tests | yes | CANONICALIZED |
| CME-11 | CME | Route to cheapest sufficient model without silent main-model change | MODEL_ROUTING_RULE | Model router | `rules/model-routing.md`, `tools/master_execution.py` | model class/effort metadata | routing/policy tests | yes | CANONICALIZED |
| CME-12 | CME | Evidence levels and mandatory VerificationGate; real ≠ synthetic | EVIDENCE_RULE | CME evidence contract | `specs/features/continuous-master-execution.spec.md`, `tools/master_execution.py` | `evidence_decision` | evidence gate tests | yes | CANONICALIZED |
| CME-13 | CME | Separate regression, pre-existing blocker, unrelated debt and environment | EVIDENCE_RULE | CME failure classifier | `tools/master_execution.py`, `rules/fallback-policy.md` | `classify_failure` | failure-class tests | yes | CANONICALIZED |
| CME-14 | CME | Completed child may clean independently; partial master stays | PROMPT_LIFECYCLE_RULE | Prompt lifecycle | `rules/prompt-queue-lifecycle.md`, `tools/master_execution.py` | hierarchy classifier | hierarchical lifecycle tests | yes | CANONICALIZED |
| CME-15 | CME | Short continuation command does not bypass state, gates or approvals | ROUTER_RULE | Global router | `AGENTS.md`, `rules/governance.md` | selected-master continuation | structural policy tests | yes | SUPERSEDED_BY_STRONGER_RULE |
| CME-16 | CME | Portable deterministic tooling, hooks and validators | SCRIPT_TOOL_RULE | Global installer/tooling | `tools/master_execution.py`, `tools/install_global.py`, `MANIFEST.txt` | stdlib CLI + managed install | install/global/CME tests | yes | CANONICALIZED |
| SEP-01 | SEP | Goal→invariants→overlay→live state→stage→contract chain | GLOBAL_RULE | Governance + SEP SPEC | `rules/governance.md`, `specs/features/specification-execution-pipeline.spec.md` | canonical execution order | SEP trace tests | yes | CANONICALIZED |
| SEP-02 | SEP | Project overlay is a bounded delta and cannot duplicate global owners | GLOBAL_RULE | Governance + placement validator | `AGENTS.md`, `tools/spec_execution.py` | placement classification | placement tests | yes | CANONICALIZED |
| SEP-03 | SEP | Resolve stage/scope before loading skills or broad context | CONTEXT_RULE | SEP router | `tools/spec_execution.py` | stage-first intake | intake/router tests | yes | CANONICALIZED |
| SEP-04 | SEP | Skill registry has explicit metadata and source ownership | SKILL_RULE | Skill registry | `skill-sources/registry.toml` | capability/stage/risk metadata | registry tests | yes | CANONICALIZED |
| SEP-05 | SEP | Load only required skills and fail closed on ambiguity | SKILL_RULE | SEP router | `tools/spec_execution.py` | relevant-only route | ambiguity/minimal-route tests | yes | CANONICALIZED |
| SEP-06 | SEP | Prefer deterministic cheapest sufficient executor | ROUTER_RULE | SEP executor router | `tools/spec_execution.py` | executor decision | executor routing tests | yes | CANONICALIZED |
| SEP-07 | SEP | Preserve compact intake constraints without using old chat as truth | CONTEXT_RULE | SEP intake | `tools/spec_execution.py`, `rules/governance.md` | typed intake | intake validation tests | yes | CANONICALIZED |
| SEP-08 | SEP | Requirement→capability→implementation→evidence trace is enforced | VALIDATOR_RULE | SEP trace validator | `tools/spec_execution.py` | critical trace validation | trace negative/positive tests | yes | CANONICALIZED |
| SEP-09 | SEP | Detect qualified automation opportunities with dedup | SCRIPT_TOOL_RULE | SEP automation detector | `tools/spec_execution.py` | opportunity decision | automation tests | yes | CANONICALIZED |
| SEP-10 | SEP | Promotion ladder: reasoning→skill→tool→module→test→hook/CI | GLOBAL_RULE | SEP SPEC/router | `specs/features/specification-execution-pipeline.spec.md`, `tools/spec_execution.py` | promotion target/placement | promotion tests | yes | CANONICALIZED |
| SEP-11 | SEP | Automation proposal never auto-writes policy/model/runtime | HOOK_RULE | SEP lifecycle boundary | `tools/spec_execution.py`, `docs/ARCHITECTURE.md` | propose/review/promote lifecycle | lifecycle/placement tests | yes | CANONICALIZED |
| SEP-12 | SEP | Context economy metrics are bounded and privacy-safe | CONTEXT_RULE | SEP diagnostics | `tools/spec_execution.py` | aggregate diagnostics | context economy tests | yes | CANONICALIZED |
| SEP-13 | SEP | Skill retirement requires unused/unreferenced evidence | SKILL_RULE | SEP retirement | `tools/spec_execution.py` | retirement decision | retirement tests | yes | CANONICALIZED |
| SEP-14 | SEP | Extend CME and Prompt Queue; never create a second state/cleanup owner | ROUTER_RULE | Architecture | `docs/ARCHITECTURE.md`, `tools/spec_execution.py` | compatibility boundary | CME compatibility tests | source | SUPERSEDED_BY_STRONGER_RULE |
| SEP-15 | SEP | Minimal launchers and project classes remain reusable entrypoints | DOCUMENTATION_ONLY | Reusable launcher + registry | Notion Minimal User Launchers, `skill-sources/registry.toml` | user entrypoint delegates to router | intake class tests | yes | CANONICALIZED |
| SEP-16 | SEP | Completed historical execution master is removable only after zero-orphan, runtime parity and regressions | PROMPT_LIFECYCLE_RULE | Prompt lifecycle PQ-13 | `rules/prompt-queue-lifecycle.md`, `specs/features/prompt-queue-lifecycle.spec.md`, `tools/prompt_queue.py` | attested exact-item guard | prompt queue + hierarchy tests | yes | CANONICALIZED |
| HIST-01 | both | Recommended rollout phases, model examples and report wording | HISTORICAL_CONTEXT | Git/Notion provenance | source prompts + Git history | non-normative provenance | not applicable | no | HISTORICAL_ONLY |

## Final classification

Durable requirements checked: **33**. `CANONICALIZED`: **30**;
`SUPERSEDED_BY_STRONGER_RULE`: **2**; `HISTORICAL_ONLY`: **1**; `ORPHAN`: **0**;
`AMBIGUOUS`: **0**. The exact counts are valid only after PQ-13 tests and active-runtime parity
PASS; until then prompt mutation remains blocked.

The reusable `DEV — Minimal User Launchers — Continue Existing / New Project — REUSABLE` is not
an execution-history item and remains in `A. DEV`.

## Verification evidence

- `py -3 -B -m unittest discover -s tools -p "test_*.py"` — 363 PASS, 7 expected
  platform skips after the final guard tests.
- `py -3 -B -m unittest tools.test_prompt_queue tools.test_master_execution
  tools.test_continuous_master_execution_policy tools.test_spec_execution` — 122 PASS,
  1 expected platform skip.
- `py -3 -B tools/validate_context.py` — 270 files PASS.
- `py -3 -B tools/validate_global_codex.py --workspace ~/codex-dev --codex-home ~/.codex` —
  global Codex layer PASS; `sync_global_skills.py` repeat read-only parity — 10 sources PASS.
- Branch-scoped installer dry-run with resolved `DEV_SOURCE_ROOT` lists only the bounded managed
  lifecycle/test/docs delta and skips protected runtime state.
- Independent correctness and security reviews found and closed child/launcher handoff mismatch,
  historical-check N/A bypass and two taxonomy/evidence wording inconsistencies; final re-review
  found no functional blocker.

Queue mutation remains separately approval-gated. The Notion parent read-back before mutation
contains both exact target IDs and the reusable launcher ID. After mutation it must contain only
the launcher inside `A. DEV`, with no target mentions or child-page links anywhere in the parent.
