from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable

try:
    from tools.dev_paths import PathResolutionError, resolve_layout
except ImportError:  # Direct execution from tools/.
    from dev_paths import PathResolutionError, resolve_layout


ROOT = Path(__file__).resolve().parents[1]
LEDGER_NAME = ".dev-install-manifest.json"
TRANSACTION_DIRECTORY = ".dev-install-transactions"
LOCK_NAME = ".dev-install.lock"
LEDGER_SCHEMA_VERSION = 1

# These entries describe or maintain the canonical source repository. They remain
# manifest-checked, but are not part of the active Codex home layer.
SOURCE_ONLY_FILES = frozenset({
    ".gitignore",
    "MANIFEST.txt",
    "install-global.ps1",
    "install-global.sh",
})
SOURCE_ONLY_PREFIXES = frozenset({".github", "skill-sources"})

# Matching is case-insensitive on every platform so a plan produced on Linux
# cannot bypass Windows runtime protection after a clone.
PROTECTED_ROOT_FILES = frozenset({
    ".codex-global-state.json",
    ".sandbox_migration",
    "auth.json",
    "cap_sid",
    "chrome-native-hosts-v2.json",
    "config.toml",
    "credentials.json",
    "dev-layout.toml",
    "installation_id",
    "models_cache.json",
    "session_index.jsonl",
    "transcription-history.jsonl",
})
PROTECTED_ROOT_DIRECTORIES = frozenset({
    ".git",
    ".sandbox",
    ".sandbox-bin",
    ".sandbox-secrets",
    ".secrets",
    ".tmp",
    "archived_sessions",
    "attachments",
    "browser",
    "browser-data",
    "browser_data",
    "cache",
    "computer-use",
    "computer_use",
    "dictation-history",
    "logs",
    "node_repl",
    "plugins",
    "runtime",
    "rollout-migrations",
    "sandbox",
    "secret-store",
    "secret-stores",
    "secret_store",
    "secret_stores",
    "secrets",
    "sessions",
    "shell_snapshots",
    "skills",
    "sqlite",
    "thread-writer-locks",
    "tmp",
    "vendor_imports",
    "visualizations",
})
PROTECTED_EXACT_PATHS = frozenset({"rules/default.rules"})
INSTALLER_RESERVED = frozenset({LEDGER_NAME.casefold(), TRANSACTION_DIRECTORY.casefold(), LOCK_NAME.casefold()})


class InstallError(RuntimeError):
    """A deterministic, user-actionable installer failure."""


@dataclass(frozen=True, order=True)
class ManagedFile:
    path: str
    sha256: str


@dataclass(frozen=True, order=True)
class InstallAction:
    kind: str
    path: str
    sha256: str = ""
    before_sha256: str = ""
    detail: str = ""


@dataclass(frozen=True)
class InstallPolicy:
    source_root: Path
    manifest_sha256: str
    files: tuple[ManagedFile, ...]
    source_only: tuple[str, ...]


@dataclass(frozen=True)
class InstallPlan:
    policy: InstallPolicy
    previous_files: tuple[ManagedFile, ...]
    actions: tuple[InstallAction, ...]
    protected_skips: tuple[str, ...]
    ledger_action: str

    @property
    def conflicts(self) -> tuple[InstallAction, ...]:
        return tuple(action for action in self.actions if action.kind == "conflict")

    @property
    def changes(self) -> tuple[InstallAction, ...]:
        return tuple(action for action in self.actions if action.kind in {"create", "update", "delete"})


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def normalize_manifest_path(raw: str) -> str:
    if not raw or raw != raw.strip() or "\\" in raw or "\0" in raw:
        raise InstallError(f"unsafe or non-canonical manifest path: {raw!r}")
    pure = PurePosixPath(raw)
    if pure.is_absolute() or raw != pure.as_posix() or any(part in {"", ".", ".."} for part in pure.parts):
        raise InstallError(f"unsafe or non-canonical manifest path: {raw}")
    if any(":" in part for part in pure.parts):
        raise InstallError(f"unsafe or non-canonical manifest path: {raw}")
    return pure.as_posix()


def is_source_only(relative: str) -> bool:
    first = PurePosixPath(relative).parts[0].casefold()
    return relative.casefold() in {item.casefold() for item in SOURCE_ONLY_FILES} or first in {
        item.casefold() for item in SOURCE_ONLY_PREFIXES
    }


def is_protected_runtime_path(relative: str) -> bool:
    normalized = normalize_manifest_path(relative)
    if normalized.casefold() in PROTECTED_EXACT_PATHS:
        return True
    parts = tuple(part.casefold() for part in PurePosixPath(normalized).parts)
    first = parts[0]
    if first in INSTALLER_RESERVED:
        return True
    if len(parts) == 1 and first in PROTECTED_ROOT_FILES:
        return True
    if len(parts) == 1 and (
        first.startswith(".codex-global-state.json.")
        or first.endswith((".sqlite", ".sqlite-shm", ".sqlite-wal"))
    ):
        return True
    if first.startswith(("browser", "computer-use", "computer_use", "runtime", "sandbox", ".sandbox", "secret")):
        return True
    return first in PROTECTED_ROOT_DIRECTORIES


def _assert_regular_contained_source(source_root: Path, relative: str) -> Path:
    candidate = source_root.joinpath(*PurePosixPath(relative).parts)
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise InstallError(f"manifest entry is missing or unreadable: {relative}: {type(exc).__name__}") from exc
    if not _is_relative_to(resolved, source_root):
        raise InstallError(f"manifest source escapes repository through a link: {relative}")
    cursor = source_root
    for part in PurePosixPath(relative).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise InstallError(f"manifest source may not be a symlink: {relative}")
    if not resolved.is_file():
        raise InstallError(f"manifest entry is not a regular file: {relative}")
    return resolved


def load_install_policy(source_root: Path) -> InstallPolicy:
    source_root = source_root.expanduser().resolve()
    manifest = source_root / "MANIFEST.txt"
    if not manifest.is_file():
        raise InstallError(f"MANIFEST.txt is missing: {manifest}")
    manifest_bytes = manifest.read_bytes()
    try:
        lines = manifest_bytes.decode("utf-8-sig").splitlines()
    except UnicodeDecodeError as exc:
        raise InstallError("MANIFEST.txt must be UTF-8") from exc

    seen: dict[str, str] = {}
    files: list[ManagedFile] = []
    source_only: list[str] = []
    protected: list[str] = []
    for line in lines:
        if not line.strip():
            continue
        relative = normalize_manifest_path(line)
        folded = relative.casefold()
        if folded in seen:
            raise InstallError(f"duplicate manifest path ignoring case: {seen[folded]} / {relative}")
        seen[folded] = relative
        source = _assert_regular_contained_source(source_root, relative)
        if is_protected_runtime_path(relative):
            protected.append(relative)
            continue
        if is_source_only(relative):
            source_only.append(relative)
        else:
            files.append(ManagedFile(relative, sha256_file(source)))

    if protected:
        joined = ", ".join(sorted(protected, key=str.casefold))
        raise InstallError(f"manifest collides with protected runtime or installer state: {joined}")
    return InstallPolicy(
        source_root=source_root,
        manifest_sha256=sha256_bytes(manifest_bytes),
        files=tuple(sorted(files)),
        source_only=tuple(sorted(source_only, key=str.casefold)),
    )


def ensure_source_git_root(source_root: Path) -> None:
    try:
        result = subprocess.run(
            ["git", "-c", f"safe.directory={source_root}", "-C", str(source_root), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise InstallError(f"source must be a Git working tree: {source_root}") from exc
    git_root = Path(result.stdout.strip()).resolve()
    if git_root != source_root.resolve():
        raise InstallError(f"installer must run from the source Git root: {source_root}")


def ensure_separate_roots(source_root: Path, codex_home: Path) -> None:
    source = source_root.resolve()
    destination = codex_home.expanduser().resolve()
    if source == destination or _is_relative_to(source, destination) or _is_relative_to(destination, source):
        raise InstallError("canonical source repository and installed Codex home must be separate trees")
    if (destination / ".git").exists():
        raise InstallError(f"destination Codex home must not be a Git working tree: {destination}")


def ledger_bytes(policy: InstallPolicy) -> bytes:
    payload = {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "manifest_sha256": policy.manifest_sha256,
        "files": [{"path": item.path, "sha256": item.sha256} for item in policy.files],
    }
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_ledger(codex_home: Path) -> tuple[str, tuple[ManagedFile, ...]]:
    ledger = codex_home / LEDGER_NAME
    if not ledger.exists():
        return "", ()
    if not ledger.is_file() or ledger.is_symlink():
        raise InstallError(f"ownership ledger is not a regular file: {ledger}")
    try:
        raw = json.loads(ledger.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InstallError(f"ownership ledger is unreadable or invalid: {type(exc).__name__}") from exc
    if not isinstance(raw, dict) or raw.get("schema_version") != LEDGER_SCHEMA_VERSION:
        raise InstallError("ownership ledger has an unsupported schema")
    manifest_hash = raw.get("manifest_sha256")
    raw_files = raw.get("files")
    if not isinstance(manifest_hash, str) or not isinstance(raw_files, list):
        raise InstallError("ownership ledger has an invalid structure")
    seen: set[str] = set()
    files: list[ManagedFile] = []
    for item in raw_files:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise InstallError("ownership ledger contains an invalid file record")
        relative = normalize_manifest_path(item["path"]) if isinstance(item.get("path"), str) else ""
        digest = item.get("sha256")
        if not relative or not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise InstallError("ownership ledger contains an invalid path or SHA-256")
        folded = relative.casefold()
        if folded in seen or is_protected_runtime_path(relative):
            raise InstallError(f"ownership ledger contains duplicate or protected path: {relative}")
        seen.add(folded)
        files.append(ManagedFile(relative, digest))
    return manifest_hash, tuple(sorted(files))


def destination_path(codex_home: Path, relative: str) -> Path:
    home = codex_home.expanduser().resolve()
    target = home.joinpath(*PurePosixPath(normalize_manifest_path(relative)).parts)
    cursor = home
    for part in PurePosixPath(relative).parts[:-1]:
        cursor = cursor / part
        if cursor.exists():
            resolved = cursor.resolve()
            if not _is_relative_to(resolved, home) or cursor.is_symlink():
                raise InstallError(f"destination path escapes Codex home through a link: {relative}")
    return target


def protected_runtime_entries(codex_home: Path) -> tuple[str, ...]:
    if not codex_home.is_dir():
        return ()
    protected: list[str] = []
    for child in codex_home.iterdir():
        relative = child.name
        if (
            is_protected_runtime_path(relative)
            and relative.casefold() != ".git"
            and relative.casefold() not in INSTALLER_RESERVED
        ):
            protected.append(relative)
    return tuple(sorted(protected, key=str.casefold))


def build_install_plan(policy: InstallPolicy, codex_home: Path) -> InstallPlan:
    codex_home = codex_home.expanduser().resolve()
    _, previous_files = load_ledger(codex_home)
    previous = {item.path.casefold(): item for item in previous_files}
    desired = {item.path.casefold(): item for item in policy.files}
    actions: list[InstallAction] = []

    for item in policy.files:
        target = destination_path(codex_home, item.path)
        old = previous.get(item.path.casefold())
        if not target.exists():
            actions.append(InstallAction("create", item.path, item.sha256))
        elif not target.is_file() or target.is_symlink():
            actions.append(InstallAction("conflict", item.path, detail="destination is not a regular file"))
        else:
            current_hash = sha256_file(target)
            if current_hash == item.sha256:
                kind = "unchanged" if old else "adopt"
                actions.append(InstallAction(kind, item.path, item.sha256, current_hash))
            elif old:
                actions.append(InstallAction("update", item.path, item.sha256, current_hash))
            else:
                actions.append(InstallAction("conflict", item.path, detail="unknown destination file differs from source"))

    for old in previous_files:
        if old.path.casefold() in desired:
            continue
        target = destination_path(codex_home, old.path)
        if not target.exists():
            actions.append(InstallAction("forget", old.path, detail="stale managed file already absent"))
        elif target.is_file() and not target.is_symlink():
            actions.append(
                InstallAction(
                    "delete",
                    old.path,
                    before_sha256=sha256_file(target),
                    detail="stale managed file",
                )
            )
        else:
            actions.append(InstallAction("conflict", old.path, detail="stale managed path is not a regular file"))

    transaction_root = codex_home / TRANSACTION_DIRECTORY
    if transaction_root.is_dir():
        for pending in sorted(transaction_root.iterdir(), key=lambda path: path.name.casefold()):
            actions.append(
                InstallAction(
                    "conflict",
                    f"{TRANSACTION_DIRECTORY}/{pending.name}",
                    detail="unresolved installer recovery data",
                )
            )

    return InstallPlan(
        policy=policy,
        previous_files=previous_files,
        actions=tuple(sorted(actions, key=lambda item: (item.path.casefold(), item.kind))),
        protected_skips=protected_runtime_entries(codex_home),
        ledger_action=(
            "create"
            if not (codex_home / LEDGER_NAME).exists()
            else "unchanged"
            if (codex_home / LEDGER_NAME).is_file() and (codex_home / LEDGER_NAME).read_bytes() == ledger_bytes(policy)
            else "update"
        ),
    )


def render_plan(plan: InstallPlan) -> str:
    lines = [
        f"source repo: {plan.policy.source_root}",
        f"managed files: {len(plan.policy.files)}",
    ]
    for action in plan.actions:
        if action.kind in {"unchanged", "forget"}:
            continue
        suffix = f" ({action.detail})" if action.detail else ""
        lines.append(f"[{action.kind}] {action.path}{suffix}")
    if plan.ledger_action != "unchanged":
        lines.append(f"[{plan.ledger_action}] {LEDGER_NAME} (DEV ownership ledger)")
    for path in plan.protected_skips:
        lines.append(f"[protected runtime skip] {path}")
    if not plan.changes and not plan.conflicts and plan.ledger_action == "unchanged":
        lines.append("[no changes] installed managed layer is current")
    return "\n".join(lines)


def _copy_atomic(source: Path, destination: Path, operation_id: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.dev-install-{operation_id}.tmp")
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def _write_atomic(data: bytes, destination: Path, operation_id: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.dev-install-{operation_id}.tmp")
    try:
        temporary.write_bytes(data)
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def _journal(transaction_root: Path, payload: dict[str, object]) -> None:
    path = transaction_root / "journal.json"
    temporary = transaction_root / ".journal.json.tmp"
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


class AppliedTransaction:
    def __init__(
        self,
        codex_home: Path,
        root: Path,
        operation_id: str,
        plan: InstallPlan,
        ledger_existed: bool,
    ) -> None:
        self.codex_home = codex_home
        self.root = root
        self.operation_id = operation_id
        self.plan = plan
        self.ledger_existed = ledger_existed
        self.closed = False

    @property
    def backup_root(self) -> Path:
        return self.root / "backup"

    def rollback(self, *, retain_recovery: bool = False) -> None:
        if self.closed:
            return
        errors: list[str] = []
        for action in reversed(self.plan.changes):
            target = destination_path(self.codex_home, action.path)
            backup = self.backup_root.joinpath(*PurePosixPath(action.path).parts)
            try:
                if action.kind == "create":
                    if target.exists():
                        if not target.is_file() or sha256_file(target) != action.sha256:
                            raise InstallError("created target changed concurrently; refusing destructive rollback")
                        target.unlink()
                elif action.kind in {"update", "delete"}:
                    if not backup.is_file():
                        raise InstallError("transaction backup is missing")
                    backup_hash = sha256_file(backup)
                    if target.exists():
                        if not target.is_file():
                            raise InstallError("target type changed concurrently; refusing rollback")
                        target_hash = sha256_file(target)
                        if target_hash == backup_hash:
                            continue
                        if action.kind == "delete" or target_hash != action.sha256:
                            raise InstallError("target changed concurrently; refusing rollback")
                    _copy_atomic(backup, target, self.operation_id)
            except (OSError, InstallError) as exc:
                errors.append(f"{action.path}: {exc}")

        ledger = self.codex_home / LEDGER_NAME
        ledger_backup = self.root / "ledger.before.json"
        try:
            if self.plan.ledger_action == "unchanged":
                pass
            elif self.ledger_existed:
                if not ledger_backup.is_file():
                    raise InstallError("ownership ledger backup is missing")
                _copy_atomic(ledger_backup, ledger, self.operation_id)
            elif ledger.exists():
                ledger.unlink()
        except (OSError, InstallError) as exc:
            errors.append(f"{LEDGER_NAME}: {exc}")

        if errors:
            _journal(self.root, {"schema_version": 1, "status": "rollback_failed", "errors": errors})
            raise InstallError("rollback failed; recovery data retained at " + str(self.root))
        if retain_recovery:
            _journal(self.root, {"schema_version": 1, "status": "recovery_retained"})
        else:
            shutil.rmtree(self.root)
        self.closed = True

    def finalize(self) -> None:
        if self.closed:
            return
        shutil.rmtree(self.root)
        parent = self.root.parent
        try:
            parent.rmdir()
        except OSError:
            pass
        self.closed = True


def apply_install_plan(plan: InstallPlan, codex_home: Path) -> AppliedTransaction:
    if plan.conflicts:
        raise InstallError("install plan contains conflicts; destination was not changed")
    codex_home = codex_home.expanduser().resolve()
    codex_home.mkdir(parents=True, exist_ok=True)
    revalidate_plan_destinations(plan, codex_home)
    operation_id = uuid.uuid4().hex
    transaction_root = codex_home / TRANSACTION_DIRECTORY / operation_id
    stage_root = transaction_root / "stage"
    backup_root = transaction_root / "backup"
    transaction_root.mkdir(parents=True)
    ledger = codex_home / LEDGER_NAME
    ledger_existed = ledger.is_file()
    transaction = AppliedTransaction(codex_home, transaction_root, operation_id, plan, ledger_existed)

    mutation_started = False
    try:
        if ledger_existed and plan.ledger_action != "unchanged":
            shutil.copy2(ledger, transaction_root / "ledger.before.json")
        for action in plan.changes:
            target = destination_path(codex_home, action.path)
            relative_parts = PurePosixPath(action.path).parts
            if action.kind in {"update", "delete"}:
                backup = backup_root.joinpath(*relative_parts)
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
            if action.kind in {"create", "update"}:
                source = plan.policy.source_root.joinpath(*relative_parts)
                staged = stage_root.joinpath(*relative_parts)
                staged.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, staged)
                if sha256_file(staged) != action.sha256:
                    raise InstallError(f"staged source changed during install: {action.path}")

        _journal(transaction_root, {
            "schema_version": 1,
            "status": "prepared",
            "actions": [{"kind": item.kind, "path": item.path, "sha256": item.sha256} for item in plan.changes],
        })
        for action in plan.changes:
            mutation_started = True
            target = destination_path(codex_home, action.path)
            relative_parts = PurePosixPath(action.path).parts
            if action.kind in {"create", "update"}:
                _copy_atomic(stage_root.joinpath(*relative_parts), target, operation_id)
            elif action.kind == "delete":
                target.unlink()
        if plan.ledger_action != "unchanged":
            _write_atomic(ledger_bytes(plan.policy), ledger, operation_id)
        _journal(transaction_root, {"schema_version": 1, "status": "applied"})
        return transaction
    except BaseException:
        if mutation_started:
            try:
                transaction.rollback()
            except InstallError:
                pass
        else:
            shutil.rmtree(transaction_root, ignore_errors=True)
        raise


def revalidate_plan_destinations(plan: InstallPlan, codex_home: Path) -> None:
    for action in plan.changes:
        target = destination_path(codex_home, action.path)
        if action.kind == "create":
            if target.exists():
                raise InstallError(f"destination changed after planning: {action.path}")
            continue
        if not target.is_file() or target.is_symlink() or sha256_file(target) != action.before_sha256:
            raise InstallError(f"destination changed after planning: {action.path}")


@contextmanager
def install_lock(codex_home: Path):
    codex_home.mkdir(parents=True, exist_ok=True)
    lock = codex_home / LOCK_NAME
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise InstallError(f"another install or unresolved install lock exists: {lock}") from exc
    try:
        with os.fdopen(descriptor, "w", encoding="ascii") as stream:
            stream.write("DEV installer lock\n")
        yield
    finally:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


def ensure_no_pending_transactions(codex_home: Path) -> None:
    root = codex_home / TRANSACTION_DIRECTORY
    if not root.is_dir():
        return
    pending = sorted(path.name for path in root.iterdir())
    if pending:
        raise InstallError(
            "unresolved installer recovery data exists: "
            + ", ".join(str(root / name) for name in pending)
        )
    root.rmdir()


def _skill_names(source_root: Path) -> tuple[str, ...]:
    if not source_root.is_dir():
        raise InstallError(f"skill source directory is missing: {source_root}")
    names: list[str] = []
    for path in sorted(source_root.iterdir()):
        if path.is_dir():
            if not (path / "SKILL.md").is_file():
                raise InstallError(f"invalid source Skill without SKILL.md: {path.name}")
            names.append(path.name)
    return tuple(names)


class SkillSnapshot:
    def __init__(self, source_root: Path, destination_root: Path, backup_root: Path) -> None:
        self.destination_root = destination_root
        self.backup_root = backup_root
        self.names = _skill_names(source_root)
        self.existed: set[str] = set()
        backup_root.mkdir(parents=True, exist_ok=True)
        for name in self.names:
            destination = destination_root / name
            if destination.exists():
                if not destination.is_dir() or destination.is_symlink():
                    raise InstallError(f"runtime Skill destination is not a regular directory: {name}")
                shutil.copytree(destination, backup_root / name)
                self.existed.add(name)

    def restore(self) -> None:
        for name in self.names:
            destination = self.destination_root / name
            if destination.exists():
                shutil.rmtree(destination)
            if name in self.existed:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(self.backup_root / name, destination)


ProcessRunner = Callable[[list[str]], None]


def checked_process(command: list[str]) -> None:
    subprocess.run(command, check=True)


def validation_commands(source_root: Path, codex_home: Path, skip_skills: bool) -> tuple[list[str], list[str]]:
    context = [sys.executable, "-B", str(source_root / "tools" / "validate_context.py")]
    global_validation = [
        sys.executable,
        "-B",
        str(source_root / "tools" / "validate_global_codex.py"),
        "--dev-source-root",
        str(source_root),
        "--codex-home",
        str(codex_home),
    ]
    if skip_skills:
        global_validation.append("--skip-skills")
    return context, global_validation


def run_validators(source_root: Path, codex_home: Path, skip_skills: bool, runner: ProcessRunner) -> None:
    for command in validation_commands(source_root, codex_home, skip_skills):
        runner(command)


def sync_skills_command(source_root: Path, destination_root: Path, backup_root: Path) -> list[str]:
    return [
        sys.executable,
        "-B",
        str(source_root / "tools" / "sync_global_skills.py"),
        "--source",
        str(source_root / "skill-sources"),
        "--destination",
        str(destination_root),
        "--backup-root",
        str(backup_root),
        "--apply",
    ]


def install(
    source_root: Path,
    codex_home: Path,
    skills_destination: Path,
    *,
    dry_run: bool = False,
    runner: ProcessRunner = checked_process,
) -> InstallPlan:
    source_root = source_root.expanduser().resolve()
    codex_home = codex_home.expanduser().resolve()
    skills_destination = skills_destination.expanduser().resolve()
    ensure_source_git_root(source_root)
    ensure_separate_roots(source_root, codex_home)
    policy = load_install_policy(source_root)
    runner(validation_commands(source_root, codex_home, True)[0])
    plan = build_install_plan(policy, codex_home)
    if plan.conflicts:
        print(render_plan(plan))
        details = "; ".join(f"{item.path}: {item.detail}" for item in plan.conflicts)
        raise InstallError(f"install plan contains conflicts: {details}")
    if dry_run:
        print(render_plan(plan))
        print("dry run: destination and runtime Skills were not changed")
        return plan

    ensure_no_pending_transactions(codex_home)
    with install_lock(codex_home):
        plan = build_install_plan(policy, codex_home)
        print(render_plan(plan))
        if plan.conflicts:
            raise InstallError("install plan changed and now contains conflicts")
        revalidate_plan_destinations(plan, codex_home)
        transaction = apply_install_plan(plan, codex_home)
        skill_snapshot: SkillSnapshot | None = None
        try:
            run_validators(source_root, codex_home, True, runner)
            skill_snapshot = SkillSnapshot(
                source_root / "skill-sources",
                skills_destination,
                transaction.root / "skills.before",
            )
            runner(sync_skills_command(source_root, skills_destination, transaction.root / "skills.tool-backup"))
            run_validators(source_root, codex_home, False, runner)
        except BaseException as exc:
            recovery_errors: list[str] = []
            if skill_snapshot is not None:
                try:
                    skill_snapshot.restore()
                except OSError as rollback_exc:
                    recovery_errors.append(f"Skill rollback failed: {rollback_exc}")
            try:
                transaction.rollback(retain_recovery=bool(recovery_errors))
            except InstallError as rollback_exc:
                recovery_errors.append(str(rollback_exc))
            if recovery_errors:
                raise InstallError(
                    "; ".join(recovery_errors) + f"; recovery data retained at {transaction.root}"
                ) from exc
            raise
        transaction.finalize()
    print("DEV installed and validated; runtime config, credentials, sessions, cache, and plugins were preserved")
    return plan


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install the canonical DEV source into the active Codex home layer")
    parser.add_argument(
        "--source",
        type=Path,
        help="compatibility assertion; must equal resolved DEV_SOURCE_ROOT",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        help="compatibility assertion; must equal resolved CODEX_HOME",
    )
    parser.add_argument(
        "--skills-destination",
        type=Path,
        help="runtime Skill destination (default: ~/.agents/skills)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        layout = resolve_layout()
        source_root = layout.dev_source_root
        codex_home = layout.codex_home
        if args.source is not None and args.source.expanduser().resolve() != source_root:
            raise InstallError("--source must match resolved DEV_SOURCE_ROOT")
        if args.codex_home is not None and args.codex_home.expanduser().resolve() != codex_home:
            raise InstallError("--codex-home must match resolved CODEX_HOME")
        if ROOT.resolve() != source_root:
            raise InstallError(
                "installer engine must execute from resolved DEV_SOURCE_ROOT; "
                "run tools/dev_paths.py diagnose before migrating a legacy checkout"
            )
        skills_destination = (
            args.skills_destination.expanduser().resolve()
            if args.skills_destination is not None
            else Path.home().resolve() / ".agents" / "skills"
        )
        install(source_root, codex_home, skills_destination, dry_run=args.dry_run)
    except (InstallError, PathResolutionError, OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
