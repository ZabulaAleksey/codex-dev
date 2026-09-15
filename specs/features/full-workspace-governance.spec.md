# SPEC: полная стандартизация ДЕВ и project repositories

Статус: APPROVED
Дата: 2026-08-24

## Цель

Сделать `~/.codex` единственным versioned global DEV context, `~/.agents/skills` — единственным runtime-расположением reusable Skills, а `~/codex-workspace` — контейнером независимых product repositories без промежуточного `projects/`.

## Scope

- source/runtime split глобальных Skills с hash validation и recoverable sync;
- flatten каждого независимого repository из `projects/<repo>` в `<repo>`;
- сохранение dirty/index/merge/worktree state;
- обновление global/project paths, trust config, hooks, validators и manifests;
- project `AGENTS.md` как delta;
- `docs/STAGES.md` как единый detailed stage source;
- canonical project docs и устранение semantic duplicates без потери уникального содержания;
- global governance policy из `rules/governance.md`;
- read-only structure/context validators.

## Non-goals

- реализация product features;
- изменение принятых tests/fixtures/goldens;
- push, PR, protected-branch merge или branch deletion без отдельного разрешения;
- production deployment, secret rotation и external projection writes;
- создание фиктивного repository для `dune-rts` placeholder.

## Safety invariants

- До физического move существует exact migration map и recoverable backup evidence.
- Dirty tracked state сохраняется отдельным Git ref; merge metadata копируется без изменения index/worktree.
- Target path проверяется на отсутствие до same-volume move.
- После каждого move проверяются Git root, branch, HEAD, remote, status и linked worktrees.
- Machine-local/runtime data не коммитится и не удаляется.

## Acceptance criteria

1. `~/codex-workspace/projects` больше не требуется.
2. Все подтверждённые product repositories находятся непосредственно в `~/codex-workspace` и сохраняют Git identity/status.
3. `dune-rts` placeholder архивирован после переноса уникального содержания.
4. Global/project canonical context не содержит активных ссылок на старый layout.
5. Versioned Skill source и runtime projection совпадают по file set/SHA-256.
6. Project stage content консолидирован в `docs/STAGES.md`; legacy stage files удалены только после content/link audit.
7. Updated global/project validators и релевантные project gates проходят либо имеют явно pre-existing/blocked evidence.
8. Final handoff содержит commits, statuses, rollback refs, gate results и оставшиеся blockers.
