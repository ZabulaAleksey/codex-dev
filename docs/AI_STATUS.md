# Текущее состояние ДЕВ / КАРКАС

Дата: 2026-08-24

## Статус

Предыдущая консолидация в `~/.codex` подтверждена commit `a195744`. Full governance migration находится в Phase 2: global source/runtime split реализован в feature-worktree, но ещё не активирован в canonical worktree.

## Реализовано

- единый канонический `~/.codex/AGENTS.md`;
- Git root `~/.codex` с сохранённой history/index на ветке `chore/codex-home-consolidation`;
- прямые `agents/`, `hooks/`, `rules/`, `docs/`, `presets/`, `tools/` и `specs/`;
- versioned Skill sources в `skill-sources/` и recoverable runtime sync в `~/.agents/skills`;
- отсутствие прежних параллельных source/installed trees;
- runtime-safe Git allowlist: auth, config, secrets, sessions, SQLite, cache и plugins игнорируются;
- project global links обновлены в отдельных migration-ветках; project roots остаются в `~/codex-workspace`;
- 11 атомарных project commits; `ai-mix` не требовал ссылочной правки;
- исходные merge-state/dirty worktrees сохранены без изменений.

## Verification evidence

- unit suite с `tools.test_sync_global_skills` — 39/39 PASS в full-governance feature-worktree;
- `py -3 -B tools/validate_context.py` — PASS, 258 managed files в feature-worktree;
- `py -3 -B tools/validate_global_codex.py --workspace ~/.codex --codex-home ~/.codex` — PASS;
- `hooks.json`, active и recommended TOML — parse PASS;
- Git ignore probes для auth/config/sessions/logs/plugins/runtime rules/system Skills — PASS;
- 12 project repositories: 7 overlay PASS; 5 имеют только pre-existing missing framework files/legacy status;
- stale global link audit migration-веток — PASS; новых `CONFLICT` и exact-global-duplicate нет;
- защищённые и грязные checkout’ы получат ссылочные изменения только после явно разрешённого merge.

## Известные ограничения

- `projects/dune-rts` не является Git repository; принято решение объединить уникальное с backlog и архивировать placeholder;
- `ai-mix`, `server`, `Task_21.07_Svelte`, `toemath` и `wifi-share` сохраняют ранее существовавшие overlay gaps;
- основной worktree `receipt-scanner-ua` и `Task_21.07_Svelte` остаётся в незавершённом merge;
- runtime validator против active `~/.codex` ожидаемо показывает drift до активации feature-ветки;
- временные worktrees и backup refs сохранены для последующего merge/проверки.

## Следующее действие

Проверить ветки и дать отдельную команду на merge. После merge можно удалить
временные worktrees и старую резервную копию migration-файлов.
