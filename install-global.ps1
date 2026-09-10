param([switch]$DryRun)

$ErrorActionPreference = "Stop"
$DevRoot = (Resolve-Path (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path

$GitRoot = (& git -c "safe.directory=$DevRoot" -C $DevRoot rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if ([IO.Path]::GetFullPath($GitRoot) -ne [IO.Path]::GetFullPath($DevRoot)) {
    throw "install-global.ps1 must run from the canonical DEV source Git root: $DevRoot"
}

$Arguments = @(
    "-3",
    "-B",
    (Join-Path $DevRoot "tools\install_global.py")
)
if ($DryRun) { $Arguments += "--dry-run" }

& py @Arguments
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
