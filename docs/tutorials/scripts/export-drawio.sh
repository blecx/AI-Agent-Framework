#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SRC_DIR="$ROOT_DIR/docs/tutorials/assets/diagrams/src"
OUT_DIR="$ROOT_DIR/docs/tutorials/assets/diagrams/generated"

mkdir -p "$OUT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required for draw.io export in this script" >&2
  exit 1
fi

for file in "$SRC_DIR"/*.drawio; do
  [ -e "$file" ] || continue
  echo "[drawio] Exporting $(basename "$file")"
  docker run --rm \
    -v "$ROOT_DIR:/data" \
    rlespinasse/drawio-desktop-headless:latest \
    -x -f svg -o "/data/docs/tutorials/assets/diagrams/generated" \
    "/data/${file#$ROOT_DIR/}"
done

echo "[drawio] SVG exports available under docs/tutorials/assets/diagrams/generated"
