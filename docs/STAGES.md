# DEV / КАРКАС — stages и execution state

- Stage ID: `DEV-GAJ-D`
- Sequence: `DEV-GAJ-A → DEV-GAJ-B → DEV-GAJ-C → DEV-GAJ-D`
- NEXT: no additional slice; await an explicitly selected DEV prompt.

## DEV-GAJ-D — Global AI Context integration/runtime gate

- Status: `verified`; `DEV-GAJ-A..D` and master execution `completed`,
  integrated and pushed to GitHub `origin/main`.
  Exact-item Notion cleanup `cleaned` with read-back receipt.
- Source: Notion queue `3d061ed8-f246-8163-b502-d1829668063c`, item
  `3db61ed8-f246-81d7-bc79-fba7f8d03a41`, revision
  `2026-09-14T20:47:07.483Z`; exact child deleted after guard `allowed`;
  source page marked `deleted`, queue membership `20 → 19`, all neighbors unchanged.
- Historical branch/worktree: `feature/global-ai-context-audit` /
  `~/Documents/Codex/2026-09-15/dev-global-ai-context-automation-script/work/dev-audit-worktree`;
  both cleaned after integration. Current `main`/`origin/main` at
  `acc30c351d4b8a5a019a454e8b1e52d43f720a14`.
- Requirements: `GAJ-001..007`; contract:
  `specs/features/global-action-journal.spec.md`; audit/evidence:
  `docs/notes/GLOBAL_AI_CONTEXT_AUDIT.md`.
- Consumer: two real manifest checks → sanitized `record ×2 → detect`
  one candidate → `preflight` reused `tools/validate_context.py`.
- PASS: post-merge 403 tests / 7 platform skips; 285-file manifest;
  active installer apply/read-back, 253 managed files, 10 Skill sources,
  immediate `[no changes]` dry-run and installed 16-script CLI consumer;
  protected config/credentials/sessions/cache/plugins preserved;
  six focused tests; 16-script catalog; CLI read-back; whitespace,
  master controller `complete`, queue guard `cleaned → noop` and relevant-only
  `dev-karkas` route. Receipt record SHA-256 `758f8608d68f3d637e4f20a3e0df04b8846dbeabe39eb707815fd2e44fae53c8`.
- GitHub read-back: `origin/main` at `acc30c3`; only remote head `main`.
- Limits: no deployment; cost saving unknown.

### Действия пользователя

- `USER-DEV-STAGES-INTEGRATION` — `DONE`: user authorized merge of the exact
  `feature/docs-stages-canonical` branch and active-runtime installer apply;
  `main` fast-forwarded to `19c2974` and pushed. Post-merge evidence: 407
  tests PASS (7 platform skips), 285-file context PASS, manifest installer
  applied 253 managed files and synchronized 10 versioned Skill sources.
  Active `~/.codex/docs/STAGES.md` hash equals source, retired managed
  `~/.codex/prompts/STAGES.md` is absent, repeat dry-run reports no changes,
  and privileged runtime validator reports no issues. Protected config,
  credentials, sessions, cache and plugins were preserved. GitHub `main`
  tree read-back contains `docs/STAGES.md` only.
- `USER-DEV-GAJ-MERGE` — `DONE`: user authorized local merge and later worktree
  removal; fast-forward `c81174a → 0884495`, clean ancestry and post-merge
  403 tests / 7 skips plus 285-file manifest PASS. Canonical source integrated;
  temporary worktree and merged feature branch cleaned.
- `USER-DEV-GAJ-RUNTIME` — `DONE`: user separately authorized manifest-managed
  apply from `~/codex-dev` into active `~/.codex`; installer validation PASS,
  253 managed files, 10 Skill sources, protected runtime preserved; immediate
  dry-run `[no changes]` and installed CLI catalog PASS (16 scripts).
- `USER-DEV-GAJ-CLEANUP` — `DONE`: user allowed deleting the Notion prompt
  after execution. Fresh source/parent fetch matched revision/membership;
  guard `allowed`; targeted child operation removed only this item; read-back
  showed source `deleted`, `20 → 19` members and unchanged neighbors; receipt
  `cleaned` at `2026-09-15T10:06:50Z`, repeat guard `noop`.
- `USER-DEV-GAJ-PUSH` — `DONE`: user authorized push to GitHub and deletion
  of already merged remote feature branches. `git push origin main` PASS; fresh
  `ls-remote --heads` shows `origin/main=acc30c3` and no feature heads, so no
  remote deletion was needed.

```master-execution
{"schema_version":2,"state_revision":6,"master":{"id":"DEV-GAJ-001","status":"completed","source":{"backend":"notion","queue_id":"3d061ed8-f246-8163-b502-d1829668063c","item_id":"3db61ed8-f246-81d7-bc79-fba7f8d03a41","revision":"2026-09-14T20:47:07.483Z","prompt_type":"master_prompt","retention":"auto"}},"tracks":[{"id":"global-ai-context","repository":"~/codex-dev","worktree":"~/Documents/Codex/2026-09-15/dev-global-ai-context-automation-script/work/dev-audit-worktree","branch":"feature/global-ai-context-audit","checkpoint":"e7a29c71e936b4fd36a8dd16ddd3be13957113a9","ownership":["GAJ source"],"status":"closed"}],"slices":[{"id":"DEV-GAJ-A","master_id":"DEV-GAJ-001","title":"DEV-GAJ-A","status":"verified","predecessors":[],"dependencies":[],"worktree_track":"global-ai-context","checkpoint_before":"c81174a705781d311e9d362a7b42c066a41a7750","checkpoint_after":"60583245ec748f7b7204d9120b7e278911010816","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["GAJ SPEC","targeted evidence"],"requirements":["GAJ-001","GAJ-002","GAJ-003","GAJ-004","GAJ-005"],"capabilities":["project.framework.governance"],"model_class":"MEDIUM","reasoning_effort":"high","stop_after":false},{"id":"DEV-GAJ-B","master_id":"DEV-GAJ-001","title":"DEV-GAJ-B","status":"verified","predecessors":["DEV-GAJ-A"],"dependencies":[],"worktree_track":"global-ai-context","checkpoint_before":"c81174a705781d311e9d362a7b42c066a41a7750","checkpoint_after":"60583245ec748f7b7204d9120b7e278911010816","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["GAJ SPEC","targeted evidence"],"requirements":["GAJ-006"],"capabilities":["project.framework.governance"],"model_class":"MEDIUM","reasoning_effort":"high","stop_after":false},{"id":"DEV-GAJ-C","master_id":"DEV-GAJ-001","title":"DEV-GAJ-C","status":"verified","predecessors":["DEV-GAJ-B"],"dependencies":[],"worktree_track":"global-ai-context","checkpoint_before":"c81174a705781d311e9d362a7b42c066a41a7750","checkpoint_after":"60583245ec748f7b7204d9120b7e278911010816","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["GAJ SPEC","targeted evidence"],"requirements":["GAJ-007"],"capabilities":["project.framework.governance"],"model_class":"MEDIUM","reasoning_effort":"high","stop_after":false},{"id":"DEV-GAJ-D","master_id":"DEV-GAJ-001","title":"Finalization gate","status":"verified","predecessors":["DEV-GAJ-C"],"dependencies":[],"worktree_track":"global-ai-context","checkpoint_before":"60583245ec748f7b7204d9120b7e278911010816","checkpoint_after":"0884495397a979a47087687d187fd028512fb315","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["merge/runtime parity"],"requirements":[],"capabilities":["project.framework.governance"],"model_class":"MEDIUM","reasoning_effort":"high","stop_after":true}],"blockers":[{"id":"global-ai-context-integration","class":"pre_existing","status":"resolved","blocking":false,"owner":"agent","evidence":"user authorized; local main fast-forward at 0884495; post-merge 403 tests/7 skips and 285-file manifest PASS"},{"id":"global-ai-context-runtime-parity","class":"pre_existing","status":"resolved","blocking":false,"owner":"agent","evidence":"explicit apply authorized; installer validated 253 managed files/10 Skill sources; immediate no-change dry-run and installed 16-script CLI PASS"}],"decisions":["sanitized-opt-in","reuse-existing-promotion","no-automatic-hook","notion-exact-item-cleaned","github-main-pushed"],"context_budget":{"max_chars":7000,"max_items":14,"max_contours":5,"max_decisions":5,"max_evidence_threads":6},"next_action":"await an explicitly selected DEV prompt; DEV-GAJ-001 has no remaining slice","integration":{"required":false,"reason":"local main fast-forward integrated at 0884495"}}
```

NEXT: await an explicitly launched DEV prompt; no autonomous slice or queue
cleanup remains for `DEV-GAJ-001`.



Этот файл — единственный canonical execution-state owner global DEV. Requirements принадлежат
SPEC, долговременный порядок — `docs/ROADMAP.md`, architecture/decisions — своим владельцам.

## DEV-REPLACEABILITY-D — Replaceable Modules Final Review + Integration

- Status: `verified`
- Lifecycle state: `completed`
- Evidence level: global `L1,L2,L3`; Electro Tutor product `L1,L2,L3,L5`.
- Source: Notion queue `3d061ed8f2468163b502d1829668063c`, item
  `3da61ed8f2468198b889d629331a310e`, revision `2026-09-13T10:15:22.756Z`.
- Prompt type / retention: `master_prompt` / `auto` (ONE-SHOT cleanup only after overall DoD).
- Prompt Queue cleanup: `cleaned`; record
  `5a290320a69a30979664efdf0e3c20348b27d709b927541c89415be5fe865fc3`; full source/parent
  read-back confirmed the source deleted and all 22 neighboring queue pages preserved; receipt
  replay returned `noop / verified_previous_cleanup`.
- Branch/worktree: `main` / `~/codex-dev`; the integrated feature worktree was removed after
  ancestry and cleanliness checks.
- Checkpoint before: `040c51a442cde48df00d7662ca2552b304b8daac`; implementation checkpoint:
  `28da49b099a2c9a614f8fd9fb560c2e5b5121be3`.
- Requirements: `FR-015`; acceptance: `AC-018`; global policy owner:
  `rules/replaceable-modules.md`.
- Inventory: 21 owned GitHub repositories, four PRIMARY ACTIVE local repositories, 17 remote-only
  UNKNOWN repositories. Exact classification and scores: `docs/notes/REPLACEABILITY_AUDIT.md`.
- P0 result: user-approved `ET-RTC-001` isolated Jitsi behind a system-owned meeting port on
  `feature/et-rtc-provider-boundary`; implementation `9a91884`, completed state `c3481ed`, local
  `main` integration/state `e1527e6`, final correctness/security reviews no findings.
- Deferred: P1 MathMorph composition cleanup, Electro Tutor test-helper naming and artifact-storage
  migration rehearsal; provider changes and production migrations are separate scopes.

### Действия пользователя

- `USER-DEV-RUNTIME-INSTALL` — `DONE`: user explicitly approved persistent rematerialization of
  merged DEV from `~/codex-dev` into active `~/.codex`; 246 managed files reconciled, protected
  runtime paths preserved, validation PASS and the immediate dry-run returned `[no changes]`.
- `USER-DEV-REPLACEABILITY-INTEGRATION` — `DONE`: user explicitly approved both merges. Electro
  Tutor local `main=e1527e6`; global DEV local `main` contains `a196b89`; three verified temporary
  worktrees were removed. No push, provider switch, migration or deploy occurred.

```master-execution
{"schema_version":2,"state_revision":8,"master":{"id":"DEV-REPLACEABILITY-001","status":"completed","source":{"backend":"notion","queue_id":"3d061ed8f2468163b502d1829668063c","item_id":"3da61ed8f2468198b889d629331a310e","revision":"2026-09-13T10:15:22.756Z","prompt_type":"master_prompt","retention":"auto"}},"tracks":[{"id":"replaceability-global","repository":"~/codex-dev","worktree":"~/codex-dev","branch":"main","checkpoint":"f4402293ea90428e12f3d41b3ef524378849ef4c","ownership":["rules/replaceable-modules.md","FR-015/AC-018","replaceability audit"],"status":"closed"}],"slices":[{"id":"DEV-REPLACEABILITY-A","master_id":"DEV-REPLACEABILITY-001","title":"Canonical global contract","status":"verified","predecessors":[],"dependencies":[],"worktree_track":"replaceability-global","checkpoint_before":"040c51a442cde48df00d7662ca2552b304b8daac","checkpoint_after":"28da49b099a2c9a614f8fd9fb560c2e5b5121be3","required_evidence":["L1","L2"],"evidence":["L1","L2"],"context_scope":["FR-015","AC-018","architecture policy","global routes"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false,"requirements":["FR-015"],"capabilities":["project.framework.governance","change.review"]},{"id":"DEV-REPLACEABILITY-B","master_id":"DEV-REPLACEABILITY-001","title":"Primary repository inventory and scoring","status":"verified","predecessors":["DEV-REPLACEABILITY-A"],"dependencies":[],"worktree_track":"replaceability-global","checkpoint_before":"040c51a442cde48df00d7662ca2552b304b8daac","checkpoint_after":"28da49b099a2c9a614f8fd9fb560c2e5b5121be3","required_evidence":["L1"],"evidence":["L1"],"context_scope":["local Git inventory","GitHub owner inventory","primary repository architecture"],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false,"requirements":["FR-015"],"capabilities":["project.framework.governance"]},{"id":"DEV-REPLACEABILITY-C","master_id":"DEV-REPLACEABILITY-001","title":"Safe P0 product retrofit","status":"verified","predecessors":["DEV-REPLACEABILITY-B"],"dependencies":[],"worktree_track":"replaceability-global","checkpoint_before":"28da49b099a2c9a614f8fd9fb560c2e5b5121be3","checkpoint_after":"e1527e62799796df96ae11ff39a2c6b7316f7f16","required_evidence":["L1","L2","L3","L5"],"evidence":["L1","L2","L3","L5"],"context_scope":["Electro Tutor RTC facade","Jitsi adapter","component contract"],"model_class":"HIGH","reasoning_effort":"high","stop_after":true,"requirements":["FR-015"],"capabilities":["change.review"]},{"id":"DEV-REPLACEABILITY-D","master_id":"DEV-REPLACEABILITY-001","title":"Overall review, integration and queue cleanup","status":"verified","predecessors":["DEV-REPLACEABILITY-C"],"dependencies":[],"worktree_track":"replaceability-global","checkpoint_before":"a196b8976014412770e5920dc9c2fb37b6e81e5b","checkpoint_after":"f4402293ea90428e12f3d41b3ef524378849ef4c","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["completion documentation gate","Notion exact-item cleanup"],"model_class":"HIGH","reasoning_effort":"high","stop_after":true,"requirements":["FR-015"],"capabilities":["change.review","project.framework.governance"]}],"blockers":[{"id":"electro-tutor-default-branch","class":"environment_unavailable","status":"resolved","blocking":false,"owner":"agent","evidence":"explicit fetch restored origin/main at 2c63e2862490eeaac8ce625852b2ae4bb0a9c84d"},{"id":"electro-tutor-stage-authority","class":"pre_existing","status":"resolved","blocking":false,"owner":"user","evidence":"user approved ET-RTC-001 and rtc-provider-boundary.spec.md; local main integration e1527e6 verified"},{"id":"integration-approval","class":"pre_existing","status":"resolved","blocking":false,"owner":"user","evidence":"user explicitly approved and local Electro Tutor/global DEV merges completed; temporary worktrees removed"},{"id":"runtime-install-approval","class":"pre_existing","status":"resolved","blocking":false,"owner":"user","evidence":"user explicitly approved persistent install; 246 managed files reconciled, protected runtime state preserved and immediate dry-run reported no changes"}],"decisions":["single-global-policy-owner","no-brittle-generic-regex-lint","replaceability-queue-cleaned","local-integration-completed","merged-runtime-parity-verified"],"context_budget":{"max_chars":7000,"max_items":14,"max_contours":5,"max_decisions":5,"max_evidence_threads":6},"next_action":"await a new explicitly approved DEV stage; completed queue source is deleted and reusable sources remain retained","integration":{"required":false,"reason":""}}
```

### Runnable slice / consumer path

Global router loads one canonical Replaceable Module Contract for a provider-bound architecture
change; dev-karkas and project framework route to it without copying the normative checklist.
Structural tests verify delivery, while product runtime/contract suites remain the evidence owner.

### Verification / stop

- PASS: 16 focused policy/i18n/master tests; 397 full tests with 7 expected platform skips;
  `tools/validate_context.py` over 278 files; staged diff whitespace review.
- PASS: user-approved merged canonical-source runtime apply reconciled 246 managed files,
  preserved protected config/credentials/sessions/cache/plugins and produced idempotent
  `[no changes]` read-back.
- PASS: Electro Tutor `ET-RTC-001` implementation/state checkpoints `9a91884`/`c3481ed`; local
  `main=e1527e6`; post-merge 110 unit/contract, Astro check, lint, 17-page build/audits and built-
  browser 46 PASS / 2 expected skips; final correctness and security reviews no findings.
- PASS: global DEV local `main` contains `a196b89`; post-merge 397 tests / 7 expected skips and
  context validator over 278 files; three clean integrated temporary worktrees removed.
- PASS: exact-item Prompt Queue cleanup returned `cleaned`, full Notion read-back preserved all 22
  neighbors, and receipt replay returned `noop / verified_previous_cleanup`.
- No push, provider switch, migration or deploy occurred.
- Overall project DoD and one-shot cleanup are complete; no push/deploy is implied.

NEXT: await an explicitly selected DEV prompt; reusable and incomplete queue sources remain retained.

## DEV-SEP-LAUNCHER-001 — Minimal User Launcher Evidence Hardening

- Status: `verified`
- Lifecycle state: `completed locally`
- Evidence level: `L1,L2,L3`
- Checkpoint: `8fecd6f87b16b508bdbbec1b9ffcfe0b1595a1c9`
- Branch/worktree: `main` / `~/codex-dev`.
- Implementation checkpoint: `f25903c`; launcher merge `bab847a`; user-actions policy merge
  `03c6acf`; post-merge state checkpoint `c4dff10`. Active-runtime materialization remains a
  separate explicit approval.
- Requirements: `SEP-012`; acceptance: `AC-SEP-G`, `AC-SEP-L`; CME recovery compatibility.
- Sources: retained Notion items `3d461ed8f246812db41cda2510a70dd3`,
  `3d561ed8f24681c0b8c6d06c1819bb4a` and reusable launcher
  `3d561ed8f246814f8430e7613f591153`. Cleanup guard result for each: `retain` because
  `master_prompt`/`reusable_template` has retention `keep`.

### Действия пользователя

- `USER-DEV-BRANCH-INTEGRATION` — `DONE`: пользователь явно разрешил объединить все DEV topic
  branches; remote `main`, launcher и durable user-actions policy включены в local `main`.
  Evidence: target-branch ancestry и post-merge checks.
- `USER-DEV-BRANCH-CLEANUP` — `DONE`: удалены два merged temporary worktree и шесть fully-merged
  local topic branches. Evidence: итоговый inventory содержит один worktree и только local `main`.
- `USER-DEV-MAIN-PUSH` — `DONE`: объединённая `main` опубликована; `HEAD` и `origin/main` равны
  `8fecd6f87b16b508bdbbec1b9ffcfe0b1595a1c9`. После fetch/prune remote inventory содержит только
  `origin/main`; remote topic branches отсутствуют.
- `USER-DEV-RUNTIME-INSTALL` — `DONE`: пользователь отдельно разрешил штатную manifest-driven
  установку canonical `~/codex-dev` в active `~/.codex`; 243 managed files reconciled, 21 actions,
  protected runtime paths preserved, повторный dry-run — `[no changes]`.

```master-execution
{"schema_version":2,"state_revision":3,"master":{"id":"DEV-SEP-LAUNCHER-001","status":"running","source":{"backend":"git","queue_id":"DEV-SEP-001","item_id":"dev-sep-launcher-evidence","revision":"f25903caf4f4d2c8fd068111d166a4c3d600a54a","prompt_type":"child_prompt","retention":"keep"}},"tracks":[{"id":"minimal-user-launcher","repository":"~/codex-dev","worktree":"~/codex-dev","branch":"main","checkpoint":"8fecd6f87b16b508bdbbec1b9ffcfe0b1595a1c9","ownership":["minimal-launcher","tools/spec_execution.py","tools/master_execution.py"],"status":"active"}],"slices":[{"id":"DEV-SEP-LAUNCHER-001","master_id":"DEV-SEP-LAUNCHER-001","title":"Minimal user launcher evidence hardening and integration handoff","status":"running","predecessors":[],"dependencies":[],"worktree_track":"minimal-user-launcher","checkpoint_before":"f25903caf4f4d2c8fd068111d166a4c3d600a54a","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["SEP-012","AC-SEP-G","AC-SEP-L","launcher recovery","integration handoff"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false,"requirements":["SEP-012"],"capabilities":["project.resume","project.framework.bootstrap"]}],"blockers":[],"decisions":["retain-protected-notion-sources","merge-approved-and-completed","active-runtime-apply-requires-separate-approval"],"context_budget":{"max_chars":6000,"max_items":12,"max_contours":5,"max_decisions":4,"max_evidence_threads":6},"next_action":"await separate explicit active-runtime installation approval","integration":{"required":false,"reason":""}}
```

### Runnable slice / consumer path

`NEW_PROJECT` produces a bounded project-framework handoff without writes; a materialized fixture
is then resumed through the same short `CONTINUE_EXISTING` entrypoint. Existing projects resolve
exact DEV bridge → selected STAGES/CME state → live Git recovery → relevant-only capability route.
No selected record/master body, secret-like intake, command execution or global mutation is exposed.

### Verification / review / stop

- Full post-merge suite: 393 PASS, 7 expected platform skips.
- Launcher/CME/spec/path regressions: 140 PASS, 1 expected platform skip; final launcher/CME
  security subset: 67 PASS.
- Context validator: 275 files PASS; manifest-driven installer dry-run PASS with zero runtime
  writes; Python compile and staged diff check PASS.
- Independent correctness/release review: PASS. Independent security review: PASS.
- Completed: remote/local main reconciliation, launcher merge and user-actions policy merge.
- Completed: fully-merged local branch/worktree cleanup and GitHub `main` publication/read-back;
  remote topic branches are absent.
- Completed: user-approved active-runtime apply and idempotent read-back.
- Completed: exact Prompt Queue cleanup of absorbed HOTFIX item
  `3d661ed8f246819bbfebc7a6d92819e3`; guard record
  `dd87745a5f8fe9844fd186da163f657c59a198143fceeeff9512204224050967`, decision `cleaned`,
  source read-back `deleted`, all 23 neighboring child pages preserved.
- Not performed: deletion of reusable/partial/integration-gated prompts or external release.

NEXT: `DEV-SEP-LAUNCHER-001`

The retention-protected Notion prompts remain in place; future source changes require the same
manifest-driven rematerialization path.

## DEV-SEP-A — Canonical Contract + Compatibility Audit

- Status: `verified`; Lifecycle: `completed`; Evidence level: `validated locally`.
- Master: `DEV-SEP-001`; master status: `running`; track: `spec-execution-pipeline`.
- Worktree/branch: `~/Documents/Codex/2026-09-11/verify-global-dev-activation/work/spec-execution-pipeline` /
  `feature/spec-execution-pipeline`; checkpoint before:
  `89539840725ad57655a1f6e6ffe45ced874ce055`.
- Source: Notion master `3d561ed8-f246-81c0-b8c6-d06c1819bb4a`, revision
  `2026-09-08T19:51:49.477Z`, type `master_prompt`, retention `keep`.
- Requirements: `SEP-001..012`; acceptance: `AC-SEP-A..L` from
  `specs/features/specification-execution-pipeline.spec.md`.

```master-execution
{"schema_version":1,"state_revision":1,"master":{"id":"DEV-SEP-001","status":"running","source":{"backend":"notion","queue_id":"3d061ed8f2468163b502d1829668063c","item_id":"3d561ed8f24681c0b8c6d06c1819bb4a","revision":"2026-09-08T19:51:49.477Z","prompt_type":"master_prompt","retention":"keep"}},"tracks":[{"id":"spec-execution-pipeline","repository":"~/codex-dev","worktree":"~/Documents/Codex/2026-09-11/verify-global-dev-activation/work/spec-execution-pipeline","branch":"feature/spec-execution-pipeline","checkpoint":"89539840725ad57655a1f6e6ffe45ced874ce055","ownership":["specification-execution-pipeline","tools/spec_execution.py","skill-sources/registry.toml"],"status":"active"}],"slices":[{"id":"DEV-SEP-A","master_id":"DEV-SEP-001","title":"Canonical contract and compatibility audit","status":"running","predecessors":[],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"89539840725ad57655a1f6e6ffe45ced874ce055","checkpoint_after":"","required_evidence":["L1"],"evidence":[],"context_scope":["SEP SPEC","CME SPEC","global architecture","gap map"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-B","master_id":"DEV-SEP-001","title":"Intake and capability router core","status":"queued","predecessors":["DEV-SEP-A"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2"],"evidence":[],"context_scope":["SEP-001..006","stage selector","dev paths","model routing"],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-SEP-C","master_id":"DEV-SEP-001","title":"Traceability and placement validation","status":"queued","predecessors":["DEV-SEP-B"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP-005","SEP-008","CME state","project overlay validator"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-D","master_id":"DEV-SEP-001","title":"Automation detector and promotion lifecycle","status":"queued","predecessors":["DEV-SEP-C"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP-007..010","AEP policy","Prompt Queue boundary"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-E","master_id":"DEV-SEP-001","title":"Context metrics and gradual integration","status":"queued","predecessors":["DEV-SEP-D"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP-009..012","Skills","hooks","validators","workflow"],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-SEP-F","master_id":"DEV-SEP-001","title":"Acceptance and compatibility audit","status":"queued","predecessors":["DEV-SEP-E"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP acceptance","security","full regression","documentation sync"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false}],"blockers":[],"decisions":["extend-cme-not-replace","single-pure-stdlib-router","skill-source-registry-metadata-only","no-automatic-promotion"],"context_budget":{"max_chars":8000,"max_items":14,"max_contours":5,"max_decisions":5,"max_evidence_threads":6},"next_action":"verify DEV-SEP-A contract checkpoint, then select DEV-SEP-B","integration":{"required":false,"reason":""}}
```

### Scope / exclusions

In scope: approved feature SPEC, existing-primitive gap map, responsibility/architecture boundary,
progressive master graph and executable structural validation. Out of scope: tool implementation,
product rollout, runtime install/config, external queue mutation, merge, push and cleanup.

### Tasks / PASS

- [x] Exact Notion source and retention fetched; existing live state restored.
- [x] Existing CME/router/selector/Skill/profiler/queue/overlay primitives mapped to bounded gaps.
- [x] Approved behavior compiled into a feature SPEC with acceptance and rollback.
- [x] Architecture/ADR and six dependency-safe slices preserve existing canonical owners.
- [x] Master graph parses from the selected record and routes uniquely after checkpoint sync.
- [x] Context validator, 74 policy regressions and `git diff --check` PASS.

### Fallback / rollback

Invalid graph, source drift or documentation conflict blocks Slice B. Rollback is a Git revert of
this isolated contract checkpoint; no runtime, product or external state is mutated.

Completion evidence: checkpoint `87edde1`; selected master graph parsed as canonical/runnable;
74 CME/documentation/stage policy tests PASS; context validator 267 files PASS;
`git diff --cached --check` PASS. Architecture and gap-map reviews converged on the same bounded
stdlib core and no-second-owner design.

## DEV-SEP-B — Intake + Capability Router Core

- Status: `verified`; Lifecycle: `completed`; predecessor `DEV-SEP-A` verified at `87edde1`.
- Goal: add one bounded stdlib-only `spec_execution.py` core, Skill metadata registry, compact
  `CONTINUE_EXISTING`/`NEW_PROJECT` intake and relevant-only deterministic/model route.
- PASS: exact four new-project classes, mandatory stage/scope before Skill selection, minimal
  relevant route, typed ambiguity/failure and old-project compatibility tests.

```master-execution
{"schema_version":1,"state_revision":2,"master":{"id":"DEV-SEP-001","status":"running","source":{"backend":"notion","queue_id":"3d061ed8f2468163b502d1829668063c","item_id":"3d561ed8f24681c0b8c6d06c1819bb4a","revision":"2026-09-08T19:51:49.477Z","prompt_type":"master_prompt","retention":"keep"}},"tracks":[{"id":"spec-execution-pipeline","repository":"~/codex-dev","worktree":"~/Documents/Codex/2026-09-11/verify-global-dev-activation/work/spec-execution-pipeline","branch":"feature/spec-execution-pipeline","checkpoint":"87edde1ac222c692a96f1a1ebd418a840ded09a8","ownership":["specification-execution-pipeline","tools/spec_execution.py","skill-sources/registry.toml"],"status":"active"}],"slices":[{"id":"DEV-SEP-A","master_id":"DEV-SEP-001","title":"Canonical contract and compatibility audit","status":"verified","predecessors":[],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"89539840725ad57655a1f6e6ffe45ced874ce055","checkpoint_after":"87edde1ac222c692a96f1a1ebd418a840ded09a8","required_evidence":["L1"],"evidence":["L1"],"context_scope":["SEP SPEC","CME SPEC","global architecture","gap map"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-B","master_id":"DEV-SEP-001","title":"Intake and capability router core","status":"running","predecessors":["DEV-SEP-A"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"87edde1ac222c692a96f1a1ebd418a840ded09a8","checkpoint_after":"","required_evidence":["L1","L2"],"evidence":[],"context_scope":["SEP-001..006","stage selector","dev paths","model routing"],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-SEP-C","master_id":"DEV-SEP-001","title":"Traceability and placement validation","status":"queued","predecessors":["DEV-SEP-B"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP-005","SEP-008","CME state","project overlay validator"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-D","master_id":"DEV-SEP-001","title":"Automation detector and promotion lifecycle","status":"queued","predecessors":["DEV-SEP-C"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP-007..010","AEP policy","Prompt Queue boundary"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-E","master_id":"DEV-SEP-001","title":"Context metrics and gradual integration","status":"queued","predecessors":["DEV-SEP-D"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP-009..012","Skills","hooks","validators","workflow"],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-SEP-F","master_id":"DEV-SEP-001","title":"Acceptance and compatibility audit","status":"queued","predecessors":["DEV-SEP-E"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP acceptance","security","full regression","documentation sync"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false}],"blockers":[],"decisions":["extend-cme-not-replace","single-pure-stdlib-router","skill-source-registry-metadata-only","no-automatic-promotion"],"context_budget":{"max_chars":8000,"max_items":14,"max_contours":5,"max_decisions":5,"max_evidence_threads":6},"next_action":"implement and verify DEV-SEP-B intake and capability router core","integration":{"required":false,"reason":""}}
```

Completion evidence: checkpoint `6e9a76a`; 13 focused intake/registry/router/executor tests PASS;
315 full tests PASS with six expected platform skips; context validator 270 files PASS;
actual registry resolves nine versioned Skills and relevant-only `project.resume` route. Installed
runtime validation PASS after integration materialization; ten source Skills pass parity.

## DEV-SEP-C — Traceability + Placement Validation

- Status: `verified`; Lifecycle: `completed`; predecessor `DEV-SEP-B` verified at `6e9a76a`.
- Goal: add machine-enforced critical requirement/capability/evidence links and global/domain/project
  placement validation without a second execution owner.
- PASS: positive/negative trace, missing evidence and overlay-duplication scenarios; CME v1 remains
  readable if its schema receives additive v2 metadata.

```master-execution
{"schema_version":1,"state_revision":3,"master":{"id":"DEV-SEP-001","status":"running","source":{"backend":"notion","queue_id":"3d061ed8f2468163b502d1829668063c","item_id":"3d561ed8f24681c0b8c6d06c1819bb4a","revision":"2026-09-08T19:51:49.477Z","prompt_type":"master_prompt","retention":"keep"}},"tracks":[{"id":"spec-execution-pipeline","repository":"~/codex-dev","worktree":"~/Documents/Codex/2026-09-11/verify-global-dev-activation/work/spec-execution-pipeline","branch":"feature/spec-execution-pipeline","checkpoint":"6e9a76a826bff9b6c342cd801cbef2a3fc218afb","ownership":["specification-execution-pipeline","tools/spec_execution.py","skill-sources/registry.toml"],"status":"active"}],"slices":[{"id":"DEV-SEP-A","master_id":"DEV-SEP-001","title":"Canonical contract and compatibility audit","status":"verified","predecessors":[],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"89539840725ad57655a1f6e6ffe45ced874ce055","checkpoint_after":"87edde1ac222c692a96f1a1ebd418a840ded09a8","required_evidence":["L1"],"evidence":["L1"],"context_scope":["SEP SPEC","CME SPEC","global architecture","gap map"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-B","master_id":"DEV-SEP-001","title":"Intake and capability router core","status":"verified","predecessors":["DEV-SEP-A"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"87edde1ac222c692a96f1a1ebd418a840ded09a8","checkpoint_after":"6e9a76a826bff9b6c342cd801cbef2a3fc218afb","required_evidence":["L1","L2"],"evidence":["L1","L2"],"context_scope":["SEP-001..006","stage selector","dev paths","model routing"],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-SEP-C","master_id":"DEV-SEP-001","title":"Traceability and placement validation","status":"running","predecessors":["DEV-SEP-B"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"6e9a76a826bff9b6c342cd801cbef2a3fc218afb","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP-005","SEP-008","CME state","project overlay validator"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-D","master_id":"DEV-SEP-001","title":"Automation detector and promotion lifecycle","status":"queued","predecessors":["DEV-SEP-C"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP-007..010","AEP policy","Prompt Queue boundary"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-E","master_id":"DEV-SEP-001","title":"Context metrics and gradual integration","status":"queued","predecessors":["DEV-SEP-D"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP-009..012","Skills","hooks","validators","workflow"],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-SEP-F","master_id":"DEV-SEP-001","title":"Acceptance and compatibility audit","status":"queued","predecessors":["DEV-SEP-E"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP acceptance","security","full regression","documentation sync"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false}],"blockers":[],"decisions":["extend-cme-not-replace","single-pure-stdlib-router","skill-source-registry-metadata-only","no-automatic-promotion"],"context_budget":{"max_chars":8000,"max_items":14,"max_contours":5,"max_decisions":5,"max_evidence_threads":6},"next_action":"implement and verify DEV-SEP-C traceability and placement validation","integration":{"required":false,"reason":""}}
```

Completion evidence: checkpoint `f100e1b`; additive CME schema v2 with v1 compatibility; valid
critical trace and rejected missing-capability/evidence completion consumer paths; global duplicate
placement rejected. 24 SEP tests, 98 targeted tests and 326 full tests PASS with six expected skips;
context validator 270 files PASS.

## DEV-SEP-D — Automation Detector + Promotion Lifecycle

- Status: `verified`; Lifecycle: `completed`; predecessor `DEV-SEP-C` verified at `f100e1b`.
- Goal: detect only qualified repeatable opportunities and return deterministic target, placement,
  lifecycle/dedup decision; no auto-write/tuning.
- PASS: one-off/unknown rejection, repeated-validator promotion, dedup/closure and sanitized optional
  profiler/learning observations.

```master-execution
{"schema_version":2,"state_revision":4,"master":{"id":"DEV-SEP-001","status":"running","source":{"backend":"notion","queue_id":"3d061ed8f2468163b502d1829668063c","item_id":"3d561ed8f24681c0b8c6d06c1819bb4a","revision":"2026-09-08T19:51:49.477Z","prompt_type":"master_prompt","retention":"keep"}},"tracks":[{"id":"spec-execution-pipeline","repository":"~/codex-dev","worktree":"~/Documents/Codex/2026-09-11/verify-global-dev-activation/work/spec-execution-pipeline","branch":"feature/spec-execution-pipeline","checkpoint":"f100e1ba0155c24f8a783c3c0532484d29705cf9","ownership":["specification-execution-pipeline","tools/spec_execution.py","skill-sources/registry.toml"],"status":"active"}],"slices":[{"id":"DEV-SEP-A","master_id":"DEV-SEP-001","title":"Canonical contract and compatibility audit","status":"verified","predecessors":[],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"89539840725ad57655a1f6e6ffe45ced874ce055","checkpoint_after":"87edde1ac222c692a96f1a1ebd418a840ded09a8","required_evidence":["L1"],"evidence":["L1"],"context_scope":["SEP SPEC","CME SPEC","global architecture","gap map"],"requirements":["SEP-001","SEP-011"],"capabilities":["project.framework.governance"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-B","master_id":"DEV-SEP-001","title":"Intake and capability router core","status":"verified","predecessors":["DEV-SEP-A"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"87edde1ac222c692a96f1a1ebd418a840ded09a8","checkpoint_after":"6e9a76a826bff9b6c342cd801cbef2a3fc218afb","required_evidence":["L1","L2"],"evidence":["L1","L2"],"context_scope":["SEP-001..006","stage selector","dev paths","model routing"],"requirements":["SEP-002","SEP-003","SEP-004","SEP-006","SEP-012"],"capabilities":["project.resume","project.framework.bootstrap","stage.implement"],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-SEP-C","master_id":"DEV-SEP-001","title":"Traceability and placement validation","status":"verified","predecessors":["DEV-SEP-B"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"6e9a76a826bff9b6c342cd801cbef2a3fc218afb","checkpoint_after":"f100e1ba0155c24f8a783c3c0532484d29705cf9","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["SEP-005","SEP-008","CME state","project overlay validator"],"requirements":["SEP-005","SEP-008","SEP-011"],"capabilities":["stage.implement","change.review"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-D","master_id":"DEV-SEP-001","title":"Automation detector and promotion lifecycle","status":"running","predecessors":["DEV-SEP-C"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"f100e1ba0155c24f8a783c3c0532484d29705cf9","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP-007..010","AEP policy","Prompt Queue boundary"],"requirements":["SEP-007","SEP-008","SEP-009","SEP-010"],"capabilities":["project.framework.governance","change.review"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-E","master_id":"DEV-SEP-001","title":"Context metrics and gradual integration","status":"queued","predecessors":["DEV-SEP-D"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP-009..012","Skills","hooks","validators","workflow"],"requirements":["SEP-009","SEP-010","SEP-011","SEP-012"],"capabilities":["project.framework.governance","project.resume"],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-SEP-F","master_id":"DEV-SEP-001","title":"Acceptance and compatibility audit","status":"queued","predecessors":["DEV-SEP-E"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP acceptance","security","full regression","documentation sync"],"requirements":["SEP-001","SEP-002","SEP-003","SEP-004","SEP-005","SEP-006","SEP-007","SEP-008","SEP-009","SEP-010","SEP-011","SEP-012"],"capabilities":["change.review","stage.implement"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false}],"blockers":[],"decisions":["extend-cme-not-replace","single-pure-stdlib-router","skill-source-registry-metadata-only","no-automatic-promotion"],"context_budget":{"max_chars":8000,"max_items":14,"max_contours":5,"max_decisions":5,"max_evidence_threads":6},"next_action":"implement and verify DEV-SEP-D automation detector and promotion lifecycle","integration":{"required":false,"reason":""}}
```

Completion evidence: checkpoint `907b3d5`; sanitized stable candidate detection, fingerprint
dedup/terminal closure, seven promotion targets, placement integration and evidence-gated lifecycle
verified. 31 SEP tests, 103 targeted tests and 333 full tests PASS with six expected skips; context
validator 270 files PASS. No external backlog, Skill, hook or policy was mutated by a decision.

## DEV-SEP-E — Context Metrics + Gradual Integration

- Status: `verified`; Lifecycle: `completed`; predecessor `DEV-SEP-D` verified at `907b3d5`.
- Goal: add lightweight diagnostics, safe Skill-retirement preflight and wire the router into existing
  validators/workflow with two proven deterministic promotion paths.
- PASS: unjustified scan/unused Skill/stale handoff detection, no sole-contract retirement, Skill
  parity and ordinary project compatibility.

```master-execution
{"schema_version":2,"state_revision":5,"master":{"id":"DEV-SEP-001","status":"running","source":{"backend":"notion","queue_id":"3d061ed8f2468163b502d1829668063c","item_id":"3d561ed8f24681c0b8c6d06c1819bb4a","revision":"2026-09-08T19:51:49.477Z","prompt_type":"master_prompt","retention":"keep"}},"tracks":[{"id":"spec-execution-pipeline","repository":"~/codex-dev","worktree":"~/Documents/Codex/2026-09-11/verify-global-dev-activation/work/spec-execution-pipeline","branch":"feature/spec-execution-pipeline","checkpoint":"907b3d59e929377167d18e3037b6447336baaa8d","ownership":["specification-execution-pipeline","tools/spec_execution.py","skill-sources/registry.toml"],"status":"active"}],"slices":[{"id":"DEV-SEP-A","master_id":"DEV-SEP-001","title":"Canonical contract and compatibility audit","status":"verified","predecessors":[],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"89539840725ad57655a1f6e6ffe45ced874ce055","checkpoint_after":"87edde1ac222c692a96f1a1ebd418a840ded09a8","required_evidence":["L1"],"evidence":["L1"],"context_scope":["SEP SPEC","CME SPEC","global architecture","gap map"],"requirements":["SEP-001","SEP-011"],"capabilities":["project.framework.governance"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-B","master_id":"DEV-SEP-001","title":"Intake and capability router core","status":"verified","predecessors":["DEV-SEP-A"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"87edde1ac222c692a96f1a1ebd418a840ded09a8","checkpoint_after":"6e9a76a826bff9b6c342cd801cbef2a3fc218afb","required_evidence":["L1","L2"],"evidence":["L1","L2"],"context_scope":["SEP-001..006","stage selector","dev paths","model routing"],"requirements":["SEP-002","SEP-003","SEP-004","SEP-006","SEP-012"],"capabilities":["project.resume","project.framework.bootstrap","stage.implement"],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-SEP-C","master_id":"DEV-SEP-001","title":"Traceability and placement validation","status":"verified","predecessors":["DEV-SEP-B"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"6e9a76a826bff9b6c342cd801cbef2a3fc218afb","checkpoint_after":"f100e1ba0155c24f8a783c3c0532484d29705cf9","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["SEP-005","SEP-008","CME state","project overlay validator"],"requirements":["SEP-005","SEP-008","SEP-011"],"capabilities":["stage.implement","change.review"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-D","master_id":"DEV-SEP-001","title":"Automation detector and promotion lifecycle","status":"verified","predecessors":["DEV-SEP-C"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"f100e1ba0155c24f8a783c3c0532484d29705cf9","checkpoint_after":"907b3d59e929377167d18e3037b6447336baaa8d","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["SEP-007..010","AEP policy","Prompt Queue boundary"],"requirements":["SEP-007","SEP-008","SEP-009","SEP-010"],"capabilities":["project.framework.governance","change.review"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-E","master_id":"DEV-SEP-001","title":"Context metrics and gradual integration","status":"running","predecessors":["DEV-SEP-D"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"907b3d59e929377167d18e3037b6447336baaa8d","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP-009..012","Skills","hooks","validators","workflow"],"requirements":["SEP-009","SEP-010","SEP-011","SEP-012"],"capabilities":["project.framework.governance","project.resume"],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-SEP-F","master_id":"DEV-SEP-001","title":"Acceptance and compatibility audit","status":"queued","predecessors":["DEV-SEP-E"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"","checkpoint_after":"","required_evidence":["L1","L2","L3"],"evidence":[],"context_scope":["SEP acceptance","security","full regression","documentation sync"],"requirements":["SEP-001","SEP-002","SEP-003","SEP-004","SEP-005","SEP-006","SEP-007","SEP-008","SEP-009","SEP-010","SEP-011","SEP-012"],"capabilities":["change.review","stage.implement"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false}],"blockers":[],"decisions":["extend-cme-not-replace","single-pure-stdlib-router","skill-source-registry-metadata-only","no-automatic-promotion"],"context_budget":{"max_chars":8000,"max_items":14,"max_contours":5,"max_decisions":5,"max_evidence_threads":6},"next_action":"implement and verify DEV-SEP-E diagnostics retirement and integration","integration":{"required":false,"reason":""}}
```

Completion evidence: checkpoint `1a0e3f4`; context diagnostics detect unused Skills, unjustified
full scans, stale handoff preference, strongest-model mechanics and unpromoted repetition without
capturing raw content. Retirement preflight blocks active/sole-owner/live-consumer/hash-drift cases
and never authorizes deletion. Registry semantics are integrated into the existing global validator;
manual Skill selection and placement review now have tested deterministic router/trace decisions.
39 SEP tests, 102 targeted regressions and 342 full tests PASS with six expected platform skips;
context validator 270 files PASS and `git diff --cached --check` PASS.

## DEV-SEP-F — Acceptance + Compatibility Audit

- Status: `verified`; Lifecycle: `completed`; predecessor `DEV-SEP-E` verified at `1a0e3f4`.
- Goal: exercise acceptance A–L and terminal documentation/security/regression gates.
- PASS: targeted/full suites, context/global/project validators, final reviewer and clean diff; master
  is completed and integrated, and its historical Notion execution source is now outside active queue.

```master-execution
{"schema_version":2,"state_revision":8,"master":{"id":"DEV-SEP-001","status":"completed","source":{"backend":"notion","queue_id":"3d061ed8f2468163b502d1829668063c","item_id":"3d561ed8f24681c0b8c6d06c1819bb4a","revision":"2026-09-08T19:51:49.477Z","prompt_type":"master_prompt","retention":"keep"}},"tracks":[{"id":"spec-execution-pipeline","repository":"~/codex-dev","worktree":"~/Documents/Codex/2026-09-11/verify-global-dev-activation/work/spec-execution-pipeline","branch":"feature/spec-execution-pipeline","checkpoint":"a715f2ee724458623725c8c7459ec0833d0302a2","ownership":["specification-execution-pipeline","tools/spec_execution.py","skill-sources/registry.toml"],"status":"integrated"}],"slices":[{"id":"DEV-SEP-A","master_id":"DEV-SEP-001","title":"Canonical contract and compatibility audit","status":"verified","predecessors":[],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"89539840725ad57655a1f6e6ffe45ced874ce055","checkpoint_after":"87edde1ac222c692a96f1a1ebd418a840ded09a8","required_evidence":["L1"],"evidence":["L1"],"context_scope":["SEP SPEC","CME SPEC","global architecture","gap map"],"requirements":["SEP-001","SEP-011"],"capabilities":["project.framework.governance"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-B","master_id":"DEV-SEP-001","title":"Intake and capability router core","status":"verified","predecessors":["DEV-SEP-A"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"87edde1ac222c692a96f1a1ebd418a840ded09a8","checkpoint_after":"6e9a76a826bff9b6c342cd801cbef2a3fc218afb","required_evidence":["L1","L2"],"evidence":["L1","L2"],"context_scope":["SEP-001..006","stage selector","dev paths","model routing"],"requirements":["SEP-002","SEP-003","SEP-004","SEP-006","SEP-012"],"capabilities":["project.resume","project.framework.bootstrap","stage.implement"],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-SEP-C","master_id":"DEV-SEP-001","title":"Traceability and placement validation","status":"verified","predecessors":["DEV-SEP-B"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"6e9a76a826bff9b6c342cd801cbef2a3fc218afb","checkpoint_after":"f100e1ba0155c24f8a783c3c0532484d29705cf9","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["SEP-005","SEP-008","CME state","project overlay validator"],"requirements":["SEP-005","SEP-008","SEP-011"],"capabilities":["stage.implement","change.review"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-D","master_id":"DEV-SEP-001","title":"Automation detector and promotion lifecycle","status":"verified","predecessors":["DEV-SEP-C"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"f100e1ba0155c24f8a783c3c0532484d29705cf9","checkpoint_after":"907b3d59e929377167d18e3037b6447336baaa8d","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["SEP-007..010","AEP policy","Prompt Queue boundary"],"requirements":["SEP-007","SEP-008","SEP-009","SEP-010"],"capabilities":["project.framework.governance","change.review"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-SEP-E","master_id":"DEV-SEP-001","title":"Context metrics and gradual integration","status":"verified","predecessors":["DEV-SEP-D"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"907b3d59e929377167d18e3037b6447336baaa8d","checkpoint_after":"1a0e3f4d53b293d1ef9ade3c8aaad97421fad6a2","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["SEP-009..012","Skills","hooks","validators","workflow"],"requirements":["SEP-009","SEP-010","SEP-011","SEP-012"],"capabilities":["project.framework.governance","project.resume"],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-SEP-F","master_id":"DEV-SEP-001","title":"Acceptance and compatibility audit","status":"verified","predecessors":["DEV-SEP-E"],"dependencies":[],"worktree_track":"spec-execution-pipeline","checkpoint_before":"1a0e3f4d53b293d1ef9ade3c8aaad97421fad6a2","checkpoint_after":"a715f2ee724458623725c8c7459ec0833d0302a2","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["SEP acceptance","security","full regression","documentation sync"],"requirements":["SEP-001","SEP-002","SEP-003","SEP-004","SEP-005","SEP-006","SEP-007","SEP-008","SEP-009","SEP-010","SEP-011","SEP-012"],"capabilities":["change.review","stage.implement"],"model_class":"HIGH","reasoning_effort":"high","stop_after":false}],"blockers":[],"decisions":["extend-cme-not-replace","single-pure-stdlib-router","skill-source-registry-metadata-only","no-automatic-promotion"],"context_budget":{"max_chars":8000,"max_items":14,"max_contours":5,"max_decisions":5,"max_evidence_threads":6},"next_action":"await an explicitly selected DEV prompt; retain Notion master","integration":{"required":false,"reason":""}}
```

Completion evidence: implementation checkpoint `a715f2e`; acceptance `AC-SEP-A..L` PASS;
54 SEP tests PASS with one expected Windows symlink skip; full suite 358 PASS with seven expected
platform skips; context validator 270 files PASS; direct Windows CLI help and diff check PASS.
Independent correctness and security reviews PASS. Fast-forward merge into local `main`,
manifest-driven active-runtime materialization, global validation and idempotent no-change dry-run
PASS. Push was not performed. A later audited cleanup moved the Notion master to Trash and removed
its active `A. DEV` entry while retaining the reusable launcher.

## DEV-PATHS-001 — Unified DEV and product path roles (standalone delta)

- Status: `completed`; Lifecycle: `verified`; Evidence level: `validated locally + physical migration verified`.
- Branch: `feature/unified-dev-product-paths`; source: direct user request 2026-09-10.
- Requirements: `FR-DPL-001..008`; acceptance: `AC-DPL-001..013` from
  `specs/features/unified-dev-path-layout.spec.md`.

### Dependencies and entry evidence

`DEV-INSTALL-LAYER-001` is the completed source/installed separation baseline at `5051018`.
The canonical source exists at `~/codex-dev`; the legacy source remains retained at
`~/codex-workspace/codex-dev` as recovery/worktree metadata. The attached physical-migration delta
authorized controlled local materialization after a clean preflight. GitHub rename, remote update,
merge and push were subsequently authorized explicitly by the user.

### Runnable slice and consumer scenario

`tools/dev_paths.py resolve|diagnose|project|move-plan` resolves the three roles, reports their
sources and builds read-only migration evidence. Installer/validator use the same resolver.
SessionStart, `Продолжай` and Prompt Queue route project policy only after an exact Git root and
valid `.codex/dev-project.toml` are verified. `dev-contract.toml` plus project-local wrappers check
schema, version, capabilities, canonical remote, installed manifest and project overlay across
clone/pull. An AGENTS-only or plain repository under `PROJECTS_ROOT` receives no DEV bootstrap.

### Scope, safety, fallback and PASS

Scope: resolver/config, Windows normalization, structured product isolation, migration
diagnostics/preflight, clone/pull bootstrap contract, installer consumers, Prompt Queue/session
bootstrap, repository identity docs, semantic audit and controlled physical migration. Out of
scope: deleting legacy repositories, changing GitHub/remote, merge and push. Invalid config, path escape, missing bridge, dirty/ambiguous source,
additional worktree/submodule problem or collision fails closed. Rollback is Git revert; migration
tooling performs no mutation.

PASS requires targeted path/installer/queue/overlay tests, full unittest suite, context and global
validators, isolated installer dry-run/apply/idempotency, wrapper syntax checks, semantic audit and
`git diff --check`. After PASS this slice may be `verified/completed`; the actual filesystem and
GitHub migration remains a separate user-controlled operation.

Current evidence: 129 targeted tests PASS with 2 expected platform skips; full 302 tests PASS with
6 expected platform skips; 266-file context manifest PASS; isolated installer dry-run, apply,
repeat idempotency, nine-Skill parity and global validator PASS; PowerShell and Git Bash bootstrap
syntax PASS; staged diff check PASS. An independent canonical clone now exists at `~/codex-dev` on
the same feature HEAD; `git fsck`, fetch, exact root, clean status and remote read-back passed. The
legacy source checkout remains retained. `math-morph` and its legitimate dirty/untracked Stage 310
state were copied losslessly to `${PROJECTS_ROOT}/math-morph`; all 14 untracked files match by
SHA-256. The independent remote-backed `math-morph-astra` WIP clone was likewise preserved at
`${PROJECTS_ROOT}/math-morph-astra`. Exact roots, HEADs, branches, remotes, fetch, worktree/submodule
metadata, file inventories and project validators passed; only semantically active path references
were updated. DEV membership remained independent from physical location. Real `CODEX_HOME` dry-run
passed, but apply hit the existing shell-environment security validator and rolled back completely;
no ledger/pending transaction or managed file remained.

NEXT: no remaining `DEV-PATHS-001` implementation work. Legacy recovery copies require an explicit
cleanup decision, and protected active-config remediation remains a separate migration item. The
canonical GitHub repository and origin are `https://github.com/ZabulaAleksey/codex-dev.git`.

## DEV-BCSC-A — Detection + Dry-Run Compatibility Plan

- Status: `verified`; Lifecycle: `completed`; Evidence level: `validated locally`.
- Master: `DEV-BCSC-001`; master status: `partial`; track: `brownfield-stage-compatibility`.
- Worktree/branch: `~/codex-workspace/.worktrees/dev-brownfield-stage-compatibility` /
  `feature/brownfield-stage-compatibility`; checkpoint before: `da86991`; checkpoint after:
  `2e442a9`.
- Source: explicit user master request 2026-09-08; prompt type `master_prompt`, retention `keep`.
- Requirements: `BSC-001..010`, `NFR-BSC-001..004`; acceptance `AC-BSC-001..007`.

### Dependencies and entry evidence

Prerequisite `DEV-CME-001` is completed and integrated in local `main` at `da86991`.
Baseline: 92 relevant CME/STAGES/reconciliation tests PASS; context validator 238 files PASS.
`electro-tutor` is Git-clean and read-only validation reports legacy AI_PLAN/AI_STATUS plus
missing same-file selector.

### Runnable slice and concrete consumer scenario

`py -3 -B tools/master_execution.py <project> --compatibility` reads only bounded known state
files and returns deterministic classification, normalized projection and optional dry-run plan.
Temporary fixtures exercise canonical, legacy, mixed, conflict, migrated and none. The same CLI
inspects `electro-tutor` twice with identical output and unchanged Git status.

### Scope, safety, fallback and PASS

Add the versioned manifest schema, pure adapter and an existing-CME CLI mode. No product writes,
apply mode, legacy removal, hook mutation or prose guessing. Invalid/ambiguous/drifted state returns
explicit conflict/migration_required. PASS requires fixture matrix, idempotency, canonical
regressions, bounded-input tests, read-only real fixture evidence, global context and diff checks.

Allowed temporary implementation: complete read-only inspection/dry-run path. Explicit plan
materialization and cleanup remain future slices and cannot be inferred from A.

After PASS: checkpoint A, select `DEV-BCSC-B`, then stop because the user explicitly limited this
run to one implementation slice.

Completion evidence: SPEC-first checkpoint `098b040`, implementation checkpoint `2e442a9`;
103 targeted CME/STAGES/compatibility tests and 204 full tests PASS; context validator 242 files
PASS; `git diff --check` PASS. `electro-tutor` remained clean and was classified twice identically
as non-runnable `mixed / migration_required` with explicit missing NEXT/blocker issues.

## DEV-BCSC-B — Explicit Migration Materialization Contract

- Status: `verified`; Lifecycle: `completed`; Evidence level: `validated locally`.
- Master: `DEV-BCSC-001`; predecessor `DEV-BCSC-A` verified at `2e442a9`.
- Goal: apply only an explicitly approved, digest-matched plan with rollback and read-back; retain
  legacy files. Product rollout remains separately authorized.

Entry router state: `ready`. Entry evidence: `DEV-BCSC-A` verified at `2e442a9`; no product repository
was changed. Scope is an explicit, digest-matched materialization command with dry-run/read-back
and rollback evidence on temporary repositories only. Legacy deletion and product rollout remain
out of scope. PASS requires stale-plan rejection, atomic write/rollback tests, canonical regression
and no change to `electro-tutor`.

Completion evidence: implementation checkpoint `1083478`; 46 targeted tests PASS plus one
POSIX-only identity test skipped on Windows; 126 relevant CME/STAGES/overlay tests PASS plus the
same skip; 227 full tests PASS plus the same skip; context validator 243 files PASS;
`git diff --check` PASS. Independent correctness and security reviews PASS. Two read-only
`electro-tutor` reports remained identical at SHA-256 `f39c0ad916bdc4c8dcf595e761db2478eaff5dc2f41501fc48b52e2fa640eb0e`;
repository clean, `mixed / migration_required / runnable=false`, no executable plan. No product
repository was materialized; legacy files were not changed or deleted.

## DEV-BCSC-C — Validator/Hook Adoption + Controlled Evidence

- Status: `verified`; Lifecycle: `completed`; Evidence level: `validated locally`.
- Master: `DEV-BCSC-001`; predecessor `DEV-BCSC-B` verified at `1083478`.
- Goal: integrate manifest validation into existing selector/overlay boundaries and gather
  controlled migration evidence without mass product mutation.

```master-execution
{"schema_version":1,"state_revision":5,"master":{"id":"DEV-BCSC-001","status":"completed","source":{"backend":"chat","queue_id":"none","item_id":"direct-user-request-2026-09-08","revision":"2026-09-08","prompt_type":"master_prompt","retention":"keep"}},"tracks":[{"id":"brownfield-stage-compatibility","repository":"~/.codex","worktree":"~/codex-workspace/.worktrees/dev-brownfield-stage-compatibility","branch":"feature/brownfield-stage-compatibility","checkpoint":"60a1efb923aa3f4ce5513215c8ecbfcb94fbc01a","ownership":["canonical-stage-compatibility","tools/master_execution.py"],"status":"integrated"}],"slices":[{"id":"DEV-BCSC-A","master_id":"DEV-BCSC-001","title":"Detection and dry-run plan","status":"verified","predecessors":[],"dependencies":[],"worktree_track":"brownfield-stage-compatibility","checkpoint_before":"da869913af008b26c64903106773140823f63518","checkpoint_after":"2e442a929dc4b4f0384807113559dedd86598b52","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["BSC SPEC","stage selector","CME CLI","compatibility tests"],"model_class":"HIGH","reasoning_effort":"high","stop_after":true},{"id":"DEV-BCSC-B","master_id":"DEV-BCSC-001","title":"Explicit materialization contract","status":"verified","predecessors":["DEV-BCSC-A"],"dependencies":[],"worktree_track":"brownfield-stage-compatibility","checkpoint_before":"2e442a929dc4b4f0384807113559dedd86598b52","checkpoint_after":"10834789536ff4eb7952190f224af6d114ffeed2","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["BSC SPEC","migration plan","validator"],"model_class":"HIGH","reasoning_effort":"high","stop_after":true},{"id":"DEV-BCSC-C","master_id":"DEV-BCSC-001","title":"Validator and controlled rollout","status":"verified","predecessors":["DEV-BCSC-B"],"dependencies":[],"worktree_track":"brownfield-stage-compatibility","checkpoint_before":"10834789536ff4eb7952190f224af6d114ffeed2","checkpoint_after":"f1f830208415e240a7d79394f1906185d83739e7","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":["BSC SPEC","hook","overlay tests"],"model_class":"HIGH","reasoning_effort":"high","stop_after":true}],"blockers":[],"decisions":["same-file-manifest","digest-matched-materialization","retained-legacy-state","no-product-mutation"],"context_budget":{"max_chars":6000,"max_items":12,"max_contours":4,"max_decisions":4,"max_evidence_threads":6},"next_action":"await an explicitly selected DEV prompt; no Slice D","integration":{"required":false,"reason":""}}
```

Completion evidence: implementation checkpoint `f1f8302`; Windows CRLF integration fixes
`3e03a24` and `60a1efb`; 164 targeted router/adapter/validator/hook/global tests, 151 CME/STAGES
regressions and 253 full DEV tests PASS plus one expected POSIX-only skip; context validator 243
files PASS; `git diff --check` PASS. Default router and validator
classify read-only `electro-tutor` as `mixed / migration_plan_unsafe`, stage `ET-09.3`, status
`blocked`, NEXT null, with exact missing blocker/NEXT issues; SessionStart is deterministic exit 0,
creates no plan/lock/write, and Git remains clean. Independent correctness and security reviews
PASS. Router state is `master_already_completed`; no Slice D exists. The feature chain was
fast-forward integrated into local `main` through `60a1efb`; push was not performed.

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

- Status: `verified`; Lifecycle: `completed`; Evidence level: `merged` into local `main` at `1e34f41`.
- Master: `DEV-CME-001`; master status: `completed`; predecessor `DEV-CME-E` verified.
- Same continuation track; checkpoint before `252e935`.
- Requirements: `CME-007..008`, `NFR-CME-002..003`; acceptance `AC-CME-006..009`.

```master-execution
{"schema_version":1,"state_revision":8,"master":{"id":"DEV-CME-001","status":"completed","source":{"backend":"notion","queue_id":"3d061ed8-f246-8163-b502-d1829668063c","item_id":"3d461ed8-f246-812d-b41c-da2510a70dd3","revision":"2026-09-07T18:46:55.040Z","prompt_type":"master_prompt","retention":"keep"}},"tracks":[{"id":"canonical-stages-policy","repository":"~/.codex","worktree":"~/codex-workspace/.worktrees/dev-canonical-stages-policy","branch":"feature/canonical-stages-policy","checkpoint":"1e34f4192aff22b0b773b7df7314b054a140ae80","ownership":["global-orchestration-contract"],"status":"integrated"}],"slices":[{"id":"DEV-CME-A","master_id":"DEV-CME-001","title":"Contract","status":"completed","predecessors":[],"dependencies":[],"worktree_track":"canonical-stages-policy","checkpoint_before":"72197b268e5e0525d19cbee712535d68346062f4","checkpoint_after":"d4f711ec43964125dcd3a4658ef87d14cfca6c4a","required_evidence":["L1"],"evidence":["L1"],"context_scope":[],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-CME-B","master_id":"DEV-CME-001","title":"Routing","status":"completed","predecessors":["DEV-CME-A"],"dependencies":[],"worktree_track":"canonical-stages-policy","checkpoint_before":"d4f711ec43964125dcd3a4658ef87d14cfca6c4a","checkpoint_after":"5401b65a925bce28af7c2d2b619781e2a4d0f392","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":[],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-CME-C","master_id":"DEV-CME-001","title":"Graph","status":"completed","predecessors":["DEV-CME-B"],"dependencies":[],"worktree_track":"canonical-stages-policy","checkpoint_before":"5401b65a925bce28af7c2d2b619781e2a4d0f392","checkpoint_after":"2f140c528d29f3af4a62ce7f3c48bc1e52ea25d9","required_evidence":["L1","L2"],"evidence":["L1","L2"],"context_scope":[],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-CME-D","master_id":"DEV-CME-001","title":"Handoff","status":"completed","predecessors":["DEV-CME-C"],"dependencies":[],"worktree_track":"canonical-stages-policy","checkpoint_before":"2f140c528d29f3af4a62ce7f3c48bc1e52ea25d9","checkpoint_after":"53138d5379458a1adaaf8c7c4e353ade045f9081","required_evidence":["L1","L2"],"evidence":["L1","L2"],"context_scope":[],"model_class":"MEDIUM","reasoning_effort":"medium","stop_after":false},{"id":"DEV-CME-E","master_id":"DEV-CME-001","title":"Evidence","status":"completed","predecessors":["DEV-CME-D"],"dependencies":[],"worktree_track":"canonical-stages-policy","checkpoint_before":"53138d5379458a1adaaf8c7c4e353ade045f9081","checkpoint_after":"252e935d75fca284edc07bf48cb8ec8439c9b115","required_evidence":["L1","L2"],"evidence":["L1","L2"],"context_scope":[],"model_class":"HIGH","reasoning_effort":"high","stop_after":false},{"id":"DEV-CME-F","master_id":"DEV-CME-001","title":"Recovery","status":"completed","predecessors":["DEV-CME-E"],"dependencies":[],"worktree_track":"canonical-stages-policy","checkpoint_before":"252e935d75fca284edc07bf48cb8ec8439c9b115","checkpoint_after":"c81ee81d5722cca3db8fbbe1b91fc4055dd1a837","required_evidence":["L1","L2","L3"],"evidence":["L1","L2","L3"],"context_scope":[],"model_class":"HIGH","reasoning_effort":"high","stop_after":true}],"blockers":[{"id":"CME-ROLLOUT-ET","class":"pre_existing","status":"active","blocking":false,"owner":"electro-tutor brownfield migration stage","evidence":"legacy AI_PLAN/AI_STATUS and missing same-file selector"}],"decisions":["keep-parent-master","integration-complete"],"context_budget":{"max_chars":6000,"max_items":12,"max_contours":4,"max_decisions":4,"max_evidence_threads":6},"next_action":"await an explicitly selected DEV prompt","integration":{"required":false,"reason":""}}
```


### Runnable slice / PASS / boundaries

Hierarchical cleanup eligibility delegates completed children to the existing guard. The recorded
source retention is `keep`; a later cleanup needs historical-master reclassification plus the
zero-orphan/runtime-parity/regression guard. Recovery covers commit/status ordering, missing branch/
worktree, stale launcher/source, dirty edits, overlapping integration, missing queue item and
compaction. Router/rules/Skills/templates/docs are synchronized.

Evidence: full 181 tests PASS; master-policy 40, queue 15 and existing governance 36 targeted tests
PASS; context validator PASS (238 files); Python and PowerShell syntax PASS; exact SessionStart
record PASS; real temporary Git worktree create/read-back supplies L3. Bash syntax is
`UNAVAILABLE` because local WSL returned `E_ACCESSDENIED`; unchanged script had prior evidence.
Read-only `electro-tutor` validation classified a pre-existing brownfield gap (legacy
`AI_PLAN/AI_STATUS`, missing same-file selector); no product mutation or regression.

Stop: master complete and fast-forward merged into local `main` at `1e34f41`; post-merge context,
80 deterministic tests, diff and completed-state smoke PASS. Push was not performed. Prompt
cleanup at that checkpoint was `retain`; the later zero-orphan audit and exact-item guard passed,
so the historical execution prompt was moved to Trash and removed from active `A. DEV`.

## DEV-CANONICAL-STAGES-001 — Canonical STAGES.md Policy

- Status: `verified`.
- Lifecycle: `completed`.
- Evidence level: `merged` into local `main` through `1e34f41`; push не выполнялся.
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
temporary full overlay with one docs/STAGES.md
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
- [x] Canonical policy and migration documentation use only `docs/STAGES.md` as execution owner.
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
- Integration: checkpoint `80a63b3` merged into local `main` through `1e34f41`; push not performed.
- NEXT: none inside this completed slice.

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

## DEV-STAGES-USER-ACTIONS-001 — Durable user actions in canonical STAGES

Status: verified
NEXT: DEV-STAGES-USER-ACTIONS-001
Checkpoint: d9625c8
Evidence: L1
Blockers: none

- Lifecycle: `completed`; Evidence level: `validated locally + committed`.
- Goal: make every project-owner-only action recoverable from selected `docs/STAGES.md` without
  relying on chat history.
- Scope: canonical governance, global router, `dev-karkas` status workflow, project framework,
  STAGES template and contract regression; no runtime installation, product rollout or external write.
- Contract: user decisions/approvals, secret or external-access needs, local setup, manual checks
  and approval-gated operations receive a stable action ID, status/condition, exact safe action,
  expected evidence and the step they unblock. Secret values are never stored in project state.
- Implementation checkpoint: `d9625c8` on `docs/stages-user-actions`; no merge or push.
- Evidence: `tools.test_documentation_sync_policy` 6 PASS; full DEV suite 364 PASS with 7 expected
  skips; `tools/validate_context.py` PASS for 271 files; `git diff --check` PASS.
- Documentation synchronization: updated `AGENTS.md`, `rules/governance.md`,
  `docs/PROJECT_FRAMEWORK.md`, `skill-sources/dev-karkas/references/STATUS_WORKFLOW.md`,
  `templates/STAGES_TEMPLATE.md` and this selected record. `README.md`, `docs/ROADMAP.md`,
  architecture, decisions, security and testing contracts were checked and remain accurate.

### Fallback / rollback / NEXT

Изменение policy не устанавливается в active `~/.codex` автоматически. Rollback — atomic Git
revert implementation/state/merge commits. Finalization actions принадлежат selected
`DEV-SEP-LAUNCHER-001`; runtime install не подразумевается.
