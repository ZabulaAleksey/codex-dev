from __future__ import annotations

import subprocess
import sys

EXPECTED_EMAIL = "158517930+ZabulaAleksey@users.noreply.github.com"


def git_config(key: str) -> str:
    result = subprocess.run(
        ["git", "config", "--get", key],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def main() -> int:
    email = git_config("user.email")
    if not email:
        print(
            "ERROR: git user.email is not configured. "
            f'Set it to "{EXPECTED_EMAIL}" before committing.',
            file=sys.stderr,
        )
        return 2

    if email.casefold() != EXPECTED_EMAIL.casefold():
        print(
            "ERROR: Git commit email privacy check failed.\n"
            f"Effective user.email: {email}\n"
            f"Expected noreply:     {EXPECTED_EMAIL}\n"
            "Fix globally with:\n"
            f'  git config --global user.email "{EXPECTED_EMAIL}"\n'
            "A repository-local user.email may override the global setting; inspect with:\n"
            "  git config --show-origin --get-regexp '^user\\.(name|email)$'",
            file=sys.stderr,
        )
        return 1

    print(f"git identity privacy: OK ({email})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
