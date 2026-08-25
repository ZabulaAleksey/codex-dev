# Карта зависимостей глобального контекста Codex

Дата проверки: 2026-08-25.

## Поток контекста

```text
~/.codex/AGENTS.md
  ├─ локальный project AGENTS.md (более специфичная delta)
  ├─ rules/README.md
  │    ├─ mode
  │    ├─ SDLC
  │    ├─ domain
  │    └─ stack
  ├─ skill trigger
  │    ├─ skill-sources/<skill>/SKILL.md
  │    └─ references/scripts только по workflow
  ├─ hooks.json
  │    └─ hooks/*.py → bounded session context / guard
  └─ agents/*.toml → специализированные субагенты
```

Приоритет: system/developer → наиболее локальный `AGENTS.md` → global `~/.codex/AGENTS.md`. Project repository наследует global router напрямую и хранит только локальную delta.

## Источники истины

| Область | Канон | Производные |
|---|---|---|
| Global instructions | `AGENTS.md` | README/диаграммы |
| Engineering rules | `rules/**` | summaries в docs |
| Skill workflow | `skill-sources/**` | `~/.agents/skills/**` |
| Hook wiring | `hooks.json`, `hooks/**` | session output |
| Current state/plan | `docs/AI_STATUS.md`, `docs/AI_PLAN.md` | handoff |
| Framework contract | `docs/PROJECT_FRAMEWORK.md`, `specs/**` | project overlay |
| Project facts | project repository | external projections |
| Project bindings | внешний project-aware слой | schema `PROJECT_REGISTRY.md` |

Notion, Eraser и другие внешние представления не заменяют Git-канон.

## Hook path

`hooks.json` выбирает скрипт. Hook определяет project root, читает только bounded набор существующих project-файлов, не следует наружу по symlink и не подмешивает глобальную библиотеку целиком. События additive: project hook допустим лишь для доказанного локального gap.

## Rules path

`rules/README.md` является индексом. Global router выбирает минимальный набор:

1. режим;
2. текущий SDLC stage;
3. релевантный domain;
4. применимый stack;
5. fallback/security правила по риску.

Для backend/runtime developer workflow router дополнительно подключает
`rules/backend-dx.md`; этот файл ссылается на dependency, database/API, testing,
security и fallback owners вместо их копирования.

Project-local rules не копируют глобальные запреты и не меняют global Git workflow.

## Skills path

`skill-sources/**` — versioned source. `tools/sync_global_skills.py` создаёт runtime projection в `~/.agents/skills/**`; `tools/validate_global_codex.py` сравнивает hashes. Ручная правка runtime projection создаёт drift.

`dev-karkas` читает только требуемые references. `backend-dx-audit` читает один
canonical `rules/backend-dx.md`, классифицирует `BDX-L0..L3` и сохраняет только
project delta в `docs/project-context.md`. `PROJECT_REGISTRY.md` задаёт
schema/discovery policy и намеренно не содержит actual project names, IDs или absolute paths.

## Subagents

`agents/*.toml` задают универсальные роли. Orchestrator делегирует bounded ownership и после завершения объединяет результаты. Project-specific специалисты живут только в project repository; generic role не должен включать продуктовый roadmap.

## MCP/plugins

`docs/MCP_CATALOG.md` описывает capability и security boundary. Фактическое включение задаёт machine-local config/runtime. Неустановленный или отключённый connector не считается обязательной зависимостью. Secrets и OAuth tokens не входят в tracked context.

## Documents

Канонические `docs/*.md` хранят только устойчивые global contracts и единственные AI plan/status. Дополнительные долговечные материалы находятся в `docs/notes/` и читаются on demand. Новая тема сначала пытается дополнить существующий канон; отдельный note создаётся только при отсутствии подходящего owner.

## Specifications/templates/tools

```text
requirements
  → specs/**
  → architecture/plan
  → implementation
  → tests
  → validators
  → MANIFEST.txt
```

`templates/**` не содержат project names. `BACKEND_DX_DELTA_TEMPLATE.md` задаёт
только форму project facts, а полная policy остаётся в `rules/backend-dx.md`.
`tools/reconcile_project_framework.py` только анализирует выбранный repository и не перезаписывает более свежий living contract.

## Runtime boundary

Не входят в active governance: credentials, `config.toml`, sessions, SQLite, caches, downloaded plugins, attachments, logs и generated artifacts. `.gitignore` использует deny-by-default allowlist, чтобы эти данные не попали в Git.

## Project boundary

Product repositories находятся непосредственно под `~/codex-workspace/*`, являются независимыми Git roots и наследуют `~/.codex/AGENTS.md`. Global repository не хранит их inventory, roadmap, design, agents или Skills.

Project-specific материалы без доказанного destination остаются quarantine/`BLOCKED`; они не подключены к router, hooks или installer. Удаление разрешено только после preservation + exact/semantic verification.

## Изменение глобального контекста

```text
change
  ├─ update canonical owner
  ├─ update all references
  ├─ regenerate MANIFEST.txt
  ├─ validate_context.py
  ├─ sync + Skill parity
  ├─ unit tests
  ├─ broken-reference scan
  └─ contamination scan
```

Recovery point сохраняется до интеграции и повторной проверки. Внешняя запись требует отдельного read-back; если read-back не прошёл, источник не удаляется.
