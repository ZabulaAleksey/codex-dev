# DEV filesystem layout and migration

## Canonical roles

| Role | Current default | Meaning |
|---|---|---|
| `DEV_SOURCE_ROOT` | `~/codex-dev` | Git-managed global DEV source |
| `CODEX_HOME` | `~/.codex` | active Codex user/runtime layer plus managed projection |
| `PROJECTS_ROOT` | `~` | parent used only to resolve/discover product repositories |

`tools/dev_paths.py` owns these semantics. Consumers must not reconstruct these paths. Resolution
precedence is environment → `~/.codex/dev-layout.toml` → default/auto-detection; ambiguity and
invalid configuration fail closed. The diagnostic is safe to share: it sanitizes remote URLs and
does not read or print credentials, runtime contents or the broader environment.

## Product isolation contract

`${PROJECTS_ROOT}/<project>` means only a candidate filesystem path. These facts are independent:

1. path exists;
2. exact path is an independent Git root;
3. global DEV integration is enabled.

The canonical bridge is a valid structured `.codex/dev-project.toml` based on
`templates/dev-project/.codex/dev-project.toml`. Deliberate adoption also adds a human-readable
line to `AGENTS.md`:

```text
Global DEV bridge: enabled
```

A directory location, `.git`, an arbitrary `.codex/` directory, unrelated `AGENTS.md`, or the
AGENTS declaration alone does not enable the bridge. Invalid marker content fails closed. Do not
materialize the structured marker in repositories that should remain ordinary independent
projects.

## Clone and pull bootstrap

`dev-contract.toml` is the single global source for DEV version, capabilities, supported project
marker schema, canonical GitHub repository and default source path. A DEV-managed project carries
only its minimum version/capability requirements plus thin wrappers; it does not copy global
rules. After clone or pull:

```powershell
.\.codex\bootstrap.ps1 check   # read-only
.\.codex\bootstrap.ps1 apply   # explicit managed-layer install/update
```

```bash
./.codex/bootstrap.sh --check
./.codex/bootstrap.sh --apply
```

The check detects missing source, canonical remote mismatch, unsupported marker schema, old DEV
version, missing capability, stale installed manifest and invalid project overlay. Missing source
produces a deterministic clone command but is never cloned automatically. Apply delegates to the
transactional global installer and is idempotent; it cannot update Git or remove runtime data.

## Resolver and diagnostics

```powershell
py -3 -B "$env:DEV_SOURCE_ROOT\tools\dev_paths.py" resolve --json
py -3 -B "$env:DEV_SOURCE_ROOT\tools\dev_paths.py" project math-morph --json
py -3 -B "$env:DEV_SOURCE_ROOT\tools\dev_paths.py" diagnose --json
py -3 -B "$env:DEV_SOURCE_ROOT\tools\dev_paths.py" move-plan math-morph --json
```

`move-plan` is read-only. A safe recommendation requires an exact Git root, known clean status,
known branch, checked remotes, no nested repositories, no additional worktrees, checked clean
submodules and no destination collision. After a user-reviewed move, verify the new Git root,
branch/status and remotes using the emitted commands. Keep the legacy repository until that
verification is complete; archive/deletion always requires a separate explicit decision.

## Repository rename

The target GitHub repository name is `codex-dev`. Rename the GitHub repository through an
authorized user workflow, then update each clone's `origin` only after verifying the account and
new remote URL. This repository does not perform remote rename, push or merge automatically.

## Installer

Run the existing wrapper from resolved `DEV_SOURCE_ROOT`. It refuses to use a different source or
a `CODEX_HOME` containing `.git`, performs a manifest-only transaction, preserves runtime state,
materializes Skills through the existing sync scheme and validates before finalizing. Always run
the dry-run first during migration.

## Laptop and desktop

Use the same three role values on both devices. PowerShell user-environment changes affect only new
processes, so close and reopen Codex and PowerShell. The optional TOML config is device-local and
must not be committed or copied as portable project state.
