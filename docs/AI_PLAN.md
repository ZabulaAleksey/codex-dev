# Текущий план ДЕВ / КАРКАС

Статус: В работе
Этап: Full governance migration — Phase 2/12
Дата: 2026-08-24

## Выполнено

1. Утверждена `specs/features/codex-home-consolidation.spec.md`.
2. `~/.codex` подготовлен как единственный Git root и active runtime-layer ДЕВ.
3. Два глобальных `AGENTS.md` объединены; source/installed duplication agents, hooks, Skills и rules устранён.
4. Runtime state и secrets закрыты deny-by-default `.gitignore`.
5. Global links обновлены в shared context, presets, Skills и migration-ветках 11 project repositories; `ai-mix` не требовал правки.
6. Для merge-in-progress/dirty repositories изменения изолированы worktrees и отдельными branches.
7. Unit contracts, manifest, global validator, JSON/TOML и project overlay audit выполнены.

## Definition of Done

- Git root `~/.codex` — PASS;
- единый global `AGENTS.md` — PASS;
- managed links на старые global paths отсутствуют в каноническом root и migration-ветках — PASS;
- runtime/secrets не видны Git — PASS;
- unit suite 34/34 — PASS;
- `validate_context.py` и `validate_global_codex.py` — PASS;
- 12 Git repositories проверены; новые compatibility conflicts отсутствуют — PASS;
- исходные dirty/merge состояния сохранены — PASS.

## Текущая цель

1. Завершить и проверить source/runtime split Skills.
2. По одному переместить независимые product repositories из `projects/<repo>` в `<repo>`, сохранив Git/dirty/worktree state.
3. Обновить paths, project overlays, `prompts/STAGES.md` и canonical docs.
4. Расширить read-only validators и выполнить gates.

## Blockers

- legacy `codex-workspace/.git` защищён ACL и требует ручного quarantine владельцем;
- merge в protected/dirty branches не разрешён и не входит в автоматическую миграцию.

## Следующее действие

Закончить Phase 2 validation, затем выполнить Phase 3 для clean repositories с lowest risk.
