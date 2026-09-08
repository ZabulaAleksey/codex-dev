# AI-команда разработки для Codex — набор для нескольких проектов

## Prompt Queue Lifecycle

Канон: `rules/prompt-queue-lifecycle.md`; read-only CLI: `tools/prompt_queue.py`.
Он проверяет task evidence перед narrow adapter operation; автоматического фонового удаления нет.
Project наследует правило через global router и добавляет только свои required checks.


Актуализировано: 2026-08-27.

Этот набор организует одну постоянную ИИ-команду разработчиков для нескольких репозиториев. Он рассчитан на работу в Codex CLI, IDE и настольном приложении с `AGENTS.md`, пользовательскими субагентами, skills, hooks, rules и MCP.

## Расположение каталогов

- `~/.codex` — этот Git repository, общая AI-инфраструктура и активный пользовательский слой Codex.
- `~/codex-workspace/<project>` — рабочий Git-репозиторий конкретного проекта.

Путь `~/codex-workspace/global/codex` не поддерживается как второй source: он конфликтует с
консолидированным Git-root `~/.codex`. В `~/.agents/skills` находится только проверяемая runtime-
проекция Skills, а не ещё один канонический repository.

Такая схема позволяет переносить домашний каталог между компьютерами без изменения документации и не смешивает шаблоны с рабочими проектами.

## Идея

Не копировать 20 одинаковых агентов в каждый проект. Вместо этого:

1. **Глобальное ядро команды** хранится в `~/.codex/agents/`.
2. **Глобальные Skills** версионируются в `~/.codex/skill-sources/` и устанавливаются в `~/.agents/skills/`.
3. Каждый репозиторий имеет тонкий `AGENTS.md`, SPEC и `docs/AI_*.md`; локальные `.codex/agents/` и `.agents/skills/` добавляются только при подтверждённом проектном пробеле.
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

Repository ДЕВ должен быть клонирован или перемещён непосредственно в `~/.codex`.
Открой PowerShell в этом каталоге:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install-global.ps1
```

### Linux / macOS

Repository также должен находиться непосредственно в `~/.codex`:

```bash
cd ~/.codex
./install-global.sh
```

Если executable bit не сохранился при переносе, запусти `bash ./install-global.sh`; сам script
не требует изменения active config.

Оба wrapper сначала проверяют canonical Git root, запускают read-only context validation, затем
materialize-ят Skills существующим Python tool и повторяют context/global validation. Они
**не перезаписывают `~/.codex/config.toml`**. Рекомендуемые настройки находятся в:

```text
config.ai-dev-team.recommended.toml
```

Их нужно объединить со своим `~/.codex/config.toml`.

`AGENTS.md`, agents, hooks и rules используются непосредственно из `~/.codex`. Versioned Skills
хранятся в `~/.codex/skill-sources`, а единственная active runtime-проекция materialize-ится в
`~/.agents/skills` с file-set/SHA-256 verification; она не является вторым source of truth.

## Проверка

Сначала проверь целостность самого набора:

```powershell
py -3 .\tools\validate_context.py
```

Затем проверь один независимый project overlay (команда ничего не изменяет):

```powershell
py -3 .\tools\validate_project_overlay.py ~\codex-workspace\<project>
py -3 .\tools\validate_project_overlay.py ~\codex-workspace\<project> --json
```

Для brownfield repository сначала выполни read-only reconciliation gate:

```powershell
py -3 .\tools\reconcile_project_framework.py ~\codex-workspace\<project>
```

Из корня рабочего репозитория `~/codex-workspace/<project>`:

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

При смене компьютера сначала синхронизируй отдельный Git repository ДЕВ в `~/.codex` и выполни
`install-global.ps1` на Windows либо `install-global.sh` на Linux/macOS, затем clone/pull нужный product repository в
`~/codex-workspace/<project>`. Рабочее состояние восстанавливается из Git и project docs по
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
