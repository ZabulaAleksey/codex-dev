---
name: bootstrap-project-framework
description: Создать или актуализировать проектный КАРКАС и АВТОМАТИЗАЦИЮ КОНТЕКСТА поверх существующей AI Dev Team. Использовать, когда пользователь просит «создай КАРКАС», «сделай автоматизацию контекста», подготовить новый repository к поэтапной Codex-разработке или выполнить gap analysis существующего project overlay без реализации продукта.
---

# Создание проектного КАРКАСА

1. Прочитай ближайшие `AGENTS.md`, `~/.codex/docs/PROJECT_FRAMEWORK.md`, `~/.codex/docs/CONTEXT_POLICY.md`, `~/.codex/docs/CONTEXT_COMPATIBILITY.md` и Stage contract из `~/.codex/rules/governance.md`.
2. Определи Git-корень, состояние рабочей копии, сложность, режим, этап SDLC, домен, стек и каноническую SPEC.
3. Классифицируй repository как `GREENFIELD` или `BROWNFIELD`. Для brownfield фактический repository и baseline-тесты — source of truth текущего состояния; КАРКАС адаптируется к реализации.
4. Для brownfield до любых mutations запусти read-only `tools/reconcile_project_framework.py` и зафиксируй compatibility matrix в `docs/CONTEXT_COMPATIBILITY.md`.
5. Сними baseline тестов до refresh; старые failures зафиксируй отдельно, а новые failures после refresh трактуй как regression.
6. Если repository уже содержит КАРКАС, выполни inspect → gap analysis; не регенерируй работающие документы.
7. Отдели стабильные требования и архитектуру от execution state. Используй канонические
   `specs/system.spec.md`, `docs/ROADMAP.md` и единственный `prompts/STAGES.md` для selector,
   current plan, lifecycle/evidence, blockers и NEXT.
8. Спроектируй минимальную project delta: локальные инварианты, архитектурные границы, решения, контракты, security/testing по риску и `prompts/STAGES.md` для полного staged overlay. Для repository вне полного overlay зафиксируй классификацию и не создавай placeholders.
9. Перед добавлением agent, hook, MCP, Skill, config или workflow классифицируй его как `INHERITED`, `EXTEND`, `PROJECT_ONLY`, `CONFLICT` или `OBSOLETE`. Запиши нетривиальный результат в проектный `docs/CONTEXT_COMPATIBILITY.md`.
10. Настрой в тонком `AGENTS.md` маршрутизацию от типа задачи к минимальному набору SPEC, architecture, decisions, security и tests. Не копируй глобальные правила.
11. Классифицируй backend applicability как `BDX-L0..L3`. Для `BDX-L1..L3` добавь в `docs/project-context.md` только project delta по `~/.codex/templates/BACKEND_DX_DELTA_TEMPLATE.md`; для `BDX-L0` не создавай пустой раздел.
12. Для каждого этапа по Stage contract из governance укажи устойчивый ID, dependency DAG только из completed prerequisites, входные предпосылки, runnable vertical slice, concrete end-to-end scenario, scope/non-goals, PASS criteria и evidence, допустимую полностью рабочую temporary implementation, deferred future scope, tests/gates, DoD, acceptance artifacts и rollback/failure conditions.
13. Проверь, что future stage только расширяет или заменяет работающий slice и не разблокирует primary path, обязательную инфраструктуру либо тестирование предыдущего stage. Mock/stub/interface-only результат классифицируй как `scaffolded`.
14. Проверь согласованность SPEC → contracts → stages → acceptance/tests, отсутствие дублирующих status/source-of-truth файлов и приемлемый context budget.
15. Оформляй человекочитаемый контекст на русском языке по умолчанию; не переводи программные идентификаторы, API, команды, пути и машинные ключи.
16. Обнови текущий status и остановись до реализации продукта, если пользователь явно не запросил код.

## Ограничения

- Не создавай приложение, runtime infrastructure или product MCP в рамках bootstrap без прямого запроса.
- Не создавай локальные generic agents, hooks, Skills, Git workflow или Codex config «на всякий случай».
- Не выдумывай неизвестное: фиксируй открытые вопросы, owner и момент решения.
- Не создавай `AI_PLAN.md`, `AI_STATUS.md`, `PLAN.md`, `STATUS.md`, `PROGRESS.md` или эквивалентный
  competing execution-state owner и не превращай stage catalog в источник требований.
