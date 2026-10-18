#!/usr/bin/env bash
set -euo pipefail
task_tools_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
task_python_bin="${GUMA_PYTHON:-python3}"
task_pip_args=(--no-cache-dir)
if [[ $# -ne 0 ]]; then
  echo 'Usage: bash setup.sh (optional GUMA_PYTHON and GUMA_V6_PIP_CACHE environment variables)' >&2
  exit 2
fi
if [[ -n "${GUMA_V6_PIP_CACHE:-}" ]]; then
  mkdir -p -- "$GUMA_V6_PIP_CACHE"
  task_pip_args=(--cache-dir "$GUMA_V6_PIP_CACHE")
fi
"$task_python_bin" -m venv "$task_tools_dir/.venv"
"$task_tools_dir/.venv/bin/python" -m pip install "${task_pip_args[@]}" -r "$task_tools_dir/requirements.txt"
echo "Installation complete: $task_tools_dir/.venv/bin/python"
