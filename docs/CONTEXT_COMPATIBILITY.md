# Аудит совместимости контекста

## Source repository → installed layer delta — 2026-09-10

| Возможность | Найденное состояние | Потребность | Статус | Канонический owner |
|---|---|---|---|---|
| DEV root | Git и runtime были совмещены в `~/.codex` | отдельный portable source clone | `CONFLICT → SUPERSEDED` | `~/codex-workspace/codex-dev` или другой source Git root |
| Installed layer | direct use без ownership metadata | manifest-only projection | `EXTEND` | `MANIFEST.txt` + `.dev-install-manifest.json` |
| Runtime state | находился рядом с tracked files | никогда не выводить ownership из directory absence | `FORBIDDEN_TO_OVERWRITE` | Codex runtime; installer protected namespaces |
| Existing managed files | legacy layout не имел ledger | безопасная миграция без blind overwrite | `EXTEND` | identical adoption; differing unknown collision fail closed |
| Stale cleanup | ownership нельзя было доказать вне Git | удалять только ранее recorded managed file | `EXTEND` | deterministic ownership ledger |
| Skills | source и runtime уже разделены | сохранить единственную runtime projection | `INHERITED` | `<dev-root>/skill-sources` → `sync_global_skills.py` → `~/.agents/skills` |
| Config | recommendation и active config имели разные роли | исключить implicit replacement/merge | `INHERITED` | installed recommendation reference; active runtime config |
| Prompt Queue | portable policy/metadata принадлежат source | подготовить future bootstrap path | `INHERITED` | manifest-managed rules/hooks/tools; runtime payload вне source |

Предыдущие решения о `~/.codex` как Git-корне ниже сохранены как audit trail и superseded этим
разделением. Installer не выполняет destructive migration `.git`; legacy repository сначала
переносится пользователем в отдельный source path.

## Brownfield stage compatibility delta — 2026-09-08

| Возможность | Найденное состояние | Потребность | Статус | Канонический owner |
|---|---|---|---|---|
| Canonical route | same-file selector уже strict | сохранить поведение без legacy scan | `INHERITED` | stage_selector + selected STAGES record |
| Legacy detection | reconciler перечисляет files, validator только отклоняет | bounded semantic classification и dry-run plan | `EXTEND` | CME compatibility adapter |
| Migrated proof | legacy может быть retained без machine proof | same-file manifest + content digests | `EXTEND` | selected STAGES record + schema |
| Conflict behavior | missing/competing state fail visibly | explicit migration_required, без guessing | `INHERITED → EXTEND` | fallback/governance + adapter |
| Product writes | repositories независимы | первый slice только read-only evidence | `FORBIDDEN_TO_OVERWRITE` | unchanged product roots |
| Runtime/hooks/services | existing controller/selector достаточны | не создавать второй framework | `INHERITED` | tools/master_execution.py |

Первый real fixture — electro-tutor read-only. Его legacy files, product code, Git state и active
runtime не изменяются. Apply/materialization и mass rollout отсутствуют.

## Canonical STAGES delta — 2026-09-08

| Возможность | До изменения | Delta | Статус |
|---|---|---|---|
| Execution-state owner | `prompts/STAGES.md` + отдельные AI plan/status | один STAGES selector/plan/lifecycle/evidence/blocker/NEXT | `CONFLICT` → `EXTEND` |
| Session context | selector читался из отдельного plan | selector и exact record читаются из одного bounded STAGES | `EXTEND` |
| Greenfield bootstrap | два AI templates плюс STAGES | один `STAGES_TEMPLATE.md` | `SUPERSEDED` → `EXTEND` |
| Brownfield migration | legacy status names только отклонялись | read-only `MERGE` classification, semantic/link audit до удаления | `EXTEND` |
| Product repositories | независимые Git roots | mass rollout не выполняется; каждый project мигрируется отдельно | `INHERITED` |
| Runtime config/data | вне versioned source | не изменяются | `INHERITED` |

Detailed contract: `specs/features/canonical-stages-policy.spec.md`; decision:
`docs/DECISIONS.md`; executable owners: `hooks/stage_selector.py`,
`hooks/session_context.py`, `tools/validate_project_overlay.py` и
`tools/reconcile_project_framework.py`.

## Prompt queue delta — 2026-09-07

| Возможность | До изменения | Delta | Статус |
|---|---|---|---|
| Stage/evidence/Notion intake | Канон существует | Routing на один queue policy owner | `EXTEND` |
| Retention/cleanup guard | Только внешний текст, исполнимого guard нет | stdlib tools/prompt_queue.py + tests | `EXTEND` |
| Queue writes | Existing Notion connector | Exact-item operation и read-back через existing adapter | `INHERITED` |
| Hooks/runtime Skills/config/profiler | Не обеспечивают queue cleanup | Не изменяются | `INHERITED` |


Используй этот шаблон перед добавлением или существенным изменением agent, hook, MCP, Skill, rules или конфигурации.

## Статусы

- `INHERITED` — возможность уже предоставляет глобальный или workspace-уровень; локальная копия не нужна.
- `EXTEND` — общая возможность подходит, но проект добавляет узкое правило или адаптер.
- `PROJECT_ONLY` — возможность относится только к одному проекту и хранится в нём.
- `CONFLICT` — определения дублируются или задают несовместимое поведение; выбери один канонический источник.
- `OBSOLETE` — возможность больше не используется и должна быть удалена отдельным согласованным изменением.

## Решение 2026-08-31 — AI Policy Profiling / Agent Economics Observe layer

| Возможность | Найденное состояние | Потребность | Статус | Канонический источник |
|---|---|---|---|---|
| Stage/status/evidence | governance и Completion Gate уже каноничны | связать outcomes с policy/experiment без второго status | `INHERITED` → `EXTEND` | optional fields/routes в STAGES owner |
| Runtime telemetry | host SQLite/JSONL рядом с `~/.codex` не является versioned API и содержит private runtime state | project-local bounded opt-in events | `CONFLICT` → `PROJECT_ONLY` | ignored `<project>/.metrics/*.jsonl`; не читать host runtime DB/logs |
| Schema/reporting | versioned telemetry schema и aggregator отсутствуют | portable envelope + JSON/Markdown dashboard | `EXTEND` | `schemas/ai-policy-profiling.schema.json` + `tools/ai_policy_profiler.py` |
| Hooks/agents/MCP | existing capabilities не дают стабильный documented usage event contract | не создавать обязательный overhead до evidence | `INHERITED` | без нового hook/agent/MCP; explicit instrumented CLI |
| Storage/dependencies | standard library и append-only files достаточны | bounded concurrent-safe local writes | `INHERITED` | Python stdlib, no SQLite/SaaS/package |
| Policy tuning | human-owned SPEC/decisions задают requirements | Observe/Measure/Compare до изменения thresholds | `INHERITED` | recommendation only; tuning требует отдельного approval |

Новые hooks, agents, Skills, MCP, dependencies, config mutation и external writes не добавляются.
Existing projects без `.metrics/` остаются unchanged; mass rollout отсутствует.

## Решение 2026-08-28 — hardening global router, selector и install path

| Возможность | Найденное состояние | Потребность | Статус | Канонический источник |
|---|---|---|---|---|
| Global `AGENTS.md` | 61 380 bytes, несколько полных policy copies | сохранить critical invariants при меньшем обязательном context | `CONFLICT` → `INHERITED` | thin `AGENTS.md` router → existing `rules/*`, `docs/*`, `dev-karkas` |
| Stage selector | exact hook parser уже работает; overlay validator ссылку не проверяет | fail-visible preflight без semantic Stage parser | `EXTEND` | shared `hooks/stage_selector.py` → hook + `validate_project_overlay.py` |
| Agent models | Sol/high и Luna/medium pins доступны; остальные agents unpinned | задокументировать default inheritance без массового pin churn | `INHERITED` | `agents/*.toml`, `rules/model-routing.md`, `docs/TEAM_ARCHITECTURE.md` |
| Install | PowerShell wrapper; Unix path отсутствует; config protected | одинаковая safe sequence на Windows и Unix-like | `EXTEND` | thin `install-global.ps1` / `install-global.sh` → existing Python tools |
| Greenfield starter | AI plan/status templates и bootstrap Skill есть; thin project AGENTS template отсутствует | минимальная project delta без local agents/Skills | `EXTEND` | `templates/AGENTS_PROJECT_TEMPLATE.md` + existing templates/Skill |
| DEGRADED/handoff/cost | уже описаны в WORKFLOW/VERIFY_SETUP/README/config | дополнить факты, не создавать вторую policy | `INHERITED` | существующие owners |
| CI | отсутствует | Linux syntax/unit consumer gate без runtime mutation | `EXTEND` | `.github/workflows/validate.yml` |
| Hooks/Skills/MCP/config | новые capabilities не нужны; runtime config запрещён к overwrite | сохранить активные границы | `INHERITED` | без новых hook events/Skills/MCP и без `config.toml` mutation |

Shared selector module не добавляет новый hook: он является pure implementation detail
существующего SessionStart/SubagentStart и read-only validator. Project repositories автоматически
не изменяются; новый mandatory selector issue обнаруживается только при явном запуске validator.
Legacy named presets сохраняются в прежнем quarantine и этой задачей не materialize-ятся.

## Решение 2026-08-27 — глобальный i18n/l10n standard

| Возможность | Найденное состояние | Потребность | Статус | Канонический источник |
|---|---|---|---|---|
| Product i18n/l10n | project-specific resources встречаются в отдельных products; общей нормы нет | наследуемая stack-independent архитектурная готовность всех user-facing продуктов | `EXTEND` | `rules/i18n-l10n.md` + `FR-010` / `AC-013` |
| Documentation language vs product locale | русский project context задан глобально, но не отделён от языка продукта | не смешивать authoring language с `language` / `locale` runtime | `CONFLICT` → `EXTEND` | i18n/l10n policy явно разделяет контракты; `AGENTS.md` остаётся владельцем языка контекста |
| Frontend/mobile/desktop/public CLI | domain rules не имеют единого владельца locale invariants | охватить все user-facing surfaces без frontend-only копии | `EXTEND` | один cross-cutting rule; domains/stacks только уточняют реализацию |
| Fallback и stage lifecycle | общие fallback и architecturally complete stage contracts уже существуют | locale fallback и initial i18n slice без второго lifecycle owner | `INHERITED` | `rules/i18n-l10n.md` ссылается на `fallback-policy.md` и governance, не копируя их |
| Project DESIGN/SPEC | проекты могут иметь собственные supported locales и UX | хранить только конкретную delta и acceptance evidence | `INHERITED` | project SPEC/DESIGN/architecture/testing; глобальный список не копируется |
| Automation/runtime | существующих routers и structural tests достаточно | автоматическое наследование без нового service/dependency/write surface | `INHERITED` | `AGENTS.md`, `rules/README.md`, `PROJECT_FRAMEWORK.md`; новый hook/Skill/MCP не добавляется |

Конфликтов с активными Skills, hooks, MCP, config и product repositories не обнаружено. Новая
policy расширяет global rule layer, не меняет runtime projection и не выполняет массовый rollout в
brownfield projects. Project-specific реализации остаются источниками факта текущего поведения,
но не конкурирующими владельцами межпроектного стандарта.

## Решение 2026-09-08 — Continuous Master Execution gap map

| Возможность | Найденное состояние | Потребность | Статус | Канонический owner |
|---|---|---|---|---|
| Current state | `prompts/STAGES.md` уже владеет selector/lifecycle/evidence/NEXT | durable master/track/graph без второго registry | `EXTEND` | selected STAGES record + versioned embedded block |
| Stage readiness | governance задаёт DAG и completion gates, semantic parser отсутствует | deterministic ready/stop transition | `EXTEND` | portable controller + SPEC/governance |
| Worktree isolation | Git policy требует isolation, но route выбирается вручную | continuation reuse и parallel ensure без чужого branch switch | `EXTEND` | guarded Git adapter; Git остаётся source of facts |
| Context | exact selected record уже bounded hook-ом | targeted scope, budget и durable launcher/handoff | `EXTEND` | controller projection внутри current record |
| Evidence | Stage contract и levels существуют prose-only | machine-checked required level/blocker/integration gates | `EXTEND` | controller; governance остаётся policy owner |
| Prompt cleanup | `prompt_queue.py` уже exact-item fail-closed guard | child/master hierarchical eligibility | `INHERITED + EXTEND` | existing queue policy/guard, без второго delete path |
| Model routing | `rules/model-routing.md` уже задаёт capability classes | per-slice metadata без runtime substitution | `INHERITED` | external runtime adapter + existing policy |
| Runtime/config | active config, sessions, credentials вне Git | никаких новых bindings для core contract | `FORBIDDEN_TO_OVERWRITE` | unchanged runtime boundary |

Отдельный scheduler, database, dependency, hook и live global track inventory не требуются.
Controlled evidence использует temporary Git repositories; product repositories этой фазой не
мутируются.

## Решение 2026-08-27 — единый project workflow без второго global layer (SUPERSEDED для DEV root)

| Возможность | Найденное состояние | Потребность | Статус | Канонический источник |
|---|---|---|---|---|
| Global DEV root | prompt предполагал `~/codex-workspace/global/codex`; installer и решения требуют непосредственный `~/.codex` | один переносимый Git-канон без installed-копии | `CONFLICT` → `INHERITED` | `~/.codex`; предполагаемый workspace path отклонён |
| Runtime Skills | `skill-sources/**` materialize в `~/.agents/skills/**` и hash-проверяются | не редактировать runtime вручную | `INHERITED` | source/runtime split не меняется; Skills этой задачей не затронуты |
| Lifecycle-команды | stage/resume Skills и разрозненные workflow sections без полного human command set | восемь copy-ready сценариев | `EXTEND` | `docs/WORKFLOW.md` как operational projection `rules/governance.md` |
| Documentation triggers | Completion Gate существовал без полной event/action table | однозначное условие записи без timestamp churn | `EXTEND` | `rules/governance.md` |
| Learning format | canonical log и template имели разные исторические формы | единые новые entries без переписывания истории | `CONFLICT` → `EXTEND` | governance trigger + `templates/LEARNING_LOG_TEMPLATE.md`; `docs/notes/LEARNING_LOG.md` frozen legacy |
| External services | services объявлены projections, Notion имел intake, остальные не имели owner/sync triggers | owner, direction, pending sync и read-back | `EXTEND` | `rules/governance.md`; connector/automation не добавляются |
| Device handoff | portable paths и clone/pull invariant существовали без исполнимого checklist | computer↔laptop restore без старого чата | `EXTEND` | governance + `docs/CONTEXT_POLICY.md` + operational `docs/WORKFLOW.md` |
| Monitoring classes | global live inventory запрещён, классы отсутствовали | `active` / `event-driven` / `frozen` как project fact | `EXTEND` | `rules/governance.md`; project mapping, не global registry |
| Global validator source argument | legacy `--workspace` можно было ошибочно передать как `~/codex-workspace`; missing source завершался `FileNotFoundError` | fail-visible structured diagnostic | `CONFLICT` → `EXTEND` | `tools/validate_global_codex.py`; option означает canonical source root |
| Legacy named presets | tracked `presets/*` не входят в active router/installer и не имеют доказанного project destination | не считать вторым overlay/framework | `OBSOLETE` / `BLOCKED` quarantine | сохранить без mutation до отдельного mapping/deletion approval |

Новые `AGENTS.md`, hooks, MCP, agents, Skills, dependencies и external write-интеграции не
добавляются. Полная норма остаётся у существующих owners; project overlays получают только ссылки
и свои facts. Текущая задача не materialize-ит uncommitted feature content в active runtime.

## Решение 2026-08-27 — архитектурно завершённые stages

| Возможность | Что уже есть | Потребность | Статус | Канонический источник |
|---|---|---|---|---|
| Stage lifecycle/evidence | Stage contract, completion gate и разрозненные fields в Skills/templates | запрет forward dependency, обязательный runnable slice/E2E/PASS evidence и scaffold-safe statuses | `EXTEND` | `specs/system.spec.md` → `rules/governance.md` |
| Planning/bootstrap/execution | `dev-karkas`, `plan-stage`, `implement-stage`, bootstrap и STAGES template | собрать обязательные fields без копирования policy | `EXTEND` | короткие routes к governance + operational projections |
| Task-aware context routing | SPEC и отдельный plan загружались, detailed stage source мог остаться вне активного context | доставлять контракт без загрузки всего catalog | `CONFLICT` → `EXTEND` | stable `Stage ID` в STAGES → exact unique heading selector существующего SessionStart/SubagentStart hook |
| Tests vs requirements | `TESTING_POLICY.md` называл tests источником требований, SDD — evidence | один source of requirements | `CONFLICT` → `INHERITED` | SPEC/ADR задают требования; accepted tests — executable contract/evidence |
| Project-file baseline | governance требовал полный overlay, references описывали часть baseline как optional | единый applicability threshold | `CONFLICT` → `INHERITED` | governance обязателен для active full staged product overlay; прочие repositories явно классифицируются |
| Architecture/ADR paths | references допускали альтернативные каноны без mapping rule | один source of truth в brownfield | `CONFLICT` → `EXTEND` | `docs/ARCHITECTURE.md` / `docs/DECISIONS.md`; legacy только через compatibility mapping и semantic/link audit |
| UI design applicability | одно правило требовало пустой DESIGN для non-UI, governance делал его conditional | исключить N/A placeholders | `CONFLICT` → `INHERITED` | `DESIGN.md` только при UI surface; отсутствие UI при необходимости фиксируется в architecture/context |
| STAGES semantic parser | structural validator без versioned stage schema | не выдавать headings за runtime evidence и не ломать legacy formats | `INHERITED` | human/agent evidence gate + новый structural policy test; parser отложен до schema/migration |

Новый hook, MCP, agent, dependency или внешняя write-интеграция не добавляются: существующий
read-only SessionStart/SubagentStart hook узко расширен bounded selector и visible degraded path.
Полная policy не копируется в project overlays; runtime Skills materialize только после интеграции
source branch.

## Решение 2026-08-26 — Completion Documentation Synchronization Gate

| Возможность | Что уже есть | Потребность | Статус | Канонический источник |
|---|---|---|---|---|
| Синхронизация завершения | conditional updates в governance и status workflow | обязательный audit README/plan/status/roadmap/stage/evidence без формального churn | `EXTEND` | `rules/governance.md`; `dev-karkas/references/STATUS_WORKFLOW.md` |
| Hooks и внешняя automation | существующие механизмы не отслеживают семантическую актуальность docs | не добавлять недостоверную автоматическую проверку смысла | `INHERITED` | human/agent evidence gate, без нового hook или runtime dependency |

Новых hooks, MCP, agents, dependencies и внешних write-интеграций не требуется. Existing
`dev-karkas` и `implement-stage` расширяются ссылкой на один канонический gate.

## Brownfield Reconciliation Gate

Для каждого brownfield bootstrap/refresh сначала создаётся read-only matrix текущего repository.
Код, проектные документы и baseline-тесты являются source of truth; framework не перезаписывает
их автоматически.

| Статус | Правило mutation |
|---|---|
| `KEEP` | сохранить подтверждённый эквивалент |
| `ADD` | добавить отсутствующий framework artifact |
| `ADAPT` | адаптировать framework artifact к проекту |
| `MERGE` | объединить, сохранив project-specific content |
| `CONFLICT` | до resolution соответствующая mutation заблокирована |
| `SUPERSEDED` | legacy artifact заменяется каноническим источником после решения |
| `FORBIDDEN_TO_OVERWRITE` | автоматическая запись в путь запрещена |

Read-only implementation: `tools/reconcile_project_framework.py`. Baseline failures записываются
отдельно; после refresh новые failures считаются regression.

### Решение 2026-08-25 — Backend Developer Experience Policy

| Возможность | Что уже есть | Потребность | Статус | Канонический источник |
|---|---|---|---|---|
| Dependency/toolchain reproducibility | dependency policy и nested read-only inventory | связать install/toolchain/lockfile с backend command/evidence contract | `INHERITED` | `rules/dependency-management.md`; Backend DX только ссылается |
| Database/API/testing/security/fallback | governance, domain rules и dev-karkas references | объединить их в применимый developer workflow без второго доменного канона | `EXTEND` | `rules/backend-dx.md` с явными ссылками на существующих владельцев |
| Backend audit workflow | generic `dev-karkas` и project validator | classification `BDX-L0..L3`, gap matrix, clean-room evidence | `EXTEND` | `skill-sources/backend-dx-audit/SKILL.md` |
| Project Backend DX facts | `docs/project-context.md` и thin `AGENTS.md` | reusable delta без копирования global policy | `EXTEND` | `templates/BACKEND_DX_DELTA_TEMPLATE.md` → project `docs/project-context.md` |
| Backend DX validation | deterministic read-only overlay validator | opt-in checks с низким false-positive profile | `EXTEND` | `tools/validate_project_overlay.py` и unit fixtures |
| Hooks / task runners / runtime stack | existing extension points либо project tooling | policy не должна создавать второй framework | `INHERITED` | без новых hooks/dependencies; project tooling переиспользуется |

Новая policy остаётся project-agnostic. Product repositories, их ports/endpoints,
credentials и live status этим изменением не модифицируются. Именованные legacy
presets остаются неактивным `BLOCKED` quarantine и не подключаются к Backend DX.

### Решение 2026-08-20 — reconciliation automation

| Возможность | Что уже есть | Потребность | Статус | Канонический источник |
|---|---|---|---|---|
| Brownfield reconciliation | read-only `validate_project_overlay.py` без классификации и baseline comparison | gate до bootstrap/refresh с matrix и regression contract | `EXTEND` | `tools/reconcile_project_framework.py` |
| Project overlay templates | только project-agnostic `templates/*`; именованные project presets запрещены | сохранить существующие project-specific решения | `PROJECT_ONLY` | фактический repository; framework docs/specs добавляются через reconciliation |
| Product code refresh | product repositories являются независимыми Git roots | исключить автоматическую перезапись | `FORBIDDEN_TO_OVERWRITE` | target repository и explicit resolutions |

## Таблица решения

| Возможность | Что уже есть глобально / в workspace | Потребность проекта | Статус | Решение и канонический источник |
|---|---|---|---|---|
| Архитектура | | | | |
| QA / тестирование | | | | |
| Безопасность | | | | |
| Review | | | | |
| Документация | | | | |
| Git workflow | | | | |
| Hooks | | | | |
| MCP | | | | |
| Skills | | | | |
| Доменные agents | | | | |
| Конфигурация Codex | | | | |

## Правила решения конфликтов

- Сначала переиспользуй существующую возможность, затем расширяй её минимальным проектным слоем.
- Не создавай второй глобальный config, второй Git workflow, дубликаты универсальных агентов или одинаковые MCP.
- Локальные hooks и MCP должны закрывать конкретный проектный пробел и иметь минимальные разрешения.
- Укажи владельца общих manifests/docs и проверь конфликты перед параллельной записью.

## Решение 2026-08-13 — общий КАРКАС проектов

| Возможность | Что уже было | Новая потребность | Статус | Решение |
|---|---|---|---|---|
| Терминология КАРКАСА | Project overlay и context policy без общего определения команды | одинаковое значение для всех `projects/*` | `EXTEND` | канонический `docs/PROJECT_FRAMEWORK.md` |
| Context routing | корневой и глобальный `AGENTS.md` | распознавать команды «создай КАРКАС» / «автоматизация контекста» | `EXTEND` | короткие routers; полный текст не копируется |
| Bootstrap workflow | generic planning/implementation Skills | повторяемый inspect → gap → minimal delta процесс | `EXTEND` | общий `bootstrap-project-framework` Skill |
| SessionStart hook | компактный активный context hook | task-aware выбор одного stage record | `EXTEND` | stable STAGES `Stage ID`; exact unique heading; не загружать всю библиотеку docs/prompts |
| Project overlays | локальные overlays | распространить определение | `INHERITED` | не копировать документ/Skill в каждый repository |
| OCR-примеры исходного brief | только Text Recognition Core | общая терминология | `CONFLICT` | оставить в TRC; глобальный документ domain-neutral |
| Язык проектного контекста | единого правила не было, часть agents и документов была на английском | единый читаемый язык новых КАРКАСОВ | `EXTEND` | русский по умолчанию в `AGENTS.md`, `PROJECT_FRAMEWORK.md` и bootstrap Skill; программные идентификаторы и внешние контракты не переводятся |

Новые hook, MCP, config и subagents не созданы. Skill валидируется штатным `quick_validate.py` и прошёл read-only forward-test на независимом document-converter сценарии.

## Решение 2026-08-13 — проверка project overlay

| Возможность | Что уже было | Новая потребность | Статус | Решение |
|---|---|---|---|---|
| Workspace validation | `tools/validate_context.py` проверяет manifest общей инфраструктуры | проверить один независимый project repository | `EXTEND` | отдельный read-only `tools/validate_project_overlay.py` |
| Rollout inventory | тематический список проектов | историческая очередь rollout этапа 1 | `OBSOLETE` | superseded 2026-08-20: ДЕВ не хранит live inventory product repositories |
| Agents / Skills / hooks / rules / workflow | канонические источники в workspace/global | не допустить точных локальных копий | `INHERITED` | SHA-256 comparison; найденные копии только диагностируются |
| Project-local automation | могла существовать без единого gate | требовать явное решение о локальной delta | `EXTEND` | при наличии automation обязателен `docs/CONTEXT_COMPATIBILITY.md` проекта |
| Fallback Policy | отдельных согласованных правил деградации не было | единый общий контракт retry/fallback/degraded/fail-closed | `EXTEND` | канонический источник — `rules/fallback-policy.md`; проекты наследуют его и хранят только предметную delta |

Новые hook, MCP, config, generic agents и workflow не добавлены. Validator использует только Python standard library и Git, не выполняет project-код и не изменяет проверяемый repository.

Live inventory product repositories больше не является capability ДЕВ.
Универсальный read-only `tools/validate_project_overlay.py` остаётся активным и
принимает один явно выбранный repository. Fallback Policy остаётся общим
каноническим источником, а `docs/FALLBACKS.md` в product repository — только
project-specific delta.

Текущий installed router находится в `~/.codex/AGENTS.md`, versioned Skill source — в
`<dev-root>/skill-sources/bootstrap-project-framework`, а
`~/.agents/skills/bootstrap-project-framework` является только hash-verified runtime projection.
Проекты наследуют router/Skill и не копируют их локально.

## Решение 2026-08-20 — нормализация глобального runtime-слоя

| Возможность | Найденное состояние | Статус | Решение и канонический источник |
|---|---|---|---|
| Global AGENTS / agents / hooks / rules | 18 installed-файлов разошлись с прежним source tree | `CONFLICT` → `INHERITED` | полезная model routing delta перенесена в канон; схема superseded консолидацией 2026-08-23 |
| Session context hook | installed-версия падала на cp1251; canonical читал полный файл и следовал внешним symlink | `CONFLICT` → `EXTEND` | UTF-8 output, repository containment и bounded read в `~/.codex/hooks/session_context.py` |
| Context7 | credential в process args, unpinned package | `CONFLICT` → `INHERITED` | no-key запуск, reviewed pin `4.0.2`; ротация старого credential остаётся внешним действием |
| GitHub | plugin и authenticated static MCP работали параллельно | `CONFLICT` | plugin — primary, static MCP — disabled fallback; permission mode требует выбора владельца |
| Atlassian | standalone MCP задан, но runtime route не подтверждён | `CONFLICT` | definition сохранён с `enabled = false` |
| Google Calendar / Slack | config помечал enabled, Plugin Management подтвердил отсутствие установки | `OBSOLETE` | inert blocks сохранены выключенными, cache вручную не удаляется |
| Browser trusted service | ссылка на отсутствующий `browser-service.mjs` и один неподтверждённый client hash | `CONFLICT` | broken browser mapping и unmatched hash удалены; `sky` не изменён; host repair проверяется после restart |
| Project trust | broad home, три неверных имени и три non-project roots | `CONFLICT` | broad/non-project trust удалён, имена заменены на существующие Git roots |
| Shell environment | spawned commands наследовали `*_TOKEN` | `CONFLICT` | `ignore_default_excludes = false`; проверка фактического нового shell после restart |
| Recommendation files | устаревший AGENTS staging и актуальный config proposal | `OBSOLETE` / `EXTEND` | obsolete AGENTS staging удалён после hash-check; config recommendation сохранён как неактивный proposal |

## Решение 2026-08-23 — консолидация ДЕВ в `~/.codex` (SUPERSEDED 2026-09-10)

| Возможность | Найденное состояние | Статус | Решение и канонический источник |
|---|---|---|---|
| Global router | active и прежний workspace router задавали пересекающиеся правила | `CONFLICT` → `INHERITED` | один объединённый `~/.codex/AGENTS.md` |
| Agents / hooks / rules | source и installed trees дублировались | `CONFLICT` → `INHERITED` | непосредственные `~/.codex/{agents,hooks,rules}` |
| Skills ДЕВ | source и runtime были одновременно discoverable | `CONFLICT` → `EXTEND` | versioned `~/.codex/skill-sources/<skill>` + hash-verified runtime `~/.agents/skills/<skill>` |
| Product repositories | независимые Git roots под `~/codex-workspace` | `KEEP` | оставить на месте; менять только ссылки на global context |
| Project-specific automation | локальные `.codex` / `.agents` в отдельных repositories | `EXTEND` / `PROJECT_ONLY` | сохранить без перезаписи |
| Runtime state Codex | secrets, auth, sessions, SQLite, cache и plugins находятся рядом с ДЕВ | `FORBIDDEN_TO_OVERWRITE` | deny-by-default `.gitignore`, versioned allowlist только для файлов ДЕВ |
