#!/usr/bin/env bash
set -euo pipefail

dev_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
codex_home="${HOME}/.codex"
skill_runtime="${HOME}/.agents/skills"
python_bin="${PYTHON_BIN:-python3}"
dry_run=()

if [[ "${1:-}" == "--dry-run" ]]; then
  dry_run=(--dry-run)
elif [[ $# -gt 0 ]]; then
  printf 'Usage: %s [--dry-run]\n' "$0" >&2
  exit 2
fi

if ! command -v "${python_bin}" >/dev/null 2>&1; then
  printf 'Python 3 executable is unavailable: %s\n' "${python_bin}" >&2
  exit 1
fi

git_root="$(git -C "${dev_root}" rev-parse --show-toplevel)"
git_root="$(cd -- "${git_root}" && pwd -P)"
if [[ "${git_root}" != "${dev_root}" ]]; then
  printf 'install-global.sh must run from the canonical DEV source Git root: %s\n' "${dev_root}" >&2
  exit 1
fi

"${python_bin}" -B "${dev_root}/tools/install_global.py" \
  --source "${dev_root}" \
  --codex-home "${codex_home}" \
  --skills-destination "${skill_runtime}" \
  "${dry_run[@]}"
