from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "AGENTS.md",
    "prompts/STAGES.md",
    "docs/ARCHITECTURE.md",
    "docs/DECISIONS.md",
    "docs/LEARNING_LOG.md",
    "docs/project-context.md",
    "docs/ROADMAP.md",
    "docs/AI_PLAN.md",
    "docs/AI_STATUS.md",
)

ALTERNATE_STATUS_NAMES = {
    "current_status.md",
    "progress.md",
    "project_snapshot.md",
    "project_status.md",
    "status.md",
}

AUTOMATION_DIRECTORIES = (
    ".agents",
    ".codex",
    ".skills",
    ".hooks",
)

AUTOMATION_FILES = (
    ".mcp.json",
    "mcp.json",
    "hooks.json",
    "docs/git-flow.md",
    "docs/WORKFLOW.md",
)

CANONICAL_SOURCES = (
    "AGENTS.md",
    "agents",
    "config.ai-dev-team.recommended.toml",
    "hooks.json",
    "hooks",
    "skill-sources",
    "rules",
    "docs/WORKFLOW.md",
)

TEXT_SUFFIXES = {".md", ".toml", ".json", ".yaml", ".yml", ".ps1", ".py", ".sh", ".bat", ".cmd", ".ts", ".tsx", ".js", ".mjs", ".cjs"}
SKIP_DIRECTORIES = {
    ".astro",
    ".dart_tool",
    ".git",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".svelte-kit",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "htmlcov",
    "node_modules",
    "target",
}
GENERATED_DEPENDENCY_DIRECTORIES = {
    ".gradle",
    ".mypy_cache",
    ".next",
    ".nuxt",
    ".pytest_cache",
    ".ruff_cache",
    ".svelte-kit",
    ".turbo",
    ".venv",
    "__pycache__",
    "bin",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "obj",
    "target",
    "venv",
}
STALE_PATH_PATTERNS = (
    "~/codex-" "workspace/AGENTS.md",
    "~/codex-" "workspace/rules/",
    "~/codex-" "workspace/docs/",
    "codex-workspace/projects/",
    "codex-workspace\\projects\\",
)


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    project: str
    ok: bool
    issues: tuple[Issue, ...]


def _posix_relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _git_root(project: Path) -> tuple[Path | None, str | None]:
    command = [
        "git",
        "-c",
        f"safe.directory={project}",
        "-C",
        str(project),
        "rev-parse",
        "--show-toplevel",
    ]
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:
        return None, "Git executable is unavailable"

    if completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()
        return None, detail[-1] if detail else "not a Git repository"

    raw_root = completed.stdout.strip()
    if not raw_root:
        return None, "Git returned an empty repository root"
    return Path(raw_root).resolve(), None


def _iter_files(path: Path) -> Iterable[Path]:
    if path.is_file():
        yield path
    elif path.is_dir():
        yield from sorted(
            (candidate for candidate in path.rglob("*") if candidate.is_file()),
            key=lambda candidate: candidate.as_posix().casefold(),
        )


def _automation_files(project: Path) -> list[Path]:
    files: set[Path] = set()
    for relative in AUTOMATION_DIRECTORIES:
        files.update(_iter_files(project / relative))
    for relative in AUTOMATION_FILES:
        candidate = project / relative
        if candidate.is_file():
            files.add(candidate)
    return sorted(files, key=lambda candidate: _posix_relative(candidate, project).casefold())


def _project_text_files(project: Path) -> Iterable[Path]:
    for candidate in project.rglob("*"):
        if not candidate.is_file() or any(part in SKIP_DIRECTORIES for part in candidate.parts):
            continue
        if candidate.suffix.casefold() in TEXT_SUFFIXES or candidate.name.startswith("Dockerfile"):
            yield candidate


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _has_project_automation_classification(path: Path) -> bool:
    content = path.read_text(encoding="utf-8-sig")
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = (cell.strip().strip("`") for cell in stripped.strip("|").split("|"))
            if any(cell in {"EXTEND", "PROJECT_ONLY"} for cell in cells):
                return True
        if stripped.startswith(("-", "*")) and re.search(r"\b(?:EXTEND|PROJECT_ONLY)\b", stripped):
            return True
    return False


def _canonical_digests(workspace_root: Path) -> dict[str, list[str]]:
    digests: dict[str, list[str]] = {}
    for relative in CANONICAL_SOURCES:
        source = workspace_root / relative
        for file_path in _iter_files(source):
            if "__pycache__" in file_path.parts or file_path.suffix in {".pyc", ".pyo"}:
                continue
            digest = _digest(file_path)
            digests.setdefault(digest, []).append(_posix_relative(file_path, workspace_root))
    for paths in digests.values():
        paths.sort(key=str.casefold)
    return digests


def _dependency_exception(project: Path) -> bool:
    for relative in ("docs/DEPENDENCIES.md", "docs/ARCHITECTURE.md"):
        candidate = project / relative
        if candidate.is_file() and "dependency-manager exception" in candidate.read_text(
            encoding="utf-8-sig", errors="replace"
        ).casefold():
            return True
    return False


def _dependency_documented(project: Path) -> bool:
    for relative in ("docs/DEPENDENCIES.md", "docs/ARCHITECTURE.md"):
        candidate = project / relative
        if not candidate.is_file():
            continue
        content = candidate.read_text(encoding="utf-8-sig", errors="replace").casefold()
        source_of_truth = "source of truth" in content or "источник истины" in content
        clean_restore = "clean restore" in content or "чистое восстановление" in content
        if source_of_truth and clean_restore:
            return True
    return False


def _declared_manager(project: Path) -> str | None:
    package_json = project / "package.json"
    if package_json.is_file():
        try:
            package = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            package = {}
        package_manager = package.get("packageManager") if isinstance(package, dict) else None
        if isinstance(package_manager, str) and package_manager.casefold().startswith("pnpm@"):
            return "pnpm"
        if (project / "pnpm-lock.yaml").is_file():
            return "pnpm"

    pyproject = project / "pyproject.toml"
    if pyproject.is_file():
        content = pyproject.read_text(encoding="utf-8-sig", errors="replace").casefold()
        if (project / "uv.lock").is_file() or "[tool.uv" in content:
            return "uv"
    return None


def _tracked_generated_paths(project: Path) -> tuple[str, ...]:
    command = ["git", "-c", f"safe.directory={project}", "-C", str(project), "ls-files", "--cached"]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        return ()
    if completed.returncode != 0:
        return ()
    tracked = []
    for line in completed.stdout.splitlines():
        parts = Path(line).parts
        if any(part in GENERATED_DEPENDENCY_DIRECTORIES for part in parts):
            tracked.append(line.replace("\\", "/"))
    return tuple(sorted(tracked, key=str.casefold))


def _ci_files(project: Path) -> Iterable[Path]:
    ci = project / ".github" / "workflows"
    if ci.is_dir():
        yield from sorted((path for path in ci.rglob("*") if path.is_file()), key=lambda path: path.as_posix().casefold())


def _dependency_issues(project: Path) -> list[Issue]:
    manager = _declared_manager(project)
    if manager is None:
        return []
    issues: list[Issue] = []
    exception = _dependency_exception(project)
    if manager == "pnpm":
        competing = ("package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "bun.lock", "bun.lockb")
        for relative in competing:
            if (project / relative).is_file() and not exception:
                issues.append(Issue("competing-lockfile", relative, "pnpm project has an undocumented competing lockfile"))
        for ci_file in _ci_files(project):
            content = ci_file.read_text(encoding="utf-8-sig", errors="replace")
            if re.search(r"\bnpm\s+(?:ci|install)\b", content) and not exception:
                issues.append(Issue("manager-inconsistent-ci", _posix_relative(ci_file, project), "pnpm project CI installs with npm"))
    elif manager == "uv":
        if not (project / "uv.lock").is_file():
            issues.append(Issue("missing-canonical-lockfile", "uv.lock", "uv project requires uv.lock"))
        for ci_file in _ci_files(project):
            content = ci_file.read_text(encoding="utf-8-sig", errors="replace").casefold()
            if "python" in content and "uv " not in content and not exception:
                issues.append(Issue("manager-inconsistent-ci", _posix_relative(ci_file, project), "uv project CI does not invoke uv"))
    for relative in _tracked_generated_paths(project):
        issues.append(Issue("tracked-generated-dependency-path", relative, "dependency/build cache path is tracked by Git"))
    if not _dependency_documented(project):
        issues.append(Issue("missing-dependency-contract", "docs/DEPENDENCIES.md", "document source of truth and clean restore for the detected manager"))
    return issues


def validate_project(project_path: Path, workspace_root: Path = WORKSPACE_ROOT) -> ValidationResult:
    project = project_path.expanduser().resolve()
    workspace = workspace_root.expanduser().resolve()
    issues: list[Issue] = []

    if not project.is_dir():
        issues.append(Issue("project-not-directory", ".", "target path is not a directory"))
        return ValidationResult(str(project), False, tuple(issues))

    git_marker = project / ".git"
    git_root, git_error = _git_root(project)
    if not git_marker.exists() or git_root is None:
        issues.append(
            Issue("not-git-root", ".", f"target is not an independent Git root: {git_error or 'missing .git'}")
        )
    elif git_root != project:
        issues.append(
            Issue("not-git-root", ".", f"Git root is {git_root}, not the target directory")
        )

    for relative in REQUIRED_FILES:
        if not (project / relative).is_file():
            issues.append(Issue("missing-required-file", relative, "required project-framework file is missing"))

    agents_file = project / "AGENTS.md"
    if agents_file.is_file() and agents_file.stat().st_size > 32 * 1024:
        issues.append(Issue("agents-not-thin", "AGENTS.md", "project router exceeds 32 KiB"))

    for base in (project, project / "docs"):
        if not base.is_dir():
            continue
        for candidate in sorted(base.iterdir(), key=lambda item: item.name.casefold()):
            if candidate.is_file() and candidate.name.casefold() in ALTERNATE_STATUS_NAMES:
                issues.append(
                    Issue(
                        "alternate-status-file",
                        _posix_relative(candidate, project),
                        "use docs/AI_STATUS.md as the only current-status source",
                    )
                )

    prompts = project / "prompts"
    if prompts.is_dir():
        for candidate in sorted(prompts.rglob("*.md"), key=lambda item: item.as_posix().casefold()):
            if candidate.name.casefold() not in {"stages.md", "readme.md"}:
                issues.append(
                    Issue(
                        "legacy-stage-file",
                        _posix_relative(candidate, project),
                        "detailed stage content must be consolidated into prompts/STAGES.md",
                    )
                )

    for candidate in _project_text_files(project):
        try:
            content = candidate.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            continue
        for pattern in STALE_PATH_PATTERNS:
            if pattern in content:
                issues.append(
                    Issue(
                        "stale-workspace-path",
                        _posix_relative(candidate, project),
                        f"contains obsolete path pattern {pattern}",
                    )
                )
                break
        if re.search(r"(?i)[A-Z]:\\Users\\[^\\]+\\codex-workspace(?:\\|$)", content):
            issues.append(
                Issue(
                    "machine-specific-workspace-path",
                    _posix_relative(candidate, project),
                    "contains a machine-specific codex-workspace path",
                )
            )

    wrong_agent_root = project / ".agents"
    if wrong_agent_root.is_dir():
        for candidate in wrong_agent_root.rglob("*.toml"):
            issues.append(
                Issue(
                    "agent-in-skill-directory",
                    _posix_relative(candidate, project),
                    "custom agent TOML belongs in .codex/agents",
                )
            )

    local_automation = _automation_files(project)
    compatibility = project / "docs/CONTEXT_COMPATIBILITY.md"
    if local_automation:
        if not compatibility.is_file():
            issues.append(
                Issue(
                    "missing-compatibility-audit",
                    "docs/CONTEXT_COMPATIBILITY.md",
                    "project-local automation requires a compatibility audit",
                )
            )
        elif not _has_project_automation_classification(compatibility):
            issues.append(
                Issue(
                    "invalid-compatibility-audit",
                    "docs/CONTEXT_COMPATIBILITY.md",
                    "audit must classify local automation as EXTEND or PROJECT_ONLY",
                )
            )

    canonical_digests = _canonical_digests(workspace)
    duplicate_candidates = set(local_automation)
    if agents_file.is_file():
        duplicate_candidates.add(agents_file)
    for candidate in sorted(duplicate_candidates, key=lambda item: _posix_relative(item, project).casefold()):
        matches = canonical_digests.get(_digest(candidate), [])
        if matches:
            issues.append(
                Issue(
                    "exact-global-duplicate",
                    _posix_relative(candidate, project),
                    f"exact copy of canonical {'; '.join(matches)}",
                )
            )

    issues.extend(_dependency_issues(project))
    ordered = tuple(sorted(issues, key=lambda item: (item.code, item.path.casefold(), item.message)))
    return ValidationResult(str(project), not ordered, ordered)


def _human_output(result: ValidationResult) -> str:
    if result.ok:
        return f"Project overlay OK: {result.project}"
    lines = [f"Project overlay validation failed: {result.project}"]
    lines.extend(f"- [{issue.code}] {issue.path}: {issue.message}" for issue in result.issues)
    return "\n".join(lines)


def _json_output(result: ValidationResult) -> str:
    return json.dumps(asdict(result), ensure_ascii=False, indent=2, sort_keys=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only validation of one project-framework overlay.")
    parser.add_argument("project", type=Path, help="path to an independent project Git repository")
    parser.add_argument("--json", action="store_true", help="emit deterministic JSON instead of human text")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=WORKSPACE_ROOT,
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_project(args.project, args.workspace_root)
    print(_json_output(result) if args.json else _human_output(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
