#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

"$ROOT_DIR/docs/tutorials/scripts/export-drawio.sh"
"$ROOT_DIR/docs/tutorials/scripts/capture-workflow-screenshots.sh" "$@"

echo "[visuals] Diagram exports + screenshots completed"
