from __future__ import annotations

import argparse
import hashlib
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "skill-sources"


@dataclass(frozen=True, order=True)
class SkillIssue:
    code: str
    path: str


def _files(root: Path) -> dict[str, str]:
    if not root.is_dir():
        return {}
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        relative = path.relative_to(root).as_posix()
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def compare_skills(source_root: Path, destination_root: Path) -> tuple[SkillIssue, ...]:
    issues: list[SkillIssue] = []
    if not source_root.is_dir():
        return (SkillIssue("missing-source-root", source_root.as_posix()),)
    for source in sorted(path for path in source_root.iterdir() if path.is_dir()):
        if not (source / "SKILL.md").is_file():
            issues.append(SkillIssue("invalid-source-skill", source.name))
            continue
        destination = destination_root / source.name
        if not destination.is_dir():
            issues.append(SkillIssue("missing-runtime-skill", source.name))
            continue
        if _files(source) != _files(destination):
            issues.append(SkillIssue("runtime-skill-drift", source.name))
    return tuple(sorted(issues))


def sync_skills(source_root: Path, destination_root: Path, backup_root: Path) -> tuple[str, ...]:
    destination_root.mkdir(parents=True, exist_ok=True)
    changed: list[str] = []
    for source in sorted(path for path in source_root.iterdir() if path.is_dir()):
        if not (source / "SKILL.md").is_file():
            raise ValueError(f"invalid source Skill without SKILL.md: {source}")
        destination = destination_root / source.name
        if destination.is_dir() and _files(source) == _files(destination):
            continue
        with tempfile.TemporaryDirectory(prefix=f".{source.name}-", dir=destination_root) as temporary:
            staged = Path(temporary) / source.name
            shutil.copytree(source, staged)
            if destination.exists():
                backup_root.mkdir(parents=True, exist_ok=True)
                shutil.move(str(destination), str(backup_root / source.name))
            shutil.move(str(staged), str(destination))
        changed.append(source.name)
    return tuple(changed)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check or install versioned global Skills")
    parser.add_argument("--apply", action="store_true", help="install drifted Skills with a recoverable backup")
    parser.add_argument("--source", type=Path, default=SOURCE_ROOT)
    parser.add_argument("--destination", type=Path, default=Path.home() / ".agents" / "skills")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    destination = args.destination.expanduser().resolve()
    if args.apply:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = destination.parent / ".migration-backup" / stamp
        changed = sync_skills(source, destination, backup)
        print("global Skills synchronized: " + (", ".join(changed) if changed else "no changes"))

    issues = compare_skills(source, destination)
    if issues:
        print("Global Skills validation failed:")
        for issue in issues:
            print(f"- [{issue.code}] {issue.path}")
        return 1
    print(f"global Skills OK ({len(tuple(source.iterdir()))} sources)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
