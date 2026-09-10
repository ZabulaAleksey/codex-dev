#!/usr/bin/env bash
set -euo pipefail
mode="${1:---apply}"
[[ "${mode}" == "--check" || "${mode}" == "--apply" ]] || { printf 'Usage: %s [--check|--apply]\n' "$0" >&2; exit 2; }
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
dev_root="${DEV_SOURCE_ROOT:-${HOME}/codex-dev}"
bootstrap="${dev_root}/tools/project_bootstrap.py"
[[ -f "${bootstrap}" ]] || { printf 'Global DEV missing at %s. Review and run: git clone https://github.com/ZabulaAleksey/codex-dev.git "%s"\n' "${dev_root}" "${dev_root}" >&2; exit 1; }
exec "${PYTHON_BIN:-python3}" -B "${bootstrap}" "${mode}" --project "${project_root}" --json
