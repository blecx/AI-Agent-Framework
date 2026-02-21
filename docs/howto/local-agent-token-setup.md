# Local Token Setup for Agent Workflows (No Repo Secrets)

This guide shows how to run `scripts/work-issue.py` with a GitHub token **without storing real secrets in the repository**.

## What is already provided

- Local example env file: `.tmp/local-agent-env.example.sh`
- Local runner wrapper: `.tmp/run-work-issue-local.sh`

Both live in `.tmp/`, which is gitignored.

## Option A: Use your existing `gh` login (recommended)

If `gh auth status` shows you are logged in, the wrapper automatically uses `gh auth token` as fallback.

Run:

```bash
./.tmp/run-work-issue-local.sh 347 --dry-run
```

## Option B: Use a local env file (still not committed)

1. Create local-only env file:

```bash
cp .tmp/local-agent-env.example.sh .tmp/local-agent-env.sh
```

2. Edit `.tmp/local-agent-env.sh` and set one variable:

- `GITHUB_TOKEN=...` or
- `GH_TOKEN=...`

3. Run:

```bash
./.tmp/run-work-issue-local.sh 347 --dry-run
```

## Verification

Successful dry run should include:

- `✅ Agent initialized and ready`
- `✅ Dry run complete: initialization succeeded`

## Security notes

- Do **not** place real tokens in tracked files.
- Keep secrets only in your shell environment or `.tmp/local-agent-env.sh`.
- `.tmp/` is gitignored, so local token files are not committed.
