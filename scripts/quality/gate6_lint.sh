#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

DIFF_MODE="${CI_DIFF_ONLY:-false}"
DIFF_RANGE="${CI_DIFF_RANGE:-origin/main...HEAD}"

if [[ "$DIFF_RANGE" == *"origin/main"* ]] && ! git rev-parse --verify origin/main >/dev/null 2>&1; then
  git fetch origin main --depth=1 >/dev/null 2>&1 || true
fi

declare -a TARGETS

if [[ "$DIFF_MODE" == "1" || "$DIFF_MODE" == "true" ]]; then
  mapfile -t TARGETS < <(git diff --name-only "$DIFF_RANGE" | grep -E '^(apps/api|apps/tui|tests)/.*\.py$' || true)
  if [[ ${#TARGETS[@]} -eq 0 ]]; then
    echo "[gate6] No changed Python files in apps/api, apps/tui, or tests for range '$DIFF_RANGE'; skipping lint gate."
    exit 0
  fi
  echo "[gate6] Running diff-only lint on ${#TARGETS[@]} changed Python file(s) for range '$DIFF_RANGE'."
else
  TARGETS=("apps/api" "apps/tui" "tests")
  echo "[gate6] Running full lint scan on apps/api, apps/tui, tests."
fi

"$PYTHON_BIN" -m black --check "${TARGETS[@]}"
"$PYTHON_BIN" -m flake8 --count --show-source --statistics "${TARGETS[@]}"

echo "[gate6] Linting passed."