#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXT_DIR="$REPO_ROOT/.vscode/extensions/issueagent"
EXPECTED_EXT_ID="ai-agent-framework.issueagent"
EXPECTED_PARTICIPANT_ID="resolve-issue.chat"
EXPECTED_PARTICIPANT_NAME="resolve-issue"

red() { printf "\033[31m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }

fail() {
  red "FAIL: $*"
  exit 1
}

info() {
  echo "- $*"
}

info "Repo root: $REPO_ROOT"
[[ -d "$EXT_DIR" ]] || fail "Extension dir not found: $EXT_DIR"

info "Checking prerequisites (code/node/npm)"
command -v code >/dev/null 2>&1 || fail "VS Code CLI 'code' not found on PATH"
command -v node >/dev/null 2>&1 || fail "node not found on PATH"
command -v npm >/dev/null 2>&1 || fail "npm not found on PATH"

VSCODE_VERSION="$(code --version | head -n 1 | tr -d '\r')"
NODE_VERSION="$(node --version | tr -d '\r')"
NPM_VERSION="$(npm --version | tr -d '\r')"

info "VS Code: $VSCODE_VERSION"
info "Node:    $NODE_VERSION"
info "npm:     $NPM_VERSION"

VSCODE_VERSION="$VSCODE_VERSION" python3 - <<'PY'
import os
import re
import sys
v = os.environ.get("VSCODE_VERSION", "")
m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", v)
if not m:
    print(f"WARN: Could not parse VS Code version: {v}")
    sys.exit(0)
major, minor, patch = map(int, m.groups())
# chatParticipants and createChatParticipant are stable well before this,
# but keep a conservative floor.
if (major, minor) < (1, 90):
    print(f"FAIL: VS Code version {v} is too old; need >= 1.90.0")
    sys.exit(1)
print("OK: VS Code version is compatible")
PY

info "Validating extension manifest + code consistency"
PKG_JSON="$EXT_DIR/package.json"
EXT_JS="$EXT_DIR/extension.js"

[[ -f "$PKG_JSON" ]] || fail "Missing $PKG_JSON"
[[ -f "$EXT_JS" ]] || fail "Missing $EXT_JS"

grep -q '"chatParticipants"' "$PKG_JSON" || fail "package.json missing contributes.chatParticipants"
grep -q "\"id\": \"$EXPECTED_PARTICIPANT_ID\"" "$PKG_JSON" || fail "package.json missing participant id $EXPECTED_PARTICIPANT_ID"
grep -q "\"name\": \"$EXPECTED_PARTICIPANT_NAME\"" "$PKG_JSON" || fail "package.json missing participant name $EXPECTED_PARTICIPANT_NAME"
grep -q "onChatParticipant:$EXPECTED_PARTICIPANT_ID" "$PKG_JSON" || fail "package.json missing activation event onChatParticipant:$EXPECTED_PARTICIPANT_ID"

grep -q "createChatParticipant" "$EXT_JS" || fail "extension.js does not use createChatParticipant"
grep -q "'${EXPECTED_PARTICIPANT_ID}'" "$EXT_JS" || fail "extension.js does not reference participant id $EXPECTED_PARTICIPANT_ID"

green "OK: manifest and code agree"

info "Packaging + installing VSIX (this is the critical step)"
bash "$REPO_ROOT/scripts/vscode/install-resolve-issue-chat.sh" >/dev/null

green "OK: VSIX packaged and installed"

info "Verifying installation in VS Code"
if ! code --list-extensions | grep -q "^${EXPECTED_EXT_ID}$"; then
  code --list-extensions | tail -n 20 || true
  fail "Extension not installed (expected id: $EXPECTED_EXT_ID)"
fi

green "OK: extension is installed: $EXPECTED_EXT_ID"

LOCATED="$(code --locate-extension "$EXPECTED_EXT_ID" 2>/dev/null || true)"
if [[ -z "$LOCATED" ]]; then
  yellow "WARN: code --locate-extension did not return a path (older code CLI behavior)."
else
  info "Installed path: $LOCATED"
  [[ -f "$LOCATED/package.json" ]] || fail "Installed extension missing package.json"
  grep -q "\"id\": \"$EXPECTED_PARTICIPANT_ID\"" "$LOCATED/package.json" || fail "Installed extension package.json missing participant id"
  green "OK: installed package.json contains participant"
fi

echo
print_next() {
  echo "NEXT (manual, <30s):"
  echo "1) VS Code Command Palette → Developer: Reload Window"
  echo "2) Open Chat and type: @resolve-issue /run"
  echo "3) If it still doesn't appear: View → Output → select 'Log (Extension Host)' and search for 'issueagent'"
}
print_next

green "SMOKE TEST PASSED"
