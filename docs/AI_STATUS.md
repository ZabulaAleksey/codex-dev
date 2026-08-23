# Текущее состояние ДЕВ / КАРКАС

Дата: 2026-08-24

## Статус

Versioned ДЕВ и active global Codex layer консолидированы в `~/.codex`.
Перенос проверен локально; merge и удаление временных worktrees требуют отдельного
разрешения владельца.

## Реализовано

- единый канонический `~/.codex/AGENTS.md`;
- Git root `~/.codex` с сохранённой history/index на ветке `chore/codex-home-consolidation`;
- прямые `agents/`, `hooks/`, `skills/`, `rules/`, `docs/`, `presets/`, `tools/` и `specs/`;
- отсутствие прежних параллельных source/installed trees;
- runtime-safe Git allowlist: auth, config, secrets, sessions, SQLite, cache и plugins игнорируются;
- project global links обновлены в отдельных migration-ветках; project roots остаются в `~/codex-workspace/projects`;
- 11 атомарных project commits; `ai-mix` не требовал ссылочной правки;
- исходные merge-state/dirty worktrees сохранены без изменений.

## Verification evidence

- unit suite `tools.test_reconcile_project_framework`, `tools.test_validate_global_codex`, `tools.test_validate_project_overlay` — 34/34 PASS;
- `py -3 -B tools/validate_context.py` — PASS, 254 managed files;
- `py -3 -B tools/validate_global_codex.py --workspace ~/.codex --codex-home ~/.codex` — PASS;
- `hooks.json`, active и recommended TOML — parse PASS;
- Git ignore probes для auth/config/sessions/logs/plugins/runtime rules/system Skills — PASS;
- 12 project repositories: 7 overlay PASS; 5 имеют только pre-existing missing framework files/legacy status;
- stale global link audit migration-веток — PASS; новых `CONFLICT` и exact-global-duplicate нет;
- защищённые и грязные checkout’ы получат ссылочные изменения только после явно разрешённого merge.

## Известные ограничения

- `projects/dune-rts` не является Git repository и не входил в repository audit;
- `ai-mix`, `server`, `Task_21.07_Svelte`, `toemath` и `wifi-share` сохраняют ранее существовавшие overlay gaps;
- основной worktree `receipt-scanner-ua` и `Task_21.07_Svelte` остаётся в незавершённом merge;
- временные worktrees сохранены для последующего merge/проверки.

## Следующее действие

Проверить ветки и дать отдельную команду на merge. После merge можно удалить
временные worktrees и старую резервную копию migration-файлов.
