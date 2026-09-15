# Canonical STAGES.md Policy

Статус: утверждена пользователем 2026-09-08 на основе Notion prompt
`DEV — Astra prompt — Canonical STAGES.md Policy — 2026-09-07`.
Source page: `https://app.notion.com/p/3d461ed8f24681059594f00e38ab3c82?pvs=204`.

## 1. Цель

Для active full staged project overlay существует один канонический источник execution state:
`docs/STAGES.md`. Он одновременно хранит выбор текущего stage, порядок и contracts stages,
lifecycle/evidence, blockers и следующий конкретный шаг. Отдельные `AI_PLAN.md`, `AI_STATUS.md`,
`PLAN.md`, `STATUS.md` и эквивалентные project-state документы не являются частью нового канона.

## 2. Scope

Входит:

- global governance, router, framework docs, Skills и templates;
- SessionStart/SubagentStart selector и project-overlay validator;
- read-only brownfield reconciliation и deterministic migration contract;
- presets и regression tests, принадлежащие global DEV;
- миграция собственного состояния global DEV в `docs/STAGES.md`.

Не входит:

- массовая mutation product repositories;
- переписывание project-specific architecture;
- автоматическое удаление legacy state files;
- изменение active `~/.codex/config.toml`, runtime state или external services;
- merge, push, release и deployment.

## 3. Functional requirements

### CSP-001 Единственный execution-state owner

Full staged overlay использует только `docs/STAGES.md` для current selector, текущего плана,
stage lifecycle/evidence, blockers и NEXT. `SPEC`, `ROADMAP`, `ARCHITECTURE`, `DECISIONS`,
`LEARNING_LOG` и Git сохраняют собственные роли и не становятся competing execution state.

### CSP-002 Machine-readable selector

`docs/STAGES.md` содержит ровно одну unfenced строку `- Stage ID: <stable-id>` и ровно один
unfenced Markdown heading с этим ID как отдельным token. Missing, invalid, ambiguous или oversized
input даёт visible `DEGRADED`/validator failure. Hook загружает только exact selected record, а не
весь catalog.

### CSP-003 Повторяемая структура stage

Каждый активный stage хранит рядом с собой ordered sequence, compact status
`planned | implemented | verified | partial | blocked | unavailable`, dependencies/entry evidence, runnable slice,
scope/non-goals, blockers, acceptance/PASS evidence и NEXT/deferred. Lifecycle и evidence level
остаются разными осями. `STAGES.md` не становится action log: исторические подробности принадлежат
Git, `CHANGELOG` или `DEV_LOG`, когда такой журнал действительно нужен.

### CSP-004 Greenfield/bootstrap

Новые full staged overlays получают `docs/STAGES.md` из единственного template и не создают
`docs/AI_PLAN.md` или `docs/AI_STATUS.md`. Router, Skills и framework documentation маршрутизируют
state updates только в `docs/STAGES.md`.

### CSP-005 Brownfield migration

До mutation выполняется read-only reconciliation существующих `docs/STAGES.md`,
`prompts/STAGES.md` (прежний владелец состояния и только migration input),
`AI_PLAN.md`, `AI_STATUS.md`, `PLAN.md`, `STATUS.md`, `PROGRESS.md` и эквивалентов. Актуальные facts,
plans, blockers и evidence семантически объединяются в `docs/STAGES.md`; conflicting claims
разрешаются по repository/test evidence и freshness. Legacy files удаляются только после content/
link audit, успешного validator и подтверждения отсутствия утраты актуального содержания.

Reconciliation остаётся read-only и классифицирует legacy state files как `MERGE`, а существующий
`docs/STAGES.md` — `KEEP`, `ADAPT` или `MERGE` по brownfield rules. Product code и unknown files
остаются `FORBIDDEN_TO_OVERWRITE`.

### CSP-006 Validation

Full-overlay validator требует `docs/STAGES.md`, отклоняет competing execution-state files и
проверяет selector/heading в одном canonical документе. Он не считает `prompts/STAGES.md`
каноническим даже при valid selector. При наличии старого пути adapter возвращает
`migration_required` или `conflict` и сохраняет источник до read-back.
Он не объявляет stage завершённым и не
удаляет файлы. Global context validator и tests фиксируют отсутствие legacy AI plan/status paths в
canonical workflow и templates.

### CSP-007 Update and completion behavior

После изменения фактического project state агент обновляет соответствующий stage record и selector/
NEXT в `docs/STAGES.md` до handoff. Completion Documentation Synchronization Gate проверяет
`README.md`, `docs/STAGES.md`, `docs/ROADMAP.md` и затронутые state-bearing contracts; mutation
точных документов не требуется.

## 4. Security and rollback

- Migration fail closed: ни один legacy file не удаляется автоматически.
- Hooks и validators читают только contained regular files с bounded size.
- Runtime credentials/config/sessions/cache не входят в scope.
- Rollback global change: discard uncommitted isolated worktree либо revert будущего atomic commit;
  product repositories мигрируются отдельно и сохраняют собственные rollback points.

## 5. Acceptance criteria

- `AC-CSP-001`: global governance/router/framework/Skills/templates назначают единственным
  execution-state owner `docs/STAGES.md`.
- `AC-CSP-002`: greenfield required set и template не содержат `AI_PLAN.md`/`AI_STATUS.md`.
- `AC-CSP-003`: validator принимает valid single-file selector/catalog и отклоняет missing,
  invalid, ambiguous selector/heading и competing legacy state files.
- `AC-CSP-004`: hook consumer path `docs/STAGES.md → selector → exact selected record` проходит;
  unrelated stages не попадают в context.
- `AC-CSP-005`: reconciliation deterministic/read-only и помечает legacy state files `MERGE` без
  их удаления или изменения Git status.
- `AC-CSP-006`: global DEV current plan/status/evidence/NEXT сохранены в `docs/STAGES.md`, а
  прежние `docs/AI_PLAN.md` и `docs/AI_STATUS.md` удалены после audit.
- `AC-CSP-007`: repository-wide canonical-workflow search не находит активных требований или
  templates, создающих competing AI plan/status pair; явно historical/migration mentions допустимы.
- `AC-CSP-008`: full unit suite, global context validator и `git diff --check` проходят.

## 6. Executable consumer scenario

1. Создать temporary independent Git project с одним `docs/STAGES.md` и exact selector.
2. Запустить project-overlay validator и получить PASS.
3. Передать project cwd в SessionStart hook и получить только selected stage record.
4. Добавить legacy `docs/AI_PLAN.md`/`docs/AI_STATUS.md`: validator обязан fail visibly, а
   reconciliation — вернуть `MERGE` без mutation.
5. Удалить legacy fixtures и повторить validation с тем же deterministic PASS.

## 7. История

- 2026-09-08 — v1: утверждён single-file execution-state contract и безопасная migration policy.
- 2026-09-15 — v2: по прямому решению пользователя canonical owner перемещён в `docs/STAGES.md`;
  `prompts/STAGES.md` сохранён как распознаваемый brownfield migration input.
