param()

$ErrorActionPreference = "Stop"
$DevRoot = (Resolve-Path (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path
$CodexHome = (Join-Path $HOME ".codex")

if ([IO.Path]::GetFullPath($DevRoot) -ne [IO.Path]::GetFullPath($CodexHome)) {
    throw "ДЕВ должен быть клонирован или перемещён непосредственно в $CodexHome. Параллельная installed-копия не поддерживается."
}

Write-Host "ДЕВ уже расположен в каноническом ~/.codex." -ForegroundColor Green
py -3 (Join-Path $DevRoot "tools\sync_global_skills.py") --apply
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3 (Join-Path $DevRoot "tools\validate_context.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3 (Join-Path $DevRoot "tools\validate_global_codex.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Проверки завершены. Runtime config.toml и secrets не изменялись." -ForegroundColor Green
