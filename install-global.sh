#!/usr/bin/env bash
set -euo pipefail

dev_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
codex_home="${HOME}/.codex"
skill_runtime="${HOME}/.agents/skills"
python_bin="${PYTHON_BIN:-python3}"

if [[ ! -d "${codex_home}" ]]; then
  printf 'ДЕВ должен быть клонирован или перемещён непосредственно в %s.\n' "${codex_home}" >&2
  exit 1
fi

canonical_codex_home="$(cd -- "${codex_home}" && pwd -P)"
if [[ "${dev_root}" != "${canonical_codex_home}" ]]; then
  printf 'ДЕВ должен быть запущен из канонического ~/.codex: %s\n' "${canonical_codex_home}" >&2
  exit 1
fi

if ! command -v "${python_bin}" >/dev/null 2>&1; then
  printf 'Python 3 executable is unavailable: %s\n' "${python_bin}" >&2
  exit 1
fi

git_root="$(git -C "${dev_root}" rev-parse --show-toplevel)"
git_root="$(cd -- "${git_root}" && pwd -P)"
if [[ "${git_root}" != "${dev_root}" ]]; then
  printf 'Git root должен совпадать с каноническим ~/.codex: %s\n' "${dev_root}" >&2
  exit 1
fi

printf 'ДЕВ уже расположен в каноническом ~/.codex.\n'
"${python_bin}" -B "${dev_root}/tools/validate_context.py"
"${python_bin}" -B "${dev_root}/tools/sync_global_skills.py" \
  --source "${dev_root}/skill-sources" \
  --destination "${skill_runtime}" \
  --apply
"${python_bin}" -B "${dev_root}/tools/validate_context.py"
"${python_bin}" -B "${dev_root}/tools/validate_global_codex.py" \
  --workspace "${dev_root}" \
  --codex-home "${canonical_codex_home}"

printf 'Проверки завершены. Runtime config.toml и secrets не изменялись.\n'
