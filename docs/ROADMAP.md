# Roadmap AI Dev Team

## Текущий internal delta — Prompt Queue Lifecycle

Retention/guard/receipt implementation и project propagation выполнены и проверены отдельно от product
master. Source policy: `rules/prompt-queue-lifecycle.md`; current evidence — AI_STATUS.
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
  task-aware `AI_PLAN → selected STAGES record` projection — fast-forward merged locally,
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
