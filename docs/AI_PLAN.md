# Текущий план ДЕВ / КАРКАС

Статус: Завершён, ожидает решения о merge
Этап: Консолидация global context в `~/.codex`
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

## Следующее действие

После проверки владельцем — отдельное разрешение на merge ветки
`chore/codex-home-consolidation` и project reference branches. Временные worktrees
не удалять без явного разрешения.
