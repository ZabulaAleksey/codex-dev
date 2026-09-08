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
- integration в существующий tools/master_execution.py CLI;
- temporary-repository tests и read-only evidence на electro-tutor.

Не входит:

- автоматическая запись или удаление файлов product repositories;
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
current_stage и next_selector обязаны быть valid stable IDs.

### BSC-005 Conflict semantics

Несогласованные selector/status facts, ambiguous/malformed canonical selector или missing/ambiguous
selected heading, invalid manifest,
manifest/source digest drift либо canonical/legacy selector mismatch дают route
migration_required и classification conflict. Controller не запускает product stage.

Наличие `prompts/STAGES.md` без same-file selector при согласованном legacy pair является
`mixed`/partial migration и может получить dry-run plan; отсутствие legacy state в том же случае
остаётся `conflict`.

### BSC-006 Dry-run migration plan

Legacy и mixed state возвращают immutable plan: target prompts/STAGES.md, source fingerprints,
normalized projection, preserve list, manual-review issues, destructive_removals=false и stable
idempotency_key. Повторный запуск на тех же bytes возвращает идентичный report/plan.

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

## 4. Non-functional and security requirements

- NFR-BSC-001: stdlib-only, deterministic JSON, sorted sources/issues and bounded reads.
- NFR-BSC-002: unknown/conflicting state fails closed; no silent fallback or prose inference.
- NFR-BSC-003: portable project-relative paths; no machine-specific path in persisted manifest.
- NFR-BSC-004: canonical repositories and existing CME/STAGES tests retain behavior.

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

## 8. Stage map

- DEV-BCSC-A: detection, manifest parser and dry-run plan; no writes.
- DEV-BCSC-B: explicit migration materialization/validation contract with rollback evidence.
- DEV-BCSC-C: project validator/hook adoption and controlled rollout evidence.

Future slices may apply an approved plan, but are not required for the runnable read-only path of A.
