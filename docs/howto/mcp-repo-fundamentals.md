# MCP Repo Fundamentals (Git + Search + Filesystem)

This stack provides local/free MCP servers for repository fundamentals over Streamable HTTP:

- Git MCP: `http://127.0.0.1:3012/mcp`
- Search MCP: `http://127.0.0.1:3013/mcp`
- Filesystem MCP: `http://127.0.0.1:3014/mcp`

Safety constraints are enforced server-side for all path-based operations:

- deny `projectDocs/`
- deny `configs/llm.json`
- deny path traversal (`..`)
- deny repository-root escape (including symlink escape)

## Provided MCP tools

- Git MCP: `status`, `diff`, `log`, `show`, `branch current`, `branch list`, `blame`, staged-path helpers
- Search MCP: ripgrep-backed search/list (`rg`) with server-enforced exclusions
- Filesystem MCP: scoped read/write/list/mkdir/delete/move/copy with deny rules

The Search MCP always excludes:

- `projectDocs/**`
- `configs/llm.json`

even when querying from scope `.`.

## Start with Docker Compose

```bash
docker compose -f docker-compose.repo-fundamentals-mcp.yml up -d --build
```

## Endpoint reachability check

```bash
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3012/mcp
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3013/mcp
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3014/mcp
```

Expected for plain curl: `406`.

## Install at boot (systemd)

```bash
chmod +x scripts/install-repo-fundamentals-mcp-systemd.sh
./scripts/install-repo-fundamentals-mcp-systemd.sh
```

## VS Code MCP settings

Workspace settings wire these server entries:

- `mcp.servers.git.url = http://127.0.0.1:3012/mcp`
- `mcp.servers.search.url = http://127.0.0.1:3013/mcp`
- `mcp.servers.filesystem.url = http://127.0.0.1:3014/mcp`

## Full MCP smoke test

```bash
bash scripts/mcp_smoke_test.sh
```
