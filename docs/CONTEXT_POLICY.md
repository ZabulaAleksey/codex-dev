# Политика контекста

## Приоритет

Для файловых инструкций действует каскад:

`Модуль → Проект → ~/.codex → глобальная конфигурация Codex`

Более локальное правило уточняет общее только в своей области. Прямая инструкция пользователя для текущей задачи имеет высший приоритет, если не нарушает ограничения безопасности.

## Порядок загрузки

1. Ближайший относящийся к задаче `AGENTS.md` / `AGENTS.override.md`.
2. Одно правило режима и только активные фрагменты SDLC, домена и стека.
3. Затрагиваемые требования и критерии приёмки из SPEC.
4. Релевантные разделы `ARCHITECTURE.md`, `DECISIONS.md`, `DESIGN.md` и `SECURITY.md`.
5. Текущий `AI_PLAN`, целевой код, тесты и diff.
6. Компактный снимок `AI_STATUS`.

Не загружай по умолчанию всю библиотеку prompts, полные исторические roadmap, все fixtures/references, старые generated reports и общие правила, уже унаследованные проектом.

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
