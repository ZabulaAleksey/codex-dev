# Системная спецификация AI Dev Team Codex

Статус: Действует
Версия: 1.6

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
выбранный stage record из `prompts/STAGES.md` и относящиеся к задаче документы; весь stage catalog
не загружается автоматически. Автоматическая проекция использует единственный stable `Stage ID`
из самого `prompts/STAGES.md` и exact unique heading; ошибка явного selector должна быть видимой деградацией,
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
следующие действия. Обязательный минимум: `README.md`, `prompts/STAGES.md`,
`docs/ROADMAP.md` и затронутые канонические документы.

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

### FR-008 Единый воспроизводимый workflow проекта

Глобальный ДЕВ должен предоставлять один операционный workflow для начала проекта, выполнения и
закрытия stage, архитектурного изменения, pre-merge review, паузы, возобновления и обработки новой
идеи. Готовые пользовательские запросы являются проекцией канонического governance, а не вторым
источником требований.

Новый Codex-сеанс должен восстанавливать состояние из Git, глобального ДЕВ, project overlay,
`README.md`, selected/current record из `prompts/STAGES.md`, архитектурных документов и релевантных записей
`LEARNING_LOG.md`. Старый чат и machine-local файлы не являются обязательной предпосылкой.
Перенос между компьютером и ноутбуком выполняется через независимые Git repositories, штатную
установку/валидацию глобального ДЕВ и восстановление project dependencies/secrets; ручное
копирование отдельных context-файлов не является основным механизмом.

### FR-009 Ответственность источников, projections и monitoring

Каждый тип информации должен иметь одного назначенного владельца. External service по умолчанию
является derived projection; он может владеть только явно назначенным ограниченным внешним
артефактом, если project mapping фиксирует направление синхронизации и repository-ссылку.
Сначала изменяется канонический источник, затем зависимые representations. Недоступная projection
получает `pending sync`/`BLOCKED`, но не меняет repository truth.

Project monitoring классифицируется как `active`, `event-driven` или `frozen` без создания
глобального live inventory. `LEARNING_LOG.md` получает только evidence-backed повторно полезные
записи в едином формате `Problem / Symptom / Root cause / Failed attempts / Fix / Verification /
Prevention / Links` и не дублирует Git history либо `prompts/STAGES.md`.

### FR-010 Глобальная готовность пользовательских продуктов к i18n / l10n

Каждый продукт с пользовательской поверхностью должен наследовать один глобальный архитектурный
контракт internationalization (`i18n`) и localization (`l10n`). `i18n` обеспечивает добавление
языков и локалей без переписывания business logic и компонентов; `l10n` адаптирует конкретные
resources, formats и региональное поведение. `language` и `locale` различаются: например, `en-US`
и `en-GB` используют один язык, но разные региональные правила.

Пользовательские строки должны находиться в translation resources (`t("...")`, locale-файлы или
stack equivalent), а locale-dependent представление должно учитывать даты/время, числа, валюты,
единицы, plural rules, sorting/collation, адреса/телефоны, часовые пояса и применимые региональные
данные. Проект обязан задать fallback locale, поведение неполного перевода, text expansion и RTL,
когда такие языки заявлены.

Project SPEC/DESIGN/architecture хранят только поддерживаемые locales, реализацию, исключения и
acceptance evidence. Начальный stage может выпускать одну production locale, только если реальная
resource/fallback infrastructure и pseudo-locale либо alternate test locale уже доказывают
расширяемость без будущего обязательного компонента.

### FR-011 Единый canonical execution state

Active full staged overlay хранит selector, current plan, lifecycle/evidence, blockers и NEXT в
единственном `prompts/STAGES.md`. Отдельные `AI_PLAN.md`, `AI_STATUS.md`, `PLAN.md`, `STATUS.md`,
`PROGRESS.md` и эквивалентные project-state owners после миграции запрещены. Brownfield migration
сначала семантически объединяет актуальное содержание и проверяет ссылки/evidence, затем удаляет
legacy files; global tooling не выполняет такую cleanup mutation автоматически.

### FR-012 Continuous Master Execution

После одного явного запуска `master_prompt` global DEV должен уметь детерминированно продолжать
последовательность dependency-ready backward-complete slices без нового пользовательского prompt
между безопасными однозначными шагами. Durable graph/track/checkpoint/evidence/NEXT сохраняются в
selected record канонического `prompts/STAGES.md`; отдельный task/status owner не создаётся.

Continuation переиспользует текущий track/worktree, независимый write-track изолируется отдельной
branch/worktree, а read-only задача не создаёт isolation механически. Critical unverified
dependency, user decision, external input, destructive/integration write, canonical conflict,
hard blocker и context budget overflow являются fail-visible stop conditions. Handoff восстанавливает
новую сессию из Git/repository evidence; merge/push/release и cleanup остаются approval-gated.

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
- AC-009 Единственный Git-канон глобального ДЕВ находится непосредственно в `~/.codex`;
  `~/codex-workspace/global/codex` не является поддерживаемым source root, а `~/.agents/skills`
  остаётся только hash-verified runtime projection.
- AC-010 `docs/WORKFLOW.md` содержит copy-ready запросы для восьми lifecycle-сценариев,
  cross-device handoff и ссылки на один канонический documentation/learning contract без его
  копирования в project overlays.
- AC-011 Governance однозначно назначает владельцев информации, триггеры документации,
  направления external sync и monitoring classes; недоступный внешний сервис не выдаётся за
  синхронизированный.
- AC-012 Global validator возвращает структурированную ошибку для неверного canonical source root,
  а не необработанный exception; read-only восстановление выбранного real project возвращает
  честный `PASS`, `DEGRADED` или `BLOCKED` с evidence без старого чата.
- AC-013 Единственный глобальный i18n/l10n contract маршрутизируется во все user-facing product
  architectures без копирования в project overlay; contract test подтверждает различие
  `language`/`locale`, resource-based строки, locale-aware форматы, fallback locale, text expansion,
  RTL и самостоятельный initial slice, не зависящий от будущей translation infrastructure.
- AC-014 `prompts/STAGES.md` является единственным execution-state owner; hook и validator читают
  selector из этого же файла, greenfield templates не создают AI plan/status pair, а read-only
  reconciliation даёт deterministic migration path существующим проектам.
- AC-015 Continuous master controller выбирает готовые slices по dependency/evidence contract,
  маршрутизирует continuation/parallel tracks, создаёт bounded handoff при context overflow и
  сохраняет partial master, не выполняя merge/push/worktree cleanup автоматически.

## 4. История изменений

- 2026-08-13 — создана начальная системная SPEC для модели `global framework → project overlay`.
- 2026-08-26 — добавлен обязательный Completion Documentation Synchronization Gate.
- 2026-08-27 — добавлен контракт архитектурно завершённых этапов и непротиворечивого контекста.
- 2026-08-27 — формализован единый project workflow, source ownership, cross-device restore,
  external projections, monitoring и единый формат learning evidence.
- 2026-08-27 — добавлен межпроектный i18n/l10n contract для всех пользовательских продуктов.
- 2026-09-08 — execution state, selector, blockers/evidence и NEXT консолидированы в единственном
  `prompts/STAGES.md`; отдельные AI plan/status sources выведены из canonical workflow.
- 2026-09-08 — добавлен portable Continuous Master Execution contract с deterministic graph,
  worktree routing, low-context handoff и verification/integration gates.
