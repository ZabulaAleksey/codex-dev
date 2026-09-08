# Brownfield Canonical Stage Compatibility

Статус: утверждена пользователем 2026-09-08.

## 1. Цель

Расширить Continuous Master Execution единым read-only compatibility adapter для brownfield
repositories, где execution state ещё распределён между prompts/STAGES.md, docs/AI_PLAN.md и
docs/AI_STATUS.md. Adapter должен детерминированно классифицировать состояние, сформировать
проверяемый dry-run migration plan и fail closed при конфликте, не изменяя product repository.

## 2. Scope

Входит:

- bounded detection canonical, legacy, mixed, conflicting, migrated и absent state;
- strict extraction только явно размеченных legacy selector/status facts;
- normalized projection current stage/master, status, next selector, blockers, checkpoint/evidence;
- versioned stage-compatibility manifest внутри selected prompts/STAGES.md record;
- content digests retained legacy sources и drift detection;
- dry-run migration plan с stable idempotency key;
- explicit digest-matched materialization API с typed stale/already-materialized/failure outcomes;
- bounded transactional writes, read-back validation и rollback на pre-materialization bytes;
- integration в существующий tools/master_execution.py CLI;
- temporary-repository tests и read-only evidence на electro-tutor.

Не входит:

- автоматическая либо неявная запись или удаление файлов product repositories;
- semantic guessing из произвольного prose;
- массовый rollout, merge, push, deployment или изменение runtime config;
- второй scheduler, task registry, hook или orchestration framework.

## 3. Functional requirements

### BSC-001 Deterministic classification

Одинаковые bytes известных state files дают один из классов canonical, legacy, mixed,
conflict, migrated или none. Порядок filesystem iteration и locale не влияют на результат.

### BSC-002 Bounded legacy adapter

Adapter читает только prompts/STAGES.md, docs/AI_PLAN.md и docs/AI_STATUS.md как contained regular
files с per-file limit. Symlink/path escape, oversized content, malformed/duplicate selector и
unsupported encoding дают conflict; product scripts и Markdown commands не выполняются.

### BSC-003 Canonical compatibility manifest

Завершённая migration фиксируется versioned stage-compatibility JSON block в selected record
prompts/STAGES.md. Block хранит canonical projection и SHA-256 каждого retained legacy source.
Это не второй state owner: runtime после migration читает projection из того же selected record.

### BSC-004 Normalized projection

Результат содержит current_stage, master_id, status, next_selector, blockers, checkpoint и
evidence. Неизвестные legacy facts представлены пустым значением и explicit issue, а не догадкой.
current_stage и next_selector обязаны быть valid stable IDs. Если отдельный legacy `NEXT`
отсутствует, adapter возвращает explicit incomplete issue и не создаёт runnable migration plan;
он не подменяет отсутствующий факт текущим stage.
Nullable master_id/checkpoint означает, что legacy project не объявляет master/checkpoint;
пустые blockers/evidence означают отсутствие exact structured facts, а не разбор prose.
Только canonical/migrated state с valid current_stage, status и next_selector получает
`runnable=true`; остальные classification всегда non-runnable независимо от CLI exit code.

### BSC-005 Conflict semantics

Несогласованные selector/status facts, ambiguous/malformed canonical selector или missing/ambiguous
selected heading, invalid manifest,
manifest/source digest drift либо canonical/legacy selector mismatch дают route
migration_required и classification conflict. Controller не запускает product stage.

Наличие `prompts/STAGES.md` без same-file selector при согласованном legacy pair является
`mixed`/partial migration и может получить dry-run plan; отсутствие legacy state в том же случае
остаётся `conflict`.

### BSC-006 Dry-run migration plan

Полный и непротиворечивый legacy/mixed state возвращает immutable plan: target prompts/STAGES.md, source fingerprints,
normalized projection, preserve list, manual-review issues, destructive_removals=false и stable
idempotency_key. Повторный запуск на тех же bytes возвращает идентичный report/plan.
Incomplete state остаётся non-runnable `migration_required` с explicit issues и без plan.

### BSC-007 No automatic mutation

Первый slice не имеет apply mode. Legacy files не удаляются, product repositories не
переписываются, Git status до и после inspection совпадает.

### BSC-008 Existing CME extension

Compatibility mode является ветвью существующего tools/master_execution.py CLI и переиспользует
stage_selector contracts. Он не создаёт второй orchestration framework или альтернативный hook.

### BSC-009 Backward compatibility

Pure canonical repository сохраняет текущий selector behavior и получает route=canonical без
migration plan. Already migrated repository с совпадающими digests также получает canonical route.

### BSC-010 Evidence fixture

electro-tutor используется только как read-only brownfield evidence. Его текущий legacy pair и
missing same-file selector должны давать migration_required без изменения Git status.

### BSC-011 Self-contained materialization plan

Executable plan является strict versioned JSON contract и содержит portable root marker,
path-bound repository identity, исходную classification/routing projection, intended canonical
state, полный ordered список writes, before/after SHA-256, source/target preconditions,
generator version, reasons/evidence, `plan_id` и собственный `plan_digest`. Materializer требует
отдельно переданный approved `expected_plan_digest`, выполняет только объявленные bytes и не
повторяет semantic inference planner-а.

### BSC-012 Stale-plan rejection

После exclusive lock и до первого write materializer повторно проверяет repository identity,
все known state sources, target existence/type/digest и plan digest. Любой relevant drift даёт
typed `stale_plan`, `writes=0`; Git HEAD сам по себе не заменяет byte preconditions.

### BSC-013 Target allow-list and apply-time containment

Operations допускают только project-relative canonical targets из versioned allow-list,
не содержат duplicate/absolute/parent traversal paths и имеют существующий contained regular
parent. Symlink/junction/non-file/escape проверяются при plan validation, после lock и
непосредственно перед staging/replace/rollback.

### BSC-014 Transactional materialization

Все intended bytes сначала записываются в exclusive sibling temporary files, flush/fsync-ятся и
только затем заменяют targets через atomic replace. Pre-image каждого target сохраняется bounded
in-memory. Ошибка до/during multi-file publish восстанавливает каждый уже опубликованный target
либо удаляет созданный target, не выдавая partial state за success.

### BSC-015 Read-back and rollback

После publish materializer сверяет target digests, запускает existing compatibility parser/router
и требует exact intended selector/projection, `classification=migrated`, `route=canonical` и
`runnable=true`. Любое несовпадение вызывает rollback и typed `readback_failed`; rollback failure
имеет отдельный fail-closed result и не маскируется как success.

### BSC-016 Idempotency and concurrency

Повторный apply того же untampered plan при unchanged non-target sources и уже совпадающих target
digests возвращает deterministic `already_materialized` без rewrite. Per-repository exclusive
create-only lock сериализует concurrent attempts; занятый lock возвращает typed
`concurrent_materialization`, не ждёт и не выполняет writes. Неизвестный/stale lock не удаляется
по возрасту автоматически и даёт `recovery_required` до явной reconciliation.

### BSC-017 Legacy preservation

`docs/AI_PLAN.md` и `docs/AI_STATUS.md` являются retained preconditions: Slice B не включает их
в write/delete operations. Manifest сохраняет provenance/digests; destructive cleanup требует
отдельного будущего разрешения.

### BSC-018 Explicit CLI boundary

Existing `tools/master_execution.py` принимает materialization только через отдельный explicit
plan-file option и отдельно переданный `expected_plan_digest`; mode несовместим с analysis/
execution options. Compatibility inspection без него остаётся read-only. CLI exit code равен нулю
только для `materialized` и `already_materialized`. Slice B применяет CLI только к temporary
repositories.

### BSC-019 Failure injection contract

Transaction имеет private deterministic test seam перед staging/publish/read-back, чтобы tests
доказывали zero-write и full rollback без ослабления production checks. Test seam не управляется
plan content и не экспортируется как CLI option. Public plan allow-list содержит только
`prompts/STAGES.md`; обязательная multi-write rollback проверка использует private transaction
primitive с synthetic targets внутри temporary repository и не создаёт второго state owner.

### BSC-020 No real product rollout in Slice B

Все positive materialization evidence создаётся в temporary repositories. `electro-tutor`
проверяется только analysis mode и остаётся non-runnable/unchanged; mass rollout и product hook/
validator adoption принадлежат `DEV-BCSC-C`.

### BSC-021 Normal route adoption

Обычные `master_execution`, project validator и SessionStart/SubagentStart используют один
read-only compatibility inspector автоматически. Explicit `--compatibility` остаётся diagnostic
mode, но больше не является обязательным предварительным знанием для обнаружения brownfield state.

### BSC-022 Typed stage-routing projection

Один compact result различает `pass_canonical`, `migration_plan_available`,
`migration_plan_unsafe`, `conflicting_stage_state` и `no_stage_state` и всегда содержит отдельные
`inspection_ok`, `canonical_valid`, `execution_allowed`, classification/route, normalized current
projection, exact issues и bounded migration handoff. Low-level Slice A classifications остаются
`canonical | migrated | legacy | mixed | conflict | none`.

### BSC-023 Canonical same-file enforcement

Canonical/migrated execution разрешён только когда current stage/master, status, NEXT, blockers и
required checkpoint/evidence однозначно разрешаются из selected `prompts/STAGES.md` record либо
его digest-verified same-file manifest. Невалидный canonical file с внешне согласованным legacy
state остаётся `conflicting_stage_state`; silent fallback на legacy запрещён.
Authorization и передаваемый consumer-у selected record принадлежат одному bounded read snapshot;
повторное чтение STAGES между route decision и execution/context injection запрещено.

### BSC-024 Validator semantics

`validate_project_overlay` включает typed stage-routing projection в Python/JSON result. Canonical
PASS имеет exit `0`; safe/unsafe migration и no-state discovery имеют отдельный non-zero advisory
exit; conflicting/canonical-invalid state и другие overlay violations остаются blocking non-zero.
Retained `AI_PLAN`/`AI_STATUS` не дублируются generic competing-file errors: ими владеет typed
compatibility result. Inspection success не означает canonical validation или execution approval.

### BSC-025 Hook semantics

SessionStart/SubagentStart выводят existing selected canonical record без compatibility noise для
valid canonical/migrated repositories. Для legacy/mixed/conflict/none hook возвращает bounded
structured stage-routing context с `execution_allowed=false`, exact issues и plan availability,
но сам остаётся read-only advisory hook и не запускает materialization/product commands.

### BSC-026 Explicit migration handoff

Safe plan projection содержит plan id/digest, `plan_persisted=false`, exact allow-listed targets,
retained legacy paths и shell-free fixed argv template с placeholders для project root и отдельно
сохранённого approved plan file. Repository content не может добавить executable arguments.
Отсутствующий plan возвращает exact issues и не формирует materialization action.

### BSC-027 Completed master and ordinary canonical compatibility

Canonical CME repositories сохраняют прежние `continue`/blocked/`master_already_completed`
decisions. Canonical repositories без `master-execution` остаются ordinary canonical stage route,
а не ошибкой compatibility. Migrated repository не получает повторный migration prompt.

### BSC-028 Controlled rollout lifecycle

Reusable repo-by-repo lifecycle равен `discover → classify → report → safe plan if possible →
explicit approval/materialization → canonical validation → separately approved legacy retirement`.
Slice C не выполняет product materialization, массовый rollout или legacy deletion.

### BSC-029 Real brownfield acceptance

Normal router, validator и hook читают `electro-tutor` только read-only и согласованно возвращают
`mixed / migration_required / runnable=false`, stage `ET-09.3`, status `blocked`, missing NEXT и
blocker issues, без plan/command. Git state до/после остаётся clean.

## 4. Non-functional and security requirements

- NFR-BSC-001: stdlib-only, deterministic JSON, sorted sources/issues, bounded reads и bounded
  scalar projection fields без control characters.
- NFR-BSC-002: unknown/conflicting state fails closed; no silent fallback or prose inference.
- NFR-BSC-003: portable project-relative paths; no machine-specific path in persisted manifest.
- NFR-BSC-004: canonical repositories and existing CME/STAGES tests retain behavior.
- NFR-BSC-005: plan/operations имеют exact fields, count/byte/depth limits и duplicate-key/type
  rejection; boolean не принимается как integer version.
- NFR-BSC-006: side-effect outcomes содержат plan_id, typed status, writes, rollback/read-back
  evidence без raw secret-bearing content.
- NFR-BSC-007: lock/temp artifacts удаляются best-effort после terminal outcome; неизвестная
  partial side effect не retry-ится автоматически.
- NFR-BSC-008: automatic discovery не создаёт и не изменяет plan/product files; materialization
  API не импортируется hook/validator как callable side effect.
- NFR-BSC-009: handoff command является data-only argv template с fixed option vocabulary,
  bounded validated digest и placeholders; shell rendering repository paths запрещён.
- NFR-BSC-010: canonical hot path выполняет только bounded known-file inspection и сохраняет
  deterministic selector/CME decision semantics.
- NFR-BSC-011: диагностические issue/error values являются allow-listed data-only codes и не могут
  закрыть Markdown boundary, внести Unicode format controls или стать executable command content.

## 5. Compatibility state contract

The stage-compatibility block contains schema_version, migration_id, state_owner,
legacy_sources and projection. Each legacy source has project-relative path, sha256 and retained
disposition. Projection owns current_stage, optional master_id, normalized status, next_selector,
blockers, checkpoint and evidence. A valid manifest is authoritative only when:

1. it is the only block in the selected record;
2. state_owner equals prompts/STAGES.md;
3. projection.current_stage equals the same-file selector;
4. every declared legacy source exists and matches its digest;
5. no undeclared known legacy state file exists.

## 6. Failure and migration behavior

Primary: canonical selector/record, optionally with a verified compatibility manifest.

Legacy fallback: bounded exact-field adapter creates a plan but never runs a stage.

Fail closed: ambiguous fields, missing required selector for automatic projection, digest drift,
invalid paths/schema/encoding or inconsistent canonical/legacy facts.

Recovery: rerun after a human-approved migration updates the canonical record and manifest.
Deletion of retained legacy sources is a separate destructive stage and is not implied.

Slice B primary: validate plan → acquire exclusive lock → revalidate every byte precondition →
stage and fsync all writes → atomic replaces → read-back through existing adapter → success.

Non-retryable: invalid/tampered plan, repository mismatch, stale precondition, path violation and
read-back mismatch. `concurrent_materialization` допускает bounded caller retry only after
reconciliation; materializer сам не retry-ит mutation. Publish failure triggers rollback;
`rollback_failed` requires manual reconciliation before any new attempt.

## 7. Acceptance criteria

- AC-BSC-001: pure canonical, pure legacy, mixed, conflicting, migrated and none fixtures have
  stable distinct classifications.
- AC-BSC-002: legacy/mixed inputs yield dry-run plan with destructive_removals=false and stable
  idempotency key; repeated routing is byte-for-byte equivalent.
- AC-BSC-003: conflicting selector/status or migrated-source drift yields explicit conflict and
  never a runnable product selector.
- AC-BSC-004: migrated manifest supplies the full normalized projection from selected STAGES only
  after digest validation.
- AC-BSC-005: master_execution compatibility CLI is read-only and emits deterministic JSON.
- AC-BSC-006: electro-tutor returns migration_required as read-only evidence and remains Git-clean.
- AC-BSC-007: existing CME/STAGES regression suite and global context validator pass.
- AC-BSC-008: valid plan materializes exact canonical bytes in a temporary repo, read-back sees
  intended same-file selector/projection and retained legacy bytes remain unchanged.
- AC-BSC-009: source/target drift, plan tampering and apply-time path escape return fail-closed
  before write; tests assert unchanged target bytes.
- AC-BSC-010: first/mid-publish/read-back injected failures restore all pre-images and never return
  success; rollback failure has a distinct typed outcome.
- AC-BSC-011: repeated successful apply returns `already_materialized`; concurrent double apply
  yields one writer and one `concurrent_materialization`/already-materialized result without
  duplicate writes.
- AC-BSC-012: analysis CLI remains read-only, materialization requires explicit plan file, all
  materialization tests use temporary repositories, and `electro-tutor` remains Git-clean.
- AC-BSC-013: existing CME/STAGES/full DEV suites, context validator, independent reviewer and
  security reviewer pass after Slice B.
- AC-BSC-014: default router emits typed stage state automatically; canonical CME decisions and
  ordinary canonical routing remain unchanged.
- AC-BSC-015: validator returns canonical PASS only for execution-allowed canonical/migrated state;
  migration/no-state and conflicting state have documented distinct non-zero outcomes.
- AC-BSC-016: SessionStart is byte-deterministic, silent for canonical compatibility, explicit for
  brownfield/conflict/no-state, and never calls materialization.
- AC-BSC-017: safe plan handoff exposes exact id/digest/targets/retained paths and fixed shell-free
  argv; unsafe/no-plan state exposes issues without a fictitious command.
- AC-BSC-018: invalid canonical state never falls back to legacy projection; migrated state uses
  canonical normal path without repeated migration.
- AC-BSC-019: real read-only electro-tutor router/validator/hook evidence matches expected state and
  Git status remains clean; other canonical repositories retain prior behavior.
- AC-BSC-020: full Slice A+B+C, CME/STAGES/overlay and DEV suites plus context/diff and independent
  correctness/security reviews pass before completed master claim.

## 8. Materialization plan v1

Canonical schema owner: `schemas/stage-materialization-plan.schema.json`.

Top-level exact fields:

- `schema_version=1`, `generator_version`, `repository`, `detected`, `intended_state`;
- ordered `preconditions` for all known state paths and targets, including explicit absent state;
- ordered `operations` with `op=write`, allow-listed relative path, expected before digest,
  after digest and exact UTF-8 content;
- `lock_path`, `reasons`, `evidence`, `destructive_removals=false`, `plan_id`, `plan_digest`.

`plan_digest` is SHA-256 of canonical JSON for every field except `plan_id` and `plan_digest`;
`plan_id` is derived from that digest. Apply recomputes it and compares it in constant time with
the separately supplied `expected_plan_digest`, so editing both plan content and its embedded
digest cannot silently expand approved work. Repository identity is a SHA-256 binding to the
resolved local root while persisted paths remain portable. No wall-clock field is required:
deterministic repeated planning is stronger evidence than mutable generated-at metadata;
generator/schema versions provide provenance.

## 9. Stage map

- DEV-BCSC-A: detection, manifest parser and dry-run plan; no writes.
- DEV-BCSC-B: explicit migration materialization/validation contract with rollback evidence.
- DEV-BCSC-C: project validator/hook adoption and controlled rollout evidence.

After verified C the BCSC master has no invented Slice D. Product migrations/legacy retirement are
separately approved repo work and do not keep this global compatibility master partial.
