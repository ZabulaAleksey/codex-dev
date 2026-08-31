# AI Policy Profiling / Agent Economics — feature specification

Статус: `IMPLEMENTED_AND_VALIDATED_LOCALLY`
Версия schema: `1`
Дата: 2026-08-31

## 1. Цель

Глобальный ДЕВ должен иметь opt-in, passive-first механизм, который связывает выполненную работу
с policies/experiments, автоматически собирает доступные технические факты, сравнивает baseline и
variant и строит воспроизводимый отчёт без чтения private content и без автоматического изменения
policy thresholds.

Главная единица результата — `verified_outcome`, а не количество токенов, вызовов или файлов.

## 2. Scope

### Входит

- versioned JSON Schema для append-only JSONL telemetry envelope;
- Python standard-library CLI для инициализации opt-in runtime-каталога, instrumented command run,
  manual handoff, discovery/reuse outcome, stage outcome и aggregation/report;
- stable policy и experiment identifiers;
- baseline/variant comparison, token/wall-time/context/profiler hotspots при наличии данных;
- bounded discovery/early-stop и human-vs-AI decision functions;
- false reuse detection и profiler-overhead metric;
- integration points для Stage/DoD без обязательного включения profiler-а в существующих проектах;
- migration/disable path и backward compatibility;
- unit, contract и internal executable consumer-path tests.

### Не входит

- self-modifying policies или automatic threshold tuning;
- network telemetry, SaaS, database, dashboard server, MCP, новый agent или hook;
- перехват host-managed Codex token usage, если среда не предоставляет его явно;
- запись prompt/code/user payload, command stdout/stderr, secrets или credentials;
- массовая mutation существующих product repositories;
- обещание статистической причинности на малой/несопоставимой выборке.

## 3. Functional requirements

### FR-AEP-001 — Opt-in passive storage

Отсутствие `.metrics/` и config означает disabled. `init` создаёт локальный runtime layout
идемпотентно. JSONL data и generated reports игнорируются локальным `.metrics/.gitignore`;
versioned schema остаётся в global ДЕВ.

### FR-AEP-002 — Safe telemetry envelope

Каждая запись содержит `schema_version`, UTC `timestamp`, `event_id`, `event_type`, `project_id`,
`stage_id`, optional `policy_ids`, `experiment_id`, `experiment_arm`, `task_class`, `metrics` и
type-specific `data`. Identifiers имеют bounded ASCII format. Unknown/invalid fields fail closed
до append. Writer не принимает или не сохраняет stdout/stderr, prompt, file content или env dump.

### FR-AEP-003 — Automatic available facts

Instrumented `run` автоматически фиксирует wall time, exit status, UTC timestamps, command class,
Git root/revision/branch/dirty state и profiler overhead. Raw command arguments и process output в
telemetry не сохраняются. Optional token/context/human metrics принимаются только как явно
предоставленные числовые observations с provenance.

### FR-AEP-004 — Policy and experiment identity

Policy IDs и experiment IDs стабильны внутри проекта. Baseline/variant сравнение требует одного
`experiment_id`, разных `experiment_arm`, совместимого `task_class` и достаточного количества
verified outcomes; отчёт всегда показывает sample size и не утверждает причинность.

Начальные policy IDs:

- `AEP_PASSIVE_OBSERVE_V1`;
- `AEP_BOUNDED_DISCOVERY_V1`;
- `AEP_HUMAN_HANDOFF_V1`;
- `AEP_REUSE_ECONOMICS_V1`.

### FR-AEP-005 — Human-vs-AI handoff

Decision function возвращает `DELEGATE_TO_HUMAN` только когда действие простое, быстрое,
не требует специальной экспертизы, AI overhead высок и batch/repetition не делает automation
выгоднее. Решение содержит reason, assumptions и estimated saving. `LEARNING` не маскируется под
economic saving. Manual handoff event фиксирует один action, expected response и completion state.

### FR-AEP-006 — Bounded discovery and early stop

Decision function сравнивает elapsed wall/tokens/cost с configured budget и expected task cost.
Превышение любого активного budget, отсутствие сильного кандидата или adaptation estimate,
достигший greenfield estimate, возвращает `STOP_DISCOVERY`. Нулевой/отсутствующий budget не
создаёт бесконечного поиска: решение fail-visible требует config либо stop.

### FR-AEP-007 — Reuse economics

Reuse outcome хранит source class, discovery/adaptation/integration/verification cost,
greenfield estimate, selected/success/verified. `REUSE_FALSE_POSITIVE` определяется, когда
выбранный reuse не дал verified outcome либо actual reuse cost не ниже greenfield estimate.

### FR-AEP-008 — Profiler overhead

Каждая mutation измеряет собственный wall overhead. Aggregation вычисляет
`profiler_overhead / observed_task_wall`, когда denominator доступен, и явно показывает missing
denominators. Profiler не генерирует обязательный длинный self-report на каждую задачу.

### FR-AEP-009 — Aggregation and report

Aggregator читает bounded files, валидирует каждую строку и строит deterministic JSON summary и
Markdown dashboard: productivity/outcomes, AI economics, quality, reuse, infrastructure/hotspots,
human handoffs и experiment comparison. Corrupt/unsupported input завершает report с ошибкой и не
перезаписывает последний валидный report.

### FR-AEP-010 — Stage/DoD integration

При включённом profiler-е Stage contract может объявить `Policy IDs`, `Experiment ID/arm` и
telemetry evidence. Это дополнительное evidence; profiler никогда не заменяет SPEC, tests, E2E или
documentation gate. Existing projects без profiler-а остаются валидными.

### FR-AEP-011 — Gradual rollout

Фазы фиксированы: Observe → Measure → Compare → Recommend → human-approved tuning → bounded
automatic tuning. Этот feature реализует Observe/Measure/Compare/Recommend. Любая mutation policy
thresholds остаётся вне scope и требует отдельной approved SPEC/decision.

### FR-AEP-012 — Portability and dependency boundary

Implementation использует только Python standard library, `pathlib`, переносимые пути от `~` и
работает на Windows/Linux/macOS Python 3.12. Git metadata optional: отсутствие Git даёт явные null
facts, а не failure записи локальной telemetry.

## 4. Security and privacy requirements

### SEC-AEP-001

Не логировать secrets, environment values, prompt/user content, source content, stdout/stderr или
raw command arguments.

### SEC-AEP-002

Все пути resolve-ятся относительно явно выбранного project root; telemetry path не может выйти за
root через `..`/symlink. JSONL append и report replacement используют bounded writes и atomic
replace для generated report.

### SEC-AEP-003

Input limits: JSONL line ≤ 1 MiB, file ≤ 64 MiB, identifier ≤ 64 chars, text observation ≤ 500
chars, numeric values finite/non-negative там, где это требуется.

## 5. Acceptance criteria

- AC-AEP-001: `init` идемпотентно создаёт opt-in layout; отсутствие layout не меняет project.
- AC-AEP-002: instrumented real subprocess пишет валидное событие без raw command/output и
  автоматически фиксирует wall/Git/profiler facts.
- AC-AEP-003: baseline и variant verified outcomes агрегируются и появляются в JSON/Markdown с
  sample size и median deltas.
- AC-AEP-004: discovery decision покрывает continue, budget stop, no-candidate stop и
  reuse-vs-greenfield stop.
- AC-AEP-005: handoff decision покрывает human, AI и learning/batch guards.
- AC-AEP-006: false reuse и profiler overhead вычисляются тестами.
- AC-AEP-007: malformed/oversized/unsupported telemetry fail closed; последний валидный report не
  повреждается.
- AC-AEP-008: existing 110-test baseline не регрессирует; new suite и context validation PASS.
- AC-AEP-009: temporary independent project проходит путь
  `init → instrumented run → stage outcome → report`, telemetry реально пишется и report читаем.
- AC-AEP-010: governance/templates/docs описывают optional Stage linkage, disable/migration path и
  запрет auto-tuning; existing projects не обязаны создавать `.metrics/`.

## 6. Rollback

Удаление вызовов CLI и локального `.metrics/` полностью отключает feature. Versioned code/docs
можно откатить одним Git revert. Telemetry schema v1 append-only; destructive migration не нужна.
