param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$SkillRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$DestinationRoot = Join-Path $HOME '.codex\skills'
$Destination = Join-Path $DestinationRoot 'dev-karkas'

if (-not (Test-Path (Join-Path $SkillRoot 'SKILL.md'))) {
    throw "SKILL.md not found in $SkillRoot"
}

New-Item -ItemType Directory -Force -Path $DestinationRoot | Out-Null

if (Test-Path $Destination) {
    if (-not $Force) {
        throw "Destination already exists: $Destination. Re-run with -Force to back it up and replace it."
    }

    $Timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $Backup = "$Destination.backup-$Timestamp"
    Copy-Item -Recurse -Force $Destination $Backup
    Write-Host "Backup created: $Backup"
    Remove-Item -Recurse -Force $Destination
}

Copy-Item -Recurse -Force $SkillRoot $Destination
Write-Host "Installed dev-karkas to: $Destination"
Write-Host "Restart/reload Codex if the skill is not detected immediately."
