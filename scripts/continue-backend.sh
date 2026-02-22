#!/usr/bin/env bash
set -euo pipefail

MAX_ISSUES=25
ISSUE_OVERRIDE=""
DRY_RUN=0
NO_PUBLISH=0
MAX_ISSUES_CAP=25

ROADMAP_PATHS=("planning/issues/step-3.yml")
ISSUE_LABEL="step:3"
BACKEND_REPO="blecx/AI-Agent-Framework"

export WORK_ISSUE_COMPACT="${WORK_ISSUE_COMPACT:-1}"
export WORK_ISSUE_MAX_PROMPT_CHARS="${WORK_ISSUE_MAX_PROMPT_CHARS:-1800}"
export LLM_CONFIG_PATH="${LLM_CONFIG_PATH:-configs/llm.workflow.json}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage: ./scripts/continue-backend.sh [options]

Runs the backend-first roadmap loop:
  publish roadmap backend issues -> select scoped backend issue -> work-issue -> prmerge

Options:
  --issue <n>              Run a single explicit backend issue.
  --paths <glob> [...]     Roadmap spec paths (default: planning/issues/step-3.yml).
  --label <name>           Label used for scoped selection (default: step:3).
  --max-issues <n>         Stop after n issues (default: 25).
  --dry-run                Select and print actions, do not execute work/merge/publish.
  --no-publish             Do not auto-publish roadmap issues.
  -h, --help               Show this help.

Notes:
  - This command is backend-only and intended for roadmap-scoped issues.
  - Client work stays in its own loop.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --issue)
      ISSUE_OVERRIDE="${2:-}"
      shift 2
      ;;
    --paths)
      ROADMAP_PATHS=()
      shift
      while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do
        ROADMAP_PATHS+=("$1")
        shift
      done
      if [[ ${#ROADMAP_PATHS[@]} -eq 0 ]]; then
        echo "--paths requires at least one glob" >&2
        exit 1
      fi
      ;;
    --label)
      ISSUE_LABEL="${2:-}"
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

if [[ "$MAX_ISSUES" -gt "$MAX_ISSUES_CAP" ]]; then
  echo "Requested --max-issues=$MAX_ISSUES exceeds default cap ($MAX_ISSUES_CAP)."
  read -r -p "Override cap and continue? (y/N): " override_cap
  if [[ ! "$override_cap" =~ ^[Yy]$ ]]; then
    echo "Cancelled. Re-run with --max-issues <= $MAX_ISSUES_CAP or confirm override."
    exit 1
  fi
fi

publish_backend_roadmap_issues() {
  if [[ "$NO_PUBLISH" == "1" ]]; then
    return 0
  fi

  ensure_backend_labels

  local cmd=(./.venv/bin/python scripts/publish_issues.py --repo "$BACKEND_REPO" --apply --paths)
  local p
  for p in "${ROADMAP_PATHS[@]}"; do
    cmd+=("$p")
  done

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: ${cmd[*]}"
    return 0
  fi

  echo "Publishing backend roadmap issue specs (idempotent map/create)..."
  "${cmd[@]}"
}

ensure_backend_labels() {
  local labels
  labels="$(
    ./.venv/bin/python - "${ROADMAP_PATHS[@]}" <<'PY'
import sys
from pathlib import Path
import yaml

paths = [Path(p) for p in sys.argv[1:]]
labels = set()
for path in paths:
    if not path.exists():
        continue
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        continue
    entries = data.get("AI-Agent-Framework")
    if not isinstance(entries, list):
        continue
    for item in entries:
        if not isinstance(item, dict):
            continue
        for label in item.get("labels", []) or []:
            label_text = str(label).strip()
            if label_text:
                labels.add(label_text)

for label in sorted(labels):
    print(label)
PY
  )"

  if [[ -z "$labels" ]]; then
    return 0
  fi

  local existing
  existing="$(GH_PAGER=cat gh label list --repo "$BACKEND_REPO" --limit 1000 --json name --jq '.[].name')"

  while IFS= read -r label; do
    [[ -z "$label" ]] && continue
    if ! grep -Fxq "$label" <<<"$existing"; then
      if [[ "$DRY_RUN" == "1" ]]; then
        echo "[dry-run] Would create label in $BACKEND_REPO: $label"
      else
        GH_PAGER=cat gh label create "$label" --repo "$BACKEND_REPO" --color BFD4F2 --description "Roadmap scoped label" >/dev/null
        echo "Created missing backend label: $label"
      fi
    fi
  done <<<"$labels"
}

validate_backend_model_policy() {
  local planning_model
  local coding_model
  planning_model="$(./.venv/bin/python - <<'PY'
from agents.llm_client import LLMClientFactory
print(LLMClientFactory.get_model_id_for_role("planning"))
PY
)"
  coding_model="$(./.venv/bin/python - <<'PY'
from agents.llm_client import LLMClientFactory
print(LLMClientFactory.get_model_id_for_role("coding"))
PY
)"

  if [[ "$planning_model" != openai/gpt-5* ]]; then
    echo "❌ Planning model policy violation: expected GPT-5 class model, got '$planning_model'" >&2
    echo "   Set LLM_CONFIG_PATH to a config with planning model openai/gpt-5.*" >&2
    exit 2
  fi

  echo "Model policy: planning=$planning_model coding=$coding_model"
}

validate_backend_issue_budget() {
  local cmd=(./.venv/bin/python scripts/check_issue_specs.py --no-legacy --strict-sections --max-body-chars 2600 --paths)
  local p
  for p in "${ROADMAP_PATHS[@]}"; do
    cmd+=("$p")
  done

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] Would run: ${cmd[*]}"
    return 0
  fi

  "${cmd[@]}"
}

select_next_backend_issue() {
  local cmd=(
    gh issue list
    --repo "$BACKEND_REPO"
    --state open
    --limit 200
    --json number
    --jq 'sort_by(.number) | .[0].number // empty'
  )

  if [[ -n "$ISSUE_LABEL" ]]; then
    cmd=(
      gh issue list
      --repo "$BACKEND_REPO"
      --state open
      --label "$ISSUE_LABEL"
      --limit 200
      --json number
      --jq 'sort_by(.number) | .[0].number // empty'
    )
  fi

  GH_PAGER=cat "${cmd[@]}"
}

cd "$ROOT_DIR"

validate_backend_model_policy
validate_backend_issue_budget

count=0
while true; do
  issue=""

  if [[ -n "$ISSUE_OVERRIDE" ]]; then
    issue="$ISSUE_OVERRIDE"
    ISSUE_OVERRIDE=""
  else
    publish_backend_roadmap_issues
    issue="$(select_next_backend_issue || true)"
  fi

  if [[ -z "$issue" ]]; then
    echo "No open scoped backend issues available; stopping backend loop."
    break
  fi

  echo "============================================================"
  echo "/continue-backend :: Processing Backend Issue #$issue"
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
    break
  fi
done

echo "Backend loop finished. Processed issues: $count"
