#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
WEB_DIR="$ROOT_DIR/apps/web"
BASE_URL="${TUTORIAL_BASE_URL:-http://localhost:5173}"

cd "$WEB_DIR"

if [[ "${1:-}" == "--docker" ]]; then
  echo "[capture] Starting docker stack for screenshots..."
  cd "$ROOT_DIR"
  mkdir -p projectDocs
  docker compose up -d
  cd "$WEB_DIR"
  BASE_URL="http://localhost:8080"
fi

echo "[capture] Using base URL: $BASE_URL"
TUTORIAL_BASE_URL="$BASE_URL" npx playwright test e2e/tutorial-screenshots.spec.mjs

echo "[capture] Screenshots written to docs/tutorials/assets/screenshots/workflow"
