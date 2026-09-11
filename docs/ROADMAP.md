# Roadmap AI Dev Team

## Текущий master — Specification → Execution Pipeline

`DEV-SEP-001` расширяет Continuous Master Execution stage-first capability/Skill routing,
requirement/evidence trace, deterministic-first execution и evidence-driven automation promotion.
Canonical owners не меняются: SPEC хранит behavior, architecture/ADR — boundaries/decisions,
selected `prompts/STAGES.md` — единственное execution state, Prompt Queue — cleanup guard, profiler —
optional observations. Progressive chain `DEV-SEP-A..F` начинает с contract/audit, затем добавляет
один bounded stdlib-only core и metadata-only Skill registry, trace/placement validation,
promotion lifecycle, diagnostics/retirement preflight и final compatibility audit. Product rollout,
runtime install, automatic promotion/tuning, merge и push не входят в automatic execution.

## Текущий internal delta — unified DEV/product path roles

`DEV-PATHS-001` переносит active architecture на единый layout
`DEV_SOURCE_ROOT=~/codex-dev`, `CODEX_HOME=~/.codex`, `PROJECTS_ROOT=~`, сохраняя logical role
abstraction. Один resolver владеет env/local-config/default precedence, normalization, project
lookup, structured `.codex/dev-project.toml` opt-in и migration diagnostics. `dev-contract.toml`
и portable wrappers добавляют clone/pull bootstrap с version/capability checks. Installer, global validator,
SessionStart/`Продолжай` и Prompt Queue потребляют resolver. Plain repositories не наследуют DEV
project policy по filesystem location. Controlled physical migration follows the attached delta;
canonical source and product repositories are now materialized and Git-verified, while legacy
recovery copies remain pending explicit cleanup. GitHub rename and origin update to `codex-dev` are
complete; real runtime install remains a separate security-gated item. Acceptance
принадлежит `specs/features/unified-dev-path-layout.spec.md`; current execution record —
`prompts/STAGES.md`. Bootstrap implementation locally validated: 129 targeted tests PASS (2
expected skips), full 302 tests PASS (6 expected skips), 266-file manifest PASS, isolated installer
dry-run/apply/idempotency + global validator PASS, both wrapper syntax checks and diff check PASS.
Canonical `~/codex-dev`, `~/math-morph` and `~/math-morph-astra` have been materialized and
Git-verified while legacy recovery copies remain. The dirty/untracked MathMorph state was preserved
losslessly; filesystem location did not change DEV membership. Real `CODEX_HOME` apply rolled back
on its pre-existing shell-environment security gate and remains outside this completed path slice.

## Текущий internal delta — DEV source → installed Codex home

`DEV-INSTALL-LAYER-001` разделяет canonical DEV Git source и installed `~/.codex`. Scope:
manifest-only materialization, protected runtime denylist, deterministic ownership ledger,
ledger-only stale cleanup, staged/atomic apply with rollback, zero-write dry-run, existing Skill
sync и повторные validators. Реальный runtime home не изменяется до отдельного запуска installer;
acceptance принадлежит `specs/features/source-installed-layer.spec.md`; current master selector в
`prompts/STAGES.md` сохранён без нового competing execution graph. Implementation validated
locally: 273 tests PASS с 6 ожидаемыми
platform skips, 246-file context manifest PASS, PowerShell isolated apply/dry-run/idempotency и
Git Bash dry-run PASS; реальный runtime home не изменялся.

## Текущий master — Brownfield Canonical Stage Compatibility

`DEV-BCSC-001` расширяет integrated CME generic compatibility adapter-ом. Runnable slice
`DEV-BCSC-A` verified at `2e442a9`: deterministic classification, same-file retained-legacy
manifest contract и read-only dry-run migration plan реализованы без product mutations.
`DEV-BCSC-B` verified at `1083478`: externally approved digest, full byte preconditions, atomic
STAGES materialization, canonical read-back, CAS rollback/recovery и idempotency реализованы и
проверены только на temporary repositories. `DEV-BCSC-C` verified at implementation checkpoint
`f1f8302`: normal router/validator/SessionStart adoption, same-snapshot selector enforcement,
typed exit semantics, explicit migration handoff и read-only product evidence завершены. Windows
CRLF parity подтверждена post-merge regression fixes `3e03a24` и `60a1efb`; master completed and
fast-forward integrated into local `main` through `60a1efb`, router returns
`master_already_completed`. Product rollout/legacy retirement не входят в master; push не
выполнялся.

## Текущий internal delta — Continuous Master Execution

Approved master выполняется поверх checkpoint `72197b2` в том же isolated track. Phase A фиксирует
SPEC/ADR/gap map; следующие backward-complete slices добавляют deterministic worktree routing,
execution graph/auto-continue, low-context handoff, evidence/integration gates и hierarchical
prompt lifecycle. Phases A–F completed; implementation checkpoint `c81ee81`, full 181 tests и
238-file context validation PASS. Master сохраняется в Notion из-за retention `keep`.
Read-only Tutor compatibility check выявил pre-existing legacy state/selector migration gap;
product mutation не выполнялась. Feature chain fast-forward merged into local `main` at
`1e34f41`; post-merge verification PASS, push не выполнялся.

## Предыдущий internal delta — Canonical STAGES.md Policy

Единый `prompts/STAGES.md` теперь владеет selector, current plan, lifecycle/evidence, blockers и
`NEXT`. Global governance/hooks/validators/Skills/templates мигрированы; legacy AI plan/status
sources удалены после semantic/link audit. Full suite 140 PASS, context validator 233 files PASS,
`git diff --cached --check` PASS. Implementation `72197b2` merged into local `main` through
`1e34f41`; push не выполнялся.

## Предыдущий internal delta — Prompt Queue Lifecycle

Retention/guard/receipt implementation и project propagation выполнены и проверены отдельно от product
master. Source policy: `rules/prompt-queue-lifecycle.md`; current evidence — `prompts/STAGES.md`.
Checkpoint `80a63b3` merged into local `main` through `1e34f41`; push не выполнялся.


## Выполнено

- базовая AI Dev Team;
- SDD и context routing;
- project framework;
- read-only project-overlay validator;
- canonical Fallback Policy;
- canonical Node package-management policy;
- canonical Backend Developer Experience Policy и audit Skill;
- Completion Documentation Synchronization Gate для task/stage/merge closeout;
- отделение состояния ДЕВ от live-состояния product repositories.
- канонический контракт архитектурно завершённых stages, scaffold-safe lifecycle/evidence и
  task-aware `STAGES selector → selected STAGES record` projection — fast-forward merged locally,
  88 tests PASS, runtime Skill parity 9/9.
- единый project workflow: canonical DEV source ownership и installed `~/.codex` projection, восемь lifecycle requests,
  documentation/LEARNING triggers, external projection rules, computer↔laptop restore, monitoring
  classes и fail-visible global source-root validation — 94 tests PASS, 199-file manifest PASS;
  feature commit `4bcdf32` fast-forward merged в локальную `main`, push не выполнялся.
- global i18n/l10n standard для всех user-facing products: один canonical policy owner,
  language/locale separation, translation resources, locale-aware formats, fallback, text
  expansion/RTL и self-contained initial slice — 101 tests PASS, 201-file manifest PASS; feature
  commit `ee3ea8a` fast-forward merged в локальную `main`, product rollout и push не выполнялись.
- AI Policy Profiling / Agent Economics Observe layer: opt-in schema/JSONL CLI, automatic safe
  command/Git/wall facts, policy/experiment/agent/reuse/handoff events, bounded discovery, false
  reuse, baseline/variant aggregation и JSON/Markdown report — 124 tests и 213-file context
  validation PASS; implementation commit `ea1fe24` fast-forward merged и pushed в `origin/main`.
  Product rollout не выполнялся; synthetic sample не является ROI evidence policy.
- Canonical STAGES.md Policy: single execution-state owner, same-file selector, deterministic
  brownfield `MERGE` classification и greenfield single template — 140 tests и 233-file context
  validation PASS; commit `72197b2` fast-forward merged into local `main` through `1e34f41`,
  push не выполнялся.

## Текущее

- Global framework hardening — `implemented_unverified`: thin global router, exact shared Stage
  selector contract, reviewed model inheritance/pins, Windows/Bash installer parity, thin project
  template и read-only CI реализованы; 110 tests и 207-file context validation PASS. Terminal
  installer/global validation блокирует только pre-existing `unmatched-browser-client-hash` в
  active runtime config; feature commit `67112aa` fast-forward merged в локальную `main`, push не
  выполнялся.

## Дальнейшие направления

- развитие model/tool routing;
- Prompt Compiler и policy validation;
- tracing/evals;
- opt-in rollout AI Policy Profiling в один selected project, затем сбор сопоставимых real task
  families до human-approved threshold recommendation;
- дополнительные reusable security/testing policies;
- улучшение validators;
- semantic broken-link/stage validation только после versioned schema и low-false-positive design;
- новые общие Skills/agents только при подтверждённой повторяемой потребности.

Product-specific rollout не является этапом этого roadmap.
