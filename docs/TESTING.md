# Проверка глобального ДЕВ

## Global Action Journal / Script Registry

`py -3 -B -m unittest tools.test_global_action` exercises explicit
init → sanitized record → read-back/no-op → exact existing-tool lookup,
configured repeat candidates, failure isolation, corrupt journal, unsafe refs,
secret-like input, oversized logs, redirected parent, dry-run,
exact existing-script reuse preflight and
duplicate/unsafe registry rejection. CLI preflight:
`py -3 -B tools/global_action.py catalog` and
`py -3 -B tools/global_action.py lookup source-validation`.
Neither test nor lookup claims active host installation. Full suite and tracked
manifest validation remain the terminal source checks below.

## Prompt Queue Lifecycle

`python -B -m unittest discover -s tools -p "test_prompt_queue.py"` проверяет fixtures/guard для
PQ-01..10 и PQ-12..13: CLI на временном Git project, receipt reconciliation, защищённые retention
types и обязательные zero-orphan/runtime-parity/regression gates historical execution master.
Real current-project/Notion operation + read-back остаётся отдельным evidence PQ-11.
Full suite: `python -B -m unittest discover -s tools -p "test_*.py"`; manifest gate:
`python -B tools/validate_context.py`. Real queue mutation/read-back фиксируется в project evidence
и не подменяется fixtures.


Этот документ описывает discoverable verification commands самого global
framework. Общие правила test contracts остаются в `AGENTS.md`,
`rules/governance.md` и dev-karkas `references/TESTING_POLICY.md`.

## Canonical commands

Из canonical DEV source Git root:

```powershell
py -3 -B tools\validate_context.py
py -3 -B -m unittest discover -s tools -p "test_*.py"
.\install-global.ps1 -DryRun
py -3 -B tools\validate_global_codex.py --workspace . --codex-home ~/.codex
git diff --check
```

## Continuous Master Execution contract

`tools.test_master_execution` проверяет embedded state/schema, cycle/ambiguity/evidence gates,
continuation/parallel routing, real temporary Git worktree create/read-back, auto-advance,
L1–L6, context budget/handoff, hierarchical prompt eligibility и recovery matrix.
`tools.test_continuous_master_execution_policy` проверяет, что router/governance/Skills/templates и
SPEC используют один state/cleanup owner и не требуют merge question после каждого slice.
Текущий global evidence: 363 tests PASS, 7 platform-specific skips, context manifest 271 files
PASS. Controlled read-only
`electro-tutor` check вернул pre-existing migration gaps и не является regression/global test
failure; temporary real Git integration остаётся positive portable adapter evidence.
После fast-forward merge в local `main`: context validator 238 files PASS, 80 deterministic
master/STAGES/overlay tests PASS, `git diff --check` и `master_already_completed` smoke PASS.

## Brownfield stage compatibility contract

`tools.test_stage_compatibility` проверяет pure canonical, pure legacy, partial/mixed,
conflicting legacy, canonical/legacy mismatch, already migrated, digest drift, absent state,
bounded paths и повторный deterministic routing. CLI остаётся частью
`tools/master_execution.py`; real `electro-tutor` используется только как read-only evidence,
а не как product-specific fixture внутри test suite.

Slice A: 103 targeted CME/STAGES/compatibility regressions и 204 full tests PASS. Два read-only
запуска на `electro-tutor` дали одинаковый report SHA-256
`f39c0ad916bdc4c8dcf595e761db2478eaff5dc2f41501fc48b52e2fa640eb0e`:
`mixed`, `migration_required`, non-runnable stage `ET-09.3`, status `blocked`. Отсутствующие exact
`NEXT` и blocker дают explicit issues и запрещают plan; Git status до и после clean. Это
compatibility evidence, не product mutation и не migration completion.

Slice B: `tools.test_stage_compatibility` содержит 47 detection/materialization tests: exact
approved apply, source/target/mixed drift, digest/field tampering, malformed JSON/fence, apply-time
path escape, first/mid-write failure, CAS rollback/read-back failure, durable recovery lock,
idempotency, real thread contention, repository replay rejection, canonical regression и read-only
analysis. На Windows 46 PASS + 1 ожидаемый skip POSIX-only case/backslash identity test; полный DEV
suite — 227 PASS + тот же 1 skip, relevant CME/STAGES/overlay subset — 126 PASS + тот же 1 skip,
context validator —
243 files PASS, `git diff --check` — PASS. Independent correctness и security reviews — PASS.
Все positive writes выполнялись только в temporary repositories. Два read-only `electro-tutor`
report остались byte-identical с SHA-256 `f39c0ad916bdc4c8dcf595e761db2478eaff5dc2f41501fc48b52e2fa640eb0e`;
repository до/после clean, plan отсутствует.

Slice C regression matrix дополнительно проверяет normal router adoption, ordinary/canonical CME
continuation, `master_already_completed`, legacy/mixed/conflict/no-state/migrated outcomes,
same-file required `Status`/`NEXT`, отсутствие legacy fallback, validator exit semantics и
deterministic SessionStart без implicit materialization. Safe plan handoff проверяется как fixed
argv data с exact digest и `plan_persisted=false`; no-plan выдаёт exact missing facts без команды.
Real `electro-tutor` остаётся read-only acceptance evidence, а не writable fixture.

Current integrated Slice C evidence: targeted router/adapter/validator/hook/global regression
set — 164 PASS + 1 expected POSIX-only skip; CME/STAGES regression set — 151 PASS + тот же skip;
full `tools/test_*.py` suite — 253 PASS + тот же skip; context validator — 243 files PASS;
`git diff --check` — PASS. Windows CRLF fenced-state parity is covered. Default `electro-tutor`
router/validator
return exit `1` with `mixed / migration_plan_unsafe`, while SessionStart returns deterministic
bounded advisory context at exit `0`; expected two missing-fact issues, no command/lock/write, Git
clean before and after. Independent correctness/security conclusions are recorded in the stage
evidence: both final read-only reviews PASS with no blockers; lexical normalization leaves
symlink-alias identity reconciliation to the explicit worktree adapter.

Evidence levels: L1 static/type/lint, L2 unit, L3 component/integration, L4 real backend/
concurrency, L5 browser/UI/runtime, L6 external/manual acceptance. Higher-risk claim требует
соответствующего real level; synthetic evidence не повышается автоматически.

## Specification → Execution contract

`tools.test_spec_execution` проверяет compact intake, exact четыре класса нового проекта,
metadata-only Skill routing, cheapest sufficient executor, requirement/capability/evidence trace,
placement, automation candidate lifecycle, context-economy diagnostics и two-phase Skill
retirement preflight. Negative fixtures покрывают duplicate/unknown/oversized input, ambiguous
capability ownership, stale state, unjustified full scan, unused Skill и попытку убрать
единственного владельца обязательной capability.

Security/correctness regressions дополнительно покрывают global+project/domain registry composition,
strict Skill frontmatter/path containment, canonical context order, full candidate dedup,
priority/evidence/provenance retention, allowlisted lifecycle fields, live CME-bound trace coverage,
status/evidence thresholds, Windows/UNC/link-like paths, command IDs, fail-closed security failures и
advisory-only retirement attestations.

`tools.test_validate_global_codex` дополнительно проверяет semantic registry validation и
совместимость workspaces без registry. Тестовые команды из metadata остаются данными и никогда не
исполняются pipeline или validator-ом.

Final `DEV-SEP-F` evidence: acceptance `AC-SEP-A..L` PASS; 54 SEP tests PASS with one expected
Windows symlink skip; full suite 358 PASS with seven expected platform skips; context validator
270 files PASS; direct Windows CLI help and `git diff --check` PASS. Independent correctness and
security reviews PASS. Fast-forward local integration, manifest-driven active-runtime
materialization, global validation and repeat no-change dry-run also PASS; push не выполнялся.

Follow-up `DEV-SEP-LAUNCHER-001` evidence at checkpoint `f25903c`: full canonical discovery
383 PASS with seven expected platform skips; launcher/CME/spec/path set 140 PASS with one expected
platform skip; final launcher/CME security subset 67 PASS. Context validator 271 files PASS,
installer dry-run made no runtime writes, Python compile and staged diff check PASS. Independent
correctness and security reviews PASS. Merge and active-runtime apply remain a separate approved
integration step.

`tools.test_install_global` использует только temporary source/home roots и проверяет separate
source, populated runtime preservation, manifest allowlist, ledger-governed stale deletion,
unknown/protected collisions, Skill routing, zero-write dry-run, rollback, validator order,
idempotency и post-pull managed-only update.

`install-global.ps1` выполняет transactional managed apply, Skill sync и основные проверки
installed layer, но
не заменяет целевой unit suite во время разработки.

Windows wrapper дополнительно проверен на isolated populated Codex home: dry-run zero-write,
managed apply, 9 Skill sources, оба validator phase, byte-identical auth/session markers и
idempotent второй install PASS. Реальный пользовательский `~/.codex` не изменялся.

## Backend DX fixture contract

`tools.test_backend_dx_policy` создаёт temporary independent Git repositories и
проверяет:

- neutral complete `BDX-L2` delta как framework clean-room fixture;
- ambiguous/L0 classification, missing fields/commands и missing route;
- local/test guard destructive reset;
- generated API/contract drift command;
- conservative `.env.example` secret detection без вывода значения;
- misplaced/duplicated global policy content;
- alignment template, policy IDs/gates, routers, Skill и existing agent roles.

Fixture доказывает read-only deterministic contract validator-а. Он не запускает
реальную DB, service, provider или production clean-room и не должен описываться
как E2E конкретного product backend.

## Documentation synchronization contract

`tools.test_documentation_sync_policy` проверяет стабильные `FR-006` / `AC-006`,
обязательный список state-bearing sources, routing Skills и поддержку AI templates.
Это structural contract test: смысловую актуальность проектной документации подтверждает
Completion Documentation Synchronization Gate, а не эвристический semantic validator.

## Architecturally complete stage contract

`tools.test_stage_completion_policy` проверяет стабильные `FR-007` / `AC-007`, единственного
владельца полного Stage contract, обязательные planning/status fields, routes Skills/templates,
разделение lifecycle/evidence, SPEC authority и отсутствие конкурирующего local backlog path.
Subprocess-тесты дополнительно проходят внутренний путь
`stage-state detection → session_context.py → exact selected STAGES record либо typed stop` и
проверяют canonical, legacy, conflict, no-selector, missing/ambiguous, bounded и repeated scenarios.

Policy-часть остаётся structural contract test глобальной автоматизации, а hook-часть — internal
E2E context-projection path. Она не валидирует семантику произвольного project
`docs/STAGES.md`, не исполняет product path и не превращает mocks/stubs в E2E evidence.

`tools.test_validate_project_overlay` дополнительно проверяет shared selector/compatibility
contract: canonical PASS, migration-required non-PASS, conflict/no-state, invalid-canonical
no-fallback, valid/missing/multiple selector, heading/token/fence cases. JSON отдельно сообщает
inspection, canonical validity и execution permission.

## Global framework hardening contract

`tools.test_global_framework_hardening` проверяет feature SPEC, размер/critical markers thin
`AGENTS.md`, допустимые explicit agent model pins и default inheritance, одинаковый порядок
install wrappers, отсутствие config write commands, minimal project router template и read-only CI.
Actual Windows/Unix installer execution и runtime Skill parity остаются отдельным environment
evidence; structural tests не повышают их до PASS.

## Unified project workflow contract

`tools.test_unified_project_workflow_policy` проверяет `FR-008..009` / `AC-009..012`, единственного
policy owner, восемь copy-ready lifecycle requests, новый LEARNING shape, external/device/monitoring
markers и фактический `~/.codex` source root. Его executable consumer path передаёт отсутствующий
canonical root в production validator и требует structured issues вместо traceback.

Это internal policy/validator E2E, а не product E2E. Восстановление реального project repository
проверяется отдельно read-only командами `reconcile_project_framework.py` и
`validate_project_overlay.py` плюс semantic link/status audit; structural PASS не маскирует stale
references.

## Global i18n/l10n contract

`tools.test_i18n_l10n_policy` проверяет `FR-010` / `AC-013`, единственного policy owner,
global routers, различие `language` / `locale`, resource-based строки, полный класс
locale-dependent данных, fallback locale, text expansion, RTL и self-contained initial slice с
pseudo-locale либо alternate test locale.

Это structural contract test global framework. Он подтверждает, что КАРКАС доставляет требование
в user-facing product architecture, но не заменяет project unit/component/integration/E2E evidence
конкретных переводов, форматирования и locale switch.

## AI Policy Profiling contract

`tools.test_ai_policy_profiler` проверяет `FR-AEP-001..012`, privacy allow-list, identifier/number
limits, opt-in/idempotent init, bounded discovery, human handoff batch guard, false reuse,
profiler overhead, baseline/variant aggregation, concurrent writers, symlink containment и
corrupt-input fail-closed behavior.

Executable consumer path создаёт temporary independent Git project и выполняет:

```text
init → real instrumented subprocess → baseline/variant stage outcomes
→ reuse + handoff + discovery + agent events → JSON/Markdown report
```

Он подтверждает, что telemetry реально пишется, command output/raw args не сохраняются, policy и
experiment linkage агрегируются, а existing project без `.metrics/` остаётся unchanged. Это
internal profiler E2E, не product E2E и не доказательство ROI конкретной policy на реальной
выборке.

## Evidence policy

Для каждой команды фиксируй command, purpose, `PASS | FAIL | BLOCKED`, scope и
caveat. Pre-existing runtime failures отделяются от regressions. Не ослабляй
принятые tests/fixtures/goldens; новые contract tests добавляются отдельным файлом.
