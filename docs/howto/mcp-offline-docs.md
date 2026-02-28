# MCP Offline Docs Index (Local-Only Grounding)

This MCP server provides Context7-like docs grounding with no network dependency
by indexing local repository docs into a SQLite full-text index.

- Offline Docs MCP: `http://127.0.0.1:3017/mcp`

## Start with Docker Compose

```bash
docker compose -f docker-compose.mcp-offline-docs.yml up -d --build
```

## Endpoint check

```bash
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3017/mcp
```

Expected for plain curl: `406`.

## Boot-time startup (systemd)

Install only Offline Docs MCP:

```bash
chmod +x scripts/install-offline-docs-mcp-systemd.sh
./scripts/install-offline-docs-mcp-systemd.sh
```

Install all MCP services:

```bash
chmod +x scripts/install-all-mcp-systemd.sh
./scripts/install-all-mcp-systemd.sh
```

## Indexed sources

By default the index includes:

- `docs/`
- `README.md`
- `QUICKSTART.md`
- `templates/`

Override via env file `/etc/default/offline-docs-mcp`:

```bash
OFFLINE_DOCS_INDEX_SOURCES=docs,README.md,QUICKSTART.md,templates
OFFLINE_DOCS_INDEX_DB=/workspace/.tmp/mcp-offline-docs/docs_index.db
```

## Core tools

- `offline_docs_index_rebuild`
- `offline_docs_index_stats`
- `offline_docs_search`
- `offline_docs_read`

## Index refresh policy

- Keep the index DB local in `.tmp/mcp-offline-docs/docs_index.db` (never commit).
- Rebuild is change-driven and triggered when indexed sources change (`docs/`, `templates/`, or configured source files).
- Boot-time rebuild is not required.
- Use `offline_docs_index_rebuild` only when you want to force a manual refresh.

## Validation

```bash
python3 scripts/check_mcp_connections.py
bash scripts/mcp_smoke_test.sh
```
