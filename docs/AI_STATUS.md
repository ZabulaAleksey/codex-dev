# Текущее состояние ДЕВ / КАРКАС

Дата: 2026-08-31

## Статус

- AI Policy Profiling lifecycle: `completed`; evidence: `merged` и `pushed` в `origin/main`;
  implementation commit `ea1fe24`.
- Integration boundary: release, deploy и product rollout не выполнялись.
- Backward compatibility: absent `<project>/.metrics/` = disabled; existing overlays не получают
  обязательный новый artifact или validator failure.
- Global framework hardening сохраняет отдельный pre-existing статус `implemented_unverified` из-за
  active runtime issue `unmatched-browser-client-hash`; profiler feature не изменяет `config.toml`
  и не скрывает этот blocker.

## Реализованный vertical slice

```text
temporary independent Git project
  → explicit opt-in init
  → real instrumented subprocess
  → validated concurrent-safe JSONL
  → baseline/variant stage + reuse/handoff/discovery/agent events
  → deterministic JSON/Markdown report
```

- `schemas/ai-policy-profiling.schema.json` задаёт v1 envelope и event-specific data contracts.
- `tools/ai_policy_profiler.py` реализует init/run/stage/policy/experiment/discovery/reuse/handoff/
  agent/report без external dependencies.
- Автоматически собираются safe command wall/exit, Git revision/branch/dirty fact и profiler
  overhead; raw command args/output, environment, prompt/user/source content не сохраняются.
- Bounded discovery останавливается по wall/token/cost budget, no-candidate и greenfield break-even.
- Reuse автоматически получает `REUSE_FALSE_POSITIVE`, если не verified либо дороже greenfield.
- Handoff decision сохраняет batch/capability guard и явный `LEARNING` reason.
- Aggregation выдаёт verified outcomes, first-pass DoD/rework, policy/agent profiles, hotspots,
  reuse/handoff economics, sample sizes и baseline/variant medians/deltas без causality claim.
- Child config/stream/report paths проходят containment/symlink checks; append использует bounded
  exclusive lock, corrupt input fail closed, report заменяется atomically.
- Governance/templates связывают optional Policy/Experiment fields со Stage, но telemetry не
  заменяет SPEC/tests/E2E/Documentation Gate и не изменяет thresholds автоматически.

## Verification evidence

- baseline до изменения: `py -3 -B -m unittest discover -s tools -p "test_*.py"` — PASS, 110 tests;
- final full suite: та же команда — PASS, 124 tests;
- targeted profiler suite: `py -3 -B -m unittest tools.test_ai_policy_profiler` — PASS, 14 tests;
- `py -3 -B tools\validate_context.py` — PASS, 213 files;
- `git diff --check` — PASS; Windows LF→CRLF warnings informational;
- executable consumer path — PASS в independent synthetic Git fixture; JSONL реально записан,
  raw output sentinel отсутствует, JSON/Markdown report создан;
- repeated corrected report: 2 verified outcomes, baseline/variant effective-cost delta `-3`,
  false reuse `1/1`, completed handoff `1`, reviewer outcome `1`, profiler overhead ratio
  `0.000513`;
- symlink escape negative test — PASS; external target bytes unchanged;
- 20 concurrent writers — PASS с complete JSONL lines; transient Windows `PermissionError`
  bounded-retry, на deadline existing lock классифицируется как contention, отсутствующий — ACL
  failure и fail closed;
- schema/manual validator mismatch, oversized/corrupt stream и wrong-stream cases — fail closed.

Synthetic fixture доказывает executable profiler contract, но не экономическую полезность конкретной
policy: sample size и costs искусственные, automatic tuning запрещён.

## Синхронизация документации

- Обновлены: `AGENTS.md`, `README.md`, `docs/AI_PLAN.md`, `docs/AI_STATUS.md`,
  `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/CONTEXT_COMPATIBILITY.md`,
  `docs/DECISIONS.md`, `docs/PROJECT_FRAMEWORK.md`, `docs/SECURITY.md`, `docs/TESTING.md`,
  `docs/WORKFLOW.md`, `docs/LEARNING_LOG.md`, feature SPEC/index, governance/rule index,
  AI plan/status templates, validator inventory и `MANIFEST.txt`.
- Добавлены: profiler policy, schema, CLI/core, tests и
  `docs/notes/AI_POLICY_PROFILING.md` migration/usage guide.
- Проверены без изменений: `QUICKSTART.md`, `docs/CONTEXT_POLICY.md`, `docs/DESIGN.md`,
  `docs/HOOK_POLICY.md`, `docs/MCP_CATALOG.md`, `docs/TEAM_ARCHITECTURE.md`,
  `docs/VERIFY_SETUP.md`, `specs/system.spec.md`, installers, recommended config и read-only CI.
- Не применяются: global `prompts/STAGES.md`, `TRACEABILITY.md`, `CHANGELOG.md`, `DEV_LOG.md`.
- Active `config.toml`, host runtime SQLite/JSONL/logs, credentials, sessions, cache, plugins,
  runtime Skills и product repositories не изменялись.

## Следующее действие

Можно выбрать один real project для явного opt-in rollout. Сначала собирать Observe/Measure данные
по сопоставимым task families; policy threshold меняется только отдельным human-approved решением
после достаточной выборки.
