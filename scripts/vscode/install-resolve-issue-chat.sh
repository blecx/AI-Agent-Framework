#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXT_DIR="$REPO_ROOT/.vscode/extensions/issueagent"
OUT_DIR="$REPO_ROOT/.tmp/vscode"
VSIX_PATH="$OUT_DIR/ai-agent-framework.issueagent.vsix"

if [[ ! -d "$EXT_DIR" ]]; then
  echo "ERROR: Extension directory not found: $EXT_DIR" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

echo "Packaging VS Code extension from: $EXT_DIR"
(
  cd "$EXT_DIR"
  # Use npx so contributors don't need a global vsce install.
  npx -y @vscode/vsce@latest package --out "$VSIX_PATH" >/dev/null
)

echo "Packaged: $VSIX_PATH"

if ! command -v code >/dev/null 2>&1; then
  echo "ERROR: VS Code CLI 'code' not found on PATH." >&2
  echo "Install VS Code's shell command, then run this script again." >&2
  exit 1
fi

echo "Installing VSIX into VS Code (force)..."
code --install-extension "$VSIX_PATH" --force

echo "Done. In VS Code run: 'Developer: Reload Window'"
echo "Then you should see '@resolve-issue' in the chat participant menu."
