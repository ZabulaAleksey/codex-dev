# Архитектура AI Dev Team

## Назначение и границы

`~/.codex` — канонический Git repository общей AI-инфраструктуры и одновременно active operational layer Codex. `agents/`, `hooks/` и `rules/` используются непосредственно. Versioned source Skills находится в `skill-sources/`, а единственная active runtime-проекция — в `~/.agents/skills/`. `docs/`, `templates/`, `tools/` и `specs/` образуют project-agnostic инженерную библиотеку. Project-specific контекст хранится только в независимых repositories под `~/codex-workspace/*`.

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

`tools/validate_project_overlay.py` принимает ровно один target repository. Он проверяет независимый Git-root, канонические документы, альтернативные status-файлы, точные копии глобальной automation и compatibility audit. Инструмент не пишет в target и не меняет Git-конфигурацию: `safe.directory` передаётся только конкретному процессу Git через `-c`.

`tools/reconcile_project_framework.py` является отдельным read-only gate перед bootstrap/refresh.
Он классифицирует target как `GREENFIELD` или `BROWNFIELD`, строит deterministic compatibility
matrix, принимает explicit conflict resolutions и сравнивает test baseline с post-refresh run.
Он не пишет файлы, не выполняет product code и не изменяет Git status.

`tools/validate_context.py` отдельно проверяет manifest самого ДЕВ.
`tools/validate_project_overlay.py` запускается для одного явно выбранного repository;
ДЕВ не хранит live inventory product repositories. Текущие этапы, blockers
и другие сведения о состоянии продукта принадлежат самому product repository.

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

`install-global.ps1` проверяет каноническое расположение repository и не перезаписывает активный `config.toml`. `tools/normalize_user_codex.py` выполняет ограниченную, идемпотентную и предварительно валидируемую нормализацию пользовательского TOML без вывода секретов. `tools/validate_global_codex.py` проверяет managed-файлы активного слоя и статические границы безопасности.

Host-managed runtime bindings не подменяются угаданными путями: отсутствующая browser service удаляется, `sky` binding сохраняется, а browser client hash допускается только при совпадении с фактически установленным client-файлом.

## Policy layer

Сквозные инженерные policies находятся в `rules/`.

Fallback/retry/degradation contract:

`rules/fallback-policy.md`

Project-specific implementation:

`~/codex-workspace/<project>/docs/FALLBACKS.md`

Архитектура проекта определяет компоненты, границы состояния,
idempotency/recovery interfaces и места возможной деградации,
но не дублирует общий fallback contract.
