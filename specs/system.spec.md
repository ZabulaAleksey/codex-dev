# Системная спецификация AI Dev Team Codex

Статус: Действует
Версия: 1.9

## 1. Назначение

AI Dev Team предоставляет один переиспользуемый пользовательский слой Codex для явно
подключённых независимых Git-репозиториев `${PROJECTS_ROOT}/<project>`. Filesystem discovery не
означает policy inheritance.

## 2. Системные требования

### FR-001 Единое глобальное ядро

Общие agents, Skills, hooks, rules, MCP-рекомендации и Git workflow должны иметь один versioned
canonical source Git repository, отдельный от `~/.codex`. Installed Codex home является
manifest-managed projection плюс protected runtime state. Runtime Skills в `~/.agents/skills`
допустимы только как hash-verified materialization `<dev-root>/skill-sources` и не являются вторым
source of truth.

### FR-002 Проект как overlay

Каждый рабочий repository должен хранить только проектные требования, архитектуру, состояние и подтверждённые локальные расширения общей AI Dev Team.

### FR-003 Независимые репозитории

Каждый product-каталог `${PROJECTS_ROOT}/<project>` должен быть самостоятельным Git-репозиторием.
Canonical DEV source разрешается через `DEV_SOURCE_ROOT` (default `~/codex-dev`), installed layer
через `CODEX_HOME` (default `~/.codex`), а product discovery через `PROJECTS_ROOT` (default `~`).
`CODEX_HOME` не должен содержать `.git` или отслеживать runtime state Codex. Product repository
принимает global DEV только через valid structured project-local `.codex/dev-project.toml`;
AGENTS declaration без marker недостаточна.

### NFR-001 Минимальный контекст

Codex должен загружать ближайшие инструкции и только относящиеся к задаче правила, SPEC,
выбранный stage record из `docs/STAGES.md` и относящиеся к задаче документы; весь stage catalog
не загружается автоматически. Автоматическая проекция использует единственный stable `Stage ID`
из самого `docs/STAGES.md` и exact unique heading; ошибка явного selector должна быть видимой деградацией,
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
следующие действия. Обязательный минимум: `README.md`, `docs/STAGES.md`,
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
`README.md`, selected/current record из `docs/STAGES.md`, архитектурных документов и релевантных записей
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
Prevention / Links` и не дублирует Git history либо `docs/STAGES.md`.

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
единственном `docs/STAGES.md`. Отдельные `AI_PLAN.md`, `AI_STATUS.md`, `PLAN.md`, `STATUS.md`,
`PROGRESS.md` и эквивалентные project-state owners после миграции запрещены. Brownfield migration
сначала семантически объединяет актуальное содержание и проверяет ссылки/evidence, затем удаляет
legacy files; global tooling не выполняет такую cleanup mutation автоматически.

### FR-012 Continuous Master Execution

После одного явного запуска `master_prompt` global DEV должен уметь детерминированно продолжать
последовательность dependency-ready backward-complete slices без нового пользовательского prompt
между безопасными однозначными шагами. Durable graph/track/checkpoint/evidence/NEXT сохраняются в
selected record канонического `docs/STAGES.md`; отдельный task/status owner не создаётся.

Continuation переиспользует текущий track/worktree, независимый write-track изолируется отдельной
branch/worktree, а read-only задача не создаёт isolation механически. Critical unverified
dependency, user decision, external input, destructive/integration write, canonical conflict,
hard blocker и context budget overflow являются fail-visible stop conditions. Handoff восстанавливает
новую сессию из Git/repository evidence; merge/push/release и cleanup остаются approval-gated.

### FR-013 Brownfield canonical stage compatibility

Continuous Master Execution должен иметь один bounded read-only adapter для repositories, где
canonical `docs/STAGES.md` ещё сосуществует с legacy `docs/AI_PLAN.md` и
`docs/AI_STATUS.md` либо same-file selector отсутствует. Adapter детерминированно классифицирует
state, выдаёт dry-run migration plan и не запускает work при неоднозначности.

Завершённая migration подтверждается versioned compatibility block внутри selected STAGES record
с canonical projection и digests retained legacy sources. Product files не переписываются и не
удаляются автоматически; conflicting или drifted state требует explicit migration.

### FR-014 Unified path roles and explicit DEV adoption

Global DEV source, active runtime layer and product discovery root разрешаются только через
`DEV_SOURCE_ROOT`, `CODEX_HOME`, `PROJECTS_ROOT` общим resolver. Current defaults равны
`~/codex-dev`, `~/.codex`, `~`. Environment имеет приоритет над device-local config; ambiguity
fail closed. Product location не является inheritance signal: project DEV policy, Prompt Queue и
resume bootstrap требуют valid project-local `.codex/dev-project.toml` и проверяемый global
version/capability contract.

### FR-015 Replaceability by Design

Значимая external/vendor-bound подсистема или реалистично сменная implementation должна быть
отделена от domain/application logic system-owned port, canonical internal DTO/event и
anti-corruption adapter. Provider selection принадлежит composition root; vendor SDK/types,
secrets и provider-specific errors не протекают в domain/application/UI. Каждая реализация имеет
общий contract suite, а provider-owned durable state — export/import/migration/rollback и
fallback/degraded contract. YAGNI исключение допустимо только с evidence, что реальной замены,
vendor lock-in, alternate implementation, fake/emulator, migration или fallback need нет.

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
- AC-009 Единственный Git-канон глобального ДЕВ находится в отдельном canonical source repository;
  `~/.codex` является manifest-installed non-Git layer, а `~/.agents/skills` остаётся только
  hash-verified runtime projection.
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
- AC-014 `docs/STAGES.md` является единственным execution-state owner; hook и validator читают
  selector из этого же файла, greenfield templates не создают AI plan/status pair, а read-only
  reconciliation даёт deterministic migration path существующим проектам.
- AC-015 Continuous master controller выбирает готовые slices по dependency/evidence contract,
  маршрутизирует continuation/parallel tracks, создаёт bounded handoff при context overflow и
  сохраняет partial master, не выполняя merge/push/worktree cleanup автоматически.
- AC-016 Brownfield compatibility adapter различает canonical/legacy/mixed/conflict/migrated/none,
  возвращает idempotent non-destructive migration plan, fail closed при конфликте и сохраняет
  прежнее поведение canonical repositories.
- AC-017 Единый resolver проходит default/env/config/Windows tests; plain Git repository остаётся
  DEV-disabled, marked overlay включается, installer сохраняет runtime, Prompt Queue/`Продолжай`
  не зависят от legacy workspace path, diagnostics классифицирует legacy layout без mutations.
- AC-018 Единственный Replaceable Module Contract маршрутизируется через global router, rule index,
  dev-karkas architecture policy и project framework; он требует port/adapter/anti-corruption,
  composition-root selection, contract tests, migration/fallback/security evidence и разрешает
  YAGNI только с явным обоснованием. Structural test не выдаётся за product runtime evidence.

## 4. История изменений

- 2026-08-13 — создана начальная системная SPEC для модели `global framework → project overlay`.
- 2026-08-26 — добавлен обязательный Completion Documentation Synchronization Gate.
- 2026-08-27 — добавлен контракт архитектурно завершённых этапов и непротиворечивого контекста.
- 2026-08-27 — формализован единый project workflow, source ownership, cross-device restore,
  external projections, monitoring и единый формат learning evidence.
- 2026-08-27 — добавлен межпроектный i18n/l10n contract для всех пользовательских продуктов.
- 2026-09-08 — execution state, selector, blockers/evidence и NEXT консолидированы в единственном
  `docs/STAGES.md`; отдельные AI plan/status sources выведены из canonical workflow.
- 2026-09-08 — добавлен portable Continuous Master Execution contract с deterministic graph,
  worktree routing, low-context handoff и verification/integration gates.
- 2026-09-08 — добавлен контракт brownfield stage compatibility и retained-legacy manifest.
- 2026-09-13 — добавлен Replaceable Module Contract и межрепозиторный evidence audit.
- 2026-09-10 — добавлены unified path roles, explicit project DEV bridge и fail-closed migration
  diagnostics для target layout `~/codex-dev`, `~/.codex`, `~/<project>`.
