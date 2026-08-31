# Текущий план ДЕВ / КАРКАС

Статус: `completed` / validated locally / internal infrastructure item
Stage ID (internal, не selector): `DEV-AI-PROFILING-001`
Рабочий item: passive AI Policy Profiling / Agent Economics Observe layer
Дата: 2026-08-31

## Applicability

Global infrastructure repository не является full staged project overlay и намеренно не имеет
`prompts/STAGES.md`. Поэтому internal Stage ID не записан selector-строкой `- Stage ID:`.

Связанные требования: `specs/features/ai-policy-profiling.spec.md`
(`FR-AEP-001..012`, `SEC-AEP-001..003`, `AC-AEP-001..010`).

## Dependency DAG и входные предпосылки

```text
global framework hardening (implemented_unverified; reusable local infrastructure available)
        ↓
approved feature SPEC + architecture/security decision
        ↓
schema + pure decision/aggregation core
        ↓
safe opt-in CLI + executable consumer path
        ↓
governance/DoD integration + docs/migration
        ↓
full tests/review/documentation synchronization
```

Evidence на старте:

- Git branch `feature/ai-policy-profiling-observe`, clean worktree at `53403af`;
- baseline full suite: PASS, 110 tests;
- `py -3 -B tools\validate_context.py`: PASS, 207 files;
- существующего AI policy profiler/schema/reporting слоя не найдено;
- existing hooks, validators, Stage/status owners будут расширены ссылками, а не дублированы;
- active `config.toml`, runtime SQLite/JSONL, credentials, sessions, cache и product repositories
  запрещены к mutation.

## Самостоятельный runnable vertical slice

```text
temporary independent Git project
  → explicit profiler init
  → instrumented real subprocess
  → validated append-only JSONL event
  → verified stage outcome with policy/experiment linkage
  → deterministic JSON + Markdown report
```

Путь исполним без network, service, dependency, MCP, agent, hook или future stage.

## Concrete end-to-end scenario

1. Создать temporary independent Git project и opt-in `.metrics/` layout.
2. Запустить через profiler реальную Python command с `baseline` arm и записать stage outcome.
3. Повторить для `variant` arm и reusable-contour outcome.
4. Сгенерировать report, проверить schema, sample sizes, baseline/variant comparison, false reuse и
   profiler overhead.
5. Убедиться, что raw command/output, env values и source/user content отсутствуют в telemetry.

## Область работы

Входит: feature SPEC, JSON Schema, standard-library profiler CLI/core, policy rules, tests,
governance/templates, architecture/decision/security/testing/workflow/README/status/roadmap и
manifest synchronization.

Не входит: active config, runtime host databases/logs, product rollout, external telemetry,
self-modifying thresholds, MCP/hooks/agents/dependencies, push/merge/release/deploy.

## Рабочие задачи

1. Зафиксировать SPEC, Stage contract и architecture/security boundary до production code.
2. Реализовать schema validation, safe append, automatic command/Git/wall/profiler facts.
3. Реализовать handoff/discovery/reuse decisions и false-positive classification.
4. Реализовать deterministic aggregation и JSON/Markdown dashboard.
5. Добавить unit/negative tests и independent-project executable consumer path.
6. Интегрировать optional Policy/Experiment fields в Stage/DoD owners без регрессии overlays.
7. Выполнить full verification/review, synchronization gate и atomic commit.

## Acceptance / PASS criteria

- [x] `AC-AEP-001..010` подтверждены tests/evidence.
- [x] Existing projects остаются valid без `.metrics/`.
- [x] Telemetry реально пишется только после explicit opt-in.
- [x] Raw command/output, env values, prompt/user/source content не попадают в telemetry.
- [x] Report показывает verified outcomes, experiments, reuse/handoff и profiler overhead.
- [x] Automatic policy tuning отсутствует и явно запрещён до отдельного approved stage.
- [x] Full suite (124 tests), context validation (213 files) и `git diff --check` PASS.
- [x] Documentation synchronization gate и read-only review завершены.

## Допустимая временная реализация

- Markdown report вместо web dashboard допустим и полностью обслуживает Observe/Measure/Compare.
- Missing host token usage хранится как `unknown`, а не оценивается выдуманным числом.
- Manual human-time/handoff observations допустимы, если помечены provenance; доступные Git/wall
  facts собираются автоматически.

## Deferred

- automatic threshold recommendations на статистически достаточной выборке;
- human-approved tuning UI;
- bounded automatic tuning;
- host-native model usage ingestion;
- organization-wide telemetry backend;
- mass migration product repositories;
- push, merge, release и deployment.

## Риски и rollback

- Privacy: allow-list schema и запрет raw payload/output/env.
- Overhead: standard library, append-only writes, bounded files, overhead measurement.
- Corrupt data: fail-closed validation и atomic generated report replacement.
- Compatibility: absent profiler layout = disabled; governance fields optional.
- Rollback: one Git revert; local `.metrics/` удаляется владельцем project отдельно.

## Documentation synchronization gate

Перед handoff проверить README, AI_PLAN, AI_STATUS, ROADMAP, architecture, decisions, security,
testing, workflow, affected SPEC/templates/rules/tools/tests, CI applicability и manifest. Менять
только изменившиеся факты; `LEARNING_LOG*` не трогать без повторно полезной ошибки.
