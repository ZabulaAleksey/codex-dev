param([ValidateSet("check", "apply")][string]$Mode = "apply")
$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$DevRoot = if ($env:DEV_SOURCE_ROOT) { $env:DEV_SOURCE_ROOT } else { Join-Path $HOME "codex-dev" }
$Bootstrap = Join-Path $DevRoot "tools\project_bootstrap.py"
if (-not (Test-Path -LiteralPath $Bootstrap -PathType Leaf)) {
    Write-Error "Global DEV missing at $DevRoot. Review and run: git clone https://github.com/ZabulaAleksey/codex-dev.git `"$DevRoot`""
}
& py -3 -B $Bootstrap "--$Mode" --project $ProjectRoot --json
exit $LASTEXITCODE
