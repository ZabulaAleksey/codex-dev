---
name: implement-stage
description: Полностью реализовать один заранее ограниченный этап дорожной карты с делегированием специалистам, тестами, проверкой и обновлением статуса.
---

1. Прочитай `AGENTS.md`, `docs/AI_STATUS.md`, `docs/AI_PLAN.md`, `docs/ARCHITECTURE.md` и `specs/README.md`.
2. Найди относящуюся к этапу SPEC и её критерии приёмки. Для новой существенной `STANDARD` или `COMPLEX` функциональности не начинай реализацию без SPEC.
3. Если ограниченного плана нет, сначала запусти процесс планирования.
4. До кода проверь Stage contract из `~/.codex/rules/governance.md`: все DAG-prerequisites завершены, входные предпосылки доступны, primary vertical slice запускается без future stage, а concrete end-to-end scenario и PASS/evidence определены.
5. Если обязательный future component отсутствует, не реализуй ложный completion: выбери `blocked`, `scaffolded`, `implemented_unverified` или `partial` и зафиксируй точный blocker.
6. Назначь непересекающиеся области файлов минимально необходимому числу агентов с правом записи.
7. До параллельной реализации явно зафиксируй контракты базы данных, API и интерфейсов.
8. Сначала запусти самые узкие релевантные тесты, затем необходимые integration/component и concrete end-to-end проверки этапа.
9. Проверь связь SPEC → критерии приёмки → тесты → реализация. Mocks/stubs/fakes подтверждают только локальный/scaffold contract и не заменяют живой user/production path.
10. Запусти `reviewer`; добавляй `security_reviewer` или `performance_engineer` только тогда, когда изменение этого требует.
11. Исправь замечания с высокой достоверностью; допускается не более двух циклов проверки.
12. Перед `DONE` подтверди terminal conditions Stage contract и выполни Completion Documentation Synchronization Gate из global Skill `dev-karkas` (`~/.agents/skills/dev-karkas/references/STATUS_WORKFLOW.md`): всегда проверь `README.md`, `docs/AI_PLAN.md`, `docs/AI_STATUS.md`, `docs/ROADMAP.md`, `prompts/STAGES.md` и другие state-bearing документы; обнови изменившиеся факты и не создавай churn в точных документах.
13. После разрешённого merge повтори gate по target branch и только затем фиксируй merge-level status и следующий этап.
14. Не выполняй push, развёртывание или публикацию, если пользователь явно не запросил это внешнее действие.
