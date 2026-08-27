# Аудит совместимости контекста

Используй этот шаблон перед добавлением или существенным изменением agent, hook, MCP, Skill, rules или конфигурации.

## Статусы

- `INHERITED` — возможность уже предоставляет глобальный или workspace-уровень; локальная копия не нужна.
- `EXTEND` — общая возможность подходит, но проект добавляет узкое правило или адаптер.
- `PROJECT_ONLY` — возможность относится только к одному проекту и хранится в нём.
- `CONFLICT` — определения дублируются или задают несовместимое поведение; выбери один канонический источник.
- `OBSOLETE` — возможность больше не используется и должна быть удалена отдельным согласованным изменением.

## Решение 2026-08-27 — архитектурно завершённые stages

| Возможность | Что уже есть | Потребность | Статус | Канонический источник |
|---|---|---|---|---|
| Stage lifecycle/evidence | Stage contract, completion gate и разрозненные fields в Skills/templates | запрет forward dependency, обязательный runnable slice/E2E/PASS evidence и scaffold-safe statuses | `EXTEND` | `specs/system.spec.md` → `rules/governance.md` |
| Planning/bootstrap/execution | `dev-karkas`, `plan-stage`, `implement-stage`, bootstrap и AI templates | собрать обязательные fields без копирования policy | `EXTEND` | короткие routes к governance + operational projections |
| Task-aware context routing | SPEC и AI_PLAN загружались, detailed stage source мог остаться вне активного context | доставлять контракт без загрузки всего catalog | `CONFLICT` → `EXTEND` | stable `Stage ID` в AI_PLAN → exact unique heading selector существующего SessionStart/SubagentStart hook |
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
| SessionStart hook | компактный активный context hook | task-aware выбор одного stage record | `EXTEND` | stable AI_PLAN `Stage ID`; exact unique heading; не загружать всю библиотеку docs/prompts |
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

Историческое решение о каноническом runtime Skill superseded 2026-08-24: `~/.codex/AGENTS.md`
остаётся каноническим router, versioned Skill source находится в
`~/.codex/skill-sources/bootstrap-project-framework`, а
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

## Решение 2026-08-23 — консолидация ДЕВ в `~/.codex`

| Возможность | Найденное состояние | Статус | Решение и канонический источник |
|---|---|---|---|
| Global router | active и прежний workspace router задавали пересекающиеся правила | `CONFLICT` → `INHERITED` | один объединённый `~/.codex/AGENTS.md` |
| Agents / hooks / rules | source и installed trees дублировались | `CONFLICT` → `INHERITED` | непосредственные `~/.codex/{agents,hooks,rules}` |
| Skills ДЕВ | source и runtime были одновременно discoverable | `CONFLICT` → `EXTEND` | versioned `~/.codex/skill-sources/<skill>` + hash-verified runtime `~/.agents/skills/<skill>` |
| Product repositories | независимые Git roots под `~/codex-workspace` | `KEEP` | оставить на месте; менять только ссылки на global context |
| Project-specific automation | локальные `.codex` / `.agents` в отдельных repositories | `EXTEND` / `PROJECT_ONLY` | сохранить без перезаписи |
| Runtime state Codex | secrets, auth, sessions, SQLite, cache и plugins находятся рядом с ДЕВ | `FORBIDDEN_TO_OVERWRITE` | deny-by-default `.gitignore`, versioned allowlist только для файлов ДЕВ |
