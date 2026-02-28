# GitHub Ops MCP (PR / Issue / CI)

This repository includes a dedicated MCP server for GitHub operations (PRs, issues, checks, workflow runs). It exists to avoid running host-dependent scripts (e.g. `gh`/`jq`) via the Bash Gateway container.

## What it provides

The `githubOps` MCP server exposes explicit tools backed by the GitHub CLI (`gh`) inside its own container.

Typical operations:

- View issue/PR details
- Fetch PR body / changed files
- Summarize PR checks and watch checks until completion
- List/cancel workflow runs
- Merge PRs (squash)
- Close issues

## Security model

- Localhost-only binding (default): `127.0.0.1:3018`
- Server-side repo allowlist via `GITHUB_OPS_ALLOWED_REPOS` (CSV)
- Audit logs written under `.tmp/mcp-github-ops/`
- Best-effort secret redaction for tokens in audit records

## Running with Docker Compose

1) Provide a GitHub token (recommended):

- `GH_TOKEN` (preferred by `gh`), or
- `GITHUB_TOKEN`

2) Start the service:

- `docker compose -f docker-compose.mcp-github-ops.yml up -d --build`

3) Endpoint:

- `http://127.0.0.1:3018/mcp`

## Running via systemd

Install and start:

- `scripts/install-github-ops-mcp-systemd.sh`

Token + allowlist overrides live in:

- `/etc/default/github-ops-mcp`

## VS Code MCP wiring

The workspace MCP configuration registers:

- server name: `githubOps`
- url: `http://127.0.0.1:3018/mcp`

See `.vscode/settings.json`.
