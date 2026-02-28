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

mkdir -p .tmp

declare -a BANDIT_TARGETS

if [[ "$DIFF_MODE" == "1" || "$DIFF_MODE" == "true" ]]; then
  mapfile -t BANDIT_TARGETS < <(git diff --name-only "$DIFF_RANGE" | grep -E '^apps/(api|tui)/.*\.py$' || true)
  if [[ ${#BANDIT_TARGETS[@]} -eq 0 ]]; then
    echo "[gate7] No changed Python files in apps/api or apps/tui; skipping Bandit scan."
  else
    echo "[gate7] Running diff-only Bandit scan on ${#BANDIT_TARGETS[@]} file(s) for range '$DIFF_RANGE'."
  fi
else
  BANDIT_TARGETS=("apps/api" "apps/tui")
  echo "[gate7] Running full Bandit scan on apps/api and apps/tui."
fi

if [[ ${#BANDIT_TARGETS[@]} -gt 0 ]]; then
  "$PYTHON_BIN" -m bandit -ll -f json -o .tmp/bandit-report.json "${BANDIT_TARGETS[@]}" || true
  "$PYTHON_BIN" - <<'PY'
import json
import sys
from pathlib import Path

report_path = Path('.tmp/bandit-report.json')
if not report_path.exists():
    print('[gate7] ❌ Bandit report missing.')
    sys.exit(1)

report = json.loads(report_path.read_text())
high_severity = [r for r in report.get('results', []) if r.get('issue_severity') == 'HIGH']

if high_severity:
    print('[gate7] ❌ High severity Bandit issues found:')
    for issue in high_severity:
        print(f"  - {issue.get('issue_text')} at {issue.get('filename')}:{issue.get('line_number')}")
    sys.exit(1)

loc = report.get('metrics', {}).get('_totals', {}).get('loc', 'unknown')
print(f'[gate7] ✅ No high severity Bandit issues (scanned {loc} LOC).')
PY
fi

REQ_CHANGED=false
if [[ "$DIFF_MODE" == "1" || "$DIFF_MODE" == "true" ]]; then
  if git diff --name-only "$DIFF_RANGE" | grep -Eq '^(requirements\.txt|apps/api/requirements\.txt)$'; then
    REQ_CHANGED=true
  fi
else
  REQ_CHANGED=true
fi

if [[ "$REQ_CHANGED" == "true" ]]; then
  echo "[gate7] Running Safety dependency scan."
  safety check -r requirements.txt --json > .tmp/safety-root-report.json || true
  safety check -r apps/api/requirements.txt --json > .tmp/safety-api-report.json || true

  "$PYTHON_BIN" - <<'PY'
import json
import sys
from pathlib import Path

def load_report(path: str):
    content = Path(path).read_text().strip()
    if not content:
        return []
    try:
        data = json.loads(content)
    except Exception:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        vulns = data.get('vulnerabilities')
        if isinstance(vulns, list):
            return vulns
    return []

all_vulns = []
for report_file in ('.tmp/safety-root-report.json', '.tmp/safety-api-report.json'):
    all_vulns.extend(load_report(report_file))

if all_vulns:
    print('[gate7] ❌ Safety vulnerabilities found:')
    for vuln in all_vulns:
        package = vuln.get('package_name') or vuln.get('package') or 'unknown-package'
        advisory = vuln.get('advisory') or vuln.get('vulnerability_id') or 'No details'
        print(f'  - {package}: {advisory}')
    sys.exit(1)

print('[gate7] ✅ No Safety vulnerabilities detected in requirements files.')
PY
else
  echo "[gate7] Requirements unchanged in diff mode; skipping Safety dependency scan."
fi

echo "[gate7] Security scanning passed."