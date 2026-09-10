from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable

try:
    from tools.dev_paths import (
        DevLayout,
        PathResolutionError,
        is_exact_git_root,
        load_dev_project_contract,
        resolve_layout,
    )
    from tools.install_global import LEDGER_NAME, InstallError, install
    from tools.validate_project_overlay import validate_project
except ImportError:  # Direct execution from tools/.
    from dev_paths import (
        DevLayout,
        PathResolutionError,
        is_exact_git_root,
        load_dev_project_contract,
        resolve_layout,
    )
    from install_global import LEDGER_NAME, InstallError, install
    from validate_project_overlay import validate_project


GLOBAL_CONTRACT_NAME = "dev-contract.toml"
GLOBAL_CONTRACT_SCHEMA = 1
CANONICAL_REPOSITORY = "https://github.com/ZabulaAleksey/codex-dev.git"
VERSION_PATTERN = re.compile(r"\d{4}\.\d{2}\.\d{2}")


class BootstrapError(RuntimeError):
    """A deterministic, actionable project bootstrap failure."""


@dataclass(frozen=True)
class GlobalDevContract:
    schema_version: int
    version: str
    capabilities: tuple[str, ...]
    repository: str
    default_path: str
    project_schema_versions: tuple[int, ...]


@dataclass(frozen=True)
class BootstrapReport:
    project: str
    mode: str
    ready: bool
    dev_managed: bool
    dev_source_root: str
    codex_home: str
    projects_root: str
    source_present: bool
    source_compatible: bool
    installed_layer_current: bool
    project_overlay_valid: bool
    dev_version: str
    required_minimum_version: str
    required_capabilities: tuple[str, ...]
    missing_capabilities: tuple[str, ...]
    issues: tuple[str, ...]
    recommended_clone_command: str


def _load_global_contract(source_root: Path) -> GlobalDevContract:
    path = source_root / GLOBAL_CONTRACT_NAME
    if not path.is_file() or path.is_symlink():
        raise BootstrapError(f"global DEV contract is missing: {path}")
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise BootstrapError(f"global DEV contract is invalid: {type(exc).__name__}") from exc
    if not isinstance(raw, dict) or set(raw) != {"schema_version", "dev", "global_dev"}:
        raise BootstrapError("global DEV contract has unknown or missing sections")
    dev = raw["dev"]
    global_dev = raw["global_dev"]
    if raw["schema_version"] != GLOBAL_CONTRACT_SCHEMA:
        raise BootstrapError("unsupported global DEV contract schema")
    if not isinstance(dev, dict) or set(dev) != {"version", "capabilities"}:
        raise BootstrapError("global DEV [dev] contract is invalid")
    if not isinstance(global_dev, dict) or set(global_dev) != {"repository", "default_path", "project_schema_versions"}:
        raise BootstrapError("global DEV [global_dev] contract is invalid")
    version = dev["version"]
    capabilities = dev["capabilities"]
    repository = global_dev["repository"]
    default_path = global_dev["default_path"]
    schemas = global_dev["project_schema_versions"]
    if not isinstance(version, str) or VERSION_PATTERN.fullmatch(version) is None:
        raise BootstrapError("global DEV version must be YYYY.MM.DD")
    if (
        not isinstance(capabilities, list)
        or not capabilities
        or any(not isinstance(item, str) or not item for item in capabilities)
        or len(set(capabilities)) != len(capabilities)
    ):
        raise BootstrapError("global DEV capabilities must be unique non-empty strings")
    if not isinstance(repository, str) or not repository.startswith("https://") or not repository.endswith("/codex-dev.git"):
        raise BootstrapError("canonical global DEV repository must be an HTTPS codex-dev.git URL")
    if default_path != "~/codex-dev":
        raise BootstrapError("canonical global DEV default path must be ~/codex-dev")
    if not isinstance(schemas, list) or not schemas or any(type(item) is not int or item < 1 for item in schemas):
        raise BootstrapError("supported project schema versions must be positive integers")
    return GlobalDevContract(
        schema_version=raw["schema_version"],
        version=version,
        capabilities=tuple(capabilities),
        repository=repository,
        default_path=default_path,
        project_schema_versions=tuple(schemas),
    )


def _version_key(value: str) -> tuple[int, int, int]:
    if VERSION_PATTERN.fullmatch(value) is None:
        raise BootstrapError(f"invalid DEV version: {value}")
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def _origin_url(source_root: Path) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={source_root}", "-C", str(source_root), "remote", "get-url", "origin"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _normalized_remote(value: str) -> str:
    return value.strip().rstrip("/").removesuffix(".git").casefold()


def _installed_layer_current(layout: DevLayout) -> bool:
    manifest = layout.dev_source_root / "MANIFEST.txt"
    ledger = layout.codex_home / LEDGER_NAME
    installed_contract = layout.codex_home / GLOBAL_CONTRACT_NAME
    if not manifest.is_file() or not ledger.is_file() or not installed_contract.is_file():
        return False
    try:
        raw = json.loads(ledger.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    expected = hashlib.sha256(manifest.read_bytes()).hexdigest()
    return raw.get("manifest_sha256") == expected


def inspect_bootstrap(project: Path, layout: DevLayout, *, mode: str) -> BootstrapReport:
    project = project.expanduser().resolve(strict=False)
    marker = load_dev_project_contract(project)
    issues: list[str] = []
    source_present = is_exact_git_root(layout.dev_source_root)
    source_compatible = False
    installed_current = False
    overlay_valid = False
    version = ""
    missing: tuple[str, ...] = ()
    clone_command = ""

    if not is_exact_git_root(project):
        issues.append("project_not_git_root")
    if not source_present:
        issues.append("global_dev_source_missing")
        clone_command = f'git clone {CANONICAL_REPOSITORY} "{layout.dev_source_root}"'
    else:
        try:
            contract = _load_global_contract(layout.dev_source_root)
            clone_command = f'git clone {contract.repository} "{layout.dev_source_root}"'
            version = contract.version
            if marker.required_contract_schema not in contract.project_schema_versions:
                issues.append("project_contract_schema_incompatible")
            missing = tuple(sorted(set(marker.required_capabilities) - set(contract.capabilities)))
            if missing:
                issues.append("required_capability_missing")
            if _version_key(contract.version) < _version_key(marker.minimum_version):
                issues.append("global_dev_version_too_old")
            origin = _origin_url(layout.dev_source_root)
            if _normalized_remote(origin) != _normalized_remote(contract.repository):
                issues.append("canonical_dev_remote_mismatch")
            source_compatible = not any(issue in issues for issue in (
                "project_contract_schema_incompatible",
                "required_capability_missing",
                "global_dev_version_too_old",
                "canonical_dev_remote_mismatch",
            ))
            installed_current = _installed_layer_current(layout)
            if not installed_current:
                issues.append("installed_global_layer_stale")
            overlay = validate_project(project, layout.dev_source_root)
            overlay_valid = overlay.ok
            if not overlay_valid:
                issues.append("project_overlay_invalid")
        except BootstrapError as exc:
            issues.append("global_dev_contract_invalid")
            clone_command = f'ERROR: {exc}'

    return BootstrapReport(
        project=str(project),
        mode=mode,
        ready=not issues,
        dev_managed=marker.managed,
        dev_source_root=str(layout.dev_source_root),
        codex_home=str(layout.codex_home),
        projects_root=str(layout.projects_root),
        source_present=source_present,
        source_compatible=source_compatible,
        installed_layer_current=installed_current,
        project_overlay_valid=overlay_valid,
        dev_version=version,
        required_minimum_version=marker.minimum_version,
        required_capabilities=marker.required_capabilities,
        missing_capabilities=missing,
        issues=tuple(issues),
        recommended_clone_command=clone_command,
    )


Installer = Callable[..., object]


def apply_bootstrap(project: Path, layout: DevLayout, *, installer: Installer = install) -> BootstrapReport:
    before = inspect_bootstrap(project, layout, mode="apply")
    blocking = set(before.issues) - {"installed_global_layer_stale"}
    if blocking:
        return before
    if not before.installed_layer_current:
        installer(
            layout.dev_source_root,
            layout.codex_home,
            Path.home().resolve() / ".agents" / "skills",
            dry_run=False,
        )
    return inspect_bootstrap(project, layout, mode="apply")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check or apply a DEV-managed project bootstrap")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="read-only compatibility and freshness check")
    mode.add_argument("--apply", action="store_true", help="install/refresh the managed global layer")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        layout = resolve_layout()
        report = apply_bootstrap(args.project, layout) if args.apply else inspect_bootstrap(args.project, layout, mode="check")
        payload = asdict(report)
        print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if report.ready else 1
    except (BootstrapError, InstallError, PathResolutionError, OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
