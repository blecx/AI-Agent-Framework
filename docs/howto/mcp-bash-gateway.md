# MCP Bash Gateway (Local Docker MCP Server)

This guide describes the policy-driven bash execution gateway for AI agents,
now exposed as a real MCP Streamable HTTP server.

## Why this exists

Running arbitrary shell commands from autonomous agents is risky. The gateway
enforces:

- allowlisted scripts only
- profile-based policy (`ci`, `issue`, `docs`, `ops`, etc.)
- timeout boundaries
- dry-run-by-default behavior when configured
- persistent run audit logs

If another domain-specific MCP server can solve the same task, that server must
be chosen first per [MCP Tool Arbitration Hard Rules](mcp-routing-rules.md).

## Implemented MCP tools

The `BashGatewayServer` currently exposes:

- `list_project_scripts(profile?)`
- `describe_script(profile, script_path)`
- `run_project_script(profile, script_path, args, dry_run, timeout_sec)`
- `get_script_run_log(run_id)`

The transport-level MCP server exposes these same operations as MCP tools at
`http://127.0.0.1:3011/mcp`.

## Current location

- `apps/mcp/bash_gateway/policy.py`
- `apps/mcp/bash_gateway/executor.py`
- `apps/mcp/bash_gateway/audit_store.py`
- `apps/mcp/bash_gateway/server.py`
- `apps/mcp/bash_gateway/mcp_server.py`
- `configs/bash_gateway_policy.default.yml`
- `docker/mcp-bash-gateway/Dockerfile`
- `docker-compose.mcp-bash-gateway.yml`

## Start local MCP server (Docker)

From repository root:

```bash
docker compose -f docker-compose.mcp-bash-gateway.yml up -d --build
```

Validate endpoint:

```bash
curl -sS -i http://127.0.0.1:3011/mcp | head
```

Expected: MCP endpoint HTTP response (for plain curl, `406 Not Acceptable` is a
common healthy response).

## Enable host boot startup (systemd)

```bash
chmod +x scripts/install-bash-gateway-mcp-systemd.sh
./scripts/install-bash-gateway-mcp-systemd.sh
```

This installs and enables `bash-gateway-mcp.service` so the container starts
automatically at host boot.

Verify:

```bash
sudo systemctl is-enabled bash-gateway-mcp.service
sudo systemctl is-active bash-gateway-mcp.service
docker ps --filter name=bash-gateway-mcp
```

## VS Code MCP settings

Workspace settings include:

- `mcp.servers.bashGateway.url = http://127.0.0.1:3011/mcp`

Reload VS Code window after starting the container.

## Example usage (Python facade)

```python
from pathlib import Path
from apps.mcp.bash_gateway.policy import BashGatewayPolicy
from apps.mcp.bash_gateway.server import BashGatewayServer

policy = BashGatewayPolicy.from_dict(
    {
        "profiles": {
            "issue": {
                "scripts": ["scripts/validate_prompts.sh"],
                "default_timeout_sec": 120,
                "max_timeout_sec": 300,
                "default_dry_run": True,
            }
        }
    }
)

server = BashGatewayServer(repo_root=Path("."), policy=policy)
print(server.list_project_scripts("issue"))
result = server.run_project_script(
    profile="issue",
    script_path="scripts/validate_prompts.sh",
)
print(result["run_id"], result["status"])
```

## Audit format

Each run stores a JSON file in `.tmp/agent-script-runs/<run_id>.json` including:

- script path
- profile
- timeout/dry-run
- status/exit code
- output
- duration
- timestamp

## Policy and safety defaults

- Scripts are allowlisted by profile in `configs/bash_gateway_policy.default.yml`
- Dry-run defaults to `true` in all default profiles
- Timeout is bounded by profile max timeout
- Path traversal and non-allowlisted scripts are rejected
