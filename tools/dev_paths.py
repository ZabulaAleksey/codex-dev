from __future__ import annotations

import argparse
import json
import ntpath
import os
import posixpath
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping
from urllib.parse import urlsplit, urlunsplit


ROLE_ENV = {
    "dev_source_root": "DEV_SOURCE_ROOT",
    "codex_home": "CODEX_HOME",
    "projects_root": "PROJECTS_ROOT",
}
DEFAULTS = {
    "dev_source_root": "~/codex-dev",
    "codex_home": "~/.codex",
    "projects_root": "~",
}
BRIDGE_MARKER = "Global DEV bridge: enabled"
CONFIG_RELATIVE_PATH = Path(".codex") / "dev-layout.toml"
LEGACY_WORKSPACE_NAME = "codex-workspace"


class PathResolutionError(RuntimeError):
    """A deterministic, user-actionable path resolution failure."""


@dataclass(frozen=True)
class DevLayout:
    dev_source_root: Path
    codex_home: Path
    projects_root: Path
    source: dict[str, str]

    def as_dict(self) -> dict[str, object]:
        return {
            "dev_source_root": str(self.dev_source_root),
            "codex_home": str(self.codex_home),
            "projects_root": str(self.projects_root),
            "source": dict(self.source),
        }


@dataclass(frozen=True)
class ProjectState:
    path: str
    exists: bool
    git_repo: bool
    dev_integration: str
    bridge: str
    dev_source_root: str


def _expand_tilde(raw: str, user_home: str) -> str:
    if raw == "~":
        return user_home
    if raw.startswith(("~/", "~\\")):
        return user_home.rstrip("/\\") + raw[1:]
    if raw.startswith("~"):
        raise PathResolutionError(f"unsupported user expansion: {raw!r}")
    return raw


def normalize_path_text(raw: str, *, user_home: str, platform: str | None = None) -> str:
    """Normalize without requiring the target platform, which keeps tests portable."""
    if not isinstance(raw, str) or not raw.strip() or "\0" in raw:
        raise PathResolutionError("path value must be a non-empty string without NUL")
    value = _expand_tilde(raw.strip(), user_home)
    selected = platform or ("nt" if os.name == "nt" else "posix")
    if selected == "nt":
        value = value.replace("/", "\\")
        if not ntpath.isabs(value):
            value = ntpath.join(user_home, value)
        return ntpath.normpath(value)
    if selected != "posix":
        raise PathResolutionError(f"unsupported path platform: {selected}")
    value = value.replace("\\", "/")
    if not posixpath.isabs(value):
        value = posixpath.join(user_home, value)
    return posixpath.normpath(value)


def normalize_path(raw: str, *, user_home: Path) -> Path:
    text = normalize_path_text(raw, user_home=str(user_home), platform="nt" if os.name == "nt" else "posix")
    return Path(text).resolve(strict=False)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _load_local_config(config_path: Path) -> dict[str, str]:
    if not config_path.exists():
        return {}
    if not config_path.is_file():
        raise PathResolutionError(f"local config is not a regular file: {config_path}")
    try:
        raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise PathResolutionError(f"local config is unreadable or invalid: {type(exc).__name__}") from exc
    paths = raw.get("paths", {})
    if not isinstance(paths, dict):
        raise PathResolutionError("local config [paths] must be a TOML table")
    unknown = set(paths) - set(ROLE_ENV)
    if unknown:
        raise PathResolutionError("local config has unknown path roles: " + ", ".join(sorted(unknown)))
    result: dict[str, str] = {}
    for role, value in paths.items():
        if not isinstance(value, str) or not value.strip():
            raise PathResolutionError(f"local config paths.{role} must be a non-empty string")
        result[role] = value
    return result


def resolve_layout(
    *,
    environ: Mapping[str, str] | None = None,
    user_home: Path | None = None,
    config_path: Path | None = None,
) -> DevLayout:
    env = os.environ if environ is None else environ
    home = (Path.home() if user_home is None else user_home).resolve(strict=False)
    local_path = config_path if config_path is not None else home / CONFIG_RELATIVE_PATH
    local = _load_local_config(local_path)
    values: dict[str, Path] = {}
    sources: dict[str, str] = {}
    for role, env_name in ROLE_ENV.items():
        if env_name in env:
            raw = env[env_name]
            source = "env"
        elif role in local:
            raw = local[role]
            source = "local_config"
        else:
            raw = DEFAULTS[role]
            source = "default"
        values[role] = normalize_path(raw, user_home=home)
        sources[role] = source
    source_root = values["dev_source_root"]
    codex_home = values["codex_home"]
    if (
        source_root == codex_home
        or _is_relative_to(source_root, codex_home)
        or _is_relative_to(codex_home, source_root)
    ):
        raise PathResolutionError("DEV_SOURCE_ROOT and CODEX_HOME must be separate non-overlapping trees")
    return DevLayout(
        dev_source_root=values["dev_source_root"],
        codex_home=values["codex_home"],
        projects_root=values["projects_root"],
        source=sources,
    )


def project_path(layout: DevLayout, project: str) -> Path:
    if not isinstance(project, str) or not project.strip():
        raise PathResolutionError("project name must be a non-empty top-level directory name")
    name = project.strip()
    if name in {".", ".."} or "/" in name or "\\" in name or Path(name).is_absolute():
        raise PathResolutionError("project name must not contain a path separator")
    candidate = (layout.projects_root / name).resolve(strict=False)
    if candidate.parent != layout.projects_root.resolve(strict=False):
        raise PathResolutionError("project path escapes PROJECTS_ROOT")
    return candidate


def _run_git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", f"safe.directory={root}", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def is_exact_git_root(path: Path) -> bool:
    if not path.is_dir():
        return False
    result = _run_git(path, "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        return False
    try:
        return Path(result.stdout.strip()).resolve(strict=False) == path.resolve(strict=False)
    except OSError:
        return False


def has_dev_bridge(project: Path) -> bool:
    agents = project / "AGENTS.md"
    if not agents.is_file():
        return False
    try:
        return any(line.strip() == BRIDGE_MARKER for line in agents.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeDecodeError):
        return False


def inspect_project(path: Path, layout: DevLayout) -> ProjectState:
    resolved = path.expanduser().resolve(strict=False)
    exists = resolved.is_dir()
    git_repo = is_exact_git_root(resolved) if exists else False
    is_source = resolved == layout.dev_source_root.resolve(strict=False)
    bridge = "dev_source" if is_source else "agents_marker" if has_dev_bridge(resolved) else "none"
    enabled = git_repo and bridge != "none"
    return ProjectState(
        path=str(resolved),
        exists=exists,
        git_repo=git_repo,
        dev_integration="enabled" if enabled else "disabled",
        bridge=bridge,
        dev_source_root=str(layout.dev_source_root),
    )


def resolve_project_reference(reference: str, layout: DevLayout) -> Path:
    if not isinstance(reference, str) or not reference.strip():
        raise PathResolutionError("project reference must be non-empty")
    value = reference.strip()
    if (
        value in {".", "..", "~"}
        or value.startswith(("./", ".\\", "../", "..\\", "~/", "~\\"))
        or Path(value).is_absolute()
        or "/" in value
        or "\\" in value
    ):
        return Path(value).expanduser().resolve(strict=False)
    return project_path(layout, value)


def _sanitize_remote(value: str) -> str:
    value = value.strip()
    if not value:
        return value
    if "://" in value:
        parsed = urlsplit(value)
        hostname = parsed.hostname or ""
        if parsed.port:
            hostname += f":{parsed.port}"
        return urlunsplit((parsed.scheme, hostname, parsed.path, "", ""))
    # SCP-like Git URL. Remove possible user identity without exposing it.
    if re.match(r"^[^/@:]+@[^/:]+:", value):
        return value.split("@", 1)[1]
    return value


def _nested_git_roots(source: Path) -> list[str]:
    ignored = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "dist", "build"}
    found: list[str] = []
    for current, directories, files in os.walk(source):
        current_path = Path(current)
        if current_path != source and (".git" in directories or ".git" in files):
            found.append(str(current_path.resolve(strict=False)))
            directories[:] = []
            continue
        directories[:] = [name for name in directories if name not in ignored]
    return sorted(found, key=str.casefold)


def project_move_preflight(source: Path, destination: Path) -> dict[str, object]:
    source = source.expanduser().resolve(strict=False)
    destination = destination.expanduser().resolve(strict=False)
    git_root = is_exact_git_root(source)
    status = _run_git(source, "status", "--porcelain=v1", "--branch") if git_root else None
    branch = _run_git(source, "branch", "--show-current") if git_root else None
    remotes = _run_git(source, "remote", "-v") if git_root else None
    worktrees = _run_git(source, "worktree", "list", "--porcelain") if git_root else None
    submodules = _run_git(source, "submodule", "status", "--recursive") if git_root else None
    status_lines = status.stdout.splitlines() if status and status.returncode == 0 else []
    dirty = any(line and not line.startswith("##") for line in status_lines)
    branch_name = branch.stdout.strip() if branch and branch.returncode == 0 else ""
    remote_lines = sorted({_sanitize_remote(line.split("\t", 1)[1].rsplit(" ", 1)[0])
                           for line in remotes.stdout.splitlines() if "\t" in line}) if remotes else []
    worktree_paths = [line[9:] for line in worktrees.stdout.splitlines() if line.startswith("worktree ")] if worktrees else []
    nested = _nested_git_roots(source) if source.is_dir() else []
    submodule_lines = submodules.stdout.splitlines() if submodules and submodules.returncode == 0 else []
    submodule_problem = any(line.startswith(("-", "+", "U")) for line in submodule_lines)
    checks = {
        "source_exists": source.is_dir(),
        "exact_git_root": git_root,
        "working_tree_known": bool(status and status.returncode == 0),
        "working_tree_clean": bool(status and status.returncode == 0 and not dirty),
        "branch_known": bool(branch_name),
        "branch": branch_name,
        "remotes_checked": bool(remotes and remotes.returncode == 0),
        "remotes": remote_lines,
        "nested_git_repositories": nested,
        "worktrees_checked": bool(worktrees and worktrees.returncode == 0),
        "additional_worktrees": worktree_paths[1:] if len(worktree_paths) > 1 else [],
        "submodules_checked": bool(submodules and submodules.returncode == 0),
        "submodules": submodule_lines,
        "submodules_clean": not submodule_problem,
        "destination_collision": destination.exists(),
    }
    safe = all((
        checks["source_exists"], checks["exact_git_root"], checks["working_tree_known"],
        checks["working_tree_clean"], checks["branch_known"], checks["remotes_checked"],
        checks["worktrees_checked"], checks["submodules_checked"], checks["submodules_clean"],
        not checks["nested_git_repositories"], not checks["additional_worktrees"],
        not checks["destination_collision"],
    ))
    commands: list[str] = []
    if safe:
        quoted_source = str(source).replace("'", "''")
        quoted_destination = str(destination).replace("'", "''")
        commands = [
            f"Move-Item -LiteralPath '{quoted_source}' -Destination '{quoted_destination}'",
            f"git -C '{quoted_destination}' status --short --branch",
            f"git -C '{quoted_destination}' remote -v",
            f"git -C '{quoted_destination}' rev-parse --show-toplevel",
        ]
    return {
        "source": str(source),
        "destination": str(destination),
        "safe": safe,
        "checks": checks,
        "recommended_commands": commands,
        "deletion_or_archive_automatic": False,
    }


def migration_diagnostics(layout: DevLayout, *, user_home: Path | None = None) -> dict[str, object]:
    home = (Path.home() if user_home is None else user_home).resolve(strict=False)
    old_workspace = home / LEGACY_WORKSPACE_NAME
    old_source_candidates = [old_workspace / "codex-dev", layout.codex_home]
    old_source_paths = [path.resolve(strict=False) for path in old_source_candidates if is_exact_git_root(path)]
    old_sources = [str(path) for path in old_source_paths]
    new_source = layout.dev_source_root.resolve(strict=False)
    source_move_plans = [project_move_preflight(path, new_source) for path in old_source_paths]
    old_projects: list[dict[str, object]] = []
    if old_workspace.is_dir():
        for candidate in sorted(old_workspace.iterdir(), key=lambda item: item.name.casefold()):
            if candidate.name in {"codex-dev", ".worktrees"} or not is_exact_git_root(candidate):
                continue
            destination = project_path(layout, candidate.name)
            old_projects.append(project_move_preflight(candidate, destination))
    collisions = [item["destination"] for item in old_projects if item["checks"]["destination_collision"]]
    source_collision = bool(
        len(old_source_paths) > 1
        or (old_source_paths and is_exact_git_root(new_source) and new_source not in old_source_paths)
    )
    new_source_detected = is_exact_git_root(new_source)
    identity_source = new_source if new_source_detected else old_source_paths[0] if len(old_source_paths) == 1 else None
    identity_remotes: list[str] = []
    if identity_source is not None:
        result = _run_git(identity_source, "remote", "-v")
        identity_remotes = sorted({_sanitize_remote(line.split("\t", 1)[1].rsplit(" ", 1)[0])
                                   for line in result.stdout.splitlines() if "\t" in line})
    legacy_remote = any("codex-workspace" in remote.casefold() for remote in identity_remotes)
    safe = (
        not source_collision
        and not collisions
        and all(bool(item["safe"]) for item in source_move_plans)
        and all(bool(item["safe"]) for item in old_projects)
    )
    return {
        "layout": layout.as_dict(),
        "old_source_detected": old_sources,
        "old_source_move_plans": source_move_plans,
        "new_source_detected": new_source_detected,
        "old_project_roots": old_projects,
        "collisions": {
            "source": source_collision,
            "products": collisions,
        },
        "repository_identity": {
            "target_name": "codex-dev",
            "source_basename": identity_source.name if identity_source is not None else new_source.name,
            "remotes": identity_remotes,
            "legacy_remote_detected": legacy_remote,
            "github_rename_ready": new_source_detected and new_source.name == "codex-dev" and not legacy_remote,
        },
        "safe": safe,
        "notes": [
            "Legacy paths are diagnostic evidence only and are never selected automatically.",
            "No source or product repository is deleted or archived by this tool.",
        ],
    }


def _render_human(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve and diagnose global DEV filesystem roles")
    subparsers = parser.add_subparsers(dest="command", required=True)
    resolve_parser = subparsers.add_parser("resolve", help="print normalized path roles and resolution sources")
    resolve_parser.add_argument("--json", action="store_true")
    diagnose_parser = subparsers.add_parser("diagnose", help="audit new and legacy layout without mutations")
    diagnose_parser.add_argument("--json", action="store_true")
    project_parser = subparsers.add_parser("project", help="inspect one product path and DEV bridge state")
    project_parser.add_argument("project", help="top-level project name or explicit path")
    project_parser.add_argument("--json", action="store_true")
    move_parser = subparsers.add_parser("move-plan", help="build a read-only legacy product move preflight")
    move_parser.add_argument("project", help="top-level project name under legacy ~/codex-workspace")
    move_parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        layout = resolve_layout()
        if args.command == "resolve":
            payload = layout.as_dict()
        elif args.command == "diagnose":
            payload = migration_diagnostics(layout)
        elif args.command == "project":
            payload = asdict(inspect_project(resolve_project_reference(args.project, layout), layout))
        else:
            source = Path.home() / LEGACY_WORKSPACE_NAME / args.project
            payload = project_move_preflight(source, project_path(layout, args.project))
        print(_render_human(payload))
        return 0
    except (PathResolutionError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
