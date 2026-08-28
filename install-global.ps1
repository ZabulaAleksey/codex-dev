param()

$ErrorActionPreference = "Stop"
$DevRoot = (Resolve-Path (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path
$CodexHome = (Join-Path $HOME ".codex")
$SkillRuntime = (Join-Path $HOME ".agents\skills")

if ([IO.Path]::GetFullPath($DevRoot) -ne [IO.Path]::GetFullPath($CodexHome)) {
    throw "DEV must be cloned or moved directly to $CodexHome. A parallel installed copy is unsupported."
}

$GitRoot = (& git -c "safe.directory=$DevRoot" -C $DevRoot rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if ([IO.Path]::GetFullPath($GitRoot) -ne [IO.Path]::GetFullPath($DevRoot)) {
    throw "Git root must match canonical ~/.codex: $DevRoot"
}

Write-Host "DEV is located in canonical ~/.codex." -ForegroundColor Green
py -3 -B (Join-Path $DevRoot "tools\validate_context.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3 -B (Join-Path $DevRoot "tools\sync_global_skills.py") --source (Join-Path $DevRoot "skill-sources") --destination $SkillRuntime --apply
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3 -B (Join-Path $DevRoot "tools\validate_context.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3 -B (Join-Path $DevRoot "tools\validate_global_codex.py") --workspace $DevRoot --codex-home $CodexHome
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Validation completed. Runtime config.toml and secrets were not changed." -ForegroundColor Green
