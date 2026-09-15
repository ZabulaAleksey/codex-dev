# AI-команда разработки для Codex — набор для нескольких проектов

## Prompt Queue Lifecycle

Канон: `rules/prompt-queue-lifecycle.md`; read-only CLI: `tools/prompt_queue.py`.
Он проверяет task evidence перед narrow adapter operation; автоматического фонового удаления нет.
Project наследует правило через global router и добавляет только свои required checks.


Актуализировано: 2026-09-10.

Этот набор организует одну постоянную ИИ-команду разработчиков для нескольких репозиториев. Он рассчитан на работу в Codex CLI, IDE и настольном приложении с `AGENTS.md`, пользовательскими субагентами, skills, hooks, rules и MCP.

## Расположение каталогов

- `DEV_SOURCE_ROOT=~/codex-dev` — canonical Git-managed DEV source repository.
- `CODEX_HOME=~/.codex` — installed active Codex home layer и runtime state; это не Git working tree.
- `PROJECTS_ROOT=~` — parent только для resolution/discovery; product path —
  `${PROJECTS_ROOT}/<project>`.

Физическое нахождение repository под `PROJECTS_ROOT` не включает global DEV. Membership включает
только valid project-local `.codex/dev-project.toml`; `Global DEV bridge: enabled` в `AGENTS.md`
является дополнительной human-readable declaration, а не самостоятельным opt-in. Plain
repositories не получают project overlay, Prompt Queue или `Продолжай` bootstrap автоматически.
Resolver/config/migration contract описан в
[`docs/DEV_LAYOUT.md`](docs/DEV_LAYOUT.md).

Canonical source materialize-ится в `~/.codex` по `MANIFEST.txt`; blanket mirror запрещён. В
`~/.agents/skills` находится только проверяемая runtime-проекция Skills, а не ещё один canonical
repository.

Такая схема позволяет переносить домашний каталог между компьютерами без изменения документации и не смешивает шаблоны с рабочими проектами.

DEV-managed project хранит portable bootstrap files из `templates/dev-project/.codex/` и после
clone/pull запускает `.\.codex\bootstrap.ps1 check|apply` или
`./.codex/bootstrap.sh --check|--apply`. Global compatibility задаётся machine-readable
`dev-contract.toml`; missing source никогда не клонируется молча — bootstrap печатает один
canonical reviewable clone command.

## Идея

Не копировать 20 одинаковых агентов в каждый проект. Вместо этого:

1. **Глобальное ядро команды** версионируется в canonical source и устанавливается в `~/.codex/`.
2. **Глобальные Skills** версионируются в `<dev-root>/skill-sources/` и устанавливаются в `~/.agents/skills/`.
3. Каждый full staged repository имеет тонкий `AGENTS.md`, SPEC и единственный execution-state
   owner `prompts/STAGES.md`; локальные `.codex/agents/` и `.agents/skills/` добавляются только при
   подтверждённом project gap.
4. Глобальные hooks защищают от опасных команд и подмешивают краткий статус проекта в контекст.
5. Rules задают детерминированную политику для опасных shell-команд.
6. MCP подключаются по принципу минимально необходимого набора инструментов.
7. `rules/` маршрутизирует режим, этап SDLC, домен и стек без загрузки всей библиотеки.
8. `specs/` хранит канонические требования, а тесты подтверждают соответствие реализации SPEC.
9. Политика контекста и аудит совместимости не допускают дублирования глобальной и проектной автоматизации.

## Разработка на основе спецификаций

Для новой существенной `STANDARD` или `COMPLEX` функциональности процесс выглядит так:

```text
Требования → SPEC → архитектура → план → код → тесты → проверка SPEC
```

- `SPEC` определяет, что система должна делать.
- `ARCHITECTURE` определяет, как система устроена.
- `DESIGN` определяет UI/UX.
- `DECISIONS` объясняет существенные решения.
- `ROADMAP` определяет порядок развития.
- Prompt определяет только текущую работу агента.

Основные правила находятся в `rules/sdd/`, шаблон — в `templates/SPEC_TEMPLATE.md`.

## Управление контекстом

Для явного глобального аудита действий ДЕВ без автоматического host capture:
`py -3 -B tools/global_action.py catalog` проверяет Script Registry,
`py -3 -B tools/global_action.py lookup source-validation` находит существующий
CLI по классу задачи. `init/record/validate/detect` работают только с
указанным локальным ignored journal directory; формат события и границы
приватности — в `specs/features/global-action-journal.spec.md`.

- [`docs/PROJECT_FRAMEWORK.md`](docs/PROJECT_FRAMEWORK.md) определяет общие для всех проектов понятия КАРКАСА и АВТОМАТИЗАЦИИ КОНТЕКСТА.
- [`docs/CONTEXT_POLICY.md`](docs/CONTEXT_POLICY.md) задаёт порядок загрузки, проектный overlay и канонические имена документов.
- [`docs/CONTEXT_COMPATIBILITY.md`](docs/CONTEXT_COMPATIBILITY.md) используется перед добавлением agents, hooks, MCP, Skills или config.
- [`docs/notes/AUTOMATION_EXTENSIONS.md`](docs/notes/AUTOMATION_EXTENSIONS.md) описывает опциональные расширения и условия, при которых они оправданы.
- [`rules/governance.md`](rules/governance.md) задаёт lifecycle/evidence contracts и
  обязательные Stage contract и Completion Documentation Synchronization Gate.
- [`rules/backend-dx.md`](rules/backend-dx.md) задаёт адаптивный `BDX-L0..L3`
  contract; Skill `backend-dx-audit` проектирует, проверяет и улучшает backend
  workflow без копирования policy в product repository.
- [`rules/i18n-l10n.md`](rules/i18n-l10n.md) задаёт наследуемую архитектурную готовность
  пользовательских продуктов к нескольким языкам и локалям, locale-aware данным, fallback,
  text expansion и RTL; проекты хранят только конкретную delta в SPEC/DESIGN/architecture.
- [`rules/replaceable-modules.md`](rules/replaceable-modules.md) задаёт единый Replaceable Module
  Contract для vendor-bound providers/backends: system-owned ports, anti-corruption adapters,
  composition-root selection, contract tests и migration/fallback evidence без YAGNI-обёрток.
- [`docs/WORKFLOW.md`](docs/WORKFLOW.md) содержит copy-ready запросы для старта, stage,
  completion, архитектурного изменения, pre-merge, паузы, возобновления и новой идеи, а также
  computer↔laptop handoff.

Project-specific инструкции, архитектура, Skills и agents хранятся только в соответствующем project repository. Глобальный framework предоставляет schema, policies, validators и универсальные templates, но не ведёт библиотеку именованных проектов.

## Синхронизация завершения

Перед завершением задачи или этапа всегда проверяются существующие `README.md`,
`prompts/STAGES.md`, `docs/ROADMAP.md` и другие
документы, которые отражают выполненные шаги или текущее состояние. Изменившиеся факты
обновляются, а точные документы остаются без timestamp-only churn. После merge эта
проверка повторяется по target branch до фиксации merge-level status.

## Архитектурно завершённые этапы

Каждый stage до реализации получает dependency DAG только из завершённых prerequisites,
самостоятельный runnable vertical slice, concrete end-to-end scenario, PASS/evidence contract,
допустимую полностью рабочую временную реализацию и явно deferred scope. Future stage может
расширить или заменить работающий slice, но не впервые сделать предыдущий stage исполнимым либо
проверяемым. Mock/stub/interface-only результат остаётся `scaffolded`, а отсутствие живого PASS
evidence — `blocked`, `partial` или `implemented_unverified`, но не `DONE`.

## Continuous Master Execution

Явно запущенный `master_prompt` хранит versioned graph/track/checkpoint внутри selected
`prompts/STAGES.md` record. Controller выбирает dependency-ready slice, маршрутизирует continuation
или isolated parallel worktree, применяет evidence/stop/context gates и строит low-context handoff;
он не исполняет task commands и не делает merge/push/cleanup.

```powershell
py -3 -B .\tools\master_execution.py <project-root>
py -3 -B .\tools\master_execution.py <project-root> --compatibility
py -3 -B .\tools\master_execution.py <project-root> --materialize-compatibility <plan.json> --expected-plan-digest <sha256>
py -3 -B -m unittest tools.test_master_execution
```

Подробный lifecycle и stop conditions принадлежат `rules/governance.md`; schema —
`schemas/master-execution.schema.json`. Project без master block продолжает обычный Stage workflow.
Обычный вызов сначала классифицирует bounded canonical/legacy state. Canonical/migrated repository
получает прежнее CME/Stage decision без compatibility noise; legacy/mixed возвращает typed
`migration_required`, conflict fail-closed, отсутствие state — `no_stage_state`. Диагностический
`--compatibility` остаётся доступным, но не обязателен для discovery. Раздельные
`inspection_ok`, `canonical_valid` и `execution_allowed` не позволяют принять successful
inspection за разрешение запуска.

Materialization является отдельным explicit two-phase действием: caller сохраняет byte-exact plan
и его independently approved digest, затем передаёт оба CLI. Перед первым publish повторно
проверяются все known state bytes и contained paths; единственный public target —
`prompts/STAGES.md`. Legacy files сохраняются. Успех требует canonical read-back; stale state,
unknown lock и rollback failure возвращаются как typed non-zero outcomes.

## Specification → Execution Pipeline

После выбора live stage `tools/spec_execution.py` компилирует компактный
`CONTINUE_EXISTING`/`NEW_PROJECT` intake. Read-only `launcher` для continuation связывает exact
DEV project/bridge, selected STAGES/CME decision и relevant-only capability route без загрузки
полного master. Pipeline выбирает только релевантные capabilities и Skill metadata,
проверяет requirement → capability → evidence trace и выдаёт read-only решения по executor,
placement, automation promotion, context economy и Skill retirement. Он не исполняет команды,
не меняет модель, hooks, policies, Skills, Git или внешние backlog-системы.

```powershell
$freshSourceRevision = "<revision from the fresh Prompt Queue read>"
py -3 -B .\tools\spec_execution.py launcher --registry .\skill-sources\registry.toml --source-root . --input .\launcher.json --available-tool dev_paths --available-tool master_execution --source-revision $freshSourceRevision --queue-item-present
py -3 -B .\tools\spec_execution.py route --registry .\skill-sources\registry.toml --input .\route.json
py -3 -B .\tools\spec_execution.py context-diagnostics --input .\context-summary.json
py -3 -B -m unittest discover -s tools -p "test_*.py"
```

Полный contract принадлежит
`specs/features/specification-execution-pipeline.spec.md`; stage-first порядок контекста и
promotion/retirement gates — `rules/governance.md`.

## AI Policy Profiling / Agent Economics

Opt-in profiler измеряет стоимость verified outcomes, policy/experiment overhead, reusable
contours, agent outcomes и manual handoffs. Он не включается автоматически, не читает private
content и не меняет policies по накопленным данным.

```powershell
py -3 -B "$env:USERPROFILE\.codex\tools\ai_policy_profiler.py" init --root . --project-id my-project
py -3 -B "$env:USERPROFILE\.codex\tools\ai_policy_profiler.py" report --root .
```

Absent `.metrics/` означает disabled. Runtime JSONL/reports остаются ignored внутри project.
Полное включение, instrumented run, experiments, bounded discovery, reuse/handoff и чтение
dashboard описаны в [`docs/notes/AI_POLICY_PROFILING.md`](docs/notes/AI_POLICY_PROFILING.md).
Каноническая policy — [`rules/ai-policy-profiling.md`](rules/ai-policy-profiling.md); telemetry
является дополнительным evidence и не заменяет Stage DoD/E2E/tests.

## Установка

### Windows

Clone/pull canonical source вне `~/.codex`, затем открой PowerShell в его Git root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install-global.ps1 -DryRun
.\install-global.ps1
```

### Linux / macOS

```bash
cd "$DEV_SOURCE_ROOT"
./install-global.sh --dry-run
./install-global.sh
```

Если executable bit не сохранился при переносе, запусти `bash ./install-global.sh`; сам script
не требует изменения active config.

Оба wrapper определяют canonical source Git root по своему расположению и передают работу единому
`tools/install_global.py`. Installer строит manifest-only plan, fail closed проверяет protected
runtime paths и unknown collisions, применяет изменения транзакционно, пишет deterministic
ownership ledger `~/.codex/.dev-install-manifest.json`, запускает validators, materialize-ит Skills
существующим `sync_global_skills.py` и повторяет validators. Validation failure входит в rollback
boundary. `-DryRun` / `--dry-run` ничего не меняет.

Installer **не перезаписывает `~/.codex/config.toml`**. Рекомендуемые настройки находятся в:

```text
config.ai-dev-team.recommended.toml
```

Это reference/template. Если настройки нужны, объединяй их со своим `~/.codex/config.toml`
явно; installer не делает неоговорённый merge.

Installed `AGENTS.md`, agents, hooks и rules используются из `~/.codex`. Versioned Skills остаются
только в `<dev-root>/skill-sources`, а active runtime-проекция materialize-ится в
`~/.agents/skills` с file-set/SHA-256 verification.

Для миграции старого layout сначала перенеси/клонируй Git repository из `~/.codex` в отдельный
source path. Пока `~/.codex/.git` существует, installer fail closed и не меняет ни Git metadata,
ни runtime state. После отделения repository запусти dry-run: идентичные installed files безопасно
принимаются в ledger; различающийся unknown file требует ручного reconcile.

## Проверка

Сначала проверь целостность самого набора:

```powershell
py -3 .\tools\validate_context.py
```

Затем проверь один независимый project overlay (команда ничего не изменяет):

```powershell
py -3 .\tools\validate_project_overlay.py "$env:PROJECTS_ROOT\<project>"
py -3 .\tools\validate_project_overlay.py "$env:PROJECTS_ROOT\<project>" --json
```

Для brownfield repository default router/validator уже выполняет stage-state discovery; общий
framework reconciliation остаётся отдельным pre-refresh gate:

```powershell
py -3 .\tools\reconcile_project_framework.py "$env:PROJECTS_ROOT\<project>"
```

Из корня рабочего репозитория `${PROJECTS_ROOT}/<project>`:

```powershell
codex --ask-for-approval never "Кратко изложи активные инструкции и перечисли доступных пользовательских агентов."
codex mcp list
```

В интерактивной сессии также проверь:

```text
/agent
/hooks
/skills
/mcp
```

## Как работать

Для обычной задачи:

```text
Исправь ошибку X. Сначала воспроизведи её и найди минимальную причину. Используй субагентов только если параллельная работа реально поможет. После исправления запусти релевантные тесты и reviewer.
```

Для большого этапа:

```text
Реализуй current selector/record из prompts/STAGES.md. До кода проверь Stage contract: completed prerequisites, DAG, runnable vertical slice, concrete E2E, PASS/evidence, temporary implementation и deferred scope. Сначала architect + explorer, затем профильные специалисты. Не давай двум агентам с правом записи редактировать одни файлы. После реализации запусти test_engineer + reviewer. Не закрывай mock-only или зависящий от будущего stage путь. Перед DONE проверь README, prompts/STAGES.md, ROADMAP и другие state-bearing документы; обнови изменившиеся факты. После merge повтори проверку по target branch.
```

Или явно вызови skill:

```text
$implement-stage
$resume-project
$fix-bug
$review-change
$explain-change
$bootstrap-project-framework
$backend-dx-audit
```

При смене компьютера clone/pull canonical DEV source в `DEV_SOURCE_ROOT`, выполни
`install-global.ps1` на Windows либо `install-global.sh` на Linux/macOS, затем clone/pull нужный
product repository в `${PROJECTS_ROOT}/<project>`. Рабочее состояние восстанавливается из Git и project docs по
[`docs/CONTEXT_POLICY.md`](docs/CONTEXT_POLICY.md), не из истории чата или ручных копий файлов.

## Важное про расход лимита

Субагенты расходуют отдельные токены. Базовое правило набора:

- маленькая задача: 0–1 субагент;
- средняя межмодульная: 2–3;
- большой этап: 3–5;
- больше пяти одновременно — только когда части действительно независимы.

Recommendation задаёт hard ceiling `max_concurrent_threads_per_session = 4`; он ограничивает
фактический параллелизм и не является целевым количеством агентов. Unpinned agents наследуют
выбранную/default Codex model; reviewed pins и reasoning описаны в
[`docs/TEAM_ARCHITECTURE.md`](docs/TEAM_ARCHITECTURE.md).

Цель — не имитировать штат компании, а получать выигрыш от специализации и параллельности.
