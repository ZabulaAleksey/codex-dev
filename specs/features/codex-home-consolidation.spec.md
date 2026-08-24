# SPEC: консолидация ДЕВ в `~/.codex`

Дата: 2026-08-23
Статус: SUPERSEDED — консолидация завершена; repository boundary уточнена 2026-08-24

> Исторический SPEC миграции. Упоминания project-named `presets/` описывают состояние на момент переноса и больше не являются активным требованием. Текущий contract: global `~/.codex` хранит только project-agnostic framework; project-specific контекст принадлежит project repository, а неоднозначный источник сохраняется только как `BLOCKED` quarantine до безопасной миграции.

## Цель

Сделать `~/.codex` единственным каноническим и versioned корнем ДЕВ / КАРКАСА, устранив разделение между repository в `~/codex-workspace` и установленным пользовательским слоем Codex.

## Scope

- перенести Git repository общей AI-инфраструктуры в `~/.codex`;
- объединить `~/.codex/AGENTS.md` и `~/.codex/AGENTS.md` в один канонический `~/.codex/AGENTS.md`;
- разместить общие agents, hooks, Skills, engineering rules, docs, presets, templates, tools и SPEC внутри `~/.codex`;
- сохранить рабочие product repositories в `~/codex-workspace/<project>` как независимые Git roots;
- обновить активные ссылки в global/project rules, hooks, Skills, validators и документации;
- исключить runtime-файлы Codex, секреты, sessions, cache и базы данных из Git;
- проверить каждый существующий project repository на конфликт с новым глобальным каноном.

## Non-goals

- перенос или изменение product-кода;
- исправление ранее существовавших project overlay gaps, не связанных со ссылками на глобальный ДЕВ;
- удаление runtime-данных Codex;
- merge, push или изменение remote без отдельного разрешения.

## Требования

### FR-CH-001 Единый канон

`~/.codex/AGENTS.md` является единственным глобальным router. Общие agents, hooks, Skills, rules и документы не должны иметь вторую каноническую копию в `~/codex-workspace`.

### FR-CH-002 Раздельные границы

`~/.codex` хранит ДЕВ и активный пользовательский слой Codex. `~/codex-workspace/*` хранит независимые product repositories. Project-specific `.codex` и `.agents` остаются внутри соответствующих repositories.

### FR-CH-003 Git safety

Git repository ДЕВ должен отслеживать только управляемые файлы. `auth.json`, `config.toml`, secrets, sessions, attachments, logs, SQLite state, caches, plugins и другие host/runtime artifacts должны быть проигнорированы.

### FR-CH-004 Ссылочная целостность

Активные ссылки на global `AGENTS.md`, `rules/`, `docs/`, `tools/`, `templates/`, `presets/`, `specs/`, hooks и Skills должны указывать на `~/.codex`. Пути к product repositories остаются `~/codex-workspace/<project>`.

### FR-CH-005 Совместимость проектов

Локальные project rules сохраняют приоритет над `~/.codex/AGENTS.md` и содержат только project-specific delta. Существующие локальные agents, Skills, hooks и configs не перезаписываются.

### NFR-CH-001 Обратимость

Перенос выполняется с сохранением Git history и текущего index. Исходные runtime-данные не удаляются. Откат versioned части возможен через Git; product repositories остаются на месте.

## Acceptance criteria

- `git rev-parse --show-toplevel` из `~/.codex` возвращает `~/.codex`;
- `~/codex-workspace` больше не является внешним Git root, а все product repositories сохраняют собственные `.git`;
- в `~/.codex` существует один объединённый `AGENTS.md` без ссылки на старый global router;
- active global links разрешаются в существующие пути под `~/.codex`;
- поиск не находит устаревших ссылок `~/codex-workspace/{AGENTS.md,rules,docs,tools,templates,presets,global,specs,backlog}` в managed context и project repositories;
- Git ignore не допускает tracking runtime/secrets;
- unit, context, global-layer и project-overlay проверки проходят либо имеют явно зафиксированный pre-existing finding без новой regression;
- каждый Git repository под `~/codex-workspace` проверен read-only; его исходный dirty status сохранён.

## Откат

До удаления старого Git metadata проверяется новый root и полный status. При неуспешной валидации канонический repository возвращается в `~/codex-workspace`; product repositories и runtime-файлы не затрагиваются.
