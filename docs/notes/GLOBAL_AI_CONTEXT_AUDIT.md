# Global DEV AI Context, Automation & Script Factory — factual audit

Scope: canonical `DEV_SOURCE_ROOT` Git source at `~/codex-dev`; audit branch
`feature/global-ai-context-audit`, fast-forward integrated into local `main`
at `0884495`. Active `CODEX_HOME` installer and read-back passed. Notion source item
`3db61ed8-f246-81d7-bc79-fba7f8d03a41`, parent queue
`3d061ed8-f246-8163-b502-d1829668063c`, revision
`2026-09-14T20:47:07.483Z`; user launched it on 2026-09-15 and allowed removal after
execution. The source was fetched in full (23,224 characters; no reported truncation),
then exact-item queue cleanup passed after overall DoD and runtime parity.

## Audit result

Overall: **PASS_WITH_GAPS**. The existing DEV has a functioning source/installed split,
stage-first context router, execution controller, governance validators and opt-in project
profiler. A new explicit, sanitized global action journal, an exact-path catalog of 15
pre-existing DEV scripts plus this new CLI, and a pure configurable repeat detector now work
in this branch. Two real sanitized source-validator actions produced one exact-repeat
candidate; preflight reused the existing `validate_context.py` rather than creating a
duplicate. Comparative cost evidence remains unknown from this tiny sample.
No evidence-backed destructive/security blocker (P0) was found in the audited source.

As-Is:

```text
user intent → AGENTS/rules + nearest project overlay → dev_paths + selected STAGES
→ master_execution dependency/evidence/context decision
→ spec_execution Skill capability router (9 versioned Skills)
→ existing CLI/hooks/validators (15 pre-existing non-test Python tools, 3 hook scripts)
→ tests + selected STAGES evidence/NEXT
→ optional project-local ai_policy_profiler observations
→ optional prompt_queue exact-item cleanup guard
canonical DEV Git source → MANIFEST installer → protected installed CODEX_HOME;
versioned skill-sources → hash-verified runtime Skills
```

Source inventory: 13 versioned agent role files; nine versioned Skills in
`skill-sources/registry.toml`; 15 existing non-test Python tools plus this new CLI;
three hook implementations behind `hooks.json`; 285 manifest entries after this delta.
The recommended config defines OpenAI docs, Context7 and disabled GitHub MCP examples;
it is not active config. `codex mcp list` in this host surfaced host-level
`cua_repl` and `node_repl` enabled, `codex_app` disabled/unsupported; it did not
prove activation of recommended Context7/OpenAI docs/GitHub entries. Its env values were
masked. No versioned RAG/vector index, knowledge graph, semantic cache, Error Atlas,
event bus or global action log was found in the tracked DEV source. Installed runtime
databases/caches were deliberately not inventoried or read as Git artifacts.

Canonical ownership:

| Concern | Owner | Projection/consumer |
|---|---|---|
| Global rules/roles/hooks/tools and source Skills | `~/codex-dev` Git, `skill-sources/` for Skill body | manifest installed `~/.codex`, hash-verified `~/.agents/skills` |
| Product behavior and project deltas | independent product Git root + valid bridge marker | global framework, when adopted |
| Requirements and decisions | `specs/`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md` | roadmap/stage references |
| Current stage, checkpoint, blockers, NEXT | selected `prompts/STAGES.md` record | SessionStart/handoff |
| Capability and Skill routing | `skill-sources/registry.toml` + `tools/spec_execution.py` | selected bounded route |
| Prompt cleanup | `rules/prompt-queue-lifecycle.md` + `tools/prompt_queue.py` | exact Notion adapter/receipt |
| Project AI economics observations | opt-in `<project>/.metrics`, schema/profiler in DEV | project report |
| Global sanitized action observations | opt-in ignored journal directory; schema + `tools/global_action.py` in DEV | repeat analysis only |
| Script discovery metadata | `schemas/script-registry.json`; implementation remains each `tools/*.py` | read-only lookup |
| Installed config, credentials, sessions, plugin/cache state | Codex host/user layer | never Git ownership |

Duplication/drift review: `ai_policy_profiler.py` records comparable project policy economics
and does not own global mechanical action frequency. The journal has a distinct opt-in
runtime boundary. `docs/notes/LEARNING_LOG.md` is explicitly frozen historical material,
while `docs/LEARNING_LOG.md` is the active reusable diagnosis owner. Current STAGES has one
selector and one selected record; no second task-state file was introduced. Historical
roadmap/test counts describe earlier checkpoints and must not be used as current evidence.
Recommended MCP config differs from this host's active discovery; runtime activation
must be checked per dependent task.

## Gap matrix — all 24 phases

Legend: `EXISTS_GOOD`, `EXISTS_PARTIAL`, `DUPLICATED`, `DRIFTED`, `MISSING`,
`SHOULD_AUTOMATE`, `SHOULD_REMOVE`. These are observed source maturity, not
an instruction to add every advanced component.

| Phase | Status | Observation / concrete owner or next gate |
|---|---|---|
| 0 Discovery | EXISTS_PARTIAL | Git/manifest, roles, routes, validators mapped here; host capability health remains task-specific |
| 1 Instructions/context architecture | EXISTS_PARTIAL | AGENTS cascade, selected stage, Skill router and context budget exist; RAG/graph/cache absent |
| 2 Global Action Journal | SHOULD_AUTOMATE → EXISTS_PARTIAL | explicit bounded `global_action.py` init/record/validate; no automatic capture |
| 3 Repeat Detector | SHOULD_AUTOMATE → EXISTS_PARTIAL | pure `detect` over validated events and `schemas/repeat-detector.json`; two safe real actions produced one candidate |
| 4 Script Factory/Registry | EXISTS_PARTIAL | 15 existing tools plus journal CLI cataloged; exact reuse preflight works, novel promotion remains reviewed |
| 5 Promotion/demotion | EXISTS_PARTIAL | pure candidate/placement/lifecycle in `spec_execution.py`; quarantine requires implementation evidence |
| 6 Replay/idempotency | EXISTS_PARTIAL | CME, installer and queue guard have receipts; new journal ID duplicate/no-op and read-back; no generic replay executor |
| 7 Authority/TTL/GC | EXISTS_PARTIAL | context owner/order existed; explicit freshness and read-only cleanup policy added to `docs/CONTEXT_POLICY.md` |
| 8 Context contracts | EXISTS_PARTIAL | Skill metadata and bounded stage contract exist; common agent/tool `requires/forbidden` schema is proposed below |
| 9 Observability | EXISTS_PARTIAL | selected STAGES evidence and opt-in profiler; new action event metadata, no host model spans/token feed |
| 10 Cost ledger | MISSING | no comparable before/after observations; do not fabricate savings |
| 11 Validators/guardrails | EXISTS_GOOD | manifest/context/global/overlay validators, destructive hook, privacy tests; registry/journal targeted tests added |
| 12 Evals | EXISTS_PARTIAL | 403 source unit/contract tests + 7 platform skips; automation outcome/false-positive evals deferred |
| 13 Sandbox/security | EXISTS_PARTIAL | host sandbox/approvals and guarded source installer; journal rejects secret-like strings; host permission matrix is contextual |
| 14 Planner/orchestration | EXISTS_GOOD | one CME controller, dependency graph, stop/handoff; no second scheduler |
| 15 Human checkpoints | EXISTS_GOOD | destructive/merge/install/cleanup boundaries in governance and queue guard |
| 16 Skills lifecycle | EXISTS_PARTIAL | registry/versioned source/hash sync/retirement preflight; routine per-Skill eval scores absent |
| 17 Error Atlas | MISSING | reusable diagnosis has active `LEARNING_LOG`, no structured failure-signature index; candidate only after recurrence |
| 18 Task/prompt queue | EXISTS_GOOD | exact-item guard/receipt; selected STAGES remains state owner |
| 19 Event bus/DAG | EXISTS_PARTIAL | CME DAG exists; no event bus; observed volume does not justify broker |
| 20 Semantic cache | MISSING | no evidence of stable high-cost repeats; only versioned local cache if later measured |
| 21 Script/tool preflight | SHOULD_AUTOMATE → EXISTS_PARTIAL | `global_action.py lookup <task_class>` returns active exact-path tool; caller still checks Skill/MCP/runtime health |
| 22 Portability/recovery | EXISTS_PARTIAL | `dev_paths`, `dev-contract.toml`, wrappers, manifest installer/rollback; journal events intentionally device-local |
| 23 Schema versioning | EXISTS_PARTIAL | existing stage/telemetry versions; new event/catalog v1 fail closed; no migration needed yet |
| 24 Dependency-safe implementation | EXISTS_PARTIAL | Stages A/B/C source slices locally validated; integration/runtime parity are later gates |

Risk-ranked findings:

- **P0:** none demonstrated by source/tests. Unverified runtime activation is a gate,
  not a reason to mutate protected host config.
- **P1:** global action frequency had no safe durable observation surface; Stage A closes
  explicit capture in this branch. It is not active runtime until manifest install.
  Repeat/cost claims need real event samples and error false-positive checks.
- **P2:** structured Error Atlas and common agent/tool context-contract metadata are
  absent; add only after measured recurrence or an actual route gap. Hook events beyond
  SessionStart/SubagentStart/PreToolUse are absent, but automatic capture would introduce
  privacy/latency risks without telemetry evidence.
- **P3:** RAG/graph/event bus/semantic cache and broad source garbage collection are
  optional research surfaces; there is no present source evidence that their maintenance
  cost is justified.

## Target architecture and staged execution

```text
USER / TASK
  ↓ nearest instructions + DEV path/stage classifier
  ↓ Script Registry lookup + Skill registry + task-specific MCP/health preflight
  ↓ Context Router (authority, freshness, budget, selected state)
  ↓ existing Model Router + CME Planner/Orchestrator
  ↓ agents, documented CLI/tools/MCP, sandbox/hooks/validators
  ↓ tests/evidence → selected STAGES/NEXT
  ↓ explicit sanitized Global Action Journal
  ↓ configurable Repeat Detector (pure candidate output)
  ↓ existing spec_execution promotion/placement decision
  ↓ human-reviewed Script Factory implementation + tests/registry update
  ↺ future exact tool preflight; regressions → quarantine/fallback/reverify
```

Backward-complete roadmap:

1. `DEV-GAJ-A`: explicit journal, exact Script Registry, read-only lookup and
   source/test validation. Working consumer path exists without later stages.
2. `DEV-GAJ-B`: pure Repeat Detector over validated v1 events. Current config:
   exact recurrence >=2, equivalent normalized pattern >=3, expensive repeated
   reasoning >=2; all configurable by versioned config, zero samples yields no
   candidate. Group failures separately. Safety-sensitive signatures always need
   human review. Candidate has SHA-256 signature, count, event IDs, risk,
   approximate effort if observed, proposed target and no source payload.
3. `DEV-GAJ-C`: `global_action.py preflight` reuses an active catalog entry only
   on exact executor name + task class and when safety review is not required.
   The two real source-validator events returned `reuse_existing`.
   Novel or sensitive candidates route to existing `spec_execution.py`
   promotion/placement and human review; choose shell/PowerShell/Python/Node/
   CLI/library/hook/service/MCP only when inputs, side effects, platform and
   risk justify it. New tool needs
   `--help`, applicable dry-run, bounded errors, idempotency, tests, version,
   registry entry, rollback and fallback. Regression moves catalog status to
   `quarantined`; lookup excludes it until reverified. No automatic creation,
   destructive/security promotion or retirement.

Action event v1 fields and limits are in `schemas/global-action-event.schema.json`
and executable validation in `global_action.py`. Raw command arguments,
prompts, source/output, environment and model reasoning are excluded.
Event ID is the idempotency key; SHA-256 input fingerprint is supplied from
safe normalized facts, not computed from credentials. An incomplete/oversized
log fails closed. Schema-version changes require explicit reader migration.
The journal is opt-in ignored runtime data, never checked into DEV Git.

Script Registry v1 is `schemas/script-registry.json`: exact path, version,
purpose, task classes, inputs/outputs/side effects, idempotency, dry-run, risk,
platform/dependencies, repeat signature/event provenance, last verification,
status, fallback and check refs. Lookup never executes a listed command.
The current 16 entries catalog the 15 pre-existing tools and this tested
journal/lookup/detector CLI.

Context contract proposal for later additive metadata:
`requires, optional, forbidden, produces, state_reads, state_writes, tools,
evidence, context_budget, freshness_requirements`. Stage/SPEC/Skill owner
references remain IDs, not copied bodies. Any `forbidden` vs `requires`
conflict fails closed. Project registry stores only project/domain delta.

Source authority and TTL: live Git/code/test evidence for current facts;
approved SPEC/ADR for requirements; selected STAGES for execution truth;
official docs for external/version facts; old report/chat/model inference
only as leads. Git/status/port/process/queue membership/permissions/runtime
activation are fetched immediately before dependent action. Version/API
facts are verified before implementation. SPEC/ADR persist until revision.
Ephemeral tokens/sessions are never retained. See canonical
`docs/CONTEXT_POLICY.md`.

Context Garbage Collector policy: read-only scan of exact known owners and
references, classify stale/superseded/shadow/unknown, issue a narrow proposed
migration with backup/rollback, then validate references, Git status and
runtime parity. No age-based deletion or search-result deletion. Notion
exact-item cleanup continues through its independent fresh guard.

Capability/sandbox matrix:

| Capability | Active evidence / boundary | Write gate |
|---|---|---|
| DEV source scripts | 15 cataloged existing files; CI/source tests verify code, not host install | isolated branch + tests |
| Hooks | three versioned implementations and `hooks.json`; source-only proof | installed manifest + host discovery |
| MCP | host `codex mcp list` showed two enabled host surfaces and one disabled; recommendation lists three separate entries | no source config overwrite |
| Product overlays | independent Git roots with structured bridge only | per-project approval/contract |
| Installed `~/.codex` | protected config/auth/sessions/plugins/cache; managed manifest source | explicit installer apply and read-back |
| External Notion queue | exact source/parent fetched; prompt cleanup guard | fresh exact-item attestation after overall DoD |
| Journal runtime | explicit ignored local directory, no hook | caller opt-in init/record |
| Destructive/merge/push/deploy | governance/hook/sandbox gates | separate explicit authorization |

Evals/observability plan: keep existing CI full suite/manifest gates; add
malicious event, duplicate ID, corrupt log, missing/duplicate catalog paths,
unknown class fallback and cross-platform newline cases. For B, test exact/
equivalent/failure recurrence, configured thresholds, false positives,
quarantine exclusion and no unsafe auto-promotion. Compare only compatible
task classes and real before/after outcomes. Metrics are
`repeated_manual_actions, candidates, verified_scripts, reuse_count,
LLM_calls_avoided, tokens_avoided, cost_saved, latency_saved,
failure_rate_before_after, maintenance_cost`; all cost/token/savings
values are **unknown** without source observations. Never log private
chain-of-thought.

Recovery: clone/pull verified `dev-contract.toml` source, resolve role paths
with `dev_paths.py`, run source manifest/full tests, dry-run/install the
managed layer through existing wrappers, validate installed parity and Skill
hashes, then check project bridge/selected STAGES. Runtime credentials are
restored by the user's host mechanism, not copied from Git. Journal events
are optional device-local evidence; exporting them requires a separate
redacted/verified transfer and is not needed for critical stage recovery.

## Evidence ledger and canonical NEXT

| Check | Result | Scope |
|---|---|---|
| Notion fetch source + parent | PASS | exact item/queue identity and full source |
| Notion parent status update/read-back | PASS, `PARTIAL / SOURCE VALIDATED / RETAINED`; all child-page neighbors unchanged, source exists | external queue projection only |
| Fresh exact-item Notion guard/operation/read-back | PASS, `allowed → cleaned → noop`; source page `deleted`, queue `20 → 19`, all neighbor URLs/order unchanged | authorized exact master cleanup; receipt record SHA-256 `758f8608d68f3d637e4f20a3e0df04b8846dbeabe39eb707815fd2e44fae53c8` |
| Git source status before edit | PASS | clean `main`; isolated worktree created |
| `py -3 -B -m unittest tools.test_global_action` | PASS, 6 tests | journal consumer/negative/lookup/detector/limit path |
| `py -3 -B tools/global_action.py catalog` | PASS, 16 scripts | exact registry validation |
| `py -3 -B tools/global_action.py lookup source-validation` | PASS | existing validator selected |
| `py -3 -B -m unittest discover -s tools -p "test_*.py"` | PASS, 403 tests, 7 platform skips | source suite |
| `py -3 -B tools/validate_context.py` | PASS, 285 manifest files after staging | tracked source integrity |
| isolated `install_global.py --dry-run` | PASS, no destination/Skill changes | source-only manifest consumer |
| Local fast-forward merge and post-merge suite/manifest | PASS, `c81174a → 0884495`; 403 tests / 7 skips; 285 files | canonical source `main` |
| GitHub push/read-back | PASS, `origin/main` at `acc30c3`; fresh remote heads contain only `main` | published DEV source; no remote feature deletion needed |
| canonical-source active installer dry-run | PASS, 16 managed file changes plus ledger planned; protected runtime skipped, no writes | active-layer preview |
| `git diff --cached --check` | PASS | whitespace |
| Active runtime install/parity | PASS, 253 managed files, 10 Skill sources; protected runtime preserved; immediate `[no changes]` dry-run | active installed DEV layer |
| Installed `~/.codex/tools/global_action.py catalog` | PASS, 16 scripts | actual runtime CLI consumer |
| real opt-in `init → record ×2 → detect → preflight` | PASS, 1 exact candidate, `reuse_existing` | live CLI → ignored journal → existing script lookup |
| `master_execution.py .` | PASS, `complete` / `DEV-GAJ-D verified` | one selected STAGES/master graph |
| `spec_execution.py route` | PASS, `dev-karkas` selected | stage-first relevant-only capability route |
| Live cost/token savings | UNKNOWN: two validations carry no cost/token baseline | no fabricated economics |

Files in Stages A/B/C delta: `specs/features/global-action-journal.spec.md`,
`schemas/global-action-event.schema.json`, `schemas/script-registry.json`,
`schemas/repeat-detector.json`,
`tools/global_action.py`, `tools/test_global_action.py`,
`README.md`, `docs/ARCHITECTURE.md`, `docs/CONTEXT_COMPATIBILITY.md`,
`docs/CONTEXT_POLICY.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md`,
`docs/SECURITY.md`, `docs/TESTING.md`, this audit record,
`MANIFEST.txt`, and `prompts/STAGES.md`.
Local merge and GitHub push are evidenced; no deployment is implied.

Canonical NEXT: execution DoD, runtime parity and exact Notion cleanup passed.
No further `DEV-GAJ-001` slice remains; await an explicitly selected DEV prompt.
The local receipt at
`~/Documents/Codex/2026-09-15/dev-global-ai-context-automation-script/work/queue_receipt.json`
records execution/source IDs, before/after membership and read-back at
`2026-09-15T10:06:50Z`.

Automation maturity at this checkpoint: nine versioned Skills; 16 cataloged
scripts including one new explicit CLI; verified active-host runtime
tools for this new capability: one; observed automation candidates:
one exact-repeat candidate, safely resolved to an existing script;
quarantined scripts: zero. Instructions-only procedures are not
meaningfully countable from source text without an agreed unit; report
`unknown`. Top repeated action in this **two-event audit sample**:
`source_manifest_validation` ×2; no claim about global frequency.
Stages A/B/C promotions made: explicit action recording, exact
verified-source script discovery, pure repeat candidate mining and
exact existing-script reuse preflight.
