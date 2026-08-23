# Текущее состояние ДЕВ / КАРКАС

Дата: 2026-08-24

## Статус

Full governance migration активирована в `~/.codex`: базовый governance commit `806ee29`, flattened-path follow-up `498a4b8`. Все 12 independent repositories физически находятся непосредственно в `~/codex-workspace`; project changes изолированы в migration-ветках до отдельного разрешения на merge.

## Project migration commits

| Project | Commit |
|---|---|
| `ai-mix` | `93ee756` |
| `electro-tutor` | `d2fa899` |
| `math-morph` | `56b9782` |
| `monte-carlo` | `6c3a220` |
| `off-screen-canvas` | `9b56423` |
| `receipt-scanner-ua` | `8e1b735` |
| `server` | `c13eb96` |
| `Task_21.07_Svelte` | `73fc902` |
| `text-recognition-core` | `b5731f4` |
| `toemath` | `35591a8` |
| `video-chronicle` | `6c879ff` |
| `wifi-share` | `c0c3aa6` |

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

- unit suite с `tools.test_sync_global_skills` — 39/39 PASS;
- `py -3 -B tools/validate_context.py` — PASS, 258 managed files;
- `py -3 -B tools/validate_global_codex.py --workspace ~/.codex --codex-home ~/.codex` — PASS;
- `hooks.json`, active и recommended TOML — parse PASS;
- Git ignore probes для auth/config/sessions/logs/plugins/runtime rules/system Skills — PASS;
- 12 project repositories: 7 overlay PASS; 5 имеют только pre-existing missing framework files/legacy status;
- stale global link audit migration-веток — PASS; новых `CONFLICT` и exact-global-duplicate нет;
- защищённые и грязные checkout’ы получат ссылочные изменения только после явно разрешённого merge.

## Известные ограничения

- прежний placeholder `dune-rts` не являлся Git repository; уникальный тестовый контракт объединён с `backlog/dune2-bot.md`, исходник архивирован;
- project overlay gaps устранены в отдельных `chore/full-governance-migration` ветках и проверяются до merge;
- основной worktree `receipt-scanner-ua` и `Task_21.07_Svelte` остаётся в незавершённом merge;
- active `~/.codex` и runtime Skills validator проходят без drift;
- machine-local root artifacts и старый root Node bundle сохранены в `~/.codex-local/workspace-legacy-20260824`;
- legacy `codex-workspace/.git` остаётся единственным некарантинированным элементом из-за защищающего ACL и требует действия владельца;
- временные worktrees и backup refs сохранены для последующего merge/проверки.

## Следующее действие

После отдельного разрешения интегрировать project migration-ветки, повторить gates на целевых branches и только затем удалить временные worktrees/migration backup.
