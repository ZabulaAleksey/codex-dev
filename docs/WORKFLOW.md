# Рабочий процесс команды

## 0. Выбор режима

- `SIMPLE` — локальная низкорисковая правка: исследование, изменение, целевая проверка и diff без лишней процессной нагрузки.
- `STANDARD` — обычная функция или исправление: требования/SPEC, ограниченный план, реализация, пропорциональные проверки, self-review и обновление затронутой документации.
- `COMPLEX` — межмодульная архитектура, безопасность, миграции, распределённые системы или критичная производительность: явные требования, анализ рисков, откат, поэтапная реализация и профильная проверка.

## A. Небольшое исправление ошибки

1. Руководитель воспроизводит проблему или вызывает `explorer`.
2. Один агент с правом записи вносит минимальное исправление.
3. `test_engineer` проверяет регрессию, если тестирование нетривиально.
4. `reviewer` нужен только для рискованных или межмодульных изменений.

## B. Функция в одном слое

1. `planner` или профильный специалист находит либо создаёт feature-SPEC и формулирует критерии приёмки.
2. Один агент с правом записи выполняет реализацию по SPEC.
3. Выполняются тесты, связанные с идентификаторами требований.
4. Проверяется соответствие SPEC.
5. Обновляется current record/NEXT в `prompts/STAGES.md`, если изменилось execution state.

## C. Межсервисная функция

1. `architect` и встроенный `explorer` работают параллельно.
2. Руководитель фиксирует общую SPEC и контракт между слоями.
3. Профильные агенты с правом записи работают только в непересекающихся областях.
4. Выполняются интеграционные тесты.
5. Запускается `reviewer`; при изменениях авторизации, сети или секретов также запускается `security_reviewer`.
6. При критичных для производительности изменениях запускается `performance_engineer`.
7. Проверяются критерии приёмки и соответствие SPEC.
8. Обновляются SPEC, архитектура, статус и журнал решений только по фактическим изменениям.

## D. Следующий этап дорожной карты

Сначала подтверди, что stage contract из `rules/governance.md` содержит completed prerequisites,
dependency DAG, runnable vertical slice, concrete end-to-end scenario, PASS/evidence contract,
temporary implementation и deferred scope. Затем используй `$implement-stage`.

## E. Исследование новой технологии

Используй `docs_researcher`; сначала изучи официальную документацию или Context7, затем проведи небольшой эксперимент. До добавления зависимости в production зафиксируй цепочку:

`проблема → цель → альтернативы → решение → критерии успеха → fallback → тесты`

Feature flag, benchmark, ADR и план отката добавляй пропорционально риску. Не выдавай успешный прототип за production-ready решение.

## F. Остановка циклов

`reviewer` может вернуть замечания. Допускается максимум два автоматических цикла «исправление → проверка» за одну задачу. После двух неудачных циклов руководитель должен сформулировать точный блокер вместо бесконечного обмена между агентами.

## G. Маршрутизация правил

Перед `STANDARD` или `COMPLEX` задачей определи режим, этап SDLC, домен, стек и соответствующую SPEC. Загружай только относящиеся к задаче файлы из `rules/` согласно `rules/README.md`.
Для stage-bound задачи stable `Stage ID` в `prompts/STAGES.md` выбирает ровно один heading
record в этом же файле. Full overlay сначала проходит read-only
`tools/validate_project_overlay.py`: missing/multiple/invalid selector и missing/ambiguous heading
являются fail-visible issues. Degraded hook context требует ручной проверки полного record.

Если задача вводит или оценивает дорогую AI-policy, agent/retrieval/reuse contour, automation,
manual handoff либо baseline/variant experiment, подключи `rules/ai-policy-profiling.md`. Начни с
Observe и не меняй thresholds автоматически. Existing project без `.metrics/` не обязан включать
profiler.

## H. Backend developer workflow

Для bootstrap, audit или изменения backend command/config/service/API/DB/test DX
используй `rules/backend-dx.md` и Skill `backend-dx-audit`. Project facts хранятся
только как `Backend DX Delta` в `docs/project-context.md`. Завершение требует
применимых `BDX-GATE-01..12` с command evidence; `N/A` без причины и fixture/mock
как production evidence запрещены.

## I. Завершение этапа

Этап считается завершённым, когда его primary vertical slice запускается без будущего stage,
конкретный end-to-end сценарий имеет PASS evidence, выполнены критерии приёмки, пройдены
релевантные проверки/review и Completion Documentation Synchronization Gate из
`rules/governance.md`. Заблокированный primary gate нельзя закрыть как `DONE`; используй
`blocked`, `scaffolded`, `implemented_unverified` или `partial`.

Всегда проверь `README.md`, `prompts/STAGES.md`, `docs/ROADMAP.md`
и другие state-bearing документы; обнови изменившиеся факты, а точные
документы оставь без формального churn. После merge повтори gate по target branch и только
тогда фиксируй интеграцию как завершённую. Merge и push выполняются только в рамках явного
разрешения пользователя и Git-правил проекта.

## J. Готовые запросы к Codex

Эти формулировки — операционная проекция `rules/governance.md`. Они не создают новый источник
требований и не отменяют более локальный project `AGENTS.md`.

### Начать работу с проектом

```text
Открой проект <project> в ~/codex-workspace. Прочитай глобальный ДЕВ из ~/.codex,
project AGENTS.md, README.md, current selector/record из prompts/STAGES.md, относящиеся к задаче
SPEC/архитектурные документы и только релевантные записи docs/LEARNING_LOG.md. Проверь
Git branch/status/diff и определи последний подтверждённый результат, blockers, monitoring class
и первый незавершённый шаг. Старый чат не используй как source of truth. Сначала дай компактный
evidence-backed снимок; не начинай новую реализацию, пока не установлен допустимый slice.
```

### Выполнить stage

```text
Выполни следующий явно выбранный stage из единственного project prompts/STAGES.md. До кода
проверь dependency DAG, completed prerequisites, входные
предпосылки, runnable vertical slice, concrete end-to-end scenario, PASS criteria/evidence,
допустимую полностью рабочую temporary implementation и deferred scope. Реализуй и проверь slice
без зависимости от будущего stage. Mock/stub/interface-only путь не закрывай как completed.
Запусти применимые unit, integration и component-проверки. Для product/user-facing stage выполни
живой E2E по пути `client → API/CLI → backend`; если обязательный backend отсутствует, поставь
`BLOCKED_BY_BACKEND` и не закрывай stage. Для internal/docs/policy stage допустим исполнимый
structural consumer path, который подтверждает действие правила или валидатора без mock. Затем
выполни documentation synchronization gate и покажи evidence.
```

### Завершить stage

```text
Проверь Definition of Done, acceptance criteria, dependency DAG, primary runnable slice и
stage-specific end-to-end evidence. Для product/user-facing stage требуй живой путь
`client → API/CLI → backend`; отсутствие обязательного backend означает `BLOCKED_BY_BACKEND`, а не
завершение. Для internal/docs/policy stage прими исполнимый structural consumer path. Проверь также
tests/linters/build/migrations и Git diff. Выполни Completion Documentation
Synchronization Gate: проверь README.md, prompts/STAGES.md, ROADMAP.md и
затронутые canonical docs; изменяй только устаревшие факты. Значимую нетривиальную ошибку оформи
в LEARNING_LOG.md по формату Problem/Symptom/Root cause/Failed attempts/Fix/Verification/
Prevention/Links. Отдельно укажи lifecycle и evidence level. Не делай commit, push или merge без
явного разрешения.
```

### Провести архитектурное изменение

```text
Сравни изменение с утверждённой SPEC, текущими ARCHITECTURE.md/DECISIONS.md, глобальным ДЕВ и
project compatibility mapping. Определи затронутые boundaries, contracts, migrations, security,
fallback, rollback и альтернативы. Зафиксируй принятое решение только в каноническом
architecture/ADR owner, затем синхронизируй зависимые STAGES/schema representations.
Не копируй одно решение в несколько независимых sources of truth и не делай внешние записи без
отдельного разрешения.
```

### Проверить перед merge

```text
Проведи read-only pre-merge review текущей ветки относительно target branch: scope/SPEC,
тесты, lint/static checks, build, migrations, security, документация, prompts/STAGES.md и
Git diff. Покажи команды, результаты, scope, commit/environment и caveats; отдельно перечисли
blockers и deferred items. Не называй локальную проверку merged evidence и не выполняй merge,
push, PR или удаление ветки без отдельного разрешения.
```

### Профилировать AI-policy

```text
Проверь, существует ли comparable baseline и относится ли задача к тому же task class. Если
profiler не включён, не создавай telemetry без явного opt-in. Для включённого profiler зафиксируй
stable Policy IDs, Experiment ID/arms и instrumented безопасные facts; unknown token/human metrics
не оценивай. Ограничь discovery wall/token/cost budget, фиксируй reuse false positives и manual
handoff reason. После verified Stage outcome создай JSON/Markdown report, покажи sample size,
median deltas, profiler overhead и caveats. Не изменяй policy thresholds без отдельного human
approval и approved SPEC/decision.
```

### Поставить проект на паузу

```text
Подготовь project к паузе. Зафиксируй в current STAGES record только изменившиеся факты: текущую branch,
последний подтверждённый результат, незавершённый slice, blockers, выполненные checks, monitoring
class и точный следующий шаг. Сверь selector/NEXT в prompts/STAGES.md и Git status/diff; важный контекст не оставляй
только в чате. Commit/push выполняй лишь по отдельному разрешению; если его нет, явно укажи, что
dirty worktree не перенесён на другое устройство.
```

### Возобновить проект

```text
Восстанови project без истории старого чата. Проверь Git root, branch/status/log, затем прочитай
глобальный ~/.codex/AGENTS.md, project AGENTS.md, README.md, current/exact STAGES record, выбранную
SPEC, architecture/decisions и релевантные learning entries. Сверь ссылки,
dependency/toolchain state и external pending sync. Если источник отсутствует или расходится,
верни DEGRADED/BLOCKED с точным gap; не выбирай следующий stage наугад.
```

### Обработать новую идею

```text
Не превращай идею автоматически в глобальное правило, утверждённую SPEC или implementation
stage. Сначала сопоставь её с существующим кодом, SPEC, DESIGN/ARCHITECTURE, ROADMAP,
prompts/STAGES.md и decisions. Классифицируй как IDEA/REFINED/PROMPT_READY,
NEEDS_RESEARCH, NEEDS_DECISION, DUPLICATE, ALREADY_IMPLEMENTED или BLOCKED; определи, относится ли
она к существующему project или требует отдельного Git repository. Подготовь запись для
назначенного Notion/backlog source, но выполняй внешнюю запись и реализацию только при явном
разрешении/approval policy.
```

## K. Компьютер ↔ ноутбук

Перед переключением устройства:

1. останови текущую операцию в консистентной точке и проверь `git status`/`git diff`;
2. выполни применимые checks и обнови current STAGES record/NEXT, только если изменились важные факты;
3. commit/push завершённого или сохранение незавершённого в отдельной ветке выполняй только при
   явном разрешении; без push зафиксируй, что другое устройство не получит dirty worktree;
4. если менялся глобальный ДЕВ, переноси его отдельным Git lifecycle от product repository;
5. не используй экспорт чата или ручное копирование отдельных Markdown как основной handoff.

На другом устройстве:

1. clone/pull глобальный ДЕВ непосредственно в `~/.codex`;
2. запусти `install-global.ps1` на Windows либо `install-global.sh` на Linux/macOS; wrappers
   выполняют context validation, Skill materialization/parity и global validator;
3. clone/pull `~/codex-workspace/<project>`, проверь branch/status и восстанови dependencies;
4. восстанови локальные secrets через разрешённый machine-local механизм, не из Git/чата;
5. используй запрос «Возобновить проект» выше и продолжай только после совпадения local state с
   repository evidence.

## L. External projections и monitoring

Полные владельцы, sync triggers, degraded behavior и классы `active` / `event-driven` / `frozen`
заданы только в `rules/governance.md`. Project сохраняет monitoring class и внешние mappings в
`docs/project-context.md` либо назначенном external registry; глобальный ДЕВ не ведёт live inventory
проектов. Ни monitoring class, ни наличие connector не являются разрешением на запись, deploy или
синхронизацию.
