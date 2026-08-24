from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_FILES = (
    "AGENTS.md",
    "specs/README.md",
    "specs/system.spec.md",
    "docs/ARCHITECTURE.md",
    "docs/DECISIONS.md",
    "docs/DESIGN.md",
    "docs/ROADMAP.md",
    "docs/AI_PLAN.md",
    "docs/AI_STATUS.md",
    "docs/CONTEXT_COMPATIBILITY.md",
)
LEGACY_STATUS_FILES = {
    "current_status.md",
    "progress.md",
    "project_snapshot.md",
    "project_status.md",
    "status.md",
}
AUTOMATION_PATHS = (".agents", ".codex", ".skills", ".hooks",
                    ".mcp.json", "mcp.json", "hooks.json")
MATRIX_STATUSES = (
    "KEEP",
    "ADD",
    "ADAPT",
    "MERGE",
    "CONFLICT",
    "SUPERSEDED",
    "FORBIDDEN_TO_OVERWRITE",
)
GENERATED_DEPENDENCY_DIRECTORIES = {
    ".gradle", ".mypy_cache", ".next", ".nuxt", ".pytest_cache", ".ruff_cache",
    ".svelte-kit", ".turbo", ".venv", "__pycache__", "bin", "build", "coverage",
    "dist", "node_modules", "obj", "target", "venv",
}


@dataclass(frozen=True)
class MatrixEntry:
    path: str
    status: str
    reason: str


@dataclass(frozen=True)
class TestBaseline:
    command: tuple[str, ...]
    returncode: int
    output_digest: str
    output: str


@dataclass(frozen=True)
class TestComparison:
    pre_existing_failure: bool
    regression: bool
    baseline_returncode: int
    refreshed_returncode: int
    baseline_failures: tuple[str, ...]
    refreshed_failures: tuple[str, ...]


@dataclass(frozen=True)
class DependencyInventory:
    manager: str | None
    manifests: tuple[str, ...]
    lockfiles: tuple[str, ...]
    tracked_generated_paths: tuple[str, ...]
    drift: tuple[str, ...]


@dataclass(frozen=True)
class ReconciliationReport:
    project: str
    classification: str
    entries: tuple[MatrixEntry, ...]
    baseline: TestBaseline | None = None
    test_comparison: TestComparison | None = None
    dependency_inventory: DependencyInventory | None = None

    @property
    def blocked(self) -> bool:
        return any(entry.status == "CONFLICT" for entry in self.entries)


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _iter_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return
    if root.is_file():
        yield root
        return
    yield from sorted((path for path in root.rglob("*") if path.is_file()), key=lambda path: path.as_posix().casefold())


def classify_project(project: Path) -> str:
    project = project.expanduser().resolve()
    for path in _iter_files(project):
        if ".git" not in path.parts:
            return "BROWNFIELD"
    return "GREENFIELD"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_forbidden(path: str, project: Path, forbidden_paths: set[str]) -> bool:
    if path in forbidden_paths:
        return True
    candidate = project / path
    return not any(path == framework or path.startswith(f"{framework}/") for framework in FRAMEWORK_FILES for _ in (0,)) and candidate.exists()


def _git_tracked_paths(project: Path) -> tuple[str, ...]:
    command = ["git", "-c", f"safe.directory={project}", "-C", str(project), "ls-files", "--cached"]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        return ()
    if completed.returncode != 0:
        return ()
    return tuple(sorted((line.replace("\\", "/") for line in completed.stdout.splitlines()), key=str.casefold))


def _git_visible_paths(project: Path) -> tuple[str, ...]:
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
    return tuple(sorted((line.replace("\\", "/") for line in completed.stdout.splitlines()), key=str.casefold))


def dependency_inventory(project_path: Path) -> DependencyInventory:
    project = project_path.expanduser().resolve()
    visible = _git_visible_paths(project)
    generated = GENERATED_DEPENDENCY_DIRECTORIES | {".git"}
    visible = tuple(path for path in visible if not any(part in generated for part in Path(path).parts))
    manifest_names = {
        "package.json", "pyproject.toml", "Cargo.toml", "go.mod", "composer.json",
        "pubspec.yaml", "Package.swift", "vcpkg.json", "conanfile.py", "conanfile.txt",
    }
    lock_names = {
        "pnpm-lock.yaml", "package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "bun.lock", "bun.lockb",
        "uv.lock", "Cargo.lock", "go.sum", "composer.lock", "pubspec.lock", "Package.resolved", "conan.lock", "packages.lock.json",
    }
    manifests = tuple(path for path in visible if Path(path).name in manifest_names or Path(path).suffix == ".csproj" or Path(path).name.startswith("build.gradle"))
    lockfiles = tuple(path for path in visible if Path(path).name in lock_names)
    managers: set[tuple[str, str]] = set()
    for relative in (path for path in manifests if Path(path).name == "package.json"):
        package_json = project / relative
        root = Path(relative).parent
        try:
            package = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            package = {}
        pinned = package.get("packageManager") if isinstance(package, dict) else None
        if isinstance(pinned, str) and pinned.casefold().startswith("pnpm@") or (root / "pnpm-lock.yaml").as_posix() in lockfiles:
            managers.add(("pnpm", root.as_posix()))
    for relative in (path for path in manifests if Path(path).name == "pyproject.toml"):
        root = Path(relative).parent
        pyproject = (project / relative).read_text(encoding="utf-8-sig", errors="replace").casefold()
        if (root / "uv.lock").as_posix() in lockfiles or "[tool.uv" in pyproject:
            managers.add(("uv", root.as_posix()))
    generic = {
        "Cargo.toml": "cargo", "go.mod": "go-modules", "composer.json": "composer",
        "pubspec.yaml": "pub", "Package.swift": "swiftpm", "vcpkg.json": "vcpkg",
        "conanfile.py": "conan", "conanfile.txt": "conan",
    }
    for relative in manifests:
        name = Path(relative).name
        root = Path(relative).parent.as_posix()
        if name in generic:
            managers.add((generic[name], root))
        elif name.endswith(".csproj"):
            managers.add(("nuget", root))
        elif name.startswith("build.gradle"):
            managers.add(("gradle", root))
    manager = ", ".join(sorted({name for name, _ in managers})) or None
    tracked_generated = tuple(path for path in _git_tracked_paths(project) if any(part in GENERATED_DEPENDENCY_DIRECTORIES for part in Path(path).parts))
    drift: list[str] = []
    for name, root in managers:
        prefix = "" if root == "." else f"{root}/"
        scope = "" if root == "." else f":{root}"
        if name == "pnpm":
            competing = {f"{prefix}{filename}" for filename in ("package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "bun.lock", "bun.lockb")}
            if any(lockfile in competing for lockfile in lockfiles):
                drift.append(f"competing-node-lockfile{scope}")
        if name == "uv" and f"{prefix}uv.lock" not in lockfiles:
            drift.append(f"missing-uv-lockfile{scope}")
    if tracked_generated:
        drift.append("tracked-generated-dependency-path")
    if managers:
        dependency_docs = (project / "docs/DEPENDENCIES.md", project / "docs/ARCHITECTURE.md")
        documented = False
        for candidate in dependency_docs:
            if not candidate.is_file():
                continue
            content = candidate.read_text(encoding="utf-8-sig", errors="replace").casefold()
            if ("source of truth" in content or "источник истины" in content) and (
                "clean restore" in content or "чистое восстановление" in content
            ):
                documented = True
                break
        if not documented:
            drift.append("missing-dependency-contract")
    return DependencyInventory(manager, manifests, lockfiles, tracked_generated, tuple(sorted(drift)))


def reconcile_project(
    project_path: Path,
    *,
    framework_root: Path | None = None,
    forbidden_paths: Iterable[str] = (),
    resolved_conflicts: Iterable[str] = (),
) -> ReconciliationReport:
    project = project_path.expanduser().resolve()
    framework_root = (framework_root or WORKSPACE_ROOT).expanduser().resolve()
    forbidden = set(forbidden_paths)
    resolved = set(resolved_conflicts)
    entries: list[MatrixEntry] = []
    inventory = dependency_inventory(project)

    for relative in FRAMEWORK_FILES:
        project_file = project / relative
        framework_file = framework_root / relative
        if not project_file.exists():
            entries.append(MatrixEntry(relative, "ADD",
                           "framework artifact is absent"))
        elif framework_file.is_file() and _digest(project_file) == _digest(framework_file):
            entries.append(MatrixEntry(relative, "KEEP",
                           "project already matches the canonical artifact"))
        elif classify_project(project) == "GREENFIELD":
            entries.append(MatrixEntry(
                relative, "ADAPT", "greenfield artifact needs project-specific content"))
        else:
            entries.append(MatrixEntry(
                relative, "MERGE", "existing project content must be preserved and reconciled"))

    for path in _iter_files(project):
        relative = _relative(path, project)
        if ".git" in path.relative_to(project).parts:
            continue
        if relative in FRAMEWORK_FILES:
            continue
        if Path(relative).name.casefold() in LEGACY_STATUS_FILES:
            entries.append(MatrixEntry(relative, "SUPERSEDED",
                           "AI_STATUS.md is the canonical current-status source"))
        elif any(relative == automation or relative.startswith(f"{automation}/") for automation in AUTOMATION_PATHS) and "conflict" in path.read_text(encoding="utf-8", errors="replace").casefold():
            status = "ADAPT" if relative in resolved else "CONFLICT"
            reason = "conflict has an explicit resolution" if relative in resolved else "project automation explicitly signals an unresolved conflict"
            entries.append(MatrixEntry(relative, status, reason))
        elif _is_forbidden(relative, project, forbidden):
            entries.append(MatrixEntry(relative, "FORBIDDEN_TO_OVERWRITE",
                           "existing project content is protected from framework writes"))

    ordered = tuple(sorted(entries, key=lambda entry: (
        entry.path.casefold(), entry.status)))
    return ReconciliationReport(str(project), classify_project(project), ordered, dependency_inventory=inventory)


def capture_test_baseline(command: Sequence[str], *, cwd: Path) -> TestBaseline:
    completed = subprocess.run(
        command, cwd=cwd, check=False, capture_output=True, text=True, encoding="utf-8")
    output = f"{completed.stdout}{completed.stderr}"
    return TestBaseline(tuple(command), completed.returncode, hashlib.sha256(output.encode("utf-8")).hexdigest(), output)


def compare_test_runs(baseline: TestBaseline, refreshed: TestBaseline) -> TestComparison:
    baseline_failures = _failure_ids(baseline.output)
    refreshed_failures = _failure_ids(refreshed.output)
    pre_existing = baseline.returncode != 0
    regression = bool(set(refreshed_failures) - set(baseline_failures)
                      ) or (not pre_existing and refreshed.returncode != 0)
    return TestComparison(pre_existing, regression, baseline.returncode, refreshed.returncode, baseline_failures, refreshed_failures)


def _failure_ids(output: str) -> tuple[str, ...]:
    failures: set[str] = set()
    for line in output.splitlines():
        if line.startswith("FAIL: ") or line.startswith("ERROR: "):
            failures.add(line.split(": ", 1)[1].strip())
    return tuple(sorted(failures))


def render_report(report: ReconciliationReport) -> str:
    lines = [
        "# Brownfield Reconciliation",
        "",
        f"- Project: `{report.project}`",
        f"- Classification: `{report.classification}`",
        f"- Mutation gate: `{'BLOCKED' if report.blocked else 'OPEN'}`",
        "",
        "| Path | Status | Reason |",
        "|---|---|---|",
    ]
    lines.extend(
        f"| `{entry.path}` | `{entry.status}` | {entry.reason} |" for entry in report.entries)
    inventory = report.dependency_inventory
    if inventory and (inventory.manager or inventory.manifests or inventory.lockfiles):
        lines.extend([
            "",
            "## Dependency inventory",
            "",
            f"- Manager: `{inventory.manager or 'undetermined'}`",
            f"- Manifests: {', '.join(f'`{item}`' for item in inventory.manifests) or 'none'}",
            f"- Lockfiles: {', '.join(f'`{item}`' for item in inventory.lockfiles) or 'none'}",
            f"- Tracked generated paths: {', '.join(f'`{item}`' for item in inventory.tracked_generated_paths) or 'none'}",
            f"- Drift: {', '.join(f'`{item}`' for item in inventory.drift) or 'none'}",
        ])
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only brownfield reconciliation for a project framework overlay.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--workspace-root", type=Path,
                        default=WORKSPACE_ROOT, help=argparse.SUPPRESS)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = reconcile_project(
        args.project, framework_root=args.workspace_root)
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_report(report), end="")
    return 1 if report.blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
