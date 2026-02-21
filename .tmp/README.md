# .tmp Workspace Scratch Directory

This directory is intentionally kept in the repository as a safe, local scratch space for agent/workflow artifacts.

## Purpose

Use `.tmp/` for temporary files such as:
- Draft PR bodies
- Issue-close payload JSON files
- Validation/check outputs
- Short-lived workflow metrics

## Rules

- Keep secrets out of all files.
- Treat files as disposable; clean regularly.
- Prefer `.tmp/` over system `/tmp` for repo-local workflows.
- Keep this directory mostly empty between runs.

## Cleanup

Typical cleanup command:

```bash
find .tmp -mindepth 1 -maxdepth 1 ! -name README.md -exec rm -rf {} +
```
