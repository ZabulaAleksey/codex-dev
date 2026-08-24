# Карта зависимостей глобального контекста Codex

Дата проверки: 2026-08-24. Канонический источник: `C:\Users\aleks\.codex`.

Документ описывает не только файлы, которые непосредственно попадают в prompt, но и весь управляемый контур, который выбирает, создаёт, проверяет или проецирует контекст. Полный пофайловый реестр находится в `docs/CONTEXT_FILE_INVENTORY.md`.

## 1. Итоговая модель

Глобальная система состоит из четырёх слоёв:

1. **Автоматически обнаруживаемый контекст** — `AGENTS.md` по цепочке каталогов и доверенные project config.
2. **Маршрутизируемый контекст** — `rules/`, `skills/`, роли субагентов, MCP и plugins; он подгружается по задаче, а не целиком.
3. **Сессионный контекст** — hook `session_context.py`, который добавляет ограниченный набор актуальных project-файлов при старте, возобновлении, compact и старте субагента.
4. **Контекст-производитель** — presets, specs, templates, tools и installer-скрипты. Они не обязаны попадать в каждый prompt, но создают и валидируют файлы первых трёх слоёв.

Официальная модель Codex подтверждает следующие инварианты:

- глобальный `~/.codex/AGENTS.md` загружается первым, затем проектные `AGENTS.md` от корня репозитория к текущему каталогу; более локальные инструкции идут позже и имеют приоритет: <https://learn.chatgpt.com/docs/agent-configuration/agents-md>;
- роли субагентов определяются TOML-файлами в `~/.codex/agents` и project `.codex/agents`, наследуют родительскую конфигурацию и добавляют свои инструкции: <https://learn.chatgpt.com/docs/agent-configuration/subagents>;
- hooks из разных уровней складываются, поэтому проект не должен без необходимости дублировать глобальные hooks: <https://learn.chatgpt.com/docs/hooks>;
- MCP определяется через `config.toml`, trusted project config и plugin config: <https://learn.chatgpt.com/docs/extend/mcp>;
- skill работает через progressive disclosure: сначала видны `name` и `description`, полный `SKILL.md` читается только при выборе skill: <https://learn.chatgpt.com/docs/build-skills>.

## 2. Главный поток формирования контекста

```text
system/developer/user request
            │
            ├── ~/.codex/AGENTS.md
            │       └── rules/README.md → selective rules
            │
            ├── <repo>/AGENTS.md
            │       └── <subtree>/AGENTS.override.md (если существует)
            │
            ├── SessionStart/SubagentStart hook
            │       └── project docs/specs, до заданного лимита
            │
            ├── выбранный skill/SKILL.md
            │       └── references/scripts/assets только по маршруту skill
            │
            ├── выбранный subagent
            │       └── ~/.codex/agents/<role>.toml + наследуемый config
            │
            └── вызванный tool
                    ├── built-in/sandbox
                    ├── MCP server
                    └── plugin capability
```

`AGENTS.md` не должен копировать все правила. Его функция — задать приоритеты, обязательные инварианты и маршрутизацию к более узким источникам. Это уменьшает конфликт правил и объём постоянно активного контекста.

## 3. Приоритеты и конфликт-резолюция

Практический порядок для управляемых файлов:

1. прямой запрос пользователя, если он не противоречит system/developer ограничениям;
2. наиболее локальный project `AGENTS.override.md` или `AGENTS.md`;
3. project `AGENTS.md`;
4. глобальный `~/.codex/AGENTS.md`;
5. выбранные глобальные rules и skill-инструкции;
6. архитектурные, статусные и feature-документы как фактическое состояние проекта.

Специфичность не даёт права ослаблять безопасность, destructive-action policy, sandbox или обязательный Definition of Done. При расхождении живого кода и документации сначала фиксируется наблюдаемое состояние, затем синхронизируются status/plan/docs.

## 4. `AGENTS.md` и selective rules

Глобальный `AGENTS.md` является входной точкой. Он:

- объявляет `C:\Users\aleks\.codex` каноническим глобальным DEV-контуром;
- требует локализовать проектные различия в проекте;
- маршрутизирует к `rules/README.md`, режимам, SDLC-этапам, доменам, стекам, governance и SDD;
- запрещает механически дублировать subagents, hooks, MCP, skills и Git workflow;
- задаёт русский язык для нового проектного контекста по умолчанию.

`rules/README.md` — индекс-маршрутизатор. Он выбирает минимальный набор по шести измерениям:

| Измерение | Каталог/файл | Пример триггера |
|---|---|---|
| База | `rules/ai-dev-team.rules` | любая инженерная задача |
| Режим | `rules/modes/` | prototype / standard / strict |
| SDLC | `rules/sdlc/` | requirements / architecture / implementation / review |
| Домен | `rules/domains/` | frontend / security / realtime / scientific computing |
| Стек | `rules/stacks/` | React / Rust / FastAPI / Postgres / WASM |
| Governance/SDD | `rules/governance.md`, `rules/sdd/` | изменение living contract или spec-first работа |

Rules не загружаются все одновременно. Индекс и текущая задача определяют применимый subset. `rules/fallback-policy.md` и `rules/model-routing.md` влияют на стратегию выполнения; `rules/node-package-management.md` и `rules/word-pdf-academic.md` — узкие политики по типу результата.

## 5. Субагенты

`config.toml` включает multi-agent режим и задаёт общие model/effort/thread defaults. Тринадцать файлов `agents/*.toml` добавляют ограниченные роли:

| Роль | Ответственность |
|---|---|
| `architect` | границы сервисов и межмодульная архитектура |
| `backend_engineer` | backend API, сервисы и бизнес-логика |
| `beginner_mentor` | учебное объяснение изменений |
| `database_engineer` | schema, migrations, indexes и invariants |
| `devops_engineer` | Docker, CI/CD и deployment operations |
| `docs_researcher` | актуальная официальная документация/API |
| `frontend_engineer` | React/Next/TypeScript UI и browser behavior |
| `performance_engineer` | latency, throughput, memory и hot paths |
| `planner` | исполняемый план и критерии приёмки |
| `release_manager` | готовность к commit/PR/release без публикации |
| `reviewer` | read-only correctness/regression review |
| `security_reviewer` | secrets, auth, permissions и untrusted input |
| `test_engineer` | воспроизведение и regression coverage |

Каждый субагент получает родительский контекст и свою role-инструкцию. `SubagentStart` дополнительно запускает `session_context.py`, поэтому проектные status/spec/architecture данные доступны и дочерней роли. Project `.codex/agents/*.toml` должен дополнять этот набор только ролью, специфичной для проекта.

## 6. Hooks

`hooks.json` регистрирует три цепочки:

| Событие | Matcher | Скрипт | Эффект |
|---|---|---|---|
| `SessionStart` | `startup|resume|compact` | `hooks/session_context.py` | bounded project context |
| `SubagentStart` | все | `hooks/session_context.py` | тот же bounded context для роли |
| `PreToolUse` | `^Bash$` | `hooks/guard_destructive.py` | отклонение известных опасных shell patterns |

`session_context.py` ищет и читает, если они существуют:

1. `docs/AI_STATUS.md`;
2. `specs/README.md`;
3. `specs/system.spec.md`;
4. `docs/AI_PLAN.md`;
5. `docs/ARCHITECTURE.md`.

Объём ограничен скриптом; отсутствие файла не является ошибкой. `AGENTS.md`, rules, `DECISIONS.md` и stage-файлы намеренно не дублируются этим hook: у них отдельные пути discovery/on-demand.

`guard_destructive.py` является дополнительной сигнальной защитой. Он не заменяет sandbox, approval policy и проверку абсолютной цели перед удалением.

## 7. Runtime `config.toml`, MCP и plugins

`~/.codex/config.toml` — runtime-файл и намеренно не входит в Git-репозиторий как активный экземпляр. Версионируемый ориентир — `config.ai-dev-team.recommended.toml`; installer и ручное сравнение не должны переносить secrets или machine-local credentials.

На момент аудита runtime config содержит:

- features: multi-agent, hooks и plugins;
- agent defaults и ограничение concurrency;
- MCP: `node_repl`, `context7`, `chrome-devtools`, `openaiDeveloperDocs`, `eraser`; GitHub и Atlassian definitions отключены;
- plugins: browser, visualize, documents, PDF, spreadsheets, presentations, template-creator, Sites и build-web-apps; Google Calendar и Slack отключены;
- trusted project entries для workspace root и девяти явно перечисленных репозиториев.

`docs/MCP_CATALOG.md` является governance-каталогом, а не автоматическим источником активации. Он описывает назначение, риски и optional/fallback серверы. Фактически активен только сервер, включённый в runtime/project/plugin config и доступный в текущей сессии.

Plugins могут добавлять skills, MCP и apps. Их cache/state под `~/.codex/plugins` — runtime dependency, но не canonical source: кэш не следует вручную копировать в repository или считать проектным контрактом.

## 8. Skills и их проекция

Каноническая цепочка:

```text
skill-sources/<skill>/...
        │
        ├── tools/sync_global_skills.py
        │       ├── сравнение file set и SHA-256
        │       ├── backup изменяемой runtime-копии
        │       └── синхронизация
        │
        └── C:\Users\aleks\.agents\skills\<skill>\...
                    └── discovery runtime
```

`skill-sources/` — единственный редактируемый source of truth для собственных skills этого репозитория. `~/.agents/skills` — исполняемая проекция. `install-global.ps1` вызывает sync и валидаторы. Внешние system/plugin skills под `~/.codex/skills/.system` и plugin cache управляются их поставщиками и не должны включаться в MANIFEST этого репозитория.

`dev-karkas` использует progressive disclosure: `SKILL.md` маршрутизирует к 12 policy/reference-файлам и двум scripts. Остальные skills имеют узкий одиночный `SKILL.md`; `bootstrap-project-framework` также содержит UI metadata `agents/openai.yaml`.

## 9. Specs, docs, status и task context

`specs/system.spec.md` фиксирует системные инварианты. `specs/features/*.spec.md` ограничивает отдельные изменения и их acceptance criteria. `specs/README.md` — индекс и статус спецификаций.

Живые документы разделены по назначению:

- `docs/ARCHITECTURE.md`, `SECURITY.md`, `DESIGN.md` — устойчивые ограничения;
- `docs/AI_STATUS.md`, `AI_PLAN.md`, `ROADMAP.md`, `DECISIONS.md` — текущее состояние, план, этапы и решения;
- `docs/CONTEXT_*`, `PROJECT_FRAMEWORK.md`, `SDD_GUIDE.md`, `HOOK_POLICY.md`, `MCP_CATALOG.md` — правила сборки контекста;
- `docs/TEAM_*`, `WORKFLOW.md`, `VERIFY_SETUP.md`, `QUICKSTART.md` — операционная навигация;
- `docs/LEARNING_LOG.md`, `MENTORING_GUIDE.md` — обучающий слой;
- `docs/AUTOMATION_EXTENSIONS.md`, `ORCHESTRATION_LATER.md` — отложенные/дополнительные расширения.

Hook автоматически поднимает только пять наиболее нужных project-файлов. Остальные выбираются AGENTS/rules/skills либо читаются при необходимости.

## 10. Presets и project overlay

Шесть каталогов `presets/*` — шаблоны project-specific delta:

```text
preset
 ├── AGENTS.md                       project root contract
 ├── **/AGENTS.override.md           subtree exception
 ├── .codex/config.toml              project-local config delta
 ├── .codex/agents/*.toml            domain roles
 ├── .codex/rules/project.rules      project-only rules
 ├── .agents/skills/*/SKILL.md        stage workflow
 ├── specs/*                         system/feature contracts
 └── docs/*                          status, plan, architecture, decisions, MCP
```

Preset не является runtime context до копирования в проект. `install-project.ps1` выполняет механическую проекцию и по умолчанию не заменяет существующие файлы. Параметр `-Force` может перезаписать project context; перед ним обязателен inspect → gap analysis → merge plan. Для существующего проекта предпочтительнее `tools/reconcile_project_framework.py`, который строит план расхождений.

Project `.codex/rules/project.rules` не должен повторять глобальные правила. Project `AGENTS.md` ссылается на `C:\Users\aleks\.codex\AGENTS.md` и описывает только локальные различия. Subtree override допустим только там, где требования реально отличаются.

## 11. Tools, installers, templates и MANIFEST

Контур изменений:

```text
developer change
  ├── specs/docs/rules/skills/presets
  ├── MANIFEST.txt (точный tracked file set)
  ├── tools/validate_context.py
  ├── tools/validate_global_codex.py
  ├── tools/validate_project_overlay.py
  ├── unit tests for validators/sync/reconcile
  └── install-global.ps1 / install-project.ps1
```

`MANIFEST.txt` — воспроизводимый список tracked-файлов, а не список runtime cache. `validate_context.py` проверяет связность repository context; `validate_global_codex.py` — глобальную установку и managed skills; `validate_project_overlay.py` — project overlay. `normalize_user_codex.py` и `reconcile_project_framework.py` строят миграционные планы; `sync_global_skills.py` поддерживает source/runtime parity.

Templates не загружаются автоматически. Они становятся контекстом только при создании нового dev/learning/spec документа.

## 12. Найденные конфликты и решения

| Состояние | Риск | Решение |
|---|---|---|
| `README.md` и `QUICKSTART.md` ссылались на удалённый слой `projects/<project>` | команды проверки указывали не туда | исправлено на `~\codex-workspace\<project>` |
| Исторические `projects/` ссылки в feature spec/learning log/tests | ложноположительное «устаревший путь» | сохранены как migration history или test fixture |
| Broad trust для `C:\Users\aleks\codex-workspace` | новый вложенный repo может наследовать доверие | не изменено автоматически; доверие является явной пользовательской политикой |
| `install-project.ps1 -Force` | возможна перезапись локального living contract | разрешать только после gap analysis; для существующего проекта использовать reconcile |
| Hooks разных уровней additive | дублирование context/guard hooks | project hook добавлять только для доказанного локального gap |
| Preset project rules | возможное повторение global policy | проверять как minimal project delta при установке |
| `~/.agents/skills` редактируется вручную | drift от source of truth | редактировать `skill-sources`, затем sync и validate |
| Runtime cache/plugins/session/state | соблазн включить в Git/backup как contract | не считать canonical; сохранять только declarative config без secrets |

## 13. Что не является активным конфликтом

- `.migration-backup` и migration worktrees сохраняются, пока соответствующие ветки не интегрированы и не проверены; возраст каталога сам по себе не делает его безопасным для удаления.
- Optional MCP из каталога не считается отсутствующей зависимостью, если server отключён.
- Historical specs со статусом `SUPERSEDED` остаются аудит-следом и не управляют новой реализацией.
- Presets не должны быть полностью синхронизированы с каждым существующим проектом: это исходные шаблоны, а не зеркала.

## 14. Обязательная проверка после изменения контекста

```powershell
git diff --cached --check
py -3 -B .\tools\validate_context.py
py -3 -B .\tools\validate_global_codex.py --workspace C:\Users\aleks\.codex --codex-home C:\Users\aleks\.codex
py -3 -B -m unittest `
  tools.test_sync_global_skills `
  tools.test_reconcile_project_framework `
  tools.test_validate_global_codex `
  tools.test_validate_project_overlay
```

Для каждого проекта дополнительно:

```powershell
py -3 -B .\tools\validate_project_overlay.py C:\Users\aleks\codex-workspace\<project>
```

Проверка должна выполняться без автоматического merge/push и без удаления migration backup до подтверждённой интеграции ветвей.
