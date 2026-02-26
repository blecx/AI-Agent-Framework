#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/docker-compose.context7.yml"
UNIT_NAME="context7-mcp.service"
UNIT_PATH="/etc/systemd/system/${UNIT_NAME}"
DOCKER_BIN="$(command -v docker || true)"
SYSTEMCTL_BIN="$(command -v systemctl || true)"
SUDO_BIN="$(command -v sudo || true)"

if [[ -z "${DOCKER_BIN}" ]]; then
  echo "docker command not found. Install Docker first."
  exit 1
fi

if [[ -z "${SYSTEMCTL_BIN}" ]]; then
  echo "systemctl not found. This script requires systemd."
  exit 1
fi

if [[ -z "${SUDO_BIN}" ]]; then
  echo "sudo command not found. This script requires sudo for unit installation."
  exit 1
fi

if [[ ! -d /run/systemd/system ]]; then
  echo "systemd does not appear to be active on this host."
  exit 1
fi

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "Compose file not found: ${COMPOSE_FILE}"
  exit 1
fi

if ! "${DOCKER_BIN}" compose version >/dev/null 2>&1; then
  echo "docker compose plugin not found. Install Docker Compose v2 support."
  exit 1
fi

sudo tee "${UNIT_PATH}" >/dev/null <<EOF
[Unit]
Description=Context7 MCP Docker Service
After=docker.service network-online.target
Wants=network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${ROOT_DIR}
ExecStart=${DOCKER_BIN} compose -f ${COMPOSE_FILE} up -d --remove-orphans
ExecStop=${DOCKER_BIN} compose -f ${COMPOSE_FILE} down
ExecReload=${DOCKER_BIN} compose -f ${COMPOSE_FILE} up -d --remove-orphans
TimeoutStartSec=120
TimeoutStopSec=120
UMask=0077
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

sudo chmod 0644 "${UNIT_PATH}"
sudo systemctl daemon-reload
sudo systemctl enable --now "${UNIT_NAME}"

echo "Installed and started ${UNIT_NAME}."
echo "Check status with: sudo systemctl status ${UNIT_NAME}"
echo "Enabled: $(sudo systemctl is-enabled "${UNIT_NAME}")"
echo "Active: $(sudo systemctl is-active "${UNIT_NAME}")"