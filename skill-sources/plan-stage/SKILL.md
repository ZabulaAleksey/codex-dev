---
name: plan-stage
description: Спланировать один этап дорожной карты или межмодульную функцию без её реализации.
---

1. Прочитай инструкции проекта, current selector/record в `docs/STAGES.md` и `specs/README.md`, если он существует.
2. Найди относящуюся к этапу SPEC. Для новой `STANDARD` или `COMPLEX` функциональности создай либо обнови SPEC до плана.
3. Запусти `architect` и встроенного `explorer` параллельно, если одновременно нужны архитектурное решение и фактические данные из репозитория.
4. Для рисков предметной области используй проектного специалиста.
5. Примени Stage contract из `~/.codex/rules/governance.md`: зафиксируй устойчивый stage ID, dependency DAG только из completed prerequisites, входные предпосылки, самостоятельный runnable vertical slice, concrete end-to-end scenario, PASS/evidence, допустимую полностью рабочую temporary implementation и deferred future scope.
6. Проверь, что ни primary path, ни обязательная инфраструктура, ни тестирование текущего stage не зависят от future stage; mock/stub/interface-only результат планируй как `scaffolded`, а не completion.
7. Подготовь упорядоченный план с идентификаторами требований, областями файлов, интерфейсами, тестами, миграциями, способом отката и критериями приёмки.
8. Записывай или обновляй план только в соответствующем record `docs/STAGES.md` и только по
   просьбе пользователя сохранить план; не создавай отдельный plan/status owner.
9. Не реализуй код.
