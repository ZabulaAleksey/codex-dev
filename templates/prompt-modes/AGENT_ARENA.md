# MODE: AGENT ARENA

> Это опциональный prompt-mode для конкурентного решения выбранной пользователем задачи. Он
> включается только явной командой `MODE: AGENT_ARENA`, не является правилом ДЕВ и не запускается
> router'ом автоматически. Общие scope/safety-границы описаны в `README.md`.

При обычной активации этот файл задаёт способ выполнить текущую задачу несколькими независимыми
кандидатами. Он **не является командой построить постоянную инфраструктуру Arena**, изменить ДЕВ
или создать все описанные ниже будущие контуры. Реализация самой Arena начинается только по
отдельному прямому запросу пользователя.

## 0. Назначение

Нужно спроектировать и постепенно реализовать в рамках моей AI/DEV-экосистемы отдельный контур **Agent Arena / АРЕНА**.

АРЕНА — это инфраструктура для конкурентного и сравнительного выполнения задач несколькими AI-агентами.

В prompt-mode это может быть облегчённый одноразовый run: доступные субагенты либо независимые
проходы, временные артефакты и компактный итоговый verdict без обязательного создания постоянной
`.arena/` структуры.

Её основная идея:

> Не доверять одному агенту автоматически.
> Для важных задач давать одну и ту же постановку нескольким агентам или нескольким независимым проходам, заставлять их предоставлять проверяемые результаты, после чего отдельный слой оценки выбирает лучшее решение или собирает итоговое решение из нескольких кандидатов.

АРЕНА не должна превращаться в декоративное «LLM voting».

Нельзя выбирать победителя просто потому, что:

- два агента из трёх сказали одно и то же;
- ответ написан увереннее;
- ответ длиннее;
- агент поставил себе высокий confidence;
- решение выглядит красивее;
- решение использует больше современных технологий.

Главным критерием должно быть:

**доказанное качество результата.**

---

# 1. Место АРЕНЫ в общей экосистеме

АРЕНА должна быть совместима и интегрируема с существующими и будущими контурами:

- ДЕВ;
- КАРКАС;
- Chronicle;
- Evidence Ledger;
- Failure Atlas;
- Mentat;
- Navigator;
- Tribunal;
- reusable contours / component registry;
- локальными моделями;
- внешними AI-моделями;
- Git/GitHub;
- CI;
- тестовой инфраструктурой;
- sandbox/worktree/containers.

Предполагаемая логическая цепочка экосистемы:

`Source → Event → Claim → Assumption → Scenario → Decision → Action → Artifact → Evidence`

АРЕНА в этой системе в первую очередь работает на уровнях:

`Scenario → Decision → Action → Artifact → Evidence`

Она получает задачу и контекст, создаёт несколько независимых вариантов решения, а затем собирает Evidence, позволяющий определить качество каждого варианта.

---

# 2. Главный архитектурный принцип

АРЕНА должна разделять:

1. **генерацию решения;**
2. **проверку решения;**
3. **оценку решения;**
4. **принятие решения.**

Один и тот же агент не должен бесконтрольно выполнять все четыре роли.

Например:

```text
Task
 ↓
Arena Orchestrator
 ↓
┌──────────┬──────────┬──────────┐
│ Agent A  │ Agent B  │ Agent C  │
└──────────┴──────────┴──────────┘
 ↓          ↓          ↓
Candidate A Candidate B Candidate C
 ↓          ↓          ↓
Independent Verification
 ↓
Evidence Ledger
 ↓
Tribunal
 ↓
Winner / Hybrid / Reject All
```

---

# 3. Shadow Arena

Первоначально АРЕНУ реализовать прежде всего как **Shadow Agent Arena**.

Это означает:

агенты не должны сразу менять production/main workspace.

Каждый кандидат работает:

- в отдельном sandbox;
- либо отдельном git worktree;
- либо отдельной ephemeral-копии repository;
- либо отдельном container/environment.

Например:

```text
main repository
      │
      ├── arena/run-001/agent-a
      ├── arena/run-001/agent-b
      ├── arena/run-001/agent-c
      └── arena/run-001/verifier
```

Никакой кандидат не получает право автоматически слить своё решение в main.

Сначала:

1. решение;
2. тесты;
3. evidence;
4. Tribunal;
5. только потом promotion.

---

# 4. Что именно должны выдавать участники АРЕНЫ

Каждый агент должен возвращать не просто ответ.

Минимальный Candidate Package:

```text
candidate/
├── PLAN.md
├── ASSUMPTIONS.md
├── CHANGES.md
├── RISKS.md
├── TEST_PLAN.md
├── EVIDENCE.md
├── RESULT.json
└── patch / branch / artifact
```

## PLAN.md

Что агент решил делать и почему.

Не огромный chain-of-thought.

Нужен нормальный инженерный rationale:

- задача;
- выбранный подход;
- ключевые решения;
- альтернативы;
- почему они были отвергнуты.

## ASSUMPTIONS.md

Все предположения, без которых решение может оказаться неверным.

Каждому assumption дать ID:

```text
ASM-001
ASM-002
...
```

## CHANGES.md

Что именно изменено.

Пример:

```text
CHG-001
Component: auth middleware
Files:
- src/auth/middleware.ts
- tests/auth.test.ts

Purpose:
Make authentication mandatory for protected routes.
```

## RISKS.md

Риски решения.

```text
RSK-001
Probability: medium
Impact: high
Mitigation: ...
```

## TEST_PLAN.md

Какие свойства решения надо доказать.

Не просто:

> tests pass

А:

```text
TC-001:
Unauthenticated user cannot access protected endpoint.

TC-002:
Valid token grants access.

TC-003:
Expired token returns expected status.

TC-004:
Existing public endpoint remains public.
```

## EVIDENCE.md

Какие доказательства получены.

Например:

```text
EV-001
Supports: TC-001
Source: pytest
Command: ...
Result: PASS
Artifact: ...
```

---

# 5. Независимость кандидатов

Это критически важно.

Agent B не должен видеть решение Agent A до завершения собственного решения.

Иначе вместо независимого поиска получится коллективное копирование ошибки.

Поэтому нужны фазы:

## Phase A — Blind Generation

Все агенты получают:

- одну задачу;
- одинаковый immutable context;
- одинаковые ограничения.

Но НЕ видят решения друг друга.

## Phase B — Candidate Freeze

Каждый результат фиксируется.

После freeze запрещено незаметно менять первоначальное решение.

## Phase C — Cross Examination

Только теперь агентам можно показать решения конкурентов.

Они могут:

- искать ошибки;
- находить пропущенные edge cases;
- указывать слабые assumptions;
- предлагать контртесты.

---

# 6. Роли АРЕНЫ

Минимально предусмотреть следующие роли.

## 6.1 Arena Orchestrator

Не решает задачу самостоятельно.

Отвечает за:

- создание Arena Run;
- нормализацию входной задачи;
- формирование immutable task packet;
- выбор участников;
- создание sandbox;
- ограничения ресурсов;
- запуск фаз;
- сбор результатов;
- передачу результатов Tribunal.

---

## 6.2 Architect Candidate

Фокусируется на:

- архитектуре;
- границах компонентов;
- интеграциях;
- зависимости от существующего КАРКАСА;
- reusable contours;
- техническом долге;
- расширяемости.

---

## 6.3 Implementer Candidate

Фокусируется на рабочей реализации.

Его задача:

> сделать минимально необходимое изменение, которое реально проходит определённый DoD.

---

## 6.4 Test Contract Author

Отдельный агент до реализации может сформировать независимый контракт поведения.

Это особенно важно.

Он НЕ должен знать реализации.

Он определяет:

- expected behavior;
- invariants;
- failure behavior;
- edge cases;
- compatibility requirements;
- обязательные тесты.

Результат:

```text
Behavior Contract
↓
Test Contract
↓
Candidate implementations
```

Таким образом агенты не могут сами себе придумать удобный тест после написания кода.

---

## 6.5 Adversarial Reviewer

Его работа — уничтожить кандидатное решение проверками.

Он ищет:

- скрытые regression;
- race conditions;
- security mistakes;
- broken assumptions;
- unsupported claims;
- архитектурные тупики;
- неправильное использование библиотек;
- fake success;
- тесты, которые ничего реально не проверяют.

Он не должен улучшать решение.

Он должен пытаться его опровергнуть.

---

## 6.6 Tribunal

Tribunal — отдельный слой принятия решения.

Его нельзя путать с простым judge-LLM.

Tribunal обязан опираться прежде всего на Evidence.

Возможные решения:

```text
ACCEPT_A
ACCEPT_B
ACCEPT_C
HYBRID_A_B
RETRY
REJECT_ALL
ESCALATE_TO_HUMAN
```

---

# 7. Tribunal должен уметь сказать REJECT ALL

Очень важное правило.

АРЕНА не обязана выбирать победителя.

Если все решения плохие:

```text
REJECT_ALL
```

является полностью валидным результатом.

Это должно считаться успехом системы проверки, а не провалом Arena Run.

Также валидны:

```text
INSUFFICIENT_EVIDENCE
ENVIRONMENT_UNAVAILABLE
CONFLICTING_REQUIREMENTS
BLOCKED
```

---

# 8. Evidence-first scoring

Нельзя основывать рейтинг преимущественно на субъективной LLM-оценке.

Создать объективную систему оценки.

Например:

```text
Score =
  correctness
+ test_strength
+ requirement_coverage
+ regression_safety
+ architecture_quality
+ security
+ maintainability
- complexity_penalty
- unsupported_claim_penalty
- regression_penalty
- flaky_test_penalty
- cost_penalty
```

Но веса не должны быть универсально фиксированными.

Для разных типов задач используется профиль.

---

# 9. Profiles

Например:

## BUGFIX

Приоритет:

1. воспроизведение бага;
2. regression test;
3. исправление;
4. отсутствие regressions;
5. минимальный diff.

## SECURITY

Приоритет:

1. exploit reproduction;
2. threat model;
3. vulnerability elimination;
4. negative tests;
5. regression;
6. blast radius.

## ARCHITECTURE

Приоритет:

1. соответствие требованиям;
2. границы компонентов;
3. reversibility;
4. dependency direction;
5. migration path;
6. testability;
7. operational complexity.

## PERFORMANCE

Приоритет:

1. benchmark до;
2. benchmark после;
3. statistically meaningful comparison;
4. correctness unchanged;
5. memory/CPU/resource effects.

---

# 10. Confidence нельзя принимать на веру

Агент может вернуть:

```text
confidence = 0.93
```

Но Arena должна вычислять отдельное:

```text
evidence_confidence
```

Например:

```text
self_confidence: 0.93
evidence_confidence: 0.61
```

Большой разрыв должен считаться подозрительным.

Можно ввести:

```text
calibration_error =
abs(self_confidence - observed_success_probability)
```

Исторически это позволит понимать, какие агенты систематически переоценивают себя.

---

# 11. Failure Atlas

Все содержательные поражения агентов должны попадать в Failure Atlas.

Не просто:

```text
Agent B lost.
```

А:

```text
FAIL-2026-00127

Task class:
Database migration

Failure:
Agent changed schema but missed rollback compatibility.

Detected by:
TC-007

Root cause:
Forward-only reasoning.

Pattern:
migration.backward_compatibility_missing

Candidate:
B

Model:
...

Prompt version:
...

Environment:
...
```

Если та же ошибка встречается снова, система должна узнавать паттерн.

---

# 12. Chronicle

Chronicle должен хранить историю Arena Runs.

Например:

```text
Arena Run #184
Task: Introduce rate limiting

A: Redis sliding window
B: DB token bucket
C: in-memory limiter

Winner: A

Reason:
Passed distributed consistency tests.
B introduced DB contention.
C failed multi-instance test.
```

Это уже становится опытом системы.

---

# 13. Mentat

Mentat должен использовать историю Arena не для слепого копирования прошлых решений, а для формирования знаний.

Например:

```text
Claim:
In multi-instance MathMorph API deployments,
in-memory rate limiting is unsafe.

Evidence:
Arena Runs 184, 212, 271.

Confidence:
0.94
```

Это становится knowledge layer.

---

# 14. Navigator

Navigator использует знания АРЕНЫ прогностически.

Например:

при планировании новой архитектуры Navigator замечает:

```text
Proposed architecture uses process-local queue.

Historical risk:
Similar architecture failed in 4 previous Arena Runs
when horizontal scaling was enabled.
```

И предупреждает заранее.

Таким образом:

```text
Arena discovers
↓
Failure Atlas records failures
↓
Chronicle records history
↓
Evidence Ledger stores evidence
↓
Mentat derives knowledge
↓
Navigator anticipates future failure
```

---

# 15. ДЕВ / КАРКАС

АРЕНА должна быть встроена в ДЕВ, но НЕ запускаться для каждой мелкой операции.

Нужны политики запуска.

Например:

## Single Agent

Использовать для:

- rename;
- formatting;
- очевидных mechanical changes;
- простых documentation changes.

## Mini Arena

2 кандидата + verifier.

Для:

- нормального bugfix;
- небольшой архитектурной развилки;
- изменения API.

## Full Arena

3–5 кандидатов + независимый test author + adversarial reviewers + Tribunal.

Для:

- auth;
- billing;
- migration;
- security;
- сложной архитектуры;
- необратимых решений;
- критической business logic.

## Extreme Arena

Использовать редко.

Например:

- дорогостоящая migration;
- production incident;
- критическая security архитектура;
- выбор фундаментального технологического решения.

---

# 16. Cost-aware Arena

АРЕНА не должна бессмысленно сжигать токены.

Нужно вести стоимость каждого Run:

```text
tokens_in
tokens_out
wall_time
model_cost
test_compute
tool_calls
iterations
```

Ввести:

```text
cost_per_verified_solution
```

а не просто стоимость генерации.

Дешёвый агент, который пять раз ошибся и потребовал перепроверки, может оказаться дороже сильного агента.

---

# 17. Heterogeneous Arena

АРЕНА должна поддерживать не только несколько экземпляров одной модели.

Например:

```text
Candidate A — GPT
Candidate B — Claude
Candidate C — local LLM
Candidate D — specialist model
```

Это особенно полезно для снижения correlated failures.

Также можно запускать:

```text
same model
+
different prompts
+
different role priors
```

---

# 18. Mutations

В дальнейшем предусмотреть экспериментальный режим:

## Candidate Mutation

Берём хорошее решение и создаём несколько controlled mutations.

Например:

```text
Parent candidate
├── mutation-1: simpler architecture
├── mutation-2: higher performance
├── mutation-3: fewer dependencies
└── mutation-4: stronger security
```

После этого снова запускается Tribunal.

Это превращает АРЕНУ частично в evolutionary search.

Но НЕ реализовывать сложную мутационную систему раньше базовой working Arena.

---

# 19. Elo / рейтинги агентов

Можно вести рейтинги, но не делать один глобальный рейтинг.

Агент может быть хорош в:

- Rust;
- SQL;
- frontend;
- architecture;
- security;

и плох в другом.

Поэтому рейтинг должен быть многомерным.

Пример:

```text
Agent X

backend: 1820
frontend: 1440
security: 1710
sql: 1900
architecture: 1760
debugging: 2010
```

Дополнительно хранить:

```text
win_rate
verified_success_rate
false_confidence_rate
regression_rate
average_cost
average_iterations
```

---

# 20. Никакого reward hacking

АРЕНА должна предполагать, что агент может случайно или намеренно оптимизироваться под scoreboard.

Запретить метрики типа:

```text
more tests = better
more files = better
more documentation = better
larger patch = better
higher confidence = better
```

Например, 100 бессмысленных тестов не должны выигрывать у 5 сильных property tests.

---

# 21. Test quality

Проверять не только:

```text
tests = PASS
```

но и качество самих тестов.

Минимально анализировать:

- действительно ли тест падает без исправления;
- действительно ли тест связан с требованием;
- нет ли tautological tests;
- нет ли mock-а всей логики;
- нет ли snapshot-а, который просто перезаписали;
- тестируется ли failure path;
- тестируется ли boundary;
- regression test воспроизводит ли настоящий дефект.

Для bugfix желательно:

```text
1. test fails on baseline
2. patch applied
3. test passes
```

---

# 22. Baseline

Перед соревнованием фиксировать baseline.

Например:

```text
BASELINE:
commit: abc1234
tests:
118 PASS
2 SKIP

known failures:
none
```

После каждого кандидата:

```text
Candidate A:
121 PASS
2 SKIP
new failures: 0
```

Это защищает от ложного успеха.

---

# 23. Reproducibility

Arena Run должен быть по возможности воспроизводим.

Хранить:

```text
run_id
timestamp
repository
baseline_commit
task_hash
context_hash
model
model_version
prompt_version
temperature/mode if available
tool permissions
environment
dependencies
candidate seed if available
```

---

# 24. Immutable Task Packet

После начала blind phase задача не должна тихо изменяться.

Создать:

```text
TASK.md
CONSTRAINTS.md
ACCEPTANCE.md
CONTEXT_MANIFEST.json
```

и hash:

```text
task_packet_hash
```

Все кандидаты должны работать относительно одного packet.

---

# 25. Human-in-the-loop

Человек должен иметь возможность:

- посмотреть кандидатов;
- посмотреть diff;
- посмотреть Evidence;
- изменить веса Tribunal;
- отклонить победителя;
- выбрать другого кандидата;
- заставить Arena повторить Run;
- создать Hybrid;
- вручную добавить constraint;
- отметить ложноположительную или ложноотрицательную оценку.

Решение человека также должно попасть в Chronicle как отдельное событие.

---

# 26. Human Learning Checkpoints

Учитывая мой режим работы с ДЕВ, Arena должна поддерживать возможность выделить участок работы, который полезнее выполнить мне самому.

Например:

```text
HUMAN_CHECKPOINT

Task:
Manually inspect network calls during login.

Instructions:
1. Open DevTools.
2. Perform login.
3. Record redirect chain.
4. Record status codes.
5. Report observations.

DoD:
Observed sequence documented.
```

После этого Arena продолжает работу на основании полученного evidence.

Не создавать искусственную ручную работу.

Отдавать человеку только те куски, которые реально дают понимание системы либо где человек является хорошим внешним наблюдателем.

---

# 27. Arena Modes

Предусмотреть архитектуру для нескольких видов Arena.

## Coding Arena

Агенты конкурируют кодом.

## Architecture Arena

Конкурируют архитектурными решениями.

## Debug Arena

Конкурируют гипотезами о причине проблемы.

Очень полезный режим.

Например:

```text
Symptom:
POST /convert occasionally hangs.

A:
RabbitMQ ack issue.

B:
DB transaction starvation.

C:
worker deadlock.
```

Вместо немедленного изменения кода каждый должен предложить минимальный discriminating experiment.

Побеждает не самая красивая гипотеза, а та, которая лучше предсказывает наблюдения.

## Research Arena

Агенты независимо исследуют вопрос и подтверждают источниками.

## Planning Arena

Несколько вариантов roadmap/architecture migration.

## Security Arena

Red Team против Blue Team.

---

# 28. Hypothesis Arena

Особенно важный режим для debugging.

Каждая гипотеза должна иметь формат:

```text
HYP-001

Claim:
...

Expected observations if true:
...

Expected observations if false:
...

Cheapest discriminating test:
...

Evidence:
...
```

Сначала эксперимент.

Только потом исправление.

Это должно уменьшить хаотичное:

> попробуем поменять вот это

---

# 29. Debate — только после независимого ответа

Если вводится debate:

```text
Agent A ↔ Agent B
```

он разрешён только после freeze независимых кандидатов.

Нельзя начинать с debate, потому что возникает anchoring.

Правильный процесс:

```text
independent generation
↓
freeze
↓
cross critique
↓
experiment
↓
Tribunal
```

---

# 30. Hybrid candidate

Иногда лучшее решение может сочетать части кандидатов.

Например:

```text
Architecture from A
Migration strategy from B
Tests from C
```

Tribunal может создать предложение:

```text
HYBRID_PROPOSAL
```

Но hybrid обязательно считается НОВЫМ candidate.

Он должен снова пройти:

- implementation;
- tests;
- verification.

Нельзя автоматически считать:

> раз каждая часть где-то победила — комбинация тоже правильная.

---

# 31. Promotion pipeline

Финальный процесс:

```text
Arena candidate
↓
Verification
↓
Tribunal
↓
Selected Candidate
↓
Final integration branch
↓
Full project gates
↓
Human/Policy approval if required
↓
Merge
```

Arena PASS не заменяет глобальный DoD проекта.

---

# 32. Связь с Component Behavior & Test Contract Policy

АРЕНА должна использовать уже существующий принцип:

для каждого компонента фиксируются:

- responsibility;
- inputs;
- outputs;
- state;
- dependencies;
- invariants;
- typical behavior;
- abnormal behavior;
- Behavior ID.

И матрица покрытия:

```text
Behavior
↓
Unit
Integration
Component/UI
E2E
```

АРЕНА не должна позволять кандидату объявить компонент завершённым, если поведение не подтверждено соответствующим уровнем тестов.

---

# 33. Не переусложнять MVP

Не пытаться сразу построить:

- собственный Kubernetes;
- distributed scheduler;
- сложный RL;
- автоматическое обучение модели;
- глобальную knowledge graph;
- миллион агентов.

Первая полезная версия должна быть маленькой.

Предлагаемый MVP:

```text
ARENA MVP

1. Task packet
2. Two independent candidates
3. Separate git worktrees
4. Test Contract
5. Candidate manifests
6. Automated tests
7. Evidence collection
8. Simple Tribunal
9. Winner / Reject All
10. Chronicle entry
```

---

# 34. Первый технический прототип

Сделать CLI примерно такого вида:

```bash
arena run TASK-123
```

Выход:

```text
Arena Run: AR-000123

Participants:
A — agent-profile/backend-safe
B — agent-profile/minimal-diff

Baseline:
PASS

Blind phase:
A COMPLETE
B COMPLETE

Verification:
A 14/15 contracts PASS
B 15/15 contracts PASS

Regression:
A FAILED 1
B PASS

Tribunal:
WINNER B

Reason:
Full contract coverage, zero regression.

Artifacts:
.arena/runs/AR-000123/
```

---

# 35. Предлагаемая структура файлов

```text
.arena/
├── config/
│   ├── profiles/
│   ├── scoring/
│   └── policies/
│
├── prompts/
│   ├── orchestrator.md
│   ├── candidate.md
│   ├── architect.md
│   ├── implementer.md
│   ├── test-contract.md
│   ├── adversarial-reviewer.md
│   └── tribunal.md
│
├── schemas/
│   ├── task.schema.json
│   ├── candidate.schema.json
│   ├── evidence.schema.json
│   └── verdict.schema.json
│
├── runs/
│
└── README.md
```

Если АРЕНА становится глобальным контуром ДЕВ, generic implementation должна жить в ДЕВ.

В конкретных проектах хранить только overlay:

```text
.arena/
└── project-policy.md
```

или аналогичную минимальную дельту.

Не копировать весь глобальный Arena framework в каждый репозиторий.

---

# 36. Схема Candidate Result

Пример:

```json
{
  "run_id": "AR-000123",
  "candidate_id": "A",
  "status": "completed",
  "claims": [],
  "assumptions": [],
  "changes": [],
  "tests": [],
  "evidence": [],
  "risks": [],
  "self_confidence": 0.81,
  "known_limitations": []
}
```

---

# 37. Схема Tribunal Verdict

```json
{
  "run_id": "AR-000123",
  "verdict": "ACCEPT_B",
  "ranking": [
    "B",
    "A"
  ],
  "reasons": [],
  "blocking_failures": {},
  "evidence_refs": [],
  "requires_human_review": false
}
```

---

# 38. Security

Считать результат агента недоверенным input.

Агент не должен автоматически получать:

- production credentials;
- unrestricted shell;
- возможность пушить main;
- secrets;
- облачные destructive permissions.

Arena sandbox должен ограничивать blast radius.

Особенно нельзя слепо исполнять команды, созданные одним агентом, с правами orchestration layer.

---

# 39. Provenance

Любой imported/forked код, который использует кандидат, должен сохранять provenance.

Если используется внешний repository/component:

- источник;
- commit/version;
- license;
- modifications;
- security checks.

Это должно стыковаться с правилом КАРКАСА:

любой внешний/forked repository сначала проходит архитектурный intake и классификацию на:

- external/upstream;
- reusable/commodity;
- project-specific integration;
- unique domain core.

---

# 40. Long-term evolution

После стабильного MVP АРЕНА потенциально может развиться в систему, где AI-экосистема эмпирически понимает:

- какая модель лучше решает какой класс задач;
- какой prompt работает лучше;
- какие архитектурные решения чаще ломаются;
- какие тестовые стратегии находят больше настоящих ошибок;
- какие агенты переоценивают confidence;
- какие reusable contours реально надёжны;
- какие решения дешевле в эксплуатации;
- какие подходы создают меньше regressions.

То есть АРЕНА должна постепенно становиться не просто comparator, а **экспериментальной установкой для развития самого ДЕВ**.

---

# 41. Главное правило

Никогда не считать LLM-output доказательством LLM-output.

То есть недопустимо:

```text
Agent A:
код правильный.

Judge Agent:
я согласен, код правильный.

Result:
PASS
```

PASS появляется только при наличии внешне проверяемого evidence там, где такая проверка технически возможна.

Предпочтительный порядок силы Evidence:

```text
runtime observation
>
automated executable test
>
static/verifiable artifact inspection
>
independent source/documentation
>
structured human observation
>
LLM reasoning
>
LLM self-assessment
```

---

# 42. Что делать при активации prompt-mode

Применить Arena к задаче и scope, которые явно указал пользователь. Не начинать проектирование или
реализацию постоянной инфраструктуры Arena, если пользователь отдельно этого не попросил.

По умолчанию:

1. Зафиксировать одинаковую постановку, ограничения и критерии результата для кандидатов.
2. Выбрать минимально полезный формат: обычно два независимых кандидата и один verifier/Tribunal.
3. Не показывать кандидатам решения друг друга до freeze.
4. Для реализации с несколькими writers использовать отдельные branches/worktrees; для анализа
   достаточно независимых read-only проходов.
5. Собрать только полезный Candidate Package; не создавать постоянные файлы ради церемонии.
6. Проверить утверждения доступным внешним evidence и разрешить `REJECT_ALL`.
7. Представить пользователю winner/hybrid/reject verdict и существенные trade-offs.
8. Не выполнять promotion, merge, push, deployment или удаление worktrees без соответствующего
   отдельного разрешения.
9. Если одновременно активны другие prompt-modes, применить их ко всему run либо назначить разным
   кандидатам — согласно параметрам пользователя.
10. После завершения удалить только безопасные временные artifacts, созданные данным run; при
    сомнении сохранить их и сообщить пользователю.

---

# 43. Конечная цель

В зрелом состоянии пользователь может дать Codex задачу:

```text
Разберись, почему иногда зависает conversion worker.
Запусти Arena.
```

После чего явно активированный prompt-mode делает примерно следующее в пределах выбранного scope:

```text
1. Создаёт immutable Task Packet.
2. Создаёт несколько независимых гипотез.
3. Каждая гипотеза предлагает discriminating experiment.
4. Эксперименты выполняются в sandbox.
5. Evidence сохраняется.
6. Неверные гипотезы отбрасываются.
7. Оставшиеся агенты предлагают исправления.
8. Несколько исправлений реализуются независимо.
9. Test Contract проверяет их.
10. Adversarial Reviewer пытается сломать решения.
11. Tribunal выбирает победителя либо REJECT_ALL.
12. Итог прогоняется через полный DoD проекта.
13. Failure Atlas получает найденные failure patterns.
14. Chronicle получает историю Run.
15. Evidence Ledger получает доказательства.
16. Mentat получает материал для формирования знания.
17. Navigator сможет использовать это знание при будущих решениях.
```

Именно такую систему считать целевым направлением Agent Arena.
