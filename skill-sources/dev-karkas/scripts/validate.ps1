$ErrorActionPreference = 'Stop'

$SkillRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

$Required = @(
    'SKILL.md',
    'agents\openai.yaml',
    'references\KARKAS.md',
    'references\PROJECT_REGISTRY.md',
    'references\PROJECT_FILES.md',
    'references\NOTION_INTAKE.md',
    'references\PROMPT_TEMPLATE.md',
    'references\STATUS_WORKFLOW.md',
    'references\TESTING_POLICY.md',
    'references\SECURITY_BASELINE.md',
    'references\FALLBACK_POLICY.md',
    'references\AUTONOMY_POLICY.md',
    'references\GIT_WORKFLOW.md',
    'references\ARCHITECTURE_POLICY.md'
)

$Missing = @()
foreach ($Relative in $Required) {
    if (-not (Test-Path (Join-Path $SkillRoot $Relative))) {
        $Missing += $Relative
    }
}

if ($Missing.Count -gt 0) {
    throw "Missing required files: $($Missing -join ', ')"
}

$Skill = Get-Content -Raw -Encoding UTF8 (Join-Path $SkillRoot 'SKILL.md')
if ($Skill -notmatch '(?s)^---\s*\r?\nname:\s*dev-karkas\s*\r?\ndescription:\s*.+?\r?\n---') {
    throw 'SKILL.md frontmatter is missing or invalid.'
}

$Frontmatter = [regex]::Match($Skill, '(?s)^---\s*\r?\n(.*?)\r?\n---').Groups[1].Value
$Keys = @()
foreach ($Line in ($Frontmatter -split "`r?`n")) {
    if ($Line -match '^([A-Za-z0-9_-]+):') {
        $Keys += $Matches[1]
    }
}
$Unexpected = $Keys | Where-Object { $_ -notin @('name','description') }
if ($Unexpected) {
    throw "Unexpected SKILL.md frontmatter keys: $($Unexpected -join ', ')"
}

Write-Host 'dev-karkas validation: OK'
Write-Host "Skill root: $SkillRoot"
