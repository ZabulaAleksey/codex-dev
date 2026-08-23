# Текущий план ДЕВ / КАРКАС

Статус: Готово к handoff
Этап: Full governance migration — Phase 12/12
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
- unit suite 39/39 — PASS;
- `validate_context.py` и `validate_global_codex.py` — PASS;
- 12 Git repositories проверены; новые compatibility conflicts отсутствуют — PASS;
- исходные dirty/merge состояния сохранены — PASS.

## Завершённый результат

1. Все 12 project migration-веток чисты, имеют отдельные commits и проходят общий stale/conflict/overlay audit.
2. Machine-local root artifacts перенесены в recoverable `~/.codex-local/workspace-legacy-20260824`.
3. Global context, runtime Skills и project paths проверены; merge/push оставлены только на отдельное разрешение пользователя.

## Blockers

- legacy `codex-workspace/.git` защищён ACL и требует ручного quarantine владельцем;
- merge в protected/dirty branches не разрешён и не входит в автоматическую миграцию.

## Следующее действие

Получить отдельное решение пользователя по интеграции project migration-веток. До этого сохранить linked worktrees, backup refs и migration backup.
