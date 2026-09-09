# SPEC: canonical source repository → installed Codex home layer

Статус: APPROVED
Дата: 2026-09-10

## Цель

Устанавливать versioned global DEV из отдельного canonical Git repository (обычно
`~/codex-workspace/codex-dev`) в active `~/.codex` без превращения runtime home в Git working tree
и без потери device-local state.

## Границы

- canonical source: Git root, содержащий `MANIFEST.txt` и installer wrappers;
- installed Codex home: `~/.codex`, только managed projection плюс runtime state Codex;
- versioned Skill source: `<dev-root>/skill-sources`;
- runtime Skills: `~/.agents/skills`, materialized только через `tools/sync_global_skills.py`;
- active `~/.codex/config.toml` не является managed artifact и не заменяется recommendation file.

Source и destination обязаны быть разными, неналоженными directory trees. Destination с `.git`
fail closed: перенос старого repository завершается до запуска installer.

## Требования

### FR-DIL-001 Source discovery

Wrapper определяет DEV root по своему расположению и проверяет, что это точный Git root. Source
может находиться в любом пользовательском path и не обязан совпадать с `~/.codex`.

### FR-DIL-002 Manifest allowlist

Каждый управляемый файл должен быть явно перечислен в `MANIFEST.txt`; glob и blanket tree mirror
запрещены. Source-maintenance entries (`.github`, `.gitignore`, wrappers и manifest) остаются только
в source. `skill-sources/` не копируется в Codex home и имеет отдельный Skill materialization path.

### SEC-DIL-001 Runtime protection

До первой записи installer case-insensitive проверяет manifest и ledger против protected runtime
namespaces: active config/auth, sessions/archives, cache, SQLite, plugins, attachments, temp,
browser/computer-use, secrets, sandbox и installer transaction state. Collision fail closed.
Неизвестный destination-файл сохраняется; конфликт по intended managed path не перезаписывается.

### FR-DIL-003 Ownership ledger и stale cleanup

`~/.codex/.dev-install-manifest.json` содержит только schema version, SHA-256 source manifest и
отсортированный список managed relative paths/SHA-256. Ledger не содержит absolute source path,
timestamp, credentials или другие secrets. Stale файл удаляется только когда предыдущий валидный
ledger подтверждает ownership; неизвестные files не выводятся из отсутствия в manifest.

### NFR-DIL-001 Transaction и rollback

Create/update/delete выполняются через staging внутри destination. До mutation обновляемые и stale
managed files и предыдущий ledger копируются в transaction backup; публикация файла и ledger
использует same-volume atomic replace. Любая apply/validation/Skill-sync ошибка восстанавливает
managed pre-image и прежние managed Skills. Rollback failure сохраняет transaction directory и
выдаёт точный recovery path.

### FR-DIL-004 Dry run

`install-global.ps1 -DryRun` и `install-global.sh --dry-run` строят тот же preflight plan и показывают
`create`, `update`, `delete`, `conflict`, ledger change и присутствующий `protected runtime skip`,
не создавая destination, ledger, staging или Skill projection.

### FR-DIL-005 Validation и Skills

До mutation `validate_context.py` подтверждает Git-tracked source/manifest parity. После managed
apply запускаются `validate_context.py` и `validate_global_codex.py --skip-skills`.
Затем `sync_global_skills.py --apply` materialize-ит Skills и оба validator запускаются повторно с
полной Skill parity. Validation failure входит в rollback boundary.

### NFR-DIL-002 Determinism и idempotency

Одинаковые source bytes создают одинаковый ledger независимо от device path. Повторный install не
переписывает managed files или ledger. После `git pull` меняются только manifest-managed artifacts;
device-local runtime и неизвестные files сохраняются.

### FR-DIL-006 Config policy

`config.ai-dev-team.recommended.toml` устанавливается только как reference. Active `config.toml` не
копируется и не заменяется. Любой будущий non-secret invariant требует отдельного explicit,
idempotent merge contract с сохранением user-specific settings.

## Acceptance criteria

- AC-DIL-001 source Git root вне `~/.codex` принимается, source==destination и destination `.git`
  отклоняются;
- AC-DIL-002 populated Codex home сохраняет runtime files byte-for-byte;
- AC-DIL-003 копируются только installable manifest entries, `.git` и `skill-sources` не копируются;
- AC-DIL-004 stale managed file удаляется по ledger, unknown file сохраняется;
- AC-DIL-005 protected collision и unknown differing destination collision fail closed до writes;
- AC-DIL-006 Skills materialize-ятся в `~/.agents/skills` существующим sync tool;
- AC-DIL-007 dry-run zero-write, failure rollback восстанавливает pre-image;
- AC-DIL-008 validators выполняются после apply и повторно после Skill sync;
- AC-DIL-009 второй install идемпотентен;
- AC-DIL-010 install после source update меняет только managed artifacts.

## Verification

`tools/test_install_global.py` покрывает AC-DIL-001..010 на isolated temporary roots. Общий suite,
`tools/validate_context.py`, `tools/validate_global_codex.py` fixtures, wrapper syntax checks и
`git diff --check` являются release gate. Реальный active `~/.codex` не изменяется тестами.

## Rollback и миграция legacy layout

Сначала clone/pull canonical repository вне `~/.codex`. Если старый `~/.codex` ещё содержит `.git`,
сохранить remote/branch/status и перенести либо архивировать Git metadata вручную; installer этого
не делает. Идентичные существующие managed files можно безопасно принять в новый ledger без
перезаписи. Различающийся unknown collision требует ручного reconcile. Runtime state остаётся на
месте.
