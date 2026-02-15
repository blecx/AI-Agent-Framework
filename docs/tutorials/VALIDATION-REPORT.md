# Tutorial Validation Report (Post-Refresh)

**Date:** 2026-02-16  
**Scope:** Documentation refresh verification for `docs/tutorials/**`

## Summary

The tutorial set was refreshed to match the currently shipped surfaces:

- TUI command groups: `projects`, `commands`, `artifacts`, `config`, `health`
- TUI proposal flow: `commands propose` / `commands apply`
- RAID and workflow operations documented via REST endpoints
- Web URLs normalized for Docker and local development

## Verification outcomes

- Stale direct CLI usage for unsupported groups was removed from tutorial guidance.
- Tutorial examples now align with currently supported command and endpoint patterns.
- Shared setup and troubleshooting guidance was updated to reduce command-surface confusion.

## Traceability

Per-file issues were created for changed tutorial files as part of the plan/issue/PR loop in this refresh cycle.

## Notes

This report supersedes older historical validation snapshots that no longer reflect current behavior after the 2026-02-16 refresh.

---

**Last Updated:** 2026-02-16
