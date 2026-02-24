#!/bin/bash
# Configure VS Code for near-zero command approvals in this workspace.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

mkdir -p "$ROOT_DIR/.tmp"

python3 "$SCRIPT_DIR/setup-vscode-autoapprove.py" --workspace-only --low-friction

echo ""
echo "✅ Low-approval mode configured for workspace + client workspace."
echo "📝 Reload VS Code: Ctrl+Shift+P -> Developer: Reload Window"
