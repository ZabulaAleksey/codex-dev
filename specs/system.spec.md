# Системная спецификация AI Dev Team Codex

Статус: Действует
Версия: 1.0

## 1. Назначение

AI Dev Team предоставляет один переиспользуемый пользовательский слой Codex для нескольких независимых Git-репозиториев в `~/codex-workspace/projects/*`.

## 2. Системные требования

### FR-001 Единое глобальное ядро

Общие agents, Skills, hooks, rules, MCP-рекомендации и Git workflow должны иметь один канонический источник непосредственно в `~/.codex` и не дублироваться отдельным installed-слоем.

### FR-002 Проект как overlay

Каждый рабочий repository должен хранить только проектные требования, архитектуру, состояние и подтверждённые локальные расширения общей AI Dev Team.

### FR-003 Независимые репозитории

Каждый каталог верхнего уровня в `~/codex-workspace/projects/` должен быть самостоятельным Git-репозиторием. Git repository ДЕВ в `~/.codex` не должен отслеживать их содержимое или runtime state Codex.

### NFR-001 Минимальный контекст

Codex должен загружать ближайшие инструкции и только относящиеся к задаче правила, SPEC и документы состояния.

### NFR-002 Безопасное изменение

Установщики и rollout не должны без явного разрешения перезаписывать пользовательские настройки, продуктовый код или незавершённые изменения проекта.

### FR-004 Brownfield Reconciliation Gate

Перед bootstrap/refresh repository классифицируется как `GREENFIELD` или `BROWNFIELD`. Для
`BROWNFIELD` read-only reconciler формирует compatibility matrix со статусами `KEEP`, `ADD`,
`ADAPT`, `MERGE`, `CONFLICT`, `SUPERSEDED`, `FORBIDDEN_TO_OVERWRITE`. Unresolved `CONFLICT`
блокирует соответствующую mutation, `FORBIDDEN_TO_OVERWRITE` запрещает автоматическую запись.

### FR-005 Baseline regression contract

До refresh фиксируется baseline тестов. Pre-existing failures сохраняются отдельно; новый failure
после refresh является regression и проваливает gate.

## 3. Критерии приёмки

- AC-001 Корневой валидатор подтверждает целостность канонической AI-инфраструктуры.
- AC-002 Project-overlay validator выявляет неполный КАРКАС и точные дубликаты глобальных capabilities без изменения проверяемого repository.
- AC-003 Активный repository можно подключить одной ограниченной project delta без копирования generic agents и workflow.
- AC-004 Brownfield reconciliation read-only, идемпотентен и не меняет product code или Git status.
- AC-005 Reconciliation report содержит классификацию, compatibility matrix и различает pre-existing failures и regressions.

## 4. История изменений

- 2026-08-13 — создана начальная системная SPEC для модели `global framework → project overlay`.
