# Context7 Setup for VS Code + Docker (Persistent)

This guide installs Context7 for VS Code, runs a local Context7 MCP endpoint in
Docker, and enables host boot startup.

## 1) Install VS Code Extension

```bash
code --install-extension upstash.context7-mcp
```

## 2) Configure API Key (recommended)

Context7 works without a key, but rate limits are better with one.

```bash
echo 'export CONTEXT7_API_KEY="YOUR_KEY_HERE"' >> ~/.bashrc
source ~/.bashrc
```

## 3) Start Local Context7 MCP via Docker

From repository root:

```bash
docker compose -f docker-compose.context7.yml up -d --build
```

Validate endpoint:

```bash
curl -sS -i http://127.0.0.1:3010/mcp | head
```

Expected: HTTP response from MCP endpoint (typically `406 Not Acceptable` for
plain curl, which indicates the MCP endpoint is live).

## 4) Enable Startup at Host Boot (systemd)

```bash
chmod +x scripts/install-context7-systemd.sh
./scripts/install-context7-systemd.sh
```

The installer creates and uses `/etc/default/context7-mcp` for optional
`CONTEXT7_API_KEY` persistence at boot.

If needed, edit it manually:

```bash
sudoedit /etc/default/context7-mcp
```

Check status:

```bash
sudo systemctl status context7-mcp.service
sudo systemctl cat context7-mcp.service | grep EnvironmentFile
docker ps --filter name=context7-mcp
```

## 5) VS Code MCP Configuration

Workspace config is pre-added in `.vscode/settings.json`:

- MCP server URL: `http://127.0.0.1:3010/mcp`
- Header: `CONTEXT7_API_KEY` from `${env:CONTEXT7_API_KEY}`

Reload VS Code window after setup:

- Command Palette → `Developer: Reload Window`

## Best-Practice Prompt Rule

Add this in your team prompt conventions:

```txt
Always use Context7 for library/API docs, setup/configuration steps, and code
generation where external framework behavior matters.
Use repository conventions for architecture and internal implementation details.
```

## 6) Reproducible Validation Checklist

Run these commands from repository root and compare with expected outcomes.

```bash
# Start / rebuild local MCP endpoint
docker compose -f docker-compose.context7.yml up -d --build

# Check MCP endpoint is reachable (406 for plain curl is expected)
curl -sS -i http://127.0.0.1:3010/mcp | head -n 14

# Verify container is up and restart policy applies
docker compose -f docker-compose.context7.yml ps context7
docker inspect -f '{{ .HostConfig.RestartPolicy.Name }}' context7-mcp

# Verify boot persistence after systemd install
systemctl is-enabled context7-mcp.service
systemctl is-active context7-mcp.service
sudo systemctl cat context7-mcp.service | grep EnvironmentFile
```

Expected outcomes:

- `curl` output includes an HTTP status line (typically `406 Not Acceptable`).
- `docker compose ... ps context7` shows service/container as running.
- `docker inspect ... context7-mcp` returns `unless-stopped`.
- `systemctl is-enabled` returns `enabled`.
- `systemctl is-active` returns `active`.
- `systemctl cat ... | grep EnvironmentFile` shows `/etc/default/context7-mcp`.
