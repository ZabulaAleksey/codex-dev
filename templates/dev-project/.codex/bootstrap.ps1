param(
    [ValidateSet("check", "apply")]
    [string]$Mode = "apply"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Expand-UserPath([string]$Value) {
    if ($Value -eq "~") { return $HOME }
    if ($Value.StartsWith("~/") -or $Value.StartsWith("~\")) {
        return Join-Path $HOME $Value.Substring(2)
    }
    return $Value
}

$DevRootValue = $env:DEV_SOURCE_ROOT
if (-not $DevRootValue) {
    $LayoutConfig = Join-Path $HOME ".codex\dev-layout.toml"
    if (Test-Path -LiteralPath $LayoutConfig -PathType Leaf) {
        $LayoutText = Get-Content -Raw -LiteralPath $LayoutConfig
        if ($LayoutText -match '(?m)^\s*dev_source_root\s*=\s*"([^"]+)"\s*$') {
            $DevRootValue = $Matches[1]
        }
    }
}
if (-not $DevRootValue) { $DevRootValue = "~/codex-dev" }
$DevRoot = [IO.Path]::GetFullPath((Expand-UserPath $DevRootValue))
$Bootstrap = Join-Path $DevRoot "tools\project_bootstrap.py"

if (-not (Test-Path -LiteralPath $Bootstrap -PathType Leaf)) {
    Write-Error @"
Global DEV is missing at $DevRoot.
Canonical recovery (review, then run):
git clone https://github.com/ZabulaAleksey/codex-dev.git "$DevRoot"
Then rerun: .\.codex\bootstrap.ps1 $Mode
"@
}

& py -3 -B $Bootstrap "--$Mode" --project $ProjectRoot --json
exit $LASTEXITCODE
