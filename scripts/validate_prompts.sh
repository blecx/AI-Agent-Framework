#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="python3"
fi

echo "[validate_prompts] Running strict prompt quality checks..."
"${PYTHON_BIN}" "${ROOT_DIR}/scripts/check_prompt_quality.py" --strict
