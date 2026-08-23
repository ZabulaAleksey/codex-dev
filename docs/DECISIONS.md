# Существенные решения

## 2026-08-20 — Brownfield Reconciliation Gate

- Решение: перед bootstrap/refresh классифицировать repository и для brownfield выполнять отдельный read-only reconciliation.
- Причина: фактическая реализация и результаты baseline-тестов должны сохраняться source of truth; шаблон не должен молча перезаписывать продуктовые решения.
- Статусы matrix: `KEEP`, `ADD`, `ADAPT`, `MERGE`, `CONFLICT`, `SUPERSEDED`, `FORBIDDEN_TO_OVERWRITE`.
- Последствие: unresolved `CONFLICT` блокирует mutation, а `FORBIDDEN_TO_OVERWRITE` запрещает автоматическую запись. После refresh новые baseline failures считаются regression.

## 2026-08-13 — Project overlay вместо копии AI Dev Team

- Решение: project хранит только локальные требования, документы и подтверждённые расширения.
- Причина: исключить drift и конфликт глобальных agents, Skills, hooks, rules и workflow.
- Альтернатива: копировать общий набор в каждый repository; отклонена из-за дублирования.
- Последствие: точная копия глобальной capability является ошибкой validator.

## 2026-08-13 — Один Markdown-каталог rollout

**Статус:** superseded 2026-08-20.

- Решение: использовать только `docs/PROJECT_CATALOG.md`.
- Причина: человеку нужен один источник lifecycle, blockers и следующего действия.
- Альтернатива: дополнительный JSON/YAML registry; отклонена как второй источник истины.

## 2026-08-13 — Read-only validator

- Решение: validator принимает путь одного repository, ничего не исправляет и поддерживает human/JSON output.
- Причина: проверка должна быть повторяемой и безопасной для независимых рабочих копий.
- Последствие: неполный или спорный repository получает issue; изменение выполняется отдельным этапом.

## 2026-08-20 — Один канонический контракт Fallback Policy

- Решение: общий контракт retry/fallback/degraded/fail-closed хранится только в `rules/fallback-policy.md`.
- Причина: fallback-правила не должны расходиться между agents, Skills, security docs и проектами.
- Проекты наследуют общий контракт и при необходимости создают только `docs/FALLBACKS.md` с предметной delta.
- `SECURITY.md` остаётся владельцем security invariants, `DECISIONS.md` — причин решений, `ARCHITECTURE.md` — границ и recovery interfaces.
- Silent fallback и fallback, ослабляющий security или evidence, запрещены.

## 2026-08-20 — ДЕВ не владеет live-статусом product repositories

**Статус:** принято.

**Решение:** AI Dev Team хранит общие инженерные правила, policies, validators,
project framework и reusable automation, но не хранит канонический live inventory
этапов, blockers или очереди отдельных product repositories.

Состояние конкретного продукта принадлежит его собственным `AI_STATUS`,
`AI_PLAN`, `ROADMAP` и другим project-specific источникам.

`validate_project_overlay.py` остаётся универсальным read-only инструментом,
который запускается для явно выбранного repository, но ДЕВ не обязан хранить
глобальную очередь таких repositories.

**Причина:** жизненный цикл общей инженерной инфраструктуры не должен зависеть
от состояния её потребителей.

**Последствия:**

- `docs/PROJECT_CATALOG.md` удаляется;
- blockers конкретных продуктов не входят в `docs/AI_STATUS.md` ДЕВ;
- product repository не становится следующим этапом ДЕВ;
- исторический pilot/forward-test может оставаться evidence в истории решений,
  если он действительно происходил;
- общие project-overlay rules и validator сохраняются.

## 2026-08-20 — Канон и runtime глобальной конфигурации разделены

**Статус:** superseded 2026-08-23 консолидацией в `~/.codex`.

**Решение:** прежний workspace source tree оставался единственным versioned source-of-truth для managed AGENTS, agents, hooks и rules. `~/.codex/config.toml` оставался runtime-specific и менялся только ограниченным идемпотентным normalizer; installer не перезаписывал его целиком.

**Причина:** слепая синхронизация теряла полезные local deltas, а полное сохранение installed-файлов закрепляло drift, Unicode defect и небезопасные настройки.

**Последствия:**

- reviewed model pins и routing сначала попадают в канон;
- `-SyncManaged` является явным режимом синхронизации;
- plugin имеет приоритет над дублирующим static MCP;
- inline secrets и broad trust являются validation errors;
- host-managed browser paths/hashes не угадываются;
- внешняя ротация credential и интерактивный trust hooks не автоматизируются.

## 2026-08-23 — `~/.codex` является Git-корнем и единственным каноном ДЕВ

**Решение:** перенести versioned AI Dev Team в `~/.codex` и использовать
`AGENTS.md`, `agents/`, `hooks/`, `skills/` и `rules/` непосредственно из активного
пользовательского слоя Codex. Product repositories остаются независимыми Git roots
в `~/codex-workspace/projects/*`.

**Причина:** прежняя схема «канон в `~/codex-workspace` → installed-копия в
`~/.codex` / `~/.agents`» создавала drift и два конфликтующих `AGENTS.md`.

**Альтернативы:**

- оставить installer и две копии — отклонено из-за повторного drift;
- поместить repository в `~/.codex/dev` — отклонено, потому что глобальный
  `AGENTS.md`, hooks и agents снова оказались бы вне Git root либо потребовали бы копирования.

**Последствия:**

- runtime state, secrets, sessions, plugins, cache и `config.toml` исключены из Git;
- engineering Markdown rules сосуществуют с runtime `.rules` в `~/.codex/rules`;
- project overlays ссылаются на `~/.codex`, но не копируют глобальную automation;
- `install-global.ps1` стал проверкой canonical placement, а не copy/sync installer;
- откат versioned части выполняется Git, runtime state не затрагивается.
