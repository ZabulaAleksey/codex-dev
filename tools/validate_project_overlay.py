from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from hooks.stage_selector import find_stage_record, parse_stage_id
from tools.master_execution import MasterExecutionError, extract_master_state
from tools.stage_compatibility import stage_routing_snapshot
from tools.dev_paths import BRIDGE_MARKER, has_agents_bridge_declaration, has_dev_bridge

REQUIRED_FILES = (
    "AGENTS.md",
    "docs/STAGES.md",
    "docs/ARCHITECTURE.md",
    "docs/DECISIONS.md",
    "docs/LEARNING_LOG.md",
    "docs/project-context.md",
    "docs/ROADMAP.md",
)

COMPETING_EXECUTION_STATE_NAMES = {
    "ai_plan.md",
    "ai_status.md",
    "current_status.md",
    "plan.md",
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

BACKEND_DX_DELTA_HEADING = re.compile(r"(?im)^##[ \t]+Backend DX Delta[ \t]*$")
BACKEND_DX_REQUIRED_FIELDS = (
    "applicability level",
    "supported local environments",
    "canonical working directory",
    "toolchain/runtime versions",
    "package manager and lockfile",
    "canonical commands",
    "required local services",
    "readiness/status command",
    "ports and collision policy",
    "config source, profiles and required variables",
    "secret redaction/effective-config diagnostics",
    "api docs/spec and generated-contract drift command",
    "db migration/status/seed/reset-local commands",
    "destructive command guard",
    "worker/scheduler commands",
    "external sandbox/stub/fallback modes",
    "clean-room smoke command or documented manual scenario",
    "project-specific quality gates",
    "known limitations",
    "explicit deviations from global backend dx policy",
)
BACKEND_DX_COMMAND_FIELDS = (
    "bootstrap",
    "doctor",
    "dev",
    "stop",
    "check",
    "test-fast",
    "test-integration",
    "build",
    "logs",
)
BACKEND_DX_CORE_COMMANDS = {
    "bootstrap", "doctor", "dev", "stop", "check", "test-fast", "logs",
}
SENSITIVE_ENV_KEY = re.compile(
    r"(?i)(?:^|_)(?:API_KEY|ACCESS_KEY|TOKEN|PASSWORD|PASS|SECRET|PRIVATE_KEY|CLIENT_SECRET|DATABASE_URL)$"
)
SAFE_ENV_MARKERS = (
    "${", "<", "example", "changeme", "change-me", "replace", "your_",
    "your-", "dummy", "fake", "not-a-secret", "local", "localhost", "test",
)
DESTRUCTIVE_COMMAND = re.compile(r"(?i)\b(?:reset|drop|truncate|mass[ -]delete)\b")
SAFE_RESET_SCOPE = re.compile(r"(?i)\b(?:local|test)\b")
RESET_ENFORCEMENT = re.compile(r"(?i)\b(?:guard|deny|refus|reject|block|abort|only|fail[ -]closed)\w*\b")


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    project: str
    ok: bool
    inspection_ok: bool
    canonical_valid: bool
    execution_allowed: bool
    stage_state: dict[str, Any]
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
    files.discard(project / ".codex/dev-project.toml")
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


def _git_visible_paths(project: Path) -> tuple[Path, ...]:
    command = [
        "git", "-c", f"safe.directory={project}", "-C", str(project),
        "ls-files", "--cached", "--others", "--exclude-standard",
    ]
    try:
        completed = subprocess.run(
            command, check=False, capture_output=True, text=True, encoding="utf-8"
        )
    except FileNotFoundError:
        return ()
    if completed.returncode != 0:
        return ()
    paths: list[Path] = []
    for relative in completed.stdout.splitlines():
        candidate = project / relative
        if any(part in GENERATED_DEPENDENCY_DIRECTORIES or part == ".git" for part in Path(relative).parts):
            continue
        if candidate.is_file():
            paths.append(candidate)
    return tuple(sorted(paths, key=lambda path: _posix_relative(path, project).casefold()))


def _declared_managers(project: Path) -> tuple[tuple[str, Path], ...]:
    visible = _git_visible_paths(project)
    visible_set = {path.resolve() for path in visible}
    managers: set[tuple[str, Path]] = set()
    for package_json in (path for path in visible if path.name == "package.json"):
        root = package_json.parent
        try:
            package = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            package = {}
        package_manager = package.get("packageManager") if isinstance(package, dict) else None
        if isinstance(package_manager, str) and package_manager.casefold().startswith("pnpm@") or (root / "pnpm-lock.yaml").resolve() in visible_set:
            managers.add(("pnpm", root))
    for pyproject in (path for path in visible if path.name == "pyproject.toml"):
        root = pyproject.parent
        content = pyproject.read_text(encoding="utf-8-sig", errors="replace").casefold()
        if (root / "uv.lock").resolve() in visible_set or "[tool.uv" in content:
            managers.add(("uv", root))
    generic = {
        "Cargo.toml": "cargo",
        "go.mod": "go-modules",
        "composer.json": "composer",
        "pubspec.yaml": "pub",
        "Package.swift": "swiftpm",
        "vcpkg.json": "vcpkg",
        "conanfile.py": "conan",
        "conanfile.txt": "conan",
    }
    for manifest in visible:
        if manifest.name in generic:
            managers.add((generic[manifest.name], manifest.parent))
        elif manifest.name.endswith(".csproj"):
            managers.add(("nuget", manifest.parent))
        elif manifest.name.startswith("build.gradle"):
            managers.add(("gradle", manifest.parent))
    return tuple(sorted(managers, key=lambda item: (item[0], _posix_relative(item[1], project).casefold())))


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
    managers = _declared_managers(project)
    if not managers:
        return []
    issues: list[Issue] = []
    exception = _dependency_exception(project)
    visible = set(_git_visible_paths(project))
    for manager, root in managers:
        root_relative = _posix_relative(root, project) or "."
        if manager == "pnpm":
            competing = ("package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "bun.lock", "bun.lockb")
            for filename in competing:
                candidate = root / filename
                if candidate in visible and not exception:
                    issues.append(Issue("competing-lockfile", _posix_relative(candidate, project), "pnpm project has an undocumented competing lockfile"))
        elif manager == "uv" and (root / "uv.lock") not in visible:
            issues.append(Issue("missing-canonical-lockfile", f"{root_relative}/uv.lock", "uv project requires uv.lock"))
    if any(manager == "pnpm" for manager, _ in managers):
        for ci_file in _ci_files(project):
            content = ci_file.read_text(encoding="utf-8-sig", errors="replace")
            if re.search(r"\bnpm\s+(?:ci|install)\b", content) and not exception:
                issues.append(Issue("manager-inconsistent-ci", _posix_relative(ci_file, project), "pnpm project CI installs with npm"))
    if any(manager == "uv" for manager, _ in managers):
        for ci_file in _ci_files(project):
            content = ci_file.read_text(encoding="utf-8-sig", errors="replace").casefold()
            if "python" in content and "uv " not in content and not exception:
                issues.append(Issue("manager-inconsistent-ci", _posix_relative(ci_file, project), "uv project CI does not invoke uv"))
    for relative in _tracked_generated_paths(project):
        issues.append(Issue("tracked-generated-dependency-path", relative, "dependency/build cache path is tracked by Git"))
    if not _dependency_documented(project):
        issues.append(Issue("missing-dependency-contract", "docs/DEPENDENCIES.md", "document source of truth and clean restore for the detected manager"))
    return issues


def _markdown_bullet_fields(content: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    pattern = re.compile(r"(?m)^[ \t]*-[ \t]+([^:\r\n]+):[ \t]*(.*)$")
    for match in pattern.finditer(content):
        label = re.sub(r"\s+", " ", match.group(1).strip().strip("`")).casefold()
        fields[label] = match.group(2).strip().strip("`")
    return fields


def _unexplained_na(value: str) -> bool:
    normalized = value.strip().strip("`").casefold()
    if not normalized.startswith("n/a") and normalized != "not applicable":
        return False
    if normalized in {"n/a", "not applicable"}:
        return True
    return bool(re.search(r"(?i)\b(?:reason|if not applicable|if none|if no )\b", normalized))


def _env_example_issues(project: Path) -> list[Issue]:
    issues: list[Issue] = []
    for candidate in _git_visible_paths(project):
        if candidate.name.casefold() != ".env.example":
            continue
        content = candidate.read_text(encoding="utf-8-sig", errors="replace")
        if "-----BEGIN " in content and " PRIVATE KEY-----" in content:
            issues.append(Issue(
                "env-example-secret",
                _posix_relative(candidate, project),
                ".env.example contains a private-key block",
            ))
            continue
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, raw_value = stripped.split("=", 1)
            value = raw_value.strip().strip("'\"")
            if not SENSITIVE_ENV_KEY.search(key.strip()) or len(value) < 16:
                continue
            lowered = value.casefold()
            if any(marker in lowered for marker in SAFE_ENV_MARKERS):
                continue
            issues.append(Issue(
                "env-example-secret",
                _posix_relative(candidate, project),
                f"{key.strip()} has a credential-like value; use a safe placeholder",
            ))
            break
    return issues


def _backend_dx_issues(project: Path, workspace: Path) -> list[Issue]:
    issues: list[Issue] = []
    locations: list[tuple[Path, str]] = []
    heading_occurrences = 0
    for candidate in _project_text_files(project):
        try:
            content = candidate.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        matches = BACKEND_DX_DELTA_HEADING.findall(content)
        if matches:
            locations.append((candidate, content))
            heading_occurrences += len(matches)

    if not locations:
        return issues

    canonical = project / "docs/project-context.md"
    canonical_entry = next((entry for entry in locations if entry[0] == canonical), None)
    for path, _ in locations:
        if path != canonical:
            issues.append(Issue(
                "misplaced-backend-dx-delta",
                _posix_relative(path, project),
                "Backend DX Delta belongs in docs/project-context.md",
            ))
    if heading_occurrences > 1:
        issues.append(Issue(
            "duplicate-backend-dx-delta",
            "docs/project-context.md",
            "declare one canonical Backend DX Delta",
        ))
    if canonical_entry is None:
        return issues

    _, content = canonical_entry
    fields = _markdown_bullet_fields(content)
    level_value = fields.get("applicability level", "")
    levels = re.findall(r"\bBDX-L[0-3]\b", level_value.upper())
    if len(levels) != 1 or "|" in level_value:
        issues.append(Issue(
            "invalid-backend-dx-level",
            "docs/project-context.md",
            "declare exactly one applicability level BDX-L1, BDX-L2 or BDX-L3",
        ))
    elif levels[0] == "BDX-L0":
        issues.append(Issue(
            "backend-dx-l0-has-delta",
            "docs/project-context.md",
            "BDX-L0 must not contain an empty Backend DX Delta",
        ))
        return issues

    agents = project / "AGENTS.md"
    agents_content = agents.read_text(encoding="utf-8-sig", errors="replace") if agents.is_file() else ""
    if "rules/backend-dx.md" not in agents_content.replace("\\", "/").casefold():
        issues.append(Issue(
            "missing-backend-dx-route",
            "AGENTS.md",
            "route backend workflow tasks to ~/.codex/rules/backend-dx.md",
        ))

    for label in BACKEND_DX_REQUIRED_FIELDS:
        if label not in fields:
            issues.append(Issue(
                "missing-backend-dx-field",
                "docs/project-context.md",
                f"Backend DX Delta is missing field: {label}",
            ))
        elif label != "canonical commands" and not fields[label]:
            issues.append(Issue(
                "empty-backend-dx-field",
                "docs/project-context.md",
                f"Backend DX Delta field has no value: {label}",
            ))

    for command in BACKEND_DX_COMMAND_FIELDS:
        value = fields.get(command)
        if value is None or not value or (command in BACKEND_DX_CORE_COMMANDS and value.casefold().startswith("n/a")):
            issues.append(Issue(
                "missing-backend-dx-command",
                "docs/project-context.md",
                f"declare applicable command or explained N/A: {command}",
            ))

    for label, value in fields.items():
        if _unexplained_na(value):
            issues.append(Issue(
                "unexplained-backend-dx-na",
                "docs/project-context.md",
                f"N/A requires a project-specific reason: {label}",
            ))

    db_commands = fields.get("db migration/status/seed/reset-local commands", "")
    reset_guard = fields.get("destructive command guard", "")
    if DESTRUCTIVE_COMMAND.search(db_commands) and not (
        SAFE_RESET_SCOPE.search(reset_guard) and RESET_ENFORCEMENT.search(reset_guard)
    ):
        issues.append(Issue(
            "unsafe-backend-dx-reset",
            "docs/project-context.md",
            "destructive DB/resource command requires an enforced local/test guard",
        ))

    api_contract = fields.get("api docs/spec and generated-contract drift command", "")
    if api_contract and not api_contract.casefold().startswith("n/a") and not re.search(
        r"(?i)\b(?:check|verify|validate|diff|drift)\b", api_contract
    ):
        issues.append(Issue(
            "missing-generated-contract-drift-check",
            "docs/project-context.md",
            "API/generated contract declaration needs a drift/check command",
        ))

    policy_path = workspace / "rules/backend-dx.md"
    if policy_path.is_file():
        normalized = re.sub(r"\s+", " ", content).casefold()
        signature = (
            "эта policy — единый глобальный контракт воспроизводимой, discoverable, "
            "диагностируемой и безопасной разработки backend/runtime services"
        ).casefold()
        if signature in normalized:
            issues.append(Issue(
                "backend-dx-policy-copy",
                "docs/project-context.md",
                "project delta copies the canonical global policy instead of linking to it",
            ))

    issues.extend(_env_example_issues(project))
    return issues


def _stage_selector_issues(project: Path) -> list[Issue]:
    stages_path = project / "docs/STAGES.md"
    if not stages_path.is_file():
        return []

    catalog = stages_path.read_text(encoding="utf-8-sig", errors="replace")
    selector = parse_stage_id(catalog)
    if selector.issue_code:
        return [
            Issue(
                selector.issue_code,
                "docs/STAGES.md",
                selector.message or "invalid Stage ID selector",
            )
        ]

    record = find_stage_record(catalog, selector.stage_id or "")
    if record.issue_code:
        return [
            Issue(
                record.issue_code,
                "docs/STAGES.md",
                record.message or "invalid Stage heading selector",
            )
        ]
    if record.record and "```master-execution" in record.record:
        try:
            extract_master_state(record.record)
        except MasterExecutionError as exc:
            return [Issue(
                "invalid-master-execution-state",
                "docs/STAGES.md",
                str(exc),
            )]
    return []


def validate_project(project_path: Path, workspace_root: Path = WORKSPACE_ROOT) -> ValidationResult:
    project = project_path.expanduser().resolve()
    workspace = workspace_root.expanduser().resolve()
    issues: list[Issue] = []

    if not project.is_dir():
        issues.append(Issue("project-not-directory", ".", "target path is not a directory"))
        return ValidationResult(str(project), False, False, False, False, {}, tuple(issues))

    routing, _ = stage_routing_snapshot(project)
    routing_status = routing["status"]
    routing_issue = {
        "migration_plan_available": (
            "stage-migration-plan-available", "brownfield stage state requires explicit migration; a safe plan is available"
        ),
        "migration_plan_unsafe": (
            "stage-migration-plan-unsafe", "brownfield stage state requires migration but a safe plan cannot be built"
        ),
        "conflicting_stage_state": (
            "conflicting-stage-state", "canonical or canonical/legacy stage state is conflicting; execution is blocked"
        ),
        "no_stage_state": (
            "no-stage-state", "repository has no canonical or legacy stage state"
        ),
    }.get(routing_status)
    if routing_issue:
        issues.append(Issue(routing_issue[0], "docs/STAGES.md", routing_issue[1]))

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
        if relative == "docs/STAGES.md" and routing_status != "pass_canonical":
            continue
        if not (project / relative).is_file():
            issues.append(Issue("missing-required-file", relative, "required project-framework file is missing"))

    agents_file = project / "AGENTS.md"
    if agents_file.is_file() and agents_file.stat().st_size > 32 * 1024:
        issues.append(Issue("agents-not-thin", "AGENTS.md", "project router exceeds 32 KiB"))
    if not has_dev_bridge(project):
        issues.append(
            Issue(
                "missing-dev-project-marker",
                ".codex/dev-project.toml",
                "full DEV overlay must contain a valid structured DEV opt-in marker",
            )
        )
    if agents_file.is_file() and not has_agents_bridge_declaration(project):
        issues.append(
            Issue(
                "missing-dev-bridge",
                "AGENTS.md",
                f"full DEV overlay must also declare exact human-readable marker: {BRIDGE_MARKER}",
            )
        )

    for base in (project, project / "docs"):
        if not base.is_dir():
            continue
        for candidate in sorted(base.iterdir(), key=lambda item: item.name.casefold()):
            relative = _posix_relative(candidate, project)
            if (candidate.is_file()
                    and candidate.name.casefold() in COMPETING_EXECUTION_STATE_NAMES
                    and relative not in {"docs/AI_PLAN.md", "docs/AI_STATUS.md"}):
                issues.append(
                    Issue(
                        "competing-execution-state-file",
                        relative,
                        "merge current facts into docs/STAGES.md, validate, then remove this competing state file",
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
                        "detailed stage content must be consolidated into docs/STAGES.md",
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
    issues.extend(_backend_dx_issues(project, workspace))
    exact_stage_codes = {
        "missing-stage-id", "ambiguous-stage-id", "invalid-stage-id",
        "missing-stage-heading", "ambiguous-stage-heading",
    }
    for code in routing["issue_codes"]:
        if code in exact_stage_codes:
            issues.append(Issue(code, "docs/STAGES.md", "invalid canonical same-file selector"))
        elif code == "invalid_master_execution":
            issues.append(Issue(
                "invalid-master-execution-state", "docs/STAGES.md",
                "master-execution block fails the canonical CME schema",
            ))
    ordered = tuple(sorted(issues, key=lambda item: (item.code, item.path.casefold(), item.message)))
    overlay_ok = not ordered and routing["canonical_valid"] is True
    return ValidationResult(
        str(project), overlay_ok, routing["inspection_ok"],
        routing["canonical_valid"], overlay_ok and routing["execution_allowed"] is True,
        routing, ordered,
    )


def _human_output(result: ValidationResult) -> str:
    if result.ok:
        return f"Project overlay OK: {result.project}"
    label = {
        "migration_required": "Project overlay migration required",
        "conflict": "Project overlay stage state conflicts",
        "no_state": "Project overlay has no stage state",
    }.get(result.stage_state.get("outcome"), "Project overlay validation failed")
    lines = [f"{label}: {result.project}"]
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
