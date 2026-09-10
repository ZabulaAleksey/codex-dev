# Политика контекста

## Приоритет

Для файловых инструкций действует каскад:

`Модуль → Проект → ~/.codex → глобальная конфигурация Codex`

Более локальное правило уточняет общее только в своей области. Прямая инструкция пользователя для текущей задачи имеет высший приоритет, если не нарушает ограничения безопасности.

Canonical global DEV Git source разрешается через `DEV_SOURCE_ROOT` (default `~/codex-dev`).
`CODEX_HOME` (default `~/.codex`) содержит manifest-installed global context и device-local
runtime state, но не является canonical Git working tree. Product repositories разрешаются как
независимые Git roots `${PROJECTS_ROOT}/<project>`; path не включает DEV policy без exact
project-local `AGENTS.md` bridge marker. Runtime Skills в `~/.agents/skills` являются только
проверяемой projection `${DEV_SOURCE_ROOT}/skill-sources`.

## Порядок загрузки

1. Ближайший относящийся к задаче `AGENTS.md` / `AGENTS.override.md`.
2. Одно правило режима и только активные фрагменты SDLC, домена и стека.
3. Затрагиваемые требования и критерии приёмки из SPEC.
4. Только выбранный stage record из `prompts/STAGES.md`, если задача относится к stage.
5. Релевантные разделы `ARCHITECTURE.md`, `DECISIONS.md`, `DESIGN.md` и `SECURITY.md`.
6. Целевой код, тесты и diff; current plan/status уже входят в selected STAGES record.

Не загружай по умолчанию все stages целиком, полные исторические roadmap, все fixtures/references,
старые generated reports и общие правила, уже унаследованные проектом.

Автоматический selector stage задаётся строкой `- Stage ID: <stable-id>` в `prompts/STAGES.md`;
тот же ID должен быть отдельным token ровно одного Markdown heading в этом же файле.
SessionStart/SubagentStart hook проецирует bounded запись первой. Без valid selector запись не проецируется;
invalid/ambiguous/oversized явный selector либо отсутствующий выбранный heading даёт видимый
`DEGRADED` context. В этом случае открой полный record вручную и не используй completion claim до
проверки. Отсутствие selector даёт visible `DEGRADED`, а full
overlay validator классифицирует его как `missing-stage-id`.

Для full project overlay read-only `tools/validate_project_overlay.py` является preflight gate:
он требует ровно одну unfenced selector-строку, валидный ASCII ID и ровно один unfenced heading.
Это structural validation ссылки, не semantic proof dependency DAG, runnable slice или evidence.

Для Continuous Master Execution selected record дополнительно содержит один bounded fenced
`master-execution` JSON block. ContextScope Resolver загружает только refs текущего slice; весь
master/catalog не перечитывается. Block хранит durable master/track/worktree/branch/checkpoint,
verified chain, blockers и NEXT. Budget overflow создаёт compact launcher/handoff из этих facts;
отдельный status/handoff owner не создаётся. Новая сессия сверяет state revision и Git checkpoint,
а stale launcher даёт fail-visible handoff/reconciliation.

## Восстановление новой сессии

Восстанавливай project в следующем порядке:

1. Git root, current branch/status/diff/log и подтверждённый target/upstream;
2. global `~/.codex/AGENTS.md` и только применимые global rules/Skills;
3. project `AGENTS.md` / ближайший `AGENTS.override.md`;
4. `README.md`, затронутая SPEC, canonical architecture/decisions и один exact
   current `prompts/STAGES.md` record;
6. target code/tests/manifests и только релевантные `LEARNING_LOG.md` entries;
7. явно назначенные external mappings и их `synced | pending sync | blocked` state.

Старый чат, search snippet, local cache и внешняя projection не заменяют этот порядок. Broken link,
missing selector, dirty state без provenance или противоречие docs с code/evidence дают видимый
`DEGRADED`/`BLOCKED`; не подставляй предполагаемый stage и не объявляй восстановление успешным.
Практический computer↔laptop handoff и copy-ready запросы находятся в `docs/WORKFLOW.md`.

## Закон проектного overlay

Проект хранит только свои отличия от общей библиотеки:

- доменные и проектные правила;
- SPEC, архитектуру, дизайн и решения;
- current selector/state в `prompts/STAGES.md` и долгосрочный `ROADMAP`;
- проектные agents, Skills, hooks и MCP только при подтверждённом пробеле общей конфигурации.

Не создавай второй глобальный config Codex, второй Git workflow, дубли универсальных агентов или MCP «на всякий случай».

## Канонические имена

- Уровни сложности: `SIMPLE`, `STANDARD`, `COMPLEX`; строгий режим для `COMPLEX` задаёт `rules/modes/strict.md`.
- Стабильные требования: `specs/system.spec.md` и `specs/features/<feature>.spec.md`.
- Текущий исполняемый срез и фактическое состояние: `prompts/STAGES.md`; отдельные
  `AI_PLAN.md`, `AI_STATUS.md`, `PLAN.md`, `STATUS.md` и `PROGRESS.md` не нужны.
- Долгосрочный порядок развития: `docs/ROADMAP.md`.
- Учебный журнал и подробная хронология создаются только при реальной пользе и не подменяют STAGES state.

## Совместимость расширений

Перед добавлением agent, hook, MCP, Skill или config используй `docs/CONTEXT_COMPATIBILITY.md`. Для нетривиальных изменений запиши решение в одноимённый документ проекта.

## Brownfield reconciliation gate

Перед `bootstrap` или `refresh` классифицируй repository как `GREENFIELD` или `BROWNFIELD`.
В brownfield фактический код, документы проекта и результаты тестов являются source of truth
текущего состояния. КАРКАС адаптируется к реализации и не перезаписывает её автоматически.

До любой mutation запусти read-only `tools/reconcile_project_framework.py`. Его matrix использует
статусы `KEEP`, `ADD`, `ADAPT`, `MERGE`, `CONFLICT`, `SUPERSEDED` и
`FORBIDDEN_TO_OVERWRITE`. Неразрешённый `CONFLICT` блокирует соответствующую mutation;
`FORBIDDEN_TO_OVERWRITE` запрещает автоматическую запись в существующий путь.

Последовательность gate: reconciliation → resolution conflicts → refresh →
`validate_project_overlay.py` → повтор baseline-тестов. Baseline failures фиксируются
отдельно как pre-existing; новые failures после refresh считаются regression.
