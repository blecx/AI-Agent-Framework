#!/usr/bin/env bash
set -euo pipefail

MAX_ISSUES=25
ISSUE_OVERRIDE=""
DRY_RUN=0
MAX_ISSUES_CAP=25
NO_PUBLISH=0

export WORK_ISSUE_COMPACT="${WORK_ISSUE_COMPACT:-1}"
export WORK_ISSUE_MAX_PROMPT_CHARS="${WORK_ISSUE_MAX_PROMPT_CHARS:-3200}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# API-friendly pacing for gh CLI calls in this script.
GH_MIN_INTERVAL_SECONDS="${GH_MIN_INTERVAL_SECONDS:-1}"
__GH_LAST_CALL_TS=""

gh() {
  local min_interval
  min_interval="${GH_MIN_INTERVAL_SECONDS:-0}"

  if [[ -n "${__GH_LAST_CALL_TS}" && "${min_interval}" != "0" ]]; then
    local now elapsed
    now="$(date +%s)"
    elapsed="$(( now - __GH_LAST_CALL_TS ))"
    if [[ "$elapsed" -lt "$min_interval" ]]; then
      sleep "$(( min_interval - elapsed ))"
    fi
  fi

  command gh "$@"
  __GH_LAST_CALL_TS="$(date +%s)"
}

usage() {
  cat <<'EOF'
Usage: ./scripts/continue-phase-3.sh [options]

Runs the /continue-phase-3 loop (backend-first):
  publish step-3 backend issues -> select next open step:3 backend issue -> work-issue -> prmerge

Options:
  --issue <n>           Run a single explicit backend issue.
  --max-issues <n>      Stop after n issues (default: 25).
  --dry-run             Select and print actions, do not execute work/merge/publish.
  --no-publish          Do not auto-publish step-3 backend issues.
  -h, --help            Show this help.

Notes:
  - This loop is backend-first by design and uses `scripts/work-issue.py` + `scripts/prmerge`.
  - Client step-3 issues are intentionally not auto-processed by this script.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --issue)
      ISSUE_OVERRIDE="${2:-}"
      shift 2
      ;;
    --max-issues)
      MAX_ISSUES="${2:-0}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --no-publish)
      NO_PUBLISH=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if ! [[ "$MAX_ISSUES" =~ ^[0-9]+$ ]]; then
  echo "Invalid --max-issues value: $MAX_ISSUES" >&2
  exit 1
fi

if [[ "$MAX_ISSUES" -lt "$MAX_ISSUES_CAP" ]]; then
  echo "--max-issues values below $MAX_ISSUES_CAP are forbidden." >&2
  echo "Use --max-issues $MAX_ISSUES_CAP (default), or set a value above it and confirm override." >&2
  exit 1
fi

if [[ "$MAX_ISSUES" -gt "$MAX_ISSUES_CAP" ]]; then
  echo "Requested --max-issues=$MAX_ISSUES exceeds hard baseline ($MAX_ISSUES_CAP)."
  read -r -p "Override baseline and continue with $MAX_ISSUES issues? (y/N): " override_cap
  if [[ ! "$override_cap" =~ ^[Yy]$ ]]; then
    echo "Cancelled. Re-run with --max-issues $MAX_ISSUES_CAP or confirm override."
    exit 1
  fi
fi

publish_step3_backend_issues() {
  if [[ "$NO_PUBLISH" == "1" ]]; then
    return 0
  fi

  local cmd=(
    ./.venv/bin/python
    scripts/publish_issues.py
    --paths planning/issues/step-3.yml
    --repo blecx/AI-Agent-Framework
    --apply
  )

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: ${cmd[*]}"
    return 0
  fi

  echo "Publishing Step-3 backend issue specs (idempotent map/create)..."
  "${cmd[@]}"
}

select_next_step3_backend_issue() {
  GH_PAGER=cat gh issue list \
    --repo blecx/AI-Agent-Framework \
    --state open \
    --label step:3 \
    --limit 200 \
    --json number \
    --jq 'sort_by(.number) | .[0].number // empty'
}

cd "$ROOT_DIR"

count=0

while true; do
  issue=""

  if [[ -n "$ISSUE_OVERRIDE" ]]; then
    issue="$ISSUE_OVERRIDE"
    ISSUE_OVERRIDE=""
  else
    publish_step3_backend_issues
    issue="$(select_next_step3_backend_issue || true)"
  fi

  if [[ -z "$issue" ]]; then
    echo "No open backend step:3 issues available; stopping phase-3 loop."
    break
  fi

  echo "============================================================"
  echo "/continue-phase-3 :: Processing Backend Issue #$issue"
  echo "============================================================"

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: ./scripts/work-issue.py --issue $issue"
    echo "[dry-run] Would run: ./scripts/prmerge $issue"
  else
    ./scripts/work-issue.py --issue "$issue"
    ./scripts/prmerge "$issue"
  fi

  count=$((count + 1))
  if [[ "$count" -ge "$MAX_ISSUES" ]]; then
    echo "Reached --max-issues=$MAX_ISSUES; stopping."
    if [[ "$MAX_ISSUES" -eq "$MAX_ISSUES_CAP" ]]; then
      echo "If more backend issues remain, re-run with --max-issues > $MAX_ISSUES_CAP and confirm override."
    fi
    break
  fi
done

echo "Phase-3 loop finished. Processed issues: $count"
