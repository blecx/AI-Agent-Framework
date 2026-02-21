# MCP Bash Gateway (Issue #338)

This guide describes the policy-driven bash execution gateway for AI agents.

## Why this exists

Running arbitrary shell commands from autonomous agents is risky. The gateway
enforces:

- allowlisted scripts only
- profile-based policy (`ci`, `issue`, `docs`, `ops`, etc.)
- timeout boundaries
- dry-run-by-default behavior when configured
- persistent run audit logs

## Implemented tool contract

The `BashGatewayServer` currently exposes:

- `list_project_scripts(profile?)`
- `describe_script(profile, script_path)`
- `run_project_script(profile, script_path, args, dry_run, timeout_sec)`
- `get_script_run_log(run_id)`

## Current location

- `apps/mcp/bash_gateway/policy.py`
- `apps/mcp/bash_gateway/executor.py`
- `apps/mcp/bash_gateway/audit_store.py`
- `apps/mcp/bash_gateway/server.py`

## Example usage (Python)

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

## Next step

Wrap this server facade in a transport-level MCP server endpoint so external
agents can call these methods through MCP directly.
