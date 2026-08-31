# AI Policy Profiling / Agent Economics — руководство

## Что это даёт

Profiler отвечает не на вопрос «сколько агент сделал действий», а на вопрос «какой ценой получен
проверенный результат». Он работает локально, без network/backend и включается отдельно в каждом
project. Existing projects не меняются автоматически.

Каноны:

- requirements: `specs/features/ai-policy-profiling.spec.md`;
- policy: `rules/ai-policy-profiling.md`;
- schema: `schemas/ai-policy-profiling.schema.json`;
- CLI: `tools/ai_policy_profiler.py`.

## Включение и отключение

Из project root на Windows:

```powershell
py -3 -B "$env:USERPROFILE\.codex\tools\ai_policy_profiler.py" init --root . --project-id my-project
```

Linux/macOS:

```bash
python3 -B ~/.codex/tools/ai_policy_profiler.py init --root . --project-id my-project
```

Это создаёт ignored runtime-каталог `.metrics/`. Отсутствие каталога означает `disabled`.
Отключение не требует migration: прекратите вызывать CLI. Удаление накопленных локальных данных —
отдельное действие владельца project; profiler сам их не удаляет.

## Passive Observe

Instrumented run сохраняет только class команды, exit status, wall time, Git revision/branch/dirty
fact и profiler overhead. Raw arguments, stdout/stderr и environment не сохраняются.

```powershell
py -3 -B "$env:USERPROFILE\.codex\tools\ai_policy_profiler.py" run `
  --root . `
  --stage-id APP-101 `
  --policy-id AEP_PASSIVE_OBSERVE_V1 `
  --task-class integration-heavy `
  --command-class unit-tests `
  -- py -3 -B -m unittest
```

Если model/runtime предоставляет token usage, его можно добавить к `stage`/`agent` observation.
Если не предоставляет — значение остаётся `unknown`; profiler не оценивает токены по ощущениям.

## Stage outcome и experiment

Сначала зарегистрируйте experiment hypothesis:

```powershell
py -3 -B "$env:USERPROFILE\.codex\tools\ai_policy_profiler.py" experiment `
  --root . --stage-id APP-101 `
  --experiment-id CONTOUR-FIRST-V3 --experiment-arm baseline `
  --hypothesis "Bounded local-first search reduces effective cost" `
  --baseline-arm baseline --variant-arm variant --minimum-sample-size 10
```

После фактического DoD запишите outcome. `--verified` допустим только при обычном Stage PASS:

```powershell
py -3 -B "$env:USERPROFILE\.codex\tools\ai_policy_profiler.py" stage `
  --root . --stage-id APP-101 `
  --policy-id AEP_BOUNDED_DISCOVERY_V1 `
  --experiment-id CONTOUR-FIRST-V3 --experiment-arm variant `
  --task-class integration-heavy `
  --verified --first-pass-dod --outcome-label oauth-integration `
  --wall-seconds 4200 --human-active-minutes 25 --tokens-total 48000 `
  --rework-minutes 5 --effective-cost 74
```

`effective_cost` требует выбранной project/unit cost model; нельзя смешивать валюту, минуты и
безразмерный score внутри одного experiment без явной normalization.

## Bounded discovery, reuse и handoff

Read-only decision не требует включённого profiler-а:

```powershell
py -3 -B "$env:USERPROFILE\.codex\tools\ai_policy_profiler.py" discovery-decision `
  --elapsed-seconds 600 --wall-budget-seconds 600 `
  --tokens-used 8000 --token-budget 10000 --candidate-strength weak
```

Команда `discovery` принимает те же observations и пишет decision event. Команда `reuse` считает
сумму discovery/evaluation/adaptation/integration/verification cost и автоматически ставит
`REUSE_FALSE_POSITIVE`, если выбранный contour не verified или actual reuse cost достиг greenfield.

Для ручного действия сначала можно вызвать `handoff-decision`, затем `handoff` записывает ровно
одно действие, expected response и completion. Не помещайте в text fields private content или
секреты.

## Report

```powershell
py -3 -B "$env:USERPROFILE\.codex\tools\ai_policy_profiler.py" report --root .
```

Результат:

- `.metrics/reports/latest.json` — machine-readable summary;
- `.metrics/reports/latest.md` — простой dashboard;
- verified outcomes, first-pass DoD, rework и effective cost;
- policy/agent profiles;
- reuse hit/false-positive/efficiency;
- human handoffs;
- token/wall hotspots;
- baseline/variant medians, deltas, task-class compatibility и sample sufficiency;
- profiler overhead.

Corrupt/oversized/unsupported JSONL завершает report с ошибкой и не перезаписывает последний
валидный report.

Если writer аварийно завершился и оставил `*.lock`, profiler fail closed. Перед ручным удалением
lock владелец должен убедиться, что другого writer process больше нет; автоматическое удаление
stale lock намеренно не выполняется.

## Как читать результат

1. Сначала проверьте `verified_outcomes` и обычное Stage evidence.
2. Сравнивайте только одинаковый `task_class` и один experiment cost model.
3. Смотрите median и sample size; маленькая выборка не доказывает причинность.
4. Проверяйте profiler overhead: telemetry сама должна оставаться дешёвой.
5. Высокий token activity без verified outcome не является пользой.
6. До достаточных данных допускается только recommendation; threshold mutation требует отдельного
   human-approved решения.

## Migration v1

- Existing project: ничего не делать, пока profiling не выбран явно.
- New opt-in: запустить `init`, добавить optional Policy/Experiment fields в текущий Stage record и
  начать с instrumented commands.
- Existing external metrics: не копировать напрямую; преобразовать в schema v1 отдельным reviewed
  adapter-ом с provenance.
- Unsupported future schema: текущий reader fail closed; destructive in-place migration запрещена.
