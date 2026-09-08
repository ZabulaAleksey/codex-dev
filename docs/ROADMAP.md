# Roadmap AI Dev Team

## Текущий internal delta — Continuous Master Execution

Approved master выполняется поверх checkpoint `72197b2` в том же isolated track. Phase A фиксирует
SPEC/ADR/gap map; следующие backward-complete slices добавляют deterministic worktree routing,
execution graph/auto-continue, low-context handoff, evidence/integration gates и hierarchical
prompt lifecycle. Phases A–F completed; implementation checkpoint `c81ee81`, full 181 tests и
238-file context validation PASS. Master сохраняется в Notion из-за retention `keep`.
Read-only Tutor compatibility check выявил pre-existing legacy state/selector migration gap;
product mutation не выполнялась. Merge/push не выполнялись.

## Предыдущий internal delta — Canonical STAGES.md Policy

Единый `prompts/STAGES.md` теперь владеет selector, current plan, lifecycle/evidence, blockers и
`NEXT`. Global governance/hooks/validators/Skills/templates мигрированы; legacy AI plan/status
sources удалены после semantic/link audit. Full suite 140 PASS, context validator 233 files PASS,
`git diff --cached --check` PASS. Implementation committed as `72197b2`; merge/push не выполнялись.

## Предыдущий internal delta — Prompt Queue Lifecycle

Retention/guard/receipt implementation и project propagation выполнены и проверены отдельно от product
master. Source policy: `rules/prompt-queue-lifecycle.md`; current evidence — `prompts/STAGES.md`.
Merge/push не выполняются до отдельного разрешения пользователя.


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
- единый project workflow: actual `~/.codex` source ownership, восемь lifecycle requests,
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
  validation PASS; validated locally without commit/merge/push.

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
