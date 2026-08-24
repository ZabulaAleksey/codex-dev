from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import tomllib
from pathlib import Path


MCP_TO_DISABLE = {"mcp_servers.github", "mcp_servers.atlassian"}
PLUGINS_TO_DISABLE = {
    'plugins."google-calendar@openai-curated"',
    'plugins."slack@openai-curated"',
}
CONTEXT7_PACKAGE = "@upstash/context7-mcp@4.0.2"
CHROME_DEVTOOLS_PACKAGE = "chrome-devtools-mcp@1.7.0"


class ConcurrentConfigUpdateError(RuntimeError):
    pass


def split_sections(text: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    lines = text.splitlines(keepends=True)
    preamble: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    current_header: str | None = None
    current_body: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if current_header is None:
                preamble = current_body
            else:
                sections.append((current_header, current_body))
            current_header = stripped[1:-1]
            current_body = []
        else:
            current_body.append(line)
    if current_header is None:
        preamble = current_body
    else:
        sections.append((current_header, current_body))
    return preamble, sections


def set_enabled_false(body: list[str], newline: str) -> list[str]:
    result = list(body)
    for index, line in enumerate(result):
        if re.match(r"^\s*enabled\s*=", line):
            indent = line[: len(line) - len(line.lstrip())]
            result[index] = f"{indent}enabled = false{newline}"
            return result
    result.insert(0, f"enabled = false{newline}")
    return result


def set_boolean(body: list[str], key: str, value: bool, newline: str) -> list[str]:
    rendered = "true" if value else "false"
    result = list(body)
    for index, line in enumerate(result):
        if re.match(rf"^\s*{re.escape(key)}\s*=", line):
            indent = line[: len(line) - len(line.lstrip())]
            result[index] = f"{indent}{key} = {rendered}{newline}"
            return result
    result.insert(0, f"{key} = {rendered}{newline}")
    return result


def browser_client_hashes(codex_home: Path) -> set[str]:
    hashes: set[str] = set()
    cache = codex_home / "plugins" / "cache"
    if not cache.is_dir():
        return hashes
    for candidate in cache.glob("**/browser-client.mjs"):
        if candidate.is_file():
            hashes.add(hashlib.sha256(candidate.read_bytes()).hexdigest())
    return hashes


def normalize_text(
    text: str,
    user_home: Path,
    valid_browser_hashes: set[str] | None = None,
) -> tuple[str, list[str]]:
    # Parse first so a malformed active config is never rewritten.
    original = tomllib.loads(text)
    newline = "\r\n" if "\r\n" in text else "\n"
    preamble, sections = split_sections(text)
    changes: list[str] = []
    broad_home = str(user_home.resolve()).casefold()
    legacy_projects_root = (user_home.resolve() / "codex-workspace" / "projects").resolve()
    output: list[str] = list(preamble)
    section_names = {header for header, _ in sections}
    has_shell_policy = "shell_environment_policy" in section_names

    for header, body in sections:
        parsed_project = re.fullmatch(r"projects\.'(.+)'", header)
        project_path = Path(parsed_project.group(
            1)).resolve() if parsed_project else None
        if project_path and str(project_path).casefold() == broad_home:
            changes.append("remove-broad-home-trust")
            continue
        if project_path and project_path.parent == legacy_projects_root:
            changes.append("remove-stale-project-trust")
            continue
        if project_path and not (project_path / ".git").exists():
            changes.append("remove-nonproject-trust")
            continue

        if header == "mcp_servers.node_repl.env":
            services_raw = original.get("mcp_servers", {}).get(
                "node_repl", {}).get("env", {}).get("NODE_REPL_TRUSTED_SERVICES")
            services: dict[str, object] | None = None
            if isinstance(services_raw, str):
                decoded = json.loads(services_raw)
                if not isinstance(decoded, dict):
                    raise ValueError("trusted services must be a JSON object")
                services = decoded
            updated: list[str] = []
            for line in body:
                if re.match(r"^\s*NODE_REPL_TRUSTED_SERVICES\s*=", line) and services is not None:
                    browser_service = services.get("browser")
                    if isinstance(browser_service, str) and "://" not in browser_service and not Path(browser_service).expanduser().exists():
                        services.pop("browser")
                        changes.append("remove-missing-browser-service")
                    if services:
                        encoded = json.dumps(json.dumps(
                            services, separators=(",", ":")))
                        updated.append(
                            f"NODE_REPL_TRUSTED_SERVICES = {encoded}{newline}")
                else:
                    updated.append(line)
            body = updated
        elif header == "mcp_servers.context7":
            replaced = False
            updated: list[str] = []
            for line in body:
                if re.match(r"^\s*args\s*=", line):
                    indent = line[: len(line) - len(line.lstrip())]
                    updated.append(
                        f'{indent}args = ["-y", "{CONTEXT7_PACKAGE}"]{newline}')
                    replaced = True
                    if "--api-key" in line:
                        changes.append("remove-context7-inline-key")
                else:
                    updated.append(line)
            body = updated
            if not replaced:
                body.insert(0, f'args = ["-y", "{CONTEXT7_PACKAGE}"]{newline}')
                changes.append("add-context7-safe-args")
        elif header == "mcp_servers.chrome-devtools":
            updated = []
            for line in body:
                if re.match(r"^\s*args\s*=", line):
                    indent = line[: len(line) - len(line.lstrip())]
                    replacement = f'{indent}args = ["-y", "{CHROME_DEVTOOLS_PACKAGE}"]{newline}'
                    if line != replacement:
                        changes.append("pin-chrome-devtools-package")
                    updated.append(replacement)
                else:
                    updated.append(line)
            body = updated
        elif header == "shell_environment_policy":
            before = "".join(body)
            body = set_boolean(body, "ignore_default_excludes", False, newline)
            if "".join(body) != before:
                changes.append("strip-secret-like-shell-environment")
        elif header in MCP_TO_DISABLE or header in PLUGINS_TO_DISABLE:
            before = "".join(body)
            body = set_enabled_false(body, newline)
            if "".join(body) != before:
                changes.append(f"disable-{header}")

        if header == "shell_environment_policy.set" and not has_shell_policy:
            output.append(f"[shell_environment_policy]{newline}")
            output.append(f"ignore_default_excludes = false{newline}{newline}")
            changes.append("strip-secret-like-shell-environment")
            has_shell_policy = True
        if header == "shell_environment_policy.set" and valid_browser_hashes is not None:
            updated = []
            for line in body:
                if re.match(r"^\s*NODE_REPL_TRUSTED_BROWSER_CLIENT_SHA256S\s*=", line):
                    configured = original.get("shell_environment_policy", {}).get(
                        "set", {}).get("NODE_REPL_TRUSTED_BROWSER_CLIENT_SHA256S", "")
                    hashes = [item.strip() for item in configured.split(
                        ",") if item.strip()] if isinstance(configured, str) else []
                    retained = [
                        item for item in hashes if item in valid_browser_hashes]
                    if retained != hashes:
                        changes.append("remove-unmatched-browser-client-hash")
                    if retained:
                        updated.append(
                            f"NODE_REPL_TRUSTED_BROWSER_CLIENT_SHA256S = {json.dumps(','.join(retained))}{newline}")
                else:
                    updated.append(line)
            body = updated
        output.append(f"[{header}]{newline}")
        output.extend(body)

    if not has_shell_policy:
        output.append(f"[shell_environment_policy]{newline}")
        output.append(f"ignore_default_excludes = false{newline}")
        changes.append("strip-secret-like-shell-environment")

    normalized = "".join(output)
    parsed = tomllib.loads(normalized)
    context7_args = parsed.get("mcp_servers", {}).get(
        "context7", {}).get("args", [])
    if any(isinstance(arg, str) and "api-key" in arg.casefold() for arg in context7_args):
        raise ValueError(
            "Context7 inline credential marker remains after normalization")
    node_env = parsed.get("mcp_servers", {}).get(
        "node_repl", {}).get("env", {})
    normalized_services_raw = node_env.get("NODE_REPL_TRUSTED_SERVICES")
    if isinstance(normalized_services_raw, str):
        normalized_services = json.loads(normalized_services_raw)
        browser_service = normalized_services.get(
            "browser") if isinstance(normalized_services, dict) else None
        if isinstance(browser_service, str) and "://" not in browser_service and not Path(browser_service).expanduser().exists():
            raise ValueError(
                "missing browser service remains after normalization")
    if parsed.get("shell_environment_policy", {}).get("ignore_default_excludes") is not False:
        raise ValueError(
            "secret-like shell environment variables are not excluded")
    for name in ("github", "atlassian"):
        if name in parsed.get("mcp_servers", {}) and parsed["mcp_servers"][name].get("enabled", True):
            raise ValueError(f"{name} MCP remains enabled after normalization")
    for name in ("google-calendar@openai-curated", "slack@openai-curated"):
        if name in parsed.get("plugins", {}) and parsed["plugins"][name].get("enabled", True):
            raise ValueError(f"{name} remains enabled after normalization")

    normalized_projects = parsed.get("projects", {})
    for project in normalized_projects:
        project_path = Path(project).resolve()
        if project_path.parent == legacy_projects_root:
            raise ValueError("stale project trust remains after normalization")
        if not (project_path / ".git").exists():
            raise ValueError("non-project trust remains after normalization")
    return normalized, sorted(set(changes))


def write_atomic(path: Path, content: str, expected_digest: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        current_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if current_digest != expected_digest:
            raise ConcurrentConfigUpdateError(
                "active config changed during normalization")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Safely normalize the active user Codex config without printing secrets.")
    parser.add_argument("--config", type=Path,
                        default=Path.home() / ".codex" / "config.toml")
    parser.add_argument("--apply", action="store_true",
                        help="Write the validated normalized config atomically.")
    args = parser.parse_args()
    path = args.config.expanduser().resolve()
    try:
        original_bytes = path.read_bytes()
        text = original_bytes.decode("utf-8")
        normalized, changes = normalize_text(
            text,
            path.parent.parent,
            browser_client_hashes(path.parent),
        )
    except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
        print(f"ERROR: normalization refused: {exc}", file=sys.stderr)
        return 2
    if normalized == text:
        print("user Codex config already normalized")
        return 0
    if not args.apply:
        print("user Codex config requires normalization: " + ", ".join(changes))
        return 1
    try:
        write_atomic(path, normalized, hashlib.sha256(
            original_bytes).hexdigest())
    except (OSError, ConcurrentConfigUpdateError) as exc:
        print(f"ERROR: normalization refused: {exc}", file=sys.stderr)
        return 2
    print("user Codex config normalized: " + ", ".join(changes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
