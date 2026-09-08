# Канон ДЕВ / КАРКАС

КАРКАС — набор инженерных обязанностей, а не повод механически генерировать файлы. Для active
product repository, явно подключённого как полный staged ДЕВ overlay, обязательный baseline и
канонические пути задаёт `~/.codex/rules/governance.md`. Одноразовые, vendor, archived и иные
неполные overlays сначала явно классифицируются и не получают placeholders.

## 1. Project identity

Зафиксируй:

- цель продукта;
- границы scope / non-goals;
- пользовательские сценарии;
- текущую зрелость: idea / prototype / MVP / production;
- ссылки на репозиторий и внешние канонические источники, если они используются.

Обычно это README, SPEC или отдельный product document. Не создавай три копии одного описания.

## 2. Agent governance

Проект должен иметь понятные инструкции для агента:

- `AGENTS.md` — project-specific правила;
- `AGENTS.override.md` — только когда действительно нужна более локальная переопределяющая инструкция;
- глобальные правила ДЕВ не копируй внутрь каждого проекта: делай overlay.

Project `AGENTS.md` должен отвечать на вопросы:

- что это за проект;
- где канонические документы;
- какие команды проверки использовать;
- какие части проекта особенно хрупкие;
- что агенту запрещено делать;
- как определить завершённость задачи.

## 3. Stages, planning and status

Полный staged overlay использует:

- `prompts/STAGES.md` — единственный detailed stage и execution-state source: current selector,
  plan, lifecycle/evidence, blockers и NEXT;
- `docs/ROADMAP.md` — порядок развития;

`SPEC` не равен текущему stage plan.

Не создавай отдельные AI plan/status files. Если они исторически существуют, сначала семантически
объедини актуальные facts/blockers/evidence в `prompts/STAGES.md`, проверь links/validator и только
после этого удаляй legacy files.

Следуй `STATUS_WORKFLOW.md`.

## 4. Architecture

Канонические роли полного overlay:

- `docs/ARCHITECTURE.md` — фактические границы, интерфейсы и потоки;
- `docs/DECISIONS.md` — решения; ADR directory может быть supplement, связанный из канона;
- `docs/DESIGN.md` — только UI/UX contract при наличии пользовательского интерфейса.

Brownfield legacy path допустим временно только через canonical mapping в
`docs/CONTEXT_COMPATIBILITY.md`, semantic/link audit и подтверждённый один source of truth.

Архитектура должна отражать фактическую систему, а не желаемую фантазию. Будущие технологии помечай как planned/optional.

Следуй `ARCHITECTURE_POLICY.md`.

## 5. Security

Для сетевого, пользовательского, SaaS или публичного продукта должен существовать security baseline:

- trust boundaries;
- auth/authz;
- secrets;
- validation;
- rate limits / quotas;
- abuse / DoS controls;
- upload limits;
- dependency / supply-chain considerations;
- logging without leaking secrets/content;
- privacy and retention;
- recovery / incident expectations.

Следуй `SECURITY_BASELINE.md`.

## 6. Testing and quality gates

Закрой уровни, которые релевантны проекту:

- formatting/lint/static analysis;
- unit;
- integration;
- component;
- E2E ключевых пользовательских сценариев;
- smoke;
- build/package;
- compatibility evidence;
- security checks;
- performance checks, если performance является требованием.

Следуй `TESTING_POLICY.md`.

## 7. Dependency management

Когда ecosystem определим, зафиксируй canonical dependency manager, manifest,
lockfile, штатный shared cache/store, project-local materialization, cleanup
classification и CI clean-restore command. Следуй глобальной
`rules/dependency-management.md`: preferred defaults не отменяют стабильный
upstream/toolchain contract; exception требует причины, а migration — clean restore
и проверки до удаления прежнего состояния.

## 8. Backend Developer Experience

Если проект содержит backend/runtime service, классифицируй его как `BDX-L1`,
`BDX-L2` или `BDX-L3` по фактической архитектуре. Для проекта без backend используй
`BDX-L0` и не создавай пустой раздел.

Полный global contract находится в `~/.codex/rules/backend-dx.md`. Project хранит
только `Backend DX Delta` в `docs/project-context.md`: support matrix, working root,
toolchain/lockfile, semantic command map, config/services, API/DB/test/diagnostics,
clean-room evidence, limitations и deviations. Используй
`~/.codex/templates/BACKEND_DX_DELTA_TEMPLATE.md` и Skill `backend-dx-audit`; не
копируй policy и не добавляй новый stack ради checklist.

## 9. Fallback and resilience

Для внешних сервисов, ускорителей, моделей, сетевых зависимостей и optional backends явно определи fallback policy.

Следуй `FALLBACK_POLICY.md`.

## 10. Prompts / staged implementation

В полном staged overlay используй только `prompts/STAGES.md` как очередь и подробный источник
самодостаточных implementation stages. Сырые идеи остаются backlog/Notion до refinement/approval.

Хороший prompt:

- маленький настолько, чтобы его можно было доказуемо завершить;
- большой настолько, чтобы давать полезную вертикальную ценность;
- имеет completed prerequisites/DAG, runnable vertical slice, concrete E2E, PASS/evidence,
  fully working temporary implementation, deferred scope и DoD;
- не зависит от future stage для primary path, обязательной инфраструктуры или проверки;
- не повторяет уже реализованное.

Следуй `PROMPT_TEMPLATE.md`.

## 11. Decisions

Фиксируй решения, когда выбор:

- влияет на несколько модулей;
- создаёт долгосрочное ограничение;
- меняет публичный контракт;
- вводит крупную зависимость;
- меняет security/privacy model;
- меняет storage/network/deployment architecture.

Запись решения должна содержать context, decision, rationale, alternatives, consequences и date/status при необходимости.

## 12. Learning / development record

Полный staged overlay содержит `docs/LEARNING_LOG.md`, но добавляет туда только повторно полезные
выводы. `docs/DEV_LOG.md` создавай лишь когда нужен trace, отличный от Git history:

- почему возникла проблема;
- как диагностировали;
- какое решение сработало;
- какие ловушки повторять нельзя.

Не превращай журнал в копию git history.

## 13. Commercial/product policy

Для коммерческого продукта при необходимости используй `COMMERCIAL_PRODUCT.md` или эквивалент для:

- тарифов / лицензирования;
- ограничений продукта;
- платных функций;
- privacy/retention promises;
- SLA/operational expectations.

Не создавай его для лабораторного скрипта без коммерческого контекста.

## 14. Tooling / automation

При необходимости КАРКАС может включать:

- hooks;
- skills;
- MCP configuration;
- CI/CD;
- release scripts;
- migrations;
- generators;
- observability;
- deployment policy.

Каждый механизм должен решать реальную повторяющуюся задачу. Не добавляй инфраструктуру ради полноты чеклиста.

## Профили сложности

### SIMPLE

Небольшая локальная утилита или эксперимент.

Если repository не подключён как полный overlay, достаточно README + AGENTS + команд проверки и
явной классификации. Если подключён — baseline governance остаётся обязательным, но документы
могут быть краткими и содержательными.

### STANDARD

Обычный активный продукт.

Используй полный staged baseline governance. Добавляй `DESIGN.md` только для UI, `SECURITY.md`
для security surface и отдельный testing contract при реальной необходимости.

### ADVANCED

Многокомпонентная система, публичный сервис, сложная инфраструктура или высокий риск.

Добавь только релевантные: detailed architecture, threat model, observability, SLO/SLA, rollout/rollback, migrations, compatibility matrix, performance budgets, incident/recovery, subagents, MCP/tool policy.

Профиль — ориентир, а не повод генерировать пустые документы.
