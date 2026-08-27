# Архитектура AI Dev Team

## Назначение и границы

`~/.codex` — канонический Git repository общей AI-инфраструктуры и одновременно active operational layer Codex. `agents/`, `hooks/` и `rules/` используются непосредственно. Versioned source Skills находится в `skill-sources/`, а единственная active runtime-проекция — в `~/.agents/skills/`. `docs/`, `templates/`, `tools/` и `specs/` образуют project-agnostic инженерную библиотеку. Project-specific контекст хранится только в независимых repositories под `~/codex-workspace/*`.

`~/codex-workspace/global/codex` не является source root и не создаётся как installed-копия.

| Слой | Путь | Роль |
|---|---|---|
| Global canonical + direct operational layer | `~/.codex` | Git, AGENTS, agents, hooks, rules, docs, tools, templates, specs |
| Versioned Skill source | `~/.codex/skill-sources` | единственный редактируемый source reusable Skills |
| Managed Skill runtime | `~/.agents/skills` | hash-verified materialization; не второй lifecycle/source |
| Product repositories | `~/codex-workspace/<project>` | независимый Git root и project-specific overlay |

## Project-framework контур

```text
SPEC и workspace policy
        ↓
тонкий project AGENTS.md + project docs/specs
        ↓
read-only validator
        ↓
детерминированный human/JSON результат
```

`tools/validate_project_overlay.py` принимает ровно один target repository. Он проверяет независимый Git-root, канонические документы, альтернативные status-файлы, точные копии глобальной automation, compatibility audit и определимый dependency drift (manager/lockfile, tracked generated directories, dependency source of truth и clean restore). Для явно объявленного `Backend DX Delta` он дополнительно проверяет applicability, project command/config/service contract, policy route, safe `.env.example`, guarded reset и generated-contract drift; проекты без delta не классифицируются эвристически. Dependency discovery охватывает Git-visible manifests в корне и вложенных `apps/*`/`web/*`, включая multi-ecosystem repositories, но исключает ignored/generated и вложенные upstream assets. Инструмент не пишет в target и не меняет Git-конфигурацию: `safe.directory` передаётся только конкретному процессу Git через `-c`.

`tools/reconcile_project_framework.py` является отдельным read-only gate перед bootstrap/refresh.
Он классифицирует target как `GREENFIELD` или `BROWNFIELD`, строит deterministic compatibility
matrix, принимает explicit conflict resolutions, добавляет read-only dependency inventory/drift и сравнивает test baseline с post-refresh run.
Он не пишет файлы, не выполняет product code и не изменяет Git status.

Единый lifecycle workflow использует существующие owners:

```text
user lifecycle intent
      ↓
docs/WORKFLOW.md (copy-ready operational request)
      ↓
rules/governance.md + SPEC (canonical contract)
      ↓
project AGENTS / STAGES / AI_PLAN / AI_STATUS
      ↓
implementation + evidence + documentation gate
      ↓
optional external projection after approval/read-back
```

Чат и `docs/WORKFLOW.md` не становятся требованиями: они только маршрутизируют к SPEC/governance.
Context recovery следует Git → global instructions → project overlay → state/plan → selected
contracts/evidence. External service outage даёт visible pending sync, а не обратную запись в Git.

Stage lifecycle проходит через отдельный policy/evidence contour:

```text
SPEC requirement
      ↓
prompts/STAGES.md: DAG + prerequisites + runnable slice + E2E + PASS/evidence
      ↓
docs/AI_PLAN.md: текущий ограниченный slice
      ↓
implementation → unit/integration/component → concrete end-to-end path
      ↓
lifecycle status + evidence level → documentation synchronization
```

Task-aware context projection использует обратную ссылку из активного плана:

```text
docs/AI_PLAN.md: stable Stage ID
      ↓ exact unique heading selector
hooks/session_context.py → bounded selected prompts/STAGES.md record first
      ↓ invalid / missing / ambiguous / oversized
visible DEGRADED warning → manual full-record check → no completion claim до проверки
```

Selector не является semantic parser: он не выводит dependency DAG, не проверяет prerequisites и
не объявляет stage завершённым. Без `Stage ID` hook сохраняет обычный compact project snapshot и
не загружает stage catalog.

Полным владельцем stage contract является `rules/governance.md`. Skills и templates только
маршрутизируют к нему и собирают операционные поля. `tools/test_stage_completion_policy.py`
структурно проверяет согласованность глобальных policy surfaces; он не подменяет runtime evidence
конкретного product repository.

`tools/validate_context.py` отдельно проверяет manifest самого ДЕВ.
`tools/validate_project_overlay.py` запускается для одного явно выбранного repository;
ДЕВ не хранит live inventory product repositories. Текущие этапы, blockers
и другие сведения о состоянии продукта принадлежат самому product repository.

Project-overlay validator остаётся детерминированным structural gate: он не объявляет stage
архитектурно завершённым по наличию headings и не интерпретирует mock/stub как production evidence.
Dependency DAG, исполнимость slice и истинность end-to-end результата подтверждаются stage evidence
и review. Отдельный semantic parser потребует versioned schema и migration существующих STAGES;
точный heading selector только проецирует явно выбранный record и не вводит такую эвристику.

## Потоки и интерфейсы

- Вход validator: путь repository и опциональный `--json`.
- Источник глобальных fingerprints: `AGENTS.md`, `agents`, `hooks`, `skill-sources`, `rules` и `docs/WORKFLOW.md`.
- Выход: код `0` при полном соответствии, `1` со стабильным отсортированным списком issues при нарушении.
- Внешняя зависимость: только executable `git`; остальная реализация использует Python standard library.

## Контур глобального runtime Codex

```text
~/.codex (канон в Git + активный runtime-слой)
        ↓ read-only validation
managed-файлы + безопасные инварианты config.toml
```

`install-global.ps1` проверяет каноническое расположение repository и не перезаписывает активный `config.toml`. `tools/normalize_user_codex.py` выполняет ограниченную, идемпотентную и предварительно валидируемую нормализацию пользовательского TOML без вывода секретов. `tools/validate_global_codex.py` проверяет managed-файлы активного слоя и статические границы безопасности. Legacy option `--workspace` означает canonical source root (обычно `~/.codex`), а не parent product workspace; отсутствующий source возвращает структурированную issue вместо exception.

Host-managed runtime bindings не подменяются угаданными путями: отсутствующая browser service удаляется, `sky` binding сохраняется, а browser client hash допускается только при совпадении с фактически установленным client-файлом.

## Policy layer

Сквозные инженерные policies находятся в `rules/`.

Lifecycle/evidence и архитектурная завершённость stages:

```text
specs/system.spec.md (FR-007 / AC-007)
        ↓
rules/governance.md (канонический Stage contract)
        ↓
dev-karkas + plan-stage + implement-stage + templates (операционные проекции)
        ↓
project evidence и review
```

Fallback/retry/degradation contract:

`rules/fallback-policy.md`

Dependency manager/cache/lockfile contract:

`rules/dependency-management.md`

Backend developer workflow contract:

```text
rules/backend-dx.md
        ↓ procedural execution
skill-sources/backend-dx-audit/SKILL.md → ~/.agents/skills/backend-dx-audit
        ↓ project-specific facts
docs/project-context.md / Backend DX Delta
        ↓ read-only evidence
tools/validate_project_overlay.py + neutral fixture tests
```

Backend DX ссылается на dependency, database/API, testing, security и fallback
contracts, но не становится вторым владельцем их предметных инвариантов.

Project-specific implementation:

`~/codex-workspace/<project>/docs/FALLBACKS.md`

Архитектура проекта определяет компоненты, границы состояния,
idempotency/recovery interfaces и места возможной деградации,
но не дублирует общий fallback contract.
