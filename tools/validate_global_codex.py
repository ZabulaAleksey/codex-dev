from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.sync_global_skills import compare_skills


@dataclass(frozen=True, order=True)
class Issue:
    code: str
    path: str
    detail: str


def managed_files(workspace: Path) -> tuple[Path, ...]:
    base = workspace
    files = [base / "AGENTS.md", base / "hooks.json", base / "rules" / "ai-dev-team.rules"]
    files.extend(sorted((base / "agents").glob("*.toml")))
    files.extend(sorted((base / "hooks").glob("*.py")))
    return tuple(files)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def installed_path(source: Path, workspace: Path, codex_home: Path) -> Path:
    relative = source.relative_to(workspace)
    return codex_home / relative


def trusted_service_paths(raw: object) -> tuple[list[tuple[str, str]], bool]:
    if not isinstance(raw, str) or not raw.strip():
        return [], True
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return [], False
    if isinstance(value, dict):
        return [(str(name), item) for name, item in value.items() if isinstance(item, str)], True
    if isinstance(value, list):
        paths: list[tuple[str, str]] = []
        for item in value:
            if isinstance(item, str):
                paths.append(("unnamed", item))
            elif isinstance(item, dict):
                paths.extend((str(name), value) for name, value in item.items() if isinstance(value, str))
        return paths, True
    return [], False


def installed_browser_hashes(codex_home: Path) -> set[str]:
    hashes: set[str] = set()
    cache = codex_home / "plugins" / "cache"
    if not cache.is_dir():
        return hashes
    for candidate in cache.glob("**/browser-client.mjs"):
        if candidate.is_file():
            hashes.add(digest(candidate))
    return hashes


def validate_global_codex(workspace: Path, codex_home: Path) -> tuple[Issue, ...]:
    workspace = workspace.resolve()
    codex_home = codex_home.expanduser().resolve()
    issues: list[Issue] = []
    for skill_issue in compare_skills(workspace / "skill-sources", codex_home.parent / ".agents" / "skills"):
        issues.append(Issue(skill_issue.code, f"skills/{skill_issue.path}", "runtime Skill differs from versioned source"))
    for source in managed_files(workspace):
        destination = installed_path(source, workspace, codex_home)
        label = destination.relative_to(codex_home).as_posix()
        if not destination.is_file():
            issues.append(Issue("missing-managed-file", label, "installed managed file is missing"))
        elif digest(source) != digest(destination):
            issues.append(Issue("managed-file-drift", label, "installed file differs from canonical source"))

    config = codex_home / "config.toml"
    if not config.is_file():
        issues.append(Issue("missing-active-config", "config.toml", "active user config is missing"))
        return tuple(sorted(issues))
    try:
        parsed = tomllib.loads(config.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        issues.append(Issue("invalid-active-config", "config.toml", f"active config cannot be parsed: {type(exc).__name__}"))
        return tuple(sorted(issues))

    for name in ("mcp_servers", "plugins", "projects", "shell_environment_policy"):
        if name in parsed and not isinstance(parsed[name], dict):
            issues.append(Issue("invalid-config-structure", "config.toml", f"{name} must be a TOML table"))
    if issues:
        return tuple(sorted(issues))

    mcp = parsed.get("mcp_servers", {})
    for name in ("context7", "chrome-devtools", "node_repl", "github", "atlassian"):
        if name in mcp and not isinstance(mcp[name], dict):
            issues.append(Issue("invalid-config-structure", "config.toml", f"mcp_servers.{name} must be a TOML table"))
    plugins = parsed.get("plugins", {})
    for name in ("google-calendar@openai-curated", "slack@openai-curated"):
        if name in plugins and not isinstance(plugins[name], dict):
            issues.append(Issue("invalid-config-structure", "config.toml", f"plugins.{name} must be a TOML table"))
    shell_policy = parsed.get("shell_environment_policy", {})
    if "set" in shell_policy and not isinstance(shell_policy["set"], dict):
        issues.append(Issue("invalid-config-structure", "config.toml", "shell_environment_policy.set must be a TOML table"))
    node_repl = mcp.get("node_repl", {}) if isinstance(mcp.get("node_repl", {}), dict) else {}
    if "env" in node_repl and not isinstance(node_repl["env"], dict):
        issues.append(Issue("invalid-config-structure", "config.toml", "mcp_servers.node_repl.env must be a TOML table"))
    if issues:
        return tuple(sorted(issues))

    context7_args = mcp.get("context7", {}).get("args", [])
    if any(isinstance(arg, str) and "api-key" in arg.casefold() for arg in context7_args):
        issues.append(Issue("inline-context7-credential", "config.toml", "Context7 process arguments contain an inline credential marker"))
    elif context7_args and not any(isinstance(arg, str) and arg == "@upstash/context7-mcp@4.0.2" for arg in context7_args):
        issues.append(Issue("unpinned-context7-package", "config.toml", "Context7 package is not pinned to the reviewed version"))

    chrome_args = mcp.get("chrome-devtools", {}).get("args", [])
    if chrome_args and not any(isinstance(arg, str) and arg == "chrome-devtools-mcp@1.7.0" for arg in chrome_args):
        issues.append(Issue("unpinned-chrome-devtools-package", "config.toml", "Chrome DevTools MCP is not pinned to the reviewed version"))

    for name in ("github", "atlassian"):
        if name in mcp and mcp[name].get("enabled", True):
            issues.append(Issue("enabled-noncanonical-mcp", "config.toml", f"{name} MCP must remain disabled until explicitly selected"))

    for name in ("google-calendar@openai-curated", "slack@openai-curated"):
        if name in plugins and plugins[name].get("enabled", True):
            issues.append(Issue("enabled-uninstalled-plugin", "config.toml", f"{name} is enabled but not installed"))

    env = mcp.get("node_repl", {}).get("env", {})
    services, services_valid = trusted_service_paths(env.get("NODE_REPL_TRUSTED_SERVICES"))
    if not services_valid:
        issues.append(Issue("invalid-trusted-services", "config.toml", "trusted services value is not valid JSON"))
    for service_name, service_path in services:
        if service_name == "browser" and not Path(service_path).expanduser().exists():
            issues.append(Issue("missing-trusted-service", "config.toml", "trusted service path does not exist"))
    configured_hashes_raw = parsed.get("shell_environment_policy", {}).get("set", {}).get("NODE_REPL_TRUSTED_BROWSER_CLIENT_SHA256S")
    if isinstance(configured_hashes_raw, str):
        configured_hashes = [item.strip() for item in configured_hashes_raw.split(",") if item.strip()]
        valid_hashes = installed_browser_hashes(codex_home)
        if isinstance(configured_hashes, list) and any(
            isinstance(item, str) and item not in valid_hashes for item in configured_hashes
        ):
            issues.append(Issue("unmatched-browser-client-hash", "config.toml", "configured browser client hash has no installed match"))

    if parsed.get("shell_environment_policy", {}).get("ignore_default_excludes") is not False:
        issues.append(Issue("secret-like-shell-environment", "config.toml", "secret-like environment variables are inherited by spawned shells"))

    user_home = codex_home.parent.resolve()
    for project_path in parsed.get("projects", {}):
        candidate = Path(project_path).expanduser()
        try:
            resolved = candidate.resolve()
        except OSError:
            resolved = candidate.absolute()
        if resolved == user_home:
            issues.append(Issue("broad-home-trust", "config.toml", "the entire user home is trusted"))
        if not candidate.exists():
            issues.append(Issue("missing-trusted-project", "config.toml", "trusted project path does not exist"))
    return tuple(sorted(issues))


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only audit of the installed global Codex layer.")
    parser.add_argument("--workspace", type=Path, default=ROOT)
    parser.add_argument("--codex-home", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    issues = validate_global_codex(args.workspace, args.codex_home)
    if args.json:
        print(json.dumps({"ok": not issues, "issues": [asdict(issue) for issue in issues]}, ensure_ascii=False, indent=2))
    elif issues:
        print("Global Codex validation failed:", file=sys.stderr)
        for issue in issues:
            print(f"- [{issue.code}] {issue.path}: {issue.detail}", file=sys.stderr)
    else:
        print("global Codex layer OK")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
