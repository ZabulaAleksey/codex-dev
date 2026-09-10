# SPEC: unified DEV and product path roles

Статус: APPROVED
Дата: 2026-09-10

## Цель

Использовать одинаковый physical filesystem layout на laptop и desktop, сохраняя явные logical
roles и независимость product repositories:

```text
DEV_SOURCE_ROOT=~/codex-dev
CODEX_HOME=~/.codex
PROJECTS_ROOT=~
```

Physical location не является policy signal. Repository под `${PROJECTS_ROOT}/<project>` не
подключается к global DEV, Prompt Queue или project overlay без explicit project-local bridge.

## Requirements

### FR-DPL-001 Single resolver

`tools/dev_paths.py` является единственным владельцем path resolution. Для каждой роли порядок
одинаков: environment variable → `~/.codex/dev-layout.toml` → deterministic default. Resolver
расширяет `~`, нормализует Windows paths, возвращает absolute paths и source resolution
`env|local_config|default|auto`. Invalid values и semantic ambiguity fail closed.

### FR-DPL-002 Local config and diagnostics

Optional device-local config имеет форму:

```toml
[paths]
dev_source_root = "~/codex-dev"
codex_home = "~/.codex"
projects_root = "~"
```

Diagnostic CLI выводит только paths, resolution sources, existence/Git facts, legacy layout,
collisions, sanitized repository identity, recommended migration commands и safe/unsafe result.
Credentials, environment inventory и runtime file contents не выводятся.

### FR-DPL-003 Product isolation

Product path разрешается только как `${PROJECTS_ROOT}/<project>`. Три факта независимы: path
exists, exact path является Git root, global DEV integration enabled. Valid structured
`.codex/dev-project.toml` является canonical machine-readable bridge. Project `AGENTS.md`
включает exact human-readable declaration `Global DEV bridge: enabled`, но одна эта строка
integration не включает. Один лишь path, `.git`, arbitrary `.codex/` или generic `AGENTS.md`
integration не включает.

Session/bootstrap/Prompt Queue проверяют bridge до project-policy routing. Global DEV source
repository распознаётся отдельно по exact `DEV_SOURCE_ROOT` и не требует product marker.

### FR-DPL-004 Installer consumers

Existing wrappers и `tools/install_global.py` получают source и destination через resolver.
Explicit legacy CLI paths допустимы только когда совпадают с resolved roles. Manifest allowlist,
ownership ledger, transaction/rollback, protected runtime state, dry-run, idempotency and Skill
materialization сохраняют контракт `source-installed-layer.spec.md`.

### FR-DPL-005 Migration preflight

Product move helper только строит read-only plan. До рекомендации move он проверяет exact Git
root, working tree, branch, remotes, nested Git repositories, linked worktrees, submodules и
destination collision. Автоматическое удаление/archive legacy repository запрещено. Legacy
source и product roots не выбираются resolver молча.

### FR-DPL-006 Repository identity and compatibility

Target repository basename и GitHub repository name — `codex-dev`. Active docs, clone examples,
validators and wrappers используют new identity. Исторические `SUPERSEDED` records и фактические
legacy-detection fixtures могут сохранять `codex-workspace` только с semantic classification.
GitHub rename, remote mutation и physical product moves остаются user/approved workflow.

### FR-DPL-007 Continue and Prompt Queue

`Продолжай`/new-chat bootstrap восстанавливает explicit DEV-enabled repository по actual Git root
и resolver, без canonical `~/codex-workspace/<project>` assumption. Plain repository получает no
global stage/Prompt Queue injection. Prompt Queue accepts explicit path or project name resolved
under `PROJECTS_ROOT`, verifies exact Git root and bridge, then applies its existing lifecycle.

### FR-DPL-008 Clone/pull bootstrap and compatibility

Global `dev-contract.toml` owns DEV version, capabilities, supported project marker schemas,
canonical `codex-dev` URL and default source path. DEV-managed projects receive only the portable
marker and `bootstrap.ps1`/`bootstrap.sh` wrappers from `templates/dev-project/.codex/`. Check is
read-only; apply delegates to the existing transactional installer. Missing source returns a
reviewable clone command without network mutation. Version, capability, schema, remote, installed
manifest and project overlay mismatches fail closed.

## Acceptance criteria

- AC-DPL-001 defaults resolve to `~/codex-dev`, `~/.codex`, and `~`;
- AC-DPL-002 env overrides each role and local config is fallback;
- AC-DPL-003 Windows separators, `~`, `.` and `..` normalize deterministically;
- AC-DPL-004 product name resolves under `PROJECTS_ROOT` without implying policy inheritance;
- AC-DPL-005 plain Git repository and generic `AGENTS.md` remain DEV-disabled;
- AC-DPL-006 structured marked overlay is DEV-enabled, AGENTS-only overlay is disabled, and the
  enabled overlay resolves global DEV source;
- AC-DPL-007 installer source differs from `CODEX_HOME`, preserves runtime state and stays
  idempotent;
- AC-DPL-008 Prompt Queue and SessionStart reject/ignore plain repositories and accept marked
  overlays;
- AC-DPL-009 invalid config, invalid product name and legacy/new collision fail closed;
- AC-DPL-010 diagnostics identify old source/project layouts and migration safety;
- AC-DPL-011 active repository references use `codex-dev` and logical roles; remaining legacy
  references are classified historical/detection/test fixtures;
- AC-DPL-012 targeted tests, full unittest suite, context/global validators, installer dry-run and
  `git diff --check` pass before commit readiness.
- AC-DPL-013 fresh clone diagnostics, read-only check, idempotent apply and version/capability
  mismatch behavior are deterministic on Windows and POSIX wrappers.

## Rollback

Code rollback is a normal Git revert. No migration helper deletes source data. If a move was
performed manually, move the repository back only after repeating the same preflight and checking
destination collision; retain legacy source until post-move Git root/remotes/status validation is
complete.
