# Политика контекста

## Приоритет

Для файловых инструкций действует каскад:

`Модуль → Проект → ~/.codex → глобальная конфигурация Codex`

Более локальное правило уточняет общее только в своей области. Прямая инструкция пользователя для текущей задачи имеет высший приоритет, если не нарушает ограничения безопасности.

Глобальный Git-канон и active operational layer находятся непосредственно в `~/.codex`.
`~/codex-workspace/global/codex` не является поддерживаемым source root. Product repositories
располагаются как независимые Git roots в `~/codex-workspace/<project>`; runtime Skills в
`~/.agents/skills` являются только проверяемой projection `~/.codex/skill-sources`.

## Порядок загрузки

1. Ближайший относящийся к задаче `AGENTS.md` / `AGENTS.override.md`.
2. Одно правило режима и только активные фрагменты SDLC, домена и стека.
3. Затрагиваемые требования и критерии приёмки из SPEC.
4. Только выбранный stage record из `prompts/STAGES.md`, если задача относится к stage.
5. Релевантные разделы `ARCHITECTURE.md`, `DECISIONS.md`, `DESIGN.md` и `SECURITY.md`.
6. Текущий `AI_PLAN`, целевой код, тесты и diff.
7. Компактный снимок `AI_STATUS`.

Не загружай по умолчанию все stages целиком, полные исторические roadmap, все fixtures/references,
старые generated reports и общие правила, уже унаследованные проектом.

Автоматический selector stage задаётся строкой `- Stage ID: <stable-id>` в `docs/AI_PLAN.md`;
тот же ID должен быть отдельным token ровно одного Markdown heading в `prompts/STAGES.md`.
SessionStart/SubagentStart hook проецирует bounded запись первой. Без selector catalog не читается;
invalid/ambiguous/oversized явный selector либо отсутствующий выбранный heading даёт видимый
`DEGRADED` context. В этом случае открой полный record вручную и не используй completion claim до
проверки. Отсутствие selector сохраняет compact snapshot для незаполненного template, но full
overlay validator классифицирует его как `missing-stage-id`.

Для full project overlay read-only `tools/validate_project_overlay.py` является preflight gate:
он требует ровно одну unfenced selector-строку, валидный ASCII ID и ровно один unfenced heading.
Это structural validation ссылки, не semantic proof dependency DAG, runnable slice или evidence.

## Восстановление новой сессии

Восстанавливай project в следующем порядке:

1. Git root, current branch/status/diff/log и подтверждённый target/upstream;
2. global `~/.codex/AGENTS.md` и только применимые global rules/Skills;
3. project `AGENTS.md` / ближайший `AGENTS.override.md`;
4. `README.md`, компактный `AI_STATUS.md`, затем текущий `AI_PLAN.md`;
5. затронутая SPEC, canonical architecture/decisions и один exact `prompts/STAGES.md` record;
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
- текущие `AI_PLAN`, `AI_STATUS` и `ROADMAP`;
- проектные agents, Skills, hooks и MCP только при подтверждённом пробеле общей конфигурации.

Не создавай второй глобальный config Codex, второй Git workflow, дубли универсальных агентов или MCP «на всякий случай».

## Канонические имена

- Уровни сложности: `SIMPLE`, `STANDARD`, `COMPLEX`; строгий режим для `COMPLEX` задаёт `rules/modes/strict.md`.
- Стабильные требования: `specs/system.spec.md` и `specs/features/<feature>.spec.md`.
- Текущий исполняемый срез: `docs/AI_PLAN.md`.
- Текущее фактическое состояние: `docs/AI_STATUS.md`; отдельный `PROGRESS.md` не нужен.
- Долгосрочный порядок развития: `docs/ROADMAP.md`.
- Учебный журнал и подробная хронология создаются только при реальной пользе и не подменяют `AI_STATUS`.

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
