# Этап реализации

Перед кодом:

- прочитай соответствующую SPEC и критерии приёмки;
- проверь `ARCHITECTURE.md`, `DECISIONS.md` и `DESIGN.md` для затронутой области;
- определи изменяемые модули, контракты и тесты.
- для stage проверь dependency DAG, completed prerequisites и исполнимость primary vertical slice
  без future component по `rules/governance.md`.

Во время работы:

- не меняй архитектуру или требования молча;
- держи изменения в пределах задачи;
- сохраняй обратную совместимость, если SPEC не говорит иного.

После работы выполни релевантные тесты и `rules/sdd/spec-validation.md`.
Mock/stub/interface-only результат не повышай выше `scaffolded`; без обязательного E2E PASS
evidence используй `blocked`, `scaffolded`, `partial` или `implemented_unverified`, но не completion claim.
