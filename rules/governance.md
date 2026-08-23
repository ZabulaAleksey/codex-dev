# Global DEV governance policy

Этот документ — канонический общий контракт для структуры контекста, project lifecycle и evidence. Project `AGENTS.md` хранит только подтверждённую delta.

## Source of truth и независимость

1. Фактическое состояние определяют repository, текущий worktree/branch и результаты проверок.
2. Утверждённая SPEC/ADR определяет требуемый контракт; статусные документы не могут переопределять код или evidence.
3. Notion, Airtable, Eraser, Figma, презентации и чаты — derived projections, а не repository truth.
4. Product repository располагается непосредственно в `~/codex-workspace/<project>` и не зависит от абсолютного пути. Scripts определяют root через Git или эквивалентный безопасный механизм.
5. Critical context должен восстанавливаться после clone/pull без старого чата и machine-local файлов.

## Context inheritance

```text
~/.codex/AGENTS.md
→ <repo>/AGENTS.md
→ optional subtree AGENTS.override.md
→ prompts/STAGES.md для выбранного stage
```

- Project `AGENTS.md` не копирует global Git/testing/security/fallback/tool policy.
- Project custom agents находятся в `<repo>/.codex/agents`.
- Project Skills находятся в `<repo>/.agents/skills` только при доказанном project-specific gap.
- Global agent TOML находится в `~/.codex/agents`; versioned Skill sources — в `~/.codex/skill-sources`, runtime Skills — в `~/.agents/skills`.

## Project state и документы

Для активного software repository обязательны содержательные:

- `AGENTS.md`;
- `prompts/STAGES.md`;
- `docs/AI_PLAN.md`;
- `docs/AI_STATUS.md`;
- `docs/ROADMAP.md`;
- `docs/ARCHITECTURE.md`;
- `docs/DECISIONS.md`;
- `docs/LEARNING_LOG.md`;
- `docs/project-context.md`.

Не создавай пустой placeholder. Для UI добавляй `DESIGN.md`, для security surface — `SECURITY.md`, для behavior traceability — `TRACEABILITY.md`, для отдельного test contract — `TESTING.md`.

- `AI_PLAN` описывает текущий/следующий исполнимый срез.
- `AI_STATUS` содержит только подтверждённые факты и evidence.
- `ROADMAP` — короткий индекс этапов, не копия prompts.
- `DECISIONS` хранит permanent decisions/ADR; `LEARNING_LOG` — диагностику, root cause, fix и regression prevention.
- Для одной роли существует один canonical документ; legacy объединяется только после проверки уникального содержания и ссылок.

## Stage contract

`prompts/STAGES.md` — единственный detailed stage source. Стабильный stage включает status, goal, context, preconditions, dependencies, scope, out-of-scope, invariants, tasks, contracts, tests, documentation/security/performance/fallback/migration impact, DoD, verification и handoff.

Stage не становится `DONE`, пока не обновлены `AI_PLAN` и `AI_STATUS`, не проверен Documentation Impact, не выполнены или явно заблокированы gates с evidence и не просмотрен Git diff.

## Contract-first и testing

```text
requirement → behavior/domain contract → API/data/component contract
→ implementation → test evidence → docs/status
```

- Mandatory behavior без evidence помечается `UNVERIFIED`.
- Unit проверяет pure logic; integration — реальные границы storage/API/provider; component — rendering/actions/states/accessibility; E2E — только критические живые пути.
- Accepted tests, fixtures и goldens нельзя ослаблять ради green. Contract change требует утверждённой SPEC/ADR до изменения теста.
- Для нетривиального component определи inputs, outputs, state, side effects, loading/empty/error/disabled/permission/accessibility и recovery behavior.

## Data, database и migrations

```text
domain requirement → data contract → canonical schema/model
→ migration → repository/query → integration evidence
```

Фиксируй keys, nullability, constraints, relations, indexes, timestamps/timezone, numeric precision, ownership, provenance и retention. Schema change без migration допустим только в явно disposable prototype. Destructive production operations deny-by-default и требуют backup/restore plan и отдельного approval.

## Security, fallback и observability

- Недоверенные вводы валидируются по schema, size/count/depth/path/content-type limits.
- AuthN не заменяет AuthZ; secrets не попадают в Git/logs/docs/tests.
- Critical security, money, permissions, cryptography, schema integrity и destructive paths fail closed.
- Fallback явно определяет primary, failure signal, degraded/unavailable behavior, telemetry и recovery; silent fallback/data loss/mock-as-real запрещены.
- Долгие операции имеют operation ID, state/progress, structured error, timeout, cancellation/retry и recovery без private-content logging.

## Tools, dependencies и performance

- MCP/hook/subagent/Skill добавляется только после доказанного gap, с минимальными permissions и bounded failure behavior.
- Hooks deterministic, non-destructive и repository-relative.
- Не добавляй dependency без проверки existing alternatives, maintenance, license, security, platform/runtime и lockfile impact.
- Performance change требует baseline → profile → targeted optimization → correctness parity → benchmark → regression guard.
- Model routing и global reusable agents не дублируются в project overlays.

## Evidence и external projections

Используй только уровни, подтверждённые фактом: `implemented locally`, `validated locally`, `committed`, `pushed`, `PR opened`, `merged`, `released`. Для каждого gate фиксируй command/check, result, scope, commit/environment и caveat. Не запущенное обозначается `NOT RUN`, недоступное — `BLOCKED / NOT VERIFIED`.

External projection синхронизируется из Git. Недоступность внешнего сервиса создаёт pending sync, но не меняет repository truth и не откатывает корректную локальную реализацию.

## Context integrity validator

Read-only validator должен выявлять отсутствующие canonical docs, alternate status, отдельные stage files, stale `projects/` paths, machine-specific paths, duplicate global rules, неправильные agent/Skill locations, broken relative links, invalid stage references и references на отсутствующие hooks/Skills/agents. Validator не исправляет repository автоматически.
