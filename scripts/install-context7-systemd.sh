#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_NAME="context7-mcp.service"
UNIT_PATH="/etc/systemd/system/${UNIT_NAME}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker command not found. Install Docker first."
  exit 1
fi

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemctl not found. This script requires systemd."
  exit 1
fi

sudo tee "${UNIT_PATH}" >/dev/null <<EOF
[Unit]
Description=Context7 MCP Docker Service
After=docker.service network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${ROOT_DIR}
ExecStart=/usr/bin/docker compose -f ${ROOT_DIR}/docker-compose.context7.yml up -d
ExecStop=/usr/bin/docker compose -f ${ROOT_DIR}/docker-compose.context7.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now "${UNIT_NAME}"

echo "Installed and started ${UNIT_NAME}."
echo "Check status with: sudo systemctl status ${UNIT_NAME}"