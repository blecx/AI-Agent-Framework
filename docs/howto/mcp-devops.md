# MCP DevOps (Docker/Compose + Test Runner)

This stack provides local/free DevOps MCP servers over Streamable HTTP:

- Docker/Compose MCP: `http://127.0.0.1:3015/mcp`
- Test Runner MCP: `http://127.0.0.1:3016/mcp`

Both services are localhost-bound and write audited execution logs under `.tmp/`.

## Start with Docker Compose

```bash
docker compose -f docker-compose.mcp-devops.yml up -d --build
```

## Endpoint reachability check

```bash
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3015/mcp
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3016/mcp
```

Expected for plain curl: `406`.

## Start at boot (systemd)

Install only DevOps MCP at boot:

```bash
chmod +x scripts/install-devops-mcp-systemd.sh
./scripts/install-devops-mcp-systemd.sh
```

Install all MCP services (Context7, Bash Gateway, Repo Fundamentals, DevOps, Offline Docs):

```bash
chmod +x scripts/install-all-mcp-systemd.sh
./scripts/install-all-mcp-systemd.sh
```

Verify:

```bash
sudo systemctl is-enabled devops-mcp.service
sudo systemctl is-active devops-mcp.service
```

## Docker/Compose MCP scope

Only allowlisted compose targets are exposed (for example `docker-compose.yml`,
`docker-compose.repo-fundamentals-mcp.yml`, `docker-compose.mcp-devops.yml`).
The server rejects compose paths that escape the workspace or target protected
paths.

Audit logs:

- `.tmp/mcp-docker-compose/<run_id>.json`

## Test Runner MCP profiles

Deterministic profiles mirror project tasks:

- `backend.format_lint`
- `backend.tests`
- `backend.tests_quick`
- `frontend.lint`
- `frontend.build`

Audit logs:

- `.tmp/mcp-test-runner/<run_id>.json`

## VS Code MCP settings

Workspace settings include:

- `mcp.servers.dockerCompose.url = http://127.0.0.1:3015/mcp`
- `mcp.servers.testRunner.url = http://127.0.0.1:3016/mcp`

## Smoke test

Use the compose-based smoke test:

```bash
bash scripts/mcp_smoke_test_compose.sh
```
