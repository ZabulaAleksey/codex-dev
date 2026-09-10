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

The existing project-local `AGENTS.md` overlay is the only bridge. Deliberate adoption adds an
exact standalone line:

```text
Global DEV bridge: enabled
```

A directory location, `.git`, `.codex/` directory or unrelated `AGENTS.md` does not enable the
bridge. Do not add this marker to repositories that should remain ordinary independent projects.

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
