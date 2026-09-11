# Specification → Execution Pipeline

Статус: утверждена пользователем 2026-09-11 на основе Notion master prompt
`DEV — Specification→Execution Pipeline, Skill Router, Automation Promotion & Context Economy — MASTER PROMPT`.
Source page: `https://app.notion.com/p/3d561ed8f24681c0b8c6d06c1819bb4a?pvs=204`;
source revision: `2026-09-08T19:51:49.477Z`.

## 1. Цель

Расширить Continuous Master Execution единым stage-first контуром, который переводит approved
SPEC и live stage в минимальный набор capabilities, Skills, deterministic executors и evidence
gates. Повторяемая механика получает evidence-driven automation candidate и bounded promotion
decision; LLM reasoning остаётся для неоднозначности, novelty, architecture и неизвестных ошибок.

Целевой поток:

```text
user intent → global invariants → project delta → live repository/current stage
→ relevant requirement/architecture boundary → capability route → required Skills/tools
→ implementation or explicit reasoning fallback → validators/tests/evidence
→ canonical STAGES update → automation promotion review
```

## 2. Scope и границы

Входит:

- versioned global capability/Skill registry и optional project/domain delta;
- stage-first request/contract, deterministic relevant-capability routing и context plan;
- compact intake для `CONTINUE_EXISTING` и `NEW_PROJECT`;
- requirement → owner → stage → capability → files → validator → evidence trace;
- deterministic-first/model-cost decision с explicit escalation reason;
- automation opportunity detection, target/placement decision, deduplication и closure;
- global/project/domain placement validation и conservative Skill-retirement audit;
- lightweight context-economy diagnostics;
- интеграция с existing CME, Stage selector, project overlay validator, profiler и Prompt Queue;
- progressive backward-compatible rollout, tests и documentation synchronization.

Не входит:

- второй scheduler, task registry, execution-state owner или prompt lifecycle;
- исполнение произвольных commands из SPEC, registry, stage или Notion;
- semantic inference из всего repository без bounded reason;
- автоматическое создание/удаление Skill, hook, CI, project overlay или product files;
- automatic model-policy tuning, merge, push, release, deployment или queue cleanup;
- массовая migration существующих product repositories;
- перенос product semantics из SPEC/ADR в registry или Skill prose.

Canonical owners:

| Источник | Вопрос | Не владеет |
|---|---|---|
| user intent | зачем работа запущена сейчас | architecture, historical state |
| global rules | какие общие invariants обязательны | project-specific commands |
| project overlay | какая project/domain delta нужна | generic DEV implementation |
| live Git + selected `prompts/STAGES.md` | что фактически активно сейчас | durable product requirements |
| SPEC / structured contract | что система обязана делать | implementation procedure |
| architecture / ADR | где responsibility и почему принято решение | current execution status |
| stage/slice | что ограниченно выполняется сейчас | полный master payload |
| capability router | какие capabilities/Skills/tools/gates нужны | requirement truth |
| Skill | как повторяемо выполнить типовую операцию | второй SPEC/architecture owner |
| tool/library | детерминированная механика | неизвестное reasoning |
| validator/test | как доказать behavior | lifecycle/evidence claim без run |
| CME / Prompt Queue / profiler | execution graph / cleanup guard / opt-in observations | этот новый registry |

## 3. Existing primitive → required capability → gap

| Existing primitive | Reuse | Bounded gap |
|---|---|---|
| `stage_selector.py`, `stage_compatibility.py`, `dev_paths.py` | exact live project/stage routing | stage contract не разрешает requirement/capability links |
| `master_execution.py` | graph, worktree, context budgets, evidence, recovery | caller вручную передаёт context items; capability route отсутствует |
| `skill-sources/`, `sync_global_skills.py` | source/runtime lifecycle и hash parity | нет capability metadata и deterministic selection |
| SPEC/STAGES templates | human requirement/test/stage contract | нет executable trace validation |
| `validate_project_overlay.py` | read-only project gate | не проверяет global-vs-overlay capability duplication |
| `ai_policy_profiler.py` | opt-in outcome/economics facts | не принимает promotion decisions и не меняет policy |
| `prompt_queue.py` | exact cleanup eligibility/receipt | не является automation backlog |
| `reconcile_project_framework.py`, bootstrap Skills | brownfield/new-project intake | нет compact machine intake/route output |

## 4. Functional requirements

### SEP-001 — Stage-first context order

Default implementation route разрешает context в порядке: applicable global rules; project
entrypoint/delta; live Git and selected STAGES/NEXT; current slice; referenced SPEC requirements;
referenced architecture/ADR boundaries; router-selected Skills; touched/dependency files; targeted
validators/tests; predecessor evidence/blockers. Full master, all SPEC/ADR/Skills, full repository,
old chat и historical handoffs запрещены по умолчанию. Full scan требует одного stable reason:
`unknown_ownership`, `architecture_drift`, `contract_conflict`, `final_audit`,
`unknown_regression`, `explicit_user_request` или `targeted_path_failed`.

### SEP-002 — Capability and Skill registry

Versioned registry entry содержит stable `id`, `scope` (`global|domain|project`), capabilities,
triggers, inputs, outputs, required tools/context, stop conditions, validators, version, maturity,
executor kind и ownership. Skill entry дополнительно указывает exact source path. Unknown fields,
duplicate IDs/capabilities, ambiguous owners, missing referenced paths и invalid bounds fail closed.
Registry — routing metadata, а не копия SPEC, architecture или execution state.

### SEP-003 — Relevant-only router

Router принимает already-resolved intent, selected stage, requirement IDs, components, change
types, risk/criticality и optional project/domain registry. До известного stage/scope Skill не
загружается. Matching required trigger не может потерять обязательную capability; irrelevant Skill
не входит в default route. Conflict, missing required capability или duplicate incompatible owner
даёт typed stop. Output упорядочен и содержит selected capabilities/Skills/tools/context/tests,
unresolved gaps и reason codes.

### SEP-004 — Deterministic-first and cheapest-sufficient execution

Executor route использует порядок: deterministic tool; validator/parser/compiler/query; Skill с
deterministic executor; bounded low-risk model; normal implementation model; high-reasoning route;
strongest available route только после evidence-backed unresolved novelty/risk/failure. Размер
задачи сам по себе не повышает модель. Failure deterministic path сохраняет stable escalation reason
и становится input promotion review; неизвестный root cause не маскируется фиктивной automation.

### SEP-005 — Requirement/capability/evidence trace

Critical route поддерживает structured link:
`requirement_id → owner_component → selected_stage → capability_ids → implementation_files →
validator_ids/test_commands → evidence`. Validator проверяет uniqueness, registry references,
stage requirement references, owner compatibility, required evidence и absence of unsupported
completion claim. Trace не заменяет accepted test contract и не исполняет commands.

### SEP-006 — Compact intake and durable constraints

Normalizer выдаёт bounded структуру: `intent`, `project`, `master_or_goal`, `requested_change`,
`explicit_constraints`, `explicit_non_goals`, `write_permissions`, `user_decisions`. Он поддерживает
`CONTINUE_EXISTING` как delta поверх live state и `NEW_PROJECT` с exact intake class:
`GREENFIELD`, `COMPOSITION`, `FORK_EXTERNAL_REPOSITORY`,
`MIGRATION_ADOPTION_EXISTING_CODEBASE`. Ambiguous new-project class требует decision и не смешивает
режимы. Compaction сохраняет explicit constraints/non-goals/permissions/decisions verbatim within
bounds; repository facts всегда новее stale handoff.

### SEP-007 — Automation Opportunity Detector

Structured observation становится candidate при повторной инструкции/механической последовательности,
повторном review defect, выражаемом кодом manual gate, stable mapping или stable input/output/pass/fail
contract. One-off product decision, unknown research, unstable procedure и negative risk/benefit
не создают candidate. Candidate имеет stable fingerprint, recurrence/evidence, priority, status,
scope и provenance without prompt/source payload. Повтор deduplicate-ится; terminal candidate не
возвращается как новый open duplicate без new version/reopen reason.

### SEP-008 — Promotion and placement decision

Pure decision выбирает durable target: documentation/contract, Skill/recipe, script/tool,
library/module, router rule/table, validator/test либо hook/CI/gate. Placement выбирается как
global DEV для generic cross-project behavior, project overlay для domain/project semantics либо
shared domain для нескольких близких проектов. Сначала проверяется equivalent global capability.
Project duplicate запрещён без explicit bounded exception/adapter delta. Decision не выполняет
write и не продвигает policy автоматически.

### SEP-009 — Automation lifecycle and Skill retirement

Candidate проходит `open → approved|rejected → implemented → verified → closed` либо остаётся
`open`/`blocked`; переходы fail closed. Skill-retirement audit только рекомендует compile/shorten/
deduplicate/retire и запрещает удаление единственного required contract, единственного route owner
или Skill с unresolved consumers. Product semantics направляется в SPEC, architecture decision —
в ADR/architecture, stable mechanics — в tool/validator.

### SEP-010 — Context economy diagnostics

Для substantial slice bounded record может фиксировать количество/IDs context sources и Skills,
full-repo/full-master scan с reason, reused automation, reasoning fallback и model/reasoning class.
Diagnostics обнаруживает unused Skill, unjustified scan, stale handoff preference, strongest-model
mechanics и repeated manual procedure. Missing opt-in telemetry остаётся unknown и не блокирует
обычный DoD; raw prompt/code/output/env/secrets не сохраняются.

### SEP-011 — CME and project compatibility

Pipeline расширяет selected CME slice optional structured execution contract-ом и не меняет ordinary
project без него. SessionStart/validators остаются read-only; invalid route даёт visible degraded/
blocked result, но не выбирает другую stage. `prompts/STAGES.md` остаётся единственным execution-state
owner; Prompt Queue — cleanup owner; profiler — optional observations owner.

### SEP-012 — Minimal user entrypoints

`Продолжай <project/master>` достаточно для `CONTINUE_EXISTING`: resolver восстанавливает exact
project/live state/current safe slice, после чего pipeline выбирает context/capabilities/evidence и
автопродолжает только по CME stop policy. `Новый проект: <name>. Цель: <goal>.` достаточно для
`NEW_PROJECT`: после explicit intake class existing КАРКАС bootstrap формирует project-specific
overlay/SPEC/STAGES, не копируя global rules. User prompt сообщает intent и новые constraints, а не
повторяет infrastructure protocol.

## 5. Security, fallback и bounds

- Реализация Python standard library only; JSON inputs bounded по file size, depth, items и strings.
- Registry/state не содержит commands для исполнения; test command является declarative evidence
  reference и запускается только existing authorized workflow.
- Project paths resolve inside exact Git root; symlink/junction escape и unknown scope fail closed.
- Contract conflict, ambiguous route, missing owner/capability, deterministic failure и stale input
  имеют typed outcome; silent fallback запрещён.
- Registry/provider outage оставляет manual reasoning route visible; completion evidence не
  повышается.
- New capability/Skill/hook/CI creation остаётся ordinary reviewed code change. Candidate/decision
  сам по себе не авторизует mutation.
- Active runtime config, credentials, sessions, plugin state и external queue остаются вне scope.

## 6. Acceptance scenarios

- `AC-SEP-A`: backend API slice выбирает SPEC/API owner/backend integration capability и исключает
  frontend/SEO/browser Skills.
- `AC-SEP-B`: DB migration route требует migration head/upgrade/downgrade checks и real-DB gate по
  risk; отсутствие environment не превращается в PASS.
- `AC-SEP-C`: повторный stable manual check deduplicate-ится и получает `validator_test` promotion.
- `AC-SEP-D`: project-format parser остаётся project/domain capability и не попадает в global DEV.
- `AC-SEP-E`: generic Git/evidence/context check переиспользует global capability; project copy
  без exception отклоняется.
- `AC-SEP-F`: unknown defect получает reasoning/debug route; после stable resolution detector может
  создать candidate, но не раньше.
- `AC-SEP-G`: short continuation использует live stage и bounded launcher без full master/repo scan.
- `AC-SEP-H`: conflicting SPEC/ADR contract блокирует auto-execution для decision.
- `AC-SEP-I`: required Skill trigger не пропускается, irrelevant Skills не загружаются и router
  output детерминирован.
- `AC-SEP-J`: trace с missing capability/test/evidence или unsupported completion fail closed.
- `AC-SEP-K`: completed candidate не остаётся вечным duplicate; retirement не удаляет единственного
  contract owner.
- `AC-SEP-L`: existing CME/ordinary Stage, Prompt Queue, profiler, project overlay and global
  installation tests остаются совместимыми; context validator и `git diff --check` PASS.

## 7. Requirement → executable evidence

| Requirement | Planned evidence |
|---|---|
| SEP-001, SEP-003, SEP-011 | route/context unit tests, selected-stage hook/overlay integration |
| SEP-002 | registry schema/parser/path/duplicate/unknown-field tests |
| SEP-004 | executor-cost decision and deterministic-failure escalation tests |
| SEP-005 | trace positive/negative validation and accepted stage evidence scenario |
| SEP-006, SEP-012 | compact intake/constraint preservation and live-vs-stale tests |
| SEP-007..009 | detector/dedup/lifecycle/promotion/placement/retirement tests |
| SEP-010 | context-economy record/diagnostic/privacy/bounds tests |
| all | targeted suite, full unittest discovery, global context validator, diff check, final review |

## 8. Progressive slices

1. `DEV-SEP-A`: source-responsibility contract, gap map, SPEC/ADR and master graph.
2. `DEV-SEP-B`: registry/schema, stage-first router, context/intake and executor-cost route.
3. `DEV-SEP-C`: executable trace and global/project/domain placement validator.
4. `DEV-SEP-D`: automation detector/promotion/lifecycle plus two deterministic promotion paths.
5. `DEV-SEP-E`: context metrics, Skill-retirement audit, hook/validator/workflow integration and
   gradual migration of duplicated procedures.
6. `DEV-SEP-F`: acceptance A–H, compatibility/security review, full verification and master sync.

Each slice is backward-complete and may stop only on CME canonical stop conditions. A checkpoint is
not a stop. The Notion master has retention `keep` and is not cleanup-eligible on completion.

## 9. Rollback

Feature artifacts are versioned and can be reverted atomically. Optional registry/contract absence
preserves prior CME behavior. Product overlays and active runtime are not migrated by this master;
no destructive data rollback is required.

## 10. History

- 2026-09-11 — v1: approved Notion master compiled into bounded requirements and progressive graph.
