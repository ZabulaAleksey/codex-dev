from __future__ import annotations

import subprocess
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.txt"
REQUIRED = {
    ".gitignore",
    ".github/workflows/validate.yml",
    "AGENTS.md",
    "config.ai-dev-team.recommended.toml",
    "hooks.json",
    "hooks/stage_selector.py",
    "install-global.sh",
    "MANIFEST.txt",
    "docs/AI_PLAN.md",
    "docs/AI_STATUS.md",
    "docs/ARCHITECTURE.md",
    "docs/notes/AUTOMATION_EXTENSIONS.md",
    "docs/CONTEXT_COMPATIBILITY.md",
    "docs/CONTEXT_POLICY.md",
    "docs/DECISIONS.md",
    "docs/DESIGN.md",
    "docs/PROJECT_FRAMEWORK.md",
    "docs/ROADMAP.md",
    "docs/SECURITY.md",
    "docs/TESTING.md",
    "docs/notes/SDD_GUIDE.md",
    "docs/WORKFLOW.md",
    "rules/fallback-policy.md",
    "rules/ai-policy-profiling.md",
    "rules/backend-dx.md",
    "rules/dependency-management.md",
    "rules/i18n-l10n.md",
    "rules/README.md",
    "rules/model-routing.md",
    "rules/modes/standard.md",
    "rules/modes/strict.md",
    "rules/node-package-management.md",
    "templates/SPEC_TEMPLATE.md",
    "templates/BACKEND_DX_DELTA_TEMPLATE.md",
    "templates/AGENTS_PROJECT_TEMPLATE.md",
    "specs/README.md",
    "specs/features/global-codex-normalization.spec.md",
    "specs/features/codex-home-consolidation.spec.md",
    "specs/system.spec.md",
    "tools/normalize_user_codex.py",
    "tools/test_validate_global_codex.py",
    "specs/features/project-overlay-rollout.spec.md",
    "specs/features/dependency-manager-policy.spec.md",
    "specs/features/backend-dx-policy.spec.md",
    "specs/features/global-framework-hardening.spec.md",
    "specs/features/ai-policy-profiling.spec.md",
    "schemas/ai-policy-profiling.schema.json",
    "skill-sources/backend-dx-audit/SKILL.md",
    "tools/validate_context.py",
    "tools/validate_global_codex.py",
    "tools/validate_project_overlay.py",
    "tools/test_validate_project_overlay.py",
    "tools/test_backend_dx_policy.py",
    "tools/test_documentation_sync_policy.py",
    "tools/test_i18n_l10n_policy.py",
    "tools/test_global_framework_hardening.py",
    "tools/ai_policy_profiler.py",
    "tools/test_ai_policy_profiler.py",
    "tools/test_stage_completion_policy.py",
    "tools/reconcile_project_framework.py",
    "tools/test_reconcile_project_framework.py",
    "tools/sync_global_skills.py",
    "tools/test_sync_global_skills.py",
}


def git_visible_files() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}


def main() -> int:
    errors: list[str] = []
    if not MANIFEST.is_file():
        print("ERROR: MANIFEST.txt is missing", file=sys.stderr)
        return 1

    entries = [line.strip() for line in MANIFEST.read_text(
        encoding="utf-8-sig").splitlines() if line.strip()]
    manifest_files: set[str] = set()
    casefolded: dict[str, str] = {}

    for entry in entries:
        path = PurePosixPath(entry)
        if "\\" in entry or path.is_absolute() or ".." in path.parts:
            errors.append(f"unsafe or non-canonical manifest path: {entry}")
            continue

        folded = entry.casefold()
        if folded in casefolded:
            errors.append(
                f"duplicate manifest path ignoring case: {casefolded[folded]} / {entry}")
        else:
            casefolded[folded] = entry
        manifest_files.add(entry)

        if not (ROOT / path).is_file():
            errors.append(f"manifest entry is missing on disk: {entry}")

    for entry in sorted(REQUIRED - manifest_files):
        errors.append(f"required file is not listed in manifest: {entry}")

    try:
        visible_files = git_visible_files()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        errors.append(f"cannot enumerate Git-visible files: {exc}")
    else:
        for entry in sorted(visible_files - manifest_files):
            errors.append(
                f"Git-visible file is not listed in manifest: {entry}")
        for entry in sorted(manifest_files - visible_files):
            errors.append(
                f"manifest entry is ignored or outside Git-visible files: {entry}")

    if errors:
        print("Context validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"~/.codex DEV context OK ({len(manifest_files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
