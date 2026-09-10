# Быстрый старт на Windows, Linux и macOS

Одинаковый canonical layout на laptop и desktop:

- `DEV_SOURCE_ROOT=~/codex-dev` — Git-managed source repository;
- `CODEX_HOME=~/.codex` — installed global layer и device-local runtime state, не Git repository;
- `PROJECTS_ROOT=~` — discovery parent независимых product repositories.

Filesystem location не включает global DEV policy. Product repository подключает DEV только
через project-local `AGENTS.md` с exact marker `Global DEV bridge: enabled`.

## Windows PowerShell

Temporary variables для текущего PowerShell:

```powershell
$env:DEV_SOURCE_ROOT = "$HOME\codex-dev"
$env:CODEX_HOME = "$HOME\.codex"
$env:PROJECTS_ROOT = "$HOME"
```

Persistent user variables:

```powershell
[Environment]::SetEnvironmentVariable("DEV_SOURCE_ROOT", "$HOME\codex-dev", "User")
[Environment]::SetEnvironmentVariable("CODEX_HOME", "$HOME\.codex", "User")
[Environment]::SetEnvironmentVariable("PROJECTS_ROOT", "$HOME", "User")
```

После persistent change полностью перезапусти Codex и открой новый PowerShell: уже работающие
processes не получают обновлённый user environment автоматически.

```powershell
git clone https://github.com/ZabulaAleksey/codex-dev.git "$HOME\codex-dev"
Set-Location "$HOME\codex-dev"
git pull --ff-only

py -3 -B .\tools\dev_paths.py resolve --json
py -3 -B .\tools\dev_paths.py diagnose --json

Set-ExecutionPolicy -Scope Process Bypass
.\install-global.ps1 -DryRun
.\install-global.ps1

# Explicitly DEV-enabled full overlay only:
py -3 "$HOME\.codex\tools\validate_project_overlay.py" "$HOME\<project>"
```

## Linux / macOS

```bash
export DEV_SOURCE_ROOT="$HOME/codex-dev"
export CODEX_HOME="$HOME/.codex"
export PROJECTS_ROOT="$HOME"

git clone https://github.com/ZabulaAleksey/codex-dev.git "$DEV_SOURCE_ROOT"
cd "$DEV_SOURCE_ROOT"
git pull --ff-only

python3 -B tools/dev_paths.py resolve --json
python3 -B tools/dev_paths.py diagnose --json
./install-global.sh --dry-run
./install-global.sh

python3 -B "$CODEX_HOME/tools/validate_project_overlay.py" "$PROJECTS_ROOT/<project>"
```

Optional per-device fallback config: `~/.codex/dev-layout.toml`.

```toml
[paths]
dev_source_root = "~/codex-dev"
codex_home = "~/.codex"
projects_root = "~"
```

Environment variables override this file; the file is not portable Git state. Full resolver and
migration procedure are documented in [`docs/DEV_LAYOUT.md`](docs/DEV_LAYOUT.md).

## Installer boundaries

Installer reads source and destination from the resolver, uses `MANIFEST.txt` as explicit
allowlist, records ownership in `~/.codex/.dev-install-manifest.json`, and never mirrors `.git` or
`skill-sources/` into `CODEX_HOME`. Runtime state, unknown files and active `config.toml` are
preserved. Differing unknown collision or protected runtime path fails before the first write.

`skill-sources/` stays under `DEV_SOURCE_ROOT`; runtime Skills materialize into
`~/.agents/skills`. Recommended config is installed only as
`~/.codex/config.ai-dev-team.recommended.toml`.

## Legacy migration

Run `tools/dev_paths.py diagnose` before moving anything. It reports legacy source/product roots,
collisions, Git preflight and exact recommended commands. It never moves, deletes or archives a
repository. If `~/.codex/.git` exists, reconcile that Git checkout before running installer;
destination Git metadata is a protected collision.

## Product repository check

```powershell
Set-Location "$env:PROJECTS_ROOT\<project>"
py -3 "$env:CODEX_HOME\tools\dev_paths.py" project . --json
```

A plain Git repository should report `dev_integration: disabled`. A deliberately adopted project
uses the existing project-local `AGENTS.md` overlay contract and exact bridge marker. Only then may
SessionStart, `Продолжай`, Prompt Queue and full overlay validation route global DEV project policy.
