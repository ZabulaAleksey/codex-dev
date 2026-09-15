# Continuous Master Execution

Статус: утверждена пользователем 2026-09-08 на основе Notion master prompt
`DEV — Continuous Master Execution, Parallel Worktrees & Low-Context Orchestration — MASTER PROMPT`.
Source page: `https://app.notion.com/p/3d461ed8f246812db41cda2510a70dd3?pvs=204`.

## 1. Цель

После одного явного запуска `master_prompt` агент восстанавливает durable live state, выбирает и
выполняет последовательность готовых backward-complete slices без новых пользовательских prompts
между однозначными безопасными шагами. Независимые write-tracks изолируются Git worktree/branch,
continuation переиспользует существующий track, а новая сессия получает bounded context и handoff
из repository evidence.

## 2. Scope

Входит:

- portable master/slice execution graph и deterministic readiness/stop transitions;
- canonical persistence execution state внутри selected record `docs/STAGES.md`;
- Git/worktree route planning и guarded adapter для continuation/parallel track;
- context scope, budget, launcher/handoff, evidence и integration checkpoint gates;
- hierarchical Prompt Queue Lifecycle и recovery scenarios;
- global rules, architecture, Skills/templates, validators и automated tests;
- controlled validation на temporary repositories.

Не входит:

- универсальный background scheduler или исполнение произвольных команд из state/prompt;
- массовый rollout/mutation product repositories;
- active `~/.codex/config.toml`, credentials, sessions, cache или external-service writes;
- автоматический merge, push, release, deployment или destructive worktree cleanup;
- привязка lifecycle к одному UI, одному prompt store или одному product domain.

## 3. Functional requirements

### CME-001 Continuous execution lifecycle

После explicit master start controller восстанавливает live state, выбирает единственный
dependency-ready slice, проверяет evidence/stop conditions и возвращает `continue`, `handoff`,
`integration_checkpoint`, `user_decision`, `blocked` либо `complete`. Checkpoint commit сам по себе
не является stop condition. При неоднозначном ready set controller останавливается fail closed.

### CME-002 Canonical durable state

Master/track/slice graph сохраняется как versioned bounded `master-execution` JSON block внутри
selected stage record `docs/STAGES.md`; отдельный plan/status/registry owner не создаётся.
State содержит master/track IDs, branch/worktree, source revision/retention, checkpoints, graph,
evidence, blockers, decisions, context budget и next action. Invalid/oversized/duplicate state
даёт stable validation failure и не запускает следующий slice.

### CME-003 Track and worktree routing

Continuation того же master/track/repository переиспользует зарегистрированный worktree. Новый
независимый write-track получает отдельные branch/worktree; read-only и same-chain work не создают
worktree механически. Adapter не переключает branch другого worktree, не перезаписывает занятый
path/branch и не удаляет worktree. Overlap architectural ownership создаёт integration risk.

### CME-004 Dependency, stop and auto-continue gates

Slice может стать ready только после terminal predecessors и доступных dependencies. Mandatory
evidence gate блокирует downstream при `implemented_unverified`, missing/unavailable evidence или
hard blocker. User decision, destructive/irreversible action, external input, canonical conflict,
integration write, context overflow, full completion и explicit stop прекращают auto-continue.

### CME-005 Low-context continuation and handoff

ContextScope Resolver возвращает минимальный ordered package: routing, current master summary,
immediate predecessor evidence, relevant SPEC/ADR, touched subsystem files/tests и blockers.
Budget учитывает chars/items/changed contours/unresolved decisions/evidence threads. Overflow
создаёт compact launcher/handoff с master/track, branch/worktree, checkpoint, verified chain,
next action, blockers, stop/merge/cleanup semantics; stale launcher определяется по checkpoint и
state revision.

### CME-006 Evidence and integration discipline

Evidence levels нормализованы как `L1..L6`; required level задаётся slice risk. Controller отделяет
`regression`, `pre_existing`, `unrelated_debt`, `environment_unavailable`. Integration checkpoint
возникает только на coherent boundary, dependency между tracks, divergence/overlap risk либо
finalization и никогда сам не выполняет merge/push/release.

### CME-007 Hierarchical prompt lifecycle

Completed one-shot launcher/child может стать cleanup-eligible независимо от partial parent master.
Partial/blocked/needs-continuation master сохраняется; master cleanup возможен только после overall
DoD и retention/authorization gates существующего Prompt Queue Lifecycle. Completed execution
master с историческим `keep` требует отдельной zero-orphan/runtime-parity/regression аттестации.
Existing exact-item
guard/receipt/read-back остаётся единственным cleanup mechanism.

### CME-008 Recovery and portability

Recovery сверяет Git HEAD/status/worktrees с durable state и классифицирует crash-after-commit,
status-before-failed-commit, missing branch/worktree, stale launcher, changed master revision,
dirty user edits, overlapping integration, absent queue item и compacted session. Unknown or
conflicting facts fail closed. Core lifecycle не зависит от Codex UI; Git, prompt store, model и
evidence являются adapters.

## 4. Non-functional and security requirements

### NFR-CME-001 Determinism and bounds

Одинаковые normalized state и adapter facts дают одинаковое решение. Files/blocks/collections,
subprocess timeouts и output bounded; unknown fields, duplicate keys/IDs и path escape отклоняются.

### NFR-CME-002 Safe side effects

State/prompt не исполняет commands. Git mutation доступна только через explicit narrow operation;
unknown outcome требует reconciliation. Merge/push/release/cleanup остаются approval-gated.

### NFR-CME-003 Backward compatibility

Project без `master-execution` block продолжает использовать обычный Stage contract. Новый block
обязателен только когда project объявляет Continuous Master Execution.

## 5. Acceptance criteria

- `AC-CME-001`: valid selected master record parses into one graph; invalid/duplicate/oversized
  state and duplicate IDs fail visibly.
- `AC-CME-002`: ready selector respects predecessor/dependency/evidence gates, stops on ambiguity
  and auto-continues across two verified deterministic slices without user prompt.
- `AC-CME-003`: same-track continuation reuses worktree; independent writer routes to isolated
  branch/worktree; read-only route creates nothing; occupied/conflicting targets fail closed.
- `AC-CME-004`: context resolver is targeted and deterministic; budget overflow emits a complete
  low-context handoff; stale launcher is rejected.
- `AC-CME-005`: `L1..L6`, verification gates, blocker classes and integration checkpoint policy
  prevent evidence inflation and automatic integration writes.
- `AC-CME-006`: completed child is cleanup-eligible while partial master is retained; existing
  prompt cleanup guard remains authoritative and repeat cleanup is `noop` with valid receipt.
- `AC-CME-007`: recovery tests cover required Git/state/prompt/context mismatch scenarios and never
  overwrite dirty work or infer missing evidence.
- `AC-CME-008`: SessionStart projects only selected bounded master slice state; project/global
  validators, full unit suite and `git diff --check` pass.
- `AC-CME-009`: docs/Skills/templates use short-command and no-repetitive-merge semantics; no new
  competing execution state, scheduler, dependency or runtime config is introduced.

## 6. Requirement-to-test mapping

| Requirement | Planned executable evidence |
|---|---|
| CME-001, CME-004 | graph readiness/auto-continue/stop-condition unit and CLI scenario tests |
| CME-002, NFR-CME-001 | selected-record parser/schema and overlay validator negatives |
| CME-003, NFR-CME-002 | temporary real Git repository/worktree integration tests |
| CME-005 | context scope, budget, launcher and stale-handoff tests |
| CME-006 | evidence/blocker/integration transition tests |
| CME-007 | prompt hierarchy tests plus existing cleanup guard suite |
| CME-008, NFR-CME-003 | recovery matrix, ordinary non-master overlay regression tests |

## 7. Open questions

Нет блокирующих вопросов. Runtime конкретного агента остаётся adapter: controller принимает
attested result/evidence и не пытается безопасно решить произвольную implementation task сам.

## 8. История

- 2026-09-08 — v1: approved master prompt converted into a bounded portable contract.
