# Существенные решения

## 2026-09-15 — Global action observation is explicit and source-separated

For `DEV-GAJ-001`, use a versioned, sanitized opt-in local journal and a read-only
exact-path Script Registry. Existing `spec_execution.py` remains the promotion/placement
decision owner; selected STAGES remains execution state; `ai_policy_profiler.py`
remains project-policy telemetry. This avoids a mandatory host hook or second task manager
before a documented safe event contract and real repeat evidence exist. Event and registry
format changes fail closed until an explicit migration. Source implementation and factual
compatibility evidence: `specs/features/global-action-journal.spec.md` and
`docs/notes/GLOBAL_AI_CONTEXT_AUDIT.md`.

## 2026-09-13 — Replaceability contract имеет одного global owner

**Контекст:** vendor SDK и provider-specific DTO могут незаметно связать domain/application/UI с
payments, identity, RTC, storage, AI и document backends. Универсальная обёртка вокруг каждого
класса, напротив, создаёт YAGNI и ложную заменяемость.

**Решение:** полный наследуемый контракт хранится в `rules/replaceable-modules.md`. Global router,
dev-karkas и project framework только маршрутизируют к нему; product repositories владеют своими
ports/adapters, исключениями и evidence. Автоматический generic regex-lint отклонён: project AST/
dependency tools предпочтительнее, а structural global test проверяет только delivery contract.

**Последствия:** provider change и durable migration остаются отдельными approval-gated slices.
P0 finding исправляется безопасным retrofit или получает точный blocker; score без file/test
evidence не считается audit result.

## 2026-09-11 — Specification pipeline расширяет CME одним pure router core

**Контекст:** approved master требует stage-first context, capability/Skill routing, traceability и
automation promotion. Existing CME уже владеет graph/evidence/context/worktree decisions; selector
и compatibility adapter владеют live stage; Prompt Queue и profiler имеют отдельные bounded roles.
Новый state store, scheduler или hook service дублировал бы эти owners.

**Решение:** сохранить CME/controller и selected `prompts/STAGES.md` без второго execution owner.
Добавить один stdlib-only pure core `tools/spec_execution.py`, который принимает bounded structured
facts и выдаёт intake/route/trace/promotion/placement/retirement decisions без side effects.
Skill routing metadata хранить в source-only `skill-sources/registry.toml`; полная procedure остаётся
в соответствующем `SKILL.md`, runtime projection — у existing Skill sync. Project/domain metadata
допустима только как delta. Promotion остаётся recommendation/state transition и не авторизует write.

**Альтернативы:** отдельный workflow engine/state database, RAG/vector Skill search, ML intake
classifier, background watcher, новый telemetry store, automatic Skill deletion и automatic policy
tuning отклонены как дублирование, недетерминированность или преждевременная сложность.

**Последствия:** existing v1 CME и ordinary stages остаются compatible. Context pruning никогда не
удаляет global invariants или selected stage. Ambiguity/conflict/missing evidence fail closed;
retirement сначала проходит reference/replacement/parity preflight и требует отдельной обычной
code-change authorization. Prompt Queue lifecycle и Notion master retention `keep` не меняются.

## 2026-09-08 — Brownfield state adapter остаётся внутри CME

**Контекст:** canonical STAGES policy намеренно отклоняет competing AI_PLAN/AI_STATUS, однако
brownfield repositories не могут безопасно перейти к same-file selector без предварительного
сопоставления current stage/status/blockers/evidence. Повторное эвристическое чтение нескольких
файлов на каждом запуске создало бы nondeterministic shadow router.

**Решение:** добавить bounded read-only compatibility adapter и dry-run plan как mode existing
master_execution CLI. До migration legacy route всегда migration_required. Завершённая migration
фиксируется stage-compatibility block внутри selected STAGES record с normalized projection и
digests retained legacy sources; digest/selector drift fail closed. Первый slice не имеет apply
mode и не изменяет product repositories.

**Альтернативы:** разрешить hook угадывать legacy state отклонено; автоматически удалить legacy
files отклонено из-за риска потери unique content; отдельный registry/service отклонён как второй
orchestration framework.

**Последствия:** pure canonical route остаётся прежним. Legacy/mixed state получает reproducible
plan и explicit review boundary. После Slice C default router, validator и SessionStart используют
один inspector: только canonical validation разрешает execution; migration/conflict/no-state
остаются typed non-ready outcomes. Hook остаётся exit-0 advisory, но не загружает guessed stage.
Safe handoff содержит fixed data-only argv template; apply требует separately persisted reviewed
plan и independently approved digest. Product rollout и legacy retirement остаются отдельно
разрешаемыми работами.

## 2026-09-08 — Materialization требует externally approved digest и read-back transaction

**Контекст:** dry-run plan должен стать исполнимым без повторной эвристической интерпретации legacy
files. Проверки только Git HEAD или embedded digest не защищают от source drift и подмены plan с
пересчитанным digest; последовательные writes без rollback могут оставить partial state.

**Решение:** materializer принимает plan file и отдельно подтверждённый full `plan_digest`, под
exclusive repository lock повторно сверяет identity и byte-digests всех известных state paths,
готовит sibling temporary file с fsync, атомарно заменяет только allow-listed
`prompts/STAGES.md`, затем проверяет exact intended selector/projection существующим router-ом.
Ошибка publish/read-back восстанавливает pre-image. Unknown leftover lock требует manual recovery;
legacy `AI_PLAN`/`AI_STATUS` остаются retained и никогда не входят в Slice B write-set.

**Альтернативы:** Git HEAD-only CAS, доверие embedded digest без external approval, in-place write,
автоматическое удаление stale lock и общий multi-product transaction framework отклонены как
недостаточно fail-closed либо преждевременно широкие.

**Последствия:** repeated exact apply возвращает `already_materialized`; drift/tampering/path escape
не выполняют publish; rollback failure имеет отдельный typed outcome. Полная защита от враждебного
same-user junction race на Windows остаётся residual platform risk.

## 2026-09-08 — Continuous master расширяет Stage contract, а не создаёт scheduler

**Контекст:** один явно запущенный master должен проходить однозначные slices без ручной диспетчеризации,
при этом `prompts/STAGES.md` уже владеет execution state, governance — Stage/evidence contract,
`prompt_queue.py` — cleanup guard, а Git worktree является существующим isolation primitive.

**Решение:** versioned `master-execution` block живёт внутри selected STAGES record. Один stdlib-only
controller валидирует graph, readiness/stop/evidence/context transitions и вызывает отдельный
guarded Git adapter только для explicit worktree ensure operation. Prompt store, model runtime и
evidence остаются adapter facts; произвольные commands из prompt/state не исполняются. Existing
Prompt Queue Lifecycle остаётся единственным cleanup owner. Integration checkpoint выдаёт решение,
но не выполняет merge/push/release.

**Альтернативы:** отдельные `MASTER_STATUS.json`/track registry отклонены как competing state;
background daemon/scheduler — как непереносимый и избыточный; instruction-only workflow — потому
что не проверяет dependency/evidence/recovery deterministically; новый worktree на каждый slice —
потому что ломает continuation и создаёт cleanup churn.

**Последствия:** ordinary non-master stage не меняется. Master получает bounded schema и executable
consumer path. Context hook по-прежнему проецирует только selected record; overflow создаёт durable
handoff/launcher, а не silent truncation. Product rollout остаётся отдельным controlled stage.

## 2026-09-08 — Один STAGES.md владеет execution state

**Статус:** принято пользователем; реализовано и validated locally в
`feature/canonical-stages-policy`, без commit/merge/push.

**Решение:** active full staged overlay использует `prompts/STAGES.md` одновременно как current
selector, detailed stage catalog, current plan, lifecycle/evidence, blockers и NEXT. Отдельные
AI plan/status documents выводятся из новых templates и validators. Brownfield reconciler только
классифицирует legacy files как `MERGE`; semantic merge, link audit и PASS validator обязательны
до их удаления.

**Причина:** разделение plan/status/catalog создавало drift и противоречивые next-step claims.
Один record рядом с acceptance/evidence делает состояние readable человеком и машиной без второго
источника истины.

**Альтернативы:** сохранить пару AI plan/status отклонено прямым requirement; автоматически
переписывать и удалять legacy files отклонено из-за риска потери brownfield content; root
`STAGES.md` вместо существующего переносимого `prompts/STAGES.md` отклонён как ненужный path churn.

**Последствия:** selector parser читает один файл; greenfield получает один STAGES template;
product repositories мигрируются отдельно через read-only reconciliation. SPEC, ROADMAP,
architecture, decisions, learning и Git сохраняют собственные роли.

## Prompt queue guard — принято 2026-09-07

Добавлен отдельный bounded pure guard в existing tools surface. Stage/evidence owners остаются
прежними; profiler JSONL не используется как proof DoD. Global policy имеет одного owner
`rules/prompt-queue-lifecycle.md`; projects наследуют routing и могут добавлять checks.
Writes остаются за существующим adapter с exact-target/read-back. Новый SDK, hook, service,
filesystem deleter и shadow task manager не нужны.


## 2026-08-28 — Thin global router, shared Stage selector и platform wrappers

**Статус:** принято в feature branch; merge не выполнялся.

**Контекст:** global `AGENTS.md` вырос до 61 380 bytes и повторял governance, SDD, test, Notion и
model policies. Session hook уже имел безопасный exact Stage selector, но full overlay validator не
мог выявить broken selector до старта сессии. Install/Skill materialization был документирован
только для PowerShell. Agent audit дополнительно требовал отличить неизвестные pins от реально
доступных `gpt-5.6-sol` / `luna` и default inheritance.

**Решение:** оставить `AGENTS.md` router меньше 32 KiB; полные norms остаются у существующих
owners. Pure parser `hooks/stage_selector.py` используется hook и validator, а semantic Stage
contract остаётся human/agent gate. `install-global.ps1` и `install-global.sh` являются thin
wrappers одинаковой последовательности Python tools и не меняют `config.toml`. Большинство agents
наследует active/default model; explicit pins остаются только у reviewed architecture/security/test
roles. CI выполняет read-only context/tests/syntax checks и не materialize-ит runtime.

**Альтернативы:** второй parser в `tools/` отклонён из-за drift; новый global `prompts/STAGES.md` —
потому что infrastructure repository не является full project overlay; удаление `gpt-5.6-sol`
только по примеру prompt — потому что model доступна в текущей среде; общий Python installer с
перезаписью config — из-за platform UX и protected runtime state.

**Последствия:** full overlays без selector теперь fail visibly и требуют remediation. Existing
hook limits/no-selector template behavior сохраняются regression tests. Unix installer требует
actual Unix-like evidence до terminal completion; CI syntax PASS не заменяет этот gate. Runtime
Skill drift шести sources, обнаруженный baseline audit, должен быть устранён approved sync либо
оставаться явным blocker в state docs.

## 2026-08-27 — Один глобальный i18n/l10n contract и thin project delta

**Статус:** принято.

**Контекст:** отдельные product repositories уже могут иметь собственные translation resources,
но глобальный ДЕВ не задавал общей границы между `i18n`, `l10n`, documentation language и product
locale. Размещение полного правила в каждом `DESIGN.md`, frontend domain rule либо project
`AGENTS.md` создало бы расходящиеся копии и не охватило бы public CLI, отчёты и другие
user-facing surfaces. Перенос полного списка в `rules/governance.md` заставил бы загружать общий
lifecycle contract для каждой locale-задачи.

**Решение:** единственный предметный владелец — `rules/i18n-l10n.md`; стабильное системное
требование — `specs/system.spec.md` (`FR-010` / `AC-013`). `AGENTS.md`, `rules/README.md` и
`docs/PROJECT_FRAMEWORK.md` являются только routers, а project SPEC, DESIGN, architecture и testing
хранят поддерживаемые locales, stack, исключения и evidence. Initial product slice может иметь
одну production locale, но обязан содержать реальный resource/fallback path и pseudo-locale либо
alternate test locale, чтобы будущий stage расширял l10n content, а не впервые разблокировал i18n.

**Альтернативы:** полный контракт в `rules/governance.md`, только в
`rules/domains/frontend.md`, новый Skill/hook и копирование checklist в каждый project overlay
отклонены. Governance остаётся владельцем lifecycle/evidence, Fallback Policy — retry/degraded
semantics, а product localization policy ссылается на них без дублирования.

**Последствия:** все новые user-facing architectures получают общий standard независимо от
стека; brownfield проекты проходят gap audit без автоматической массовой замены строк. Язык
проектной документации не считается product locale. Новые runtime services, dependencies,
hooks, MCP и Skills не добавляются; product repositories этим решением не модифицируются.

## 2026-08-27 — Один global root и один операционный project workflow

**Статус:** SUPERSEDED для DEV placement решением 2026-09-10; workflow ownership сохраняется.

**Контекст:** новый workflow brief предполагал отдельный source
`~/codex-workspace/global/codex` и installed runtime в `~/.codex`. Фактическая архитектура уже
консолидирована: `~/.codex` является Git-корнем и direct operational layer, а только Skills имеют
managed projection в `~/.agents/skills`. Создание предполагаемого root восстановило бы два
глобальных lifecycle и конфликтующие `AGENTS.md`. Одновременно lifecycle-команды, external sync,
device handoff, documentation triggers и monitoring были распределены по существующим policies без
одной human-readable operational projection.

**Решение:** сохранить `~/.codex` единственным global source/operational root. Полный policy owner
для source responsibility, docs/learning triggers, external projections, device restore и
monitoring — `rules/governance.md`; system requirements — `specs/system.spec.md`; copy-ready
формулировки — существующий `docs/WORKFLOW.md`; context loading — `docs/CONTEXT_POLICY.md`.
Projects наследуют правило и не копируют его. Skills/hooks/MCP/runtime не расширяются, потому что
для workflow достаточно существующих routes.

**Альтернативы:** отдельный `~/codex-workspace/global/codex`, новый workspace `AGENTS.md`, новый
prompt catalog и автоматическая синхронизация всех external services отклонены как конкурирующие
sources и необоснованные write surfaces.

**Последствия:** cross-device restore использует два независимых Git lifecycle — global DEV и
выбранный product repository. External service без approval/read-back остаётся `pending sync`.
Legacy `presets/*` остаётся неактивным `BLOCKED` quarantine до отдельного mapping/deletion решения.
Global validator обязан fail visibly при неверном source root. Uncommitted feature branch не
materialize-ится в active runtime до разрешённой интеграции.

## 2026-08-27 — Один канонический контракт архитектурно завершённых этапов

**Статус:** принято.

**Контекст:** прежние stage surfaces требовали dependencies, acceptance и tests, но позволяли
прочитать заблокированный gate как допустимый для `DONE`, не отделяли scaffold от production
evidence и не запрещали forward dependency на будущую обязательную инфраструктуру. Дополнительно
`TESTING_POLICY.md` называл tests источником требований, а project-file references расходились в
порогах полного staged overlay. Detailed stage source также отсутствовал в минимальном
task-aware context route между SPEC и current stage contract.

**Решение:** стабильное требование принадлежит `specs/system.spec.md` (`FR-007`/`AC-007`), а
единственный полный lifecycle/evidence contract — `rules/governance.md`. Planning/execution Skills,
`dev-karkas`, templates и workflow содержат только ссылки и поля проекции. Полный project overlay
имеет единый baseline из governance; UI `DESIGN.md` остаётся условным. Tests являются исполняемым
контрактом принятого поведения и evidence, но не первичным source of requirements. Stage-bound
задача задаёт stable `Stage ID` в `prompts/STAGES.md`; существующий SessionStart/SubagentStart hook
проецирует только один exact unique heading record из этого же файла, а не весь catalog.

**Альтернативы:** копирование полной нормы во все Skills отклонено из-за drift; эвристический parser
произвольных `prompts/STAGES.md` отклонён до появления versioned schema/migration, чтобы не создать
false positives и несовместимость существующих project overlays. Exact heading selector принят как
узкая context projection: он не интерпретирует DAG, prerequisites, PASS criteria или evidence.

**Последствия:** future stage не может задним числом завершить primary path предыдущего stage;
mock/stub-only результат остаётся `scaffolded`; structural global test защищает маршрутизацию,
production hook test подтверждает путь `STAGES selector → selected STAGES record`, а фактический
end-to-end PASS stage по-прежнему подтверждается project evidence и review. Invalid, missing,
ambiguous или oversized selector даёт видимый `DEGRADED` context и запрещает completion claim.

## 2026-08-26 — Обязательный documentation audit без формального churn

- Решение: перед завершением task/stage и после merge всегда выполнять Completion
  Documentation Synchronization Gate для `README`, `prompts/STAGES.md`, `ROADMAP`
  и других state-bearing документов.
- Причина: условное «обновить документацию при необходимости» не выявляло stale plan/status,
  старое verification evidence и возможности README, уже не совпадающие с кодом.
- Альтернатива: обновлять все документы и даты после каждой задачи; отклонена, потому что
  создаёт шум и скрывает содержательные изменения.
- Последствия: аудит обязателен, mutation зависит от фактов; после merge gate повторяется по
  target branch, а handoff различает обновлённые и проверенные без изменений документы.

## 2026-08-25 — Один канонический Backend DX contract с opt-in validation

- Решение: полный Backend Developer Experience contract хранится только в
  `rules/backend-dx.md`; `AGENTS.md` и framework docs содержат routing, Skill —
  процедуру, project `docs/project-context.md` — только delta.
- Applicability: `BDX-L0..L3` определяется фактической архитектурой. Validator не
  угадывает backend по Python/Node manifests и включается только при явном
  `## Backend DX Delta`.
- Автоматизация: расширяется существующий read-only project validator; новый hook,
  task runner, runtime dependency и devops/platform role не создаются.
- Причина: policy должна выявлять hidden setup, unsafe reset, stale config/docs и
  CI drift без создания второго framework или false positives для non-backend
  проектов.
- Последствия: reusable template хранится в `templates/`, runtime Skill синхронизируется
  штатным source/runtime flow, а fixture evidence доказывает только framework
  contract и не считается production clean-room evidence конкретного backend.

## 2026-08-20 — Brownfield Reconciliation Gate

- Решение: перед bootstrap/refresh классифицировать repository и для brownfield выполнять отдельный read-only reconciliation.
- Причина: фактическая реализация и результаты baseline-тестов должны сохраняться source of truth; шаблон не должен молча перезаписывать продуктовые решения.
- Статусы matrix: `KEEP`, `ADD`, `ADAPT`, `MERGE`, `CONFLICT`, `SUPERSEDED`, `FORBIDDEN_TO_OVERWRITE`.
- Последствие: unresolved `CONFLICT` блокирует mutation, а `FORBIDDEN_TO_OVERWRITE` запрещает автоматическую запись. После refresh новые baseline failures считаются regression.

## 2026-08-13 — Project overlay вместо копии AI Dev Team

- Решение: project хранит только локальные требования, документы и подтверждённые расширения.
- Причина: исключить drift и конфликт глобальных agents, Skills, hooks, rules и workflow.
- Альтернатива: копировать общий набор в каждый repository; отклонена из-за дублирования.
- Последствие: точная копия глобальной capability является ошибкой validator.

## 2026-08-13 — Один Markdown-каталог rollout

**Статус:** superseded 2026-08-20.

- Решение: использовать только `docs/PROJECT_CATALOG.md`.
- Причина: человеку нужен один источник lifecycle, blockers и следующего действия.
- Альтернатива: дополнительный JSON/YAML registry; отклонена как второй источник истины.

## 2026-08-13 — Read-only validator

- Решение: validator принимает путь одного repository, ничего не исправляет и поддерживает human/JSON output.
- Причина: проверка должна быть повторяемой и безопасной для независимых рабочих копий.
- Последствие: неполный или спорный repository получает issue; изменение выполняется отдельным этапом.

## 2026-08-20 — Один канонический контракт Fallback Policy

- Решение: общий контракт retry/fallback/degraded/fail-closed хранится только в `rules/fallback-policy.md`.
- Причина: fallback-правила не должны расходиться между agents, Skills, security docs и проектами.
- Проекты наследуют общий контракт и при необходимости создают только `docs/FALLBACKS.md` с предметной delta.
- `SECURITY.md` остаётся владельцем security invariants, `DECISIONS.md` — причин решений, `ARCHITECTURE.md` — границ и recovery interfaces.
- Silent fallback и fallback, ослабляющий security или evidence, запрещены.

## 2026-08-20 — ДЕВ не владеет live-статусом product repositories

**Статус:** принято.

**Решение:** AI Dev Team хранит общие инженерные правила, policies, validators,
project framework и reusable automation, но не хранит канонический live inventory
этапов, blockers или очереди отдельных product repositories.

Состояние конкретного продукта принадлежит его собственному `prompts/STAGES.md`,
`ROADMAP` и другим project-specific каноническим источникам.

`validate_project_overlay.py` остаётся универсальным read-only инструментом,
который запускается для явно выбранного repository, но ДЕВ не обязан хранить
глобальную очередь таких repositories.

**Причина:** жизненный цикл общей инженерной инфраструктуры не должен зависеть
от состояния её потребителей.

**Последствия:**

- `docs/PROJECT_CATALOG.md` удаляется;
- blockers конкретных продуктов не входят в global `prompts/STAGES.md` ДЕВ;
- product repository не становится следующим этапом ДЕВ;
- исторический pilot/forward-test может оставаться evidence в истории решений,
  если он действительно происходил;
- общие project-overlay rules и validator сохраняются.

## 2026-08-20 — Канон и runtime глобальной конфигурации разделены

**Статус:** superseded 2026-08-23 консолидацией в `~/.codex`.

**Решение:** прежний workspace source tree оставался единственным versioned source-of-truth для managed AGENTS, agents, hooks и rules. `~/.codex/config.toml` оставался runtime-specific и менялся только ограниченным идемпотентным normalizer; installer не перезаписывал его целиком.

**Причина:** слепая синхронизация теряла полезные local deltas, а полное сохранение installed-файлов закрепляло drift, Unicode defect и небезопасные настройки.

**Последствия:**

- reviewed model pins и routing сначала попадают в канон;
- `-SyncManaged` является явным режимом синхронизации;
- plugin имеет приоритет над дублирующим static MCP;
- inline secrets и broad trust являются validation errors;
- host-managed browser paths/hashes не угадываются;
- внешняя ротация credential и интерактивный trust hooks не автоматизируются.

## 2026-08-23 — `~/.codex` является Git-корнем и единственным каноном ДЕВ

**Статус:** SUPERSEDED 2026-09-10 решением об отдельном canonical source repository и installed layer.

**Решение:** перенести versioned AI Dev Team в `~/.codex` и использовать
`AGENTS.md`, `agents/`, `hooks/`, `skills/` и `rules/` непосредственно из активного
пользовательского слоя Codex. Product repositories остаются независимыми Git roots
в `~/codex-workspace/*`.

**Причина:** прежняя схема «канон в `~/codex-workspace` → installed-копия в
`~/.codex` / `~/.agents`» создавала drift и два конфликтующих `AGENTS.md`.

**Альтернативы:**

- оставить installer и две копии — отклонено из-за повторного drift;
- поместить repository в `~/.codex/dev` — отклонено, потому что глобальный
  `AGENTS.md`, hooks и agents снова оказались бы вне Git root либо потребовали бы копирования.

**Последствия:**

- runtime state, secrets, sessions, plugins, cache и `config.toml` исключены из Git;
- engineering Markdown rules сосуществуют с runtime `.rules` в `~/.codex/rules`;
- project overlays ссылаются на `~/.codex`, но не копируют глобальную automation;
- `install-global.ps1` стал проверкой canonical placement, а не copy/sync installer;
- откат versioned части выполняется Git, runtime state не затрагивается.

## 2026-08-24 — Skills разделены на versioned source и runtime projection

**Статус:** принято; supersedes часть решения 2026-08-23 о непосредственном использовании `~/.codex/skills` для Skills ДЕВ.

**Решение:** versioned source reusable Skills хранится в `~/.codex/skill-sources`. Единственная active runtime-проекция ДЕВ находится в `~/.agents/skills`. `tools/sync_global_skills.py` сравнивает file set/SHA-256, не удаляет unmanaged Skills и перед заменой drifted runtime Skill переносит прежнюю копию в `~/.agents/.migration-backup`.

**Причина:** Codex использует `.codex/skills` и `.agents/skills` как discovery roots, поэтому одинаковые Skills обнаруживались дважды. При этом source должен оставаться в Git для cross-device восстановления.

**Альтернативы:** отдельный Git repository `.agents` отклонён из-за отсутствия отдельного remote и появления второго lifecycle; junction отклонён из-за двойного discovery и неясной Git-portability на Windows.

**Последствия:** host-managed `.codex/skills/.system` и unmanaged Skills не затрагиваются; после clone выполняется `install-global.ps1`; runtime drift является validation error.

## 2026-08-24 — workspace flatten и единый project governance contract

**Статус:** принято.

**Решение:** product repositories располагаются непосредственно в `~/codex-workspace/<project>`, canonical stage source — `prompts/STAGES.md`, а общие lifecycle/evidence/database/security/tooling policies находятся в `rules/governance.md`.

**Причина:** промежуточный `projects/`, смешанные prompt formats и неполные project state contracts создавали path coupling и затрудняли восстановление новой сессии.

**Последствия:** physical moves проверяются по одному repository; dirty/merge state сохраняется backup refs; legacy stage files удаляются только после semantic content/link audit; внешние projections остаются derived.

## 2026-08-24 — Дополнительные Markdown-файлы изолируются в `docs/notes`

**Статус:** принято.

**Решение:** непосредственно в `docs/` создаются только обязательные и условные канонические документы КАРКАСА. Новый долговечный Markdown без собственной канонической роли хранится в `docs/notes/<topic>.md`; временный scratch и одноразовые audit outputs не коммитятся.

**Причина:** произвольные документы на верхнем уровне `docs/` размывают источник истины и увеличивают контекстный шум.

**Последствия:** сначала обновляется существующий canonical source; правило применяется forward-only; legacy files переносятся только после semantic/link audit без потери содержания.

## 2026-08-31 — AI policy profiling запускается opt-in и passive-first

**Статус:** принято для `DEV-AI-PROFILING-001`.

**Решение:** добавить один standard-library CLI/core, versioned JSON Schema и project-local
ignored `.metrics/*.jsonl`. Использовать существующие SPEC/governance/Stage/status owners и
добавить только optional policy/experiment linkage. Не добавлять hook, MCP, agent, database,
network backend или automatic policy mutation.

**Причина:** доступные wall/Git/subprocess facts можно собирать дёшево и детерминированно, но host
token usage и human active time доступны не всегда. Обязательный global hook создал бы overhead,
privacy risk и ложную точность для всех задач до подтверждения ROI самого profiler-а.

**Альтернативы:** SQLite отклонён как избыточный и конфликтующий с runtime databases рядом с
`~/.codex`; web dashboard/SaaS отложен из-за deployment/privacy cost; ручной длинный self-report
отклонён как profiler overhead; self-tuning запрещён до данных и отдельного approval.

**Последствия:** existing projects остаются backward-compatible; explicit `init` включает
observation. Corrupt telemetry fail closed. Markdown/JSON report является достаточным dashboard
Observe-фазы. Threshold tuning остаётся human-approved future scope.

## 2026-09-10 — DEV source и installed Codex home являются разными слоями

**Статус:** принято; supersedes решение 2026-08-23 о `~/.codex` как Git-корне и уточняет
Skill-source paths решения 2026-08-24.

**Решение:** canonical Git-managed DEV source находится в `~/codex-workspace/codex-dev` или другом
отдельном пользовательском path. `~/.codex` является только installed active Codex home layer и
runtime home, не Git working tree. Существующие wrappers используют один Python engine,
`MANIFEST.txt` как explicit file allowlist и deterministic ownership ledger. `skill-sources/`
остаётся в source и materialize-ится в `~/.agents/skills` существующим sync tool.

**Причина:** совмещение Git worktree с credentials, sessions, caches, plugins, SQLite и другим
runtime state делало source lifecycle зависимым от host state и создавало риск destructive Git
operations. Отдельный source clone обеспечивает обычный clone/pull flow и детерминированную
установку на нескольких устройствах.

**Альтернативы:** blanket mirror отклонён из-за риска копирования `.git`/runtime-like artifacts;
полный overwrite `~/.codex` отклонён из-за потери user state; второй installer отклонён — wrappers
остаются единственными entry points и делегируют общей engine; active `config.toml` merge не введён,
поскольку нет утверждённого узкого non-secret invariant.

**Последствия:** unknown destination collisions и manifest/runtime collisions fail closed; stale
managed files удаляются только по ledger; staging/backup/atomic replace и post-apply validation
образуют rollback boundary. Legacy `~/.codex/.git` переносится вручную до install. Historical docs
могут упоминать прежнюю схему только с явным `SUPERSEDED` context.

## 2026-09-10 — DEV и product paths унифицированы через logical roles

**Статус:** принято; supersedes physical-path часть решений 2026-08-24 и 2026-09-10, но сохраняет
source/installed separation и independent Git roots.

**Решение:** `DEV_SOURCE_ROOT`, `CODEX_HOME` и `PROJECTS_ROOT` разрешаются единственным
`tools/dev_paths.py` по precedence environment → local config → default. Current defaults:
`~/codex-dev`, `~/.codex`, `~`. Product repository path не является policy signal; global DEV
adoption требует valid structured `.codex/dev-project.toml`. Exact `Global DEV bridge: enabled`
line в existing project-local `AGENTS.md` остаётся только human-readable declaration.

**Причина:** одинаковая physical layout на устройствах упрощает перенос, но hardcoded path и
автоматическое inheritance по parent directory связывают discovery с governance и способны
подключить plain repository к Prompt Queue/overlay без согласия проекта.

**Альтернативы:** автоматически наследовать DEV всем repositories под `PROJECTS_ROOT` отклонено
из-за нарушения isolation; неструктурированная AGENTS-only membership отклонена, потому что не
даёт строгого version/capability contract; silent legacy auto-detection отклонён из-за ambiguity
и риска неверного move/install source.

**Последствия:** installer/validator/hooks/Prompt Queue потребляют resolver; `dev-contract.toml` и
project marker обеспечивают clone/pull compatibility; legacy layout только диагностируется;
migration helper не выполняет move/delete; GitHub rename и remote update остаются user-authorized
operations. Исторические records сохраняют прежние paths как audit trail.
