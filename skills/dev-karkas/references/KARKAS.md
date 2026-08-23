# Канон ДЕВ / КАРКАС

КАРКАС — не фиксированное дерево файлов. Это набор инженерных обязанностей, которые должны быть закрыты подходящим способом для конкретного проекта.

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

## 3. Planning and status

Предпочтительный минимум:

- `AI_PLAN.md` — что делать дальше;
- `AI_STATUS.md` — что подтверждённо сделано сейчас.

`SPEC` не равен `AI_PLAN`.

Не вводи третий статусный файл без необходимости. Если исторически существует PROGRESS, сначала реши, можно ли его роль безопасно объединить с существующим каноном без потери данных.

Следуй `STATUS_WORKFLOW.md`.

## 4. Architecture

Нужен канонический источник архитектурных решений. В зависимости от проекта:

- `DESIGN.md`;
- `docs/architecture/...`;
- `decisions.md` или ADR directory.

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

## 7. Fallback and resilience

Для внешних сервисов, ускорителей, моделей, сетевых зависимостей и optional backends явно определи fallback policy.

Следуй `FALLBACK_POLICY.md`.

## 8. Prompts / staged implementation

Если проект развивается этапами, используй `PROMPTS/` как очередь самодостаточных implementation prompts.

Хороший prompt:

- маленький настолько, чтобы его можно было доказуемо завершить;
- большой настолько, чтобы давать полезную вертикальную ценность;
- имеет scope, constraints, tests, acceptance criteria и DoD;
- не повторяет уже реализованное.

Следуй `PROMPT_TEMPLATE.md`.

## 9. Decisions

Фиксируй решения, когда выбор:

- влияет на несколько модулей;
- создаёт долгосрочное ограничение;
- меняет публичный контракт;
- вводит крупную зависимость;
- меняет security/privacy model;
- меняет storage/network/deployment architecture.

Запись решения должна содержать context, decision, rationale, alternatives, consequences и date/status при необходимости.

## 10. Learning / development record

Используй `LEARNING.md` и/или `DEV_LOG.md`, только если проект действительно получает ценность от истории:

- почему возникла проблема;
- как диагностировали;
- какое решение сработало;
- какие ловушки повторять нельзя.

Не превращай журнал в копию git history.

## 11. Commercial/product policy

Для коммерческого продукта при необходимости используй `COMMERCIAL_PRODUCT.md` или эквивалент для:

- тарифов / лицензирования;
- ограничений продукта;
- платных функций;
- privacy/retention promises;
- SLA/operational expectations.

Не создавай его для лабораторного скрипта без коммерческого контекста.

## 12. Tooling / automation

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

Минимум: README + AGENTS + команды проверки + понятный статус/roadmap при длительной разработке.

### STANDARD

Обычный активный продукт.

Добавь: DESIGN, SECURITY при наличии внешней поверхности, AI_PLAN/AI_STATUS, PROMPTS, testing policy, decisions.

### ADVANCED

Многокомпонентная система, публичный сервис, сложная инфраструктура или высокий риск.

Добавь только релевантные: detailed architecture, threat model, observability, SLO/SLA, rollout/rollback, migrations, compatibility matrix, performance budgets, incident/recovery, subagents, MCP/tool policy.

Профиль — ориентир, а не повод генерировать пустые документы.
