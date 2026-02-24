# Context7 Setup for VS Code + Docker (Persistent)

This guide installs Context7 for VS Code, runs a local Context7 MCP endpoint in Docker, and enables host boot startup.

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

Expected: HTTP response from MCP endpoint (typically `406 Not Acceptable` for plain curl, which indicates the MCP endpoint is live).

## 4) Enable Startup at Host Boot (systemd)

```bash
chmod +x scripts/install-context7-systemd.sh
./scripts/install-context7-systemd.sh
```

Check status:

```bash
sudo systemctl status context7-mcp.service
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
Always use Context7 for library/API docs, setup/configuration steps, and code generation where external framework behavior matters.
Use repository conventions for architecture and internal implementation details.
```