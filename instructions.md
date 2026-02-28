# Instructions

## Safe Chat Archive Workflow

Use the safe archive wrapper to avoid false "pending edits" warnings caused by
live `.tmp` log churn from `dev_stack_supervisor`.

- Script: `scripts/archive-goals-safe.sh`
- VS Code tasks:
  - `🗄️ Archive Goals (.tmp)`
  - `🗄️ Archive Goals (.tmp, move)`

### Behavior

1. Detect whether `dev_stack_supervisor` is running via `.tmp/dev-stack-supervisor.pid`.
2. If running, stop it temporarily.
3. Execute `scripts/archive-goals.sh` with the same arguments.
4. Restart `dev_stack_supervisor` automatically if it was running before.

### Why this matters

- `dev_stack_supervisor` continuously appends to `.tmp/dev-backend.log` and
  `.tmp/dev-frontend.log`.
- Some UI/archive flows treat this ongoing file mutation as "pending edits" even
  when git status is clean.
- The safe wrapper removes that race condition while preserving your dev workflow.

### Notes

- This does **not** change git-tracked files during archive.
- The Offline Docs index at `.tmp/mcp-offline-docs/docs_index.db` remains local
  and is intentionally kept between chats.
