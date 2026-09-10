#!/usr/bin/env bash
set -euo pipefail

mode="${1:---apply}"
if [[ "${mode}" != "--check" && "${mode}" != "--apply" ]]; then
  printf 'Usage: %s [--check|--apply]\n' "$0" >&2
  exit 2
fi

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
dev_root_value="${DEV_SOURCE_ROOT:-}"
if [[ -z "${dev_root_value}" && -f "${HOME}/.codex/dev-layout.toml" ]]; then
  dev_root_value="$(sed -nE 's/^[[:space:]]*dev_source_root[[:space:]]*=[[:space:]]*"([^"]+)"[[:space:]]*$/\1/p' "${HOME}/.codex/dev-layout.toml" | head -n 1)"
fi
dev_root_value="${dev_root_value:-~/codex-dev}"
case "${dev_root_value}" in
  "~") dev_root="${HOME}" ;;
  "~/"*) dev_root="${HOME}/${dev_root_value#\~/}" ;;
  *) dev_root="${dev_root_value}" ;;
esac
bootstrap="${dev_root}/tools/project_bootstrap.py"
python_bin="${PYTHON_BIN:-python3}"

if [[ ! -f "${bootstrap}" ]]; then
  printf 'Global DEV is missing at %s.\n' "${dev_root}" >&2
  printf 'Canonical recovery (review, then run):\n' >&2
  printf 'git clone https://github.com/ZabulaAleksey/codex-dev.git "%s"\n' "${dev_root}" >&2
  printf 'Then rerun: ./.codex/bootstrap.sh %s\n' "${mode}" >&2
  exit 1
fi

exec "${python_bin}" -B "${bootstrap}" "${mode}" --project "${project_root}" --json
