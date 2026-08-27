# Системная спецификация AI Dev Team Codex

Статус: Действует
Версия: 1.2

## 1. Назначение

AI Dev Team предоставляет один переиспользуемый пользовательский слой Codex для нескольких независимых Git-репозиториев в `~/codex-workspace/*`.

## 2. Системные требования

### FR-001 Единое глобальное ядро

Общие agents, Skills, hooks, rules, MCP-рекомендации и Git workflow должны иметь один versioned канонический источник непосредственно в `~/.codex`. Runtime-проекция Skills в `~/.agents/skills` допустима только как hash-verified materialization канона и не является вторым source of truth.

### FR-002 Проект как overlay

Каждый рабочий repository должен хранить только проектные требования, архитектуру, состояние и подтверждённые локальные расширения общей AI Dev Team.

### FR-003 Независимые репозитории

Каждый каталог верхнего уровня в `~/codex-workspace/` должен быть самостоятельным Git-репозиторием. Git repository ДЕВ в `~/.codex` не должен отслеживать их содержимое или runtime state Codex.

### NFR-001 Минимальный контекст

Codex должен загружать ближайшие инструкции и только относящиеся к задаче правила, SPEC,
выбранный stage record из `prompts/STAGES.md` и документы состояния; весь stage catalog не
загружается автоматически. Автоматическая проекция использует stable `Stage ID` активного
`docs/AI_PLAN.md` и exact unique heading; ошибка явного selector должна быть видимой деградацией,
а не silent fallback к другой записи.

### NFR-002 Безопасное изменение

Установщики и rollout не должны без явного разрешения перезаписывать пользовательские настройки, продуктовый код или незавершённые изменения проекта.

### NFR-003 Непротиворечивый контекст

`AGENTS.md`, policies, Skills, templates и status workflow не должны задавать конкурирующие
источники требований или ослаблять канонические lifecycle/evidence contracts. Полная норма
принадлежит одному владельцу; производные поверхности маршрутизируют к ней и добавляют только
необходимую операционную форму.

### FR-004 Brownfield Reconciliation Gate

Перед bootstrap/refresh repository классифицируется как `GREENFIELD` или `BROWNFIELD`. Для
`BROWNFIELD` read-only reconciler формирует compatibility matrix со статусами `KEEP`, `ADD`,
`ADAPT`, `MERGE`, `CONFLICT`, `SUPERSEDED`, `FORBIDDEN_TO_OVERWRITE`. Unresolved `CONFLICT`
блокирует соответствующую mutation, `FORBIDDEN_TO_OVERWRITE` запрещает автоматическую запись.

### FR-005 Baseline regression contract

До refresh фиксируется baseline тестов. Pre-existing failures сохраняются отдельно; новый failure
после refresh является regression и проваливает gate.

### FR-006 Completion Documentation Synchronization Gate

Перед завершением задачи или этапа и после разрешённого merge Codex должен проверить все
существующие источники, которые описывают возможности, выполненные шаги, текущий статус и
следующие действия. Обязательный минимум: `README.md`, `docs/AI_PLAN.md`,
`docs/AI_STATUS.md`, `docs/ROADMAP.md`, `prompts/STAGES.md` и затронутые канонические документы.

Проверка обязательна всегда; изменение содержимого обязательно только тогда, когда изменились
подтверждённые факты. Gate должен устранять устаревшие задачи, этапы, blockers, test evidence и
ложные уровни интеграции, не создавая timestamp-only churn и не выдумывая evidence.

### FR-007 Архитектурно завершённые этапы

Каждый этап ДЕВ должен быть самостоятельным, исполнимым и проверяемым на момент закрытия.
До начала этапа должны быть определены dependency DAG, завершённые prerequisite-этапы,
входные предпосылки, runnable vertical slice, конкретный end-to-end сценарий, PASS-критерии,
требуемое evidence, допустимые временные реализации и явно отложенная функциональность.

Этап может зависеть только от уже завершённых prerequisite-этапов. Будущий этап может расширить,
оптимизировать или заменить полностью рабочую временную реализацию, но не может задним числом
разблокировать основной путь, добавить отсутствующую обязательную инфраструктуру, превратить
заглушку в реальную реализацию или впервые сделать возможной проверку ранее закрытого этапа.

Если объявленный slice нельзя запустить и проверить без будущего компонента, допустимы только
нетерминальные статусы `blocked`, `scaffolded`, `implemented_unverified` или `partial`.
Mocks, stubs, fakes и заранее подготовленные интерфейсы подтверждают только scaffold/локальный
контракт и не являются evidence завершённого пользовательского или production-пути.

## 3. Критерии приёмки

- AC-001 Корневой валидатор подтверждает целостность канонической AI-инфраструктуры.
- AC-002 Project-overlay validator выявляет неполный КАРКАС и точные дубликаты глобальных capabilities без изменения проверяемого repository.
- AC-003 Активный repository можно подключить одной ограниченной project delta без копирования generic agents и workflow.
- AC-004 Brownfield reconciliation read-only, идемпотентен и не меняет product code или Git status.
- AC-005 Reconciliation report содержит классификацию, compatibility matrix и различает pre-existing failures и regressions.
- AC-006 Stage/task/merge нельзя объявить завершённым, пока state-bearing документы не проверены,
  изменившиеся факты не синхронизированы, а неизменённые документы не признаны актуальными.
- AC-007 Ни один stage со ссылкой на будущий prerequisite, неисполняемым основным slice,
  отсутствующим end-to-end PASS evidence или mock/stub-only путём не имеет статуса
  `completed`, `verified` или `DONE`.
- AC-008 Канонический stage contract, planning/execution Skills, templates и status workflow
  структурно согласованы и не превращают tests или status documents в источник требований.

## 4. История изменений

- 2026-08-13 — создана начальная системная SPEC для модели `global framework → project overlay`.
- 2026-08-26 — добавлен обязательный Completion Documentation Synchronization Gate.
- 2026-08-27 — добавлен контракт архитектурно завершённых этапов и непротиворечивого контекста.
