# Tutorial Refresh Completion Record (2026-02-15)

## Outcome

Tutorial documentation was aligned to the currently shipped surfaces across TUI, Web UI, and REST API.

## Completed scope

- Updated tutorial files in `docs/tutorials/` to reflect current command and endpoint behavior.
- Removed or replaced stale instructions for unsupported CLI paths.
- Standardized environment URL for Docker web UI: `http://localhost:8080`
- Standardized environment URL for local dev web UI: `http://localhost:5173`

## Final command-surface baseline

### TUI

- `projects`: `create`, `list`, `get`
- `commands`: `propose`, `apply`
- `artifacts`: `list`, `get`
- `config`
- `health`

### Propose command choices

- `assess_gaps`
- `generate_artifact` (with required artifact parameters)
- `generate_plan`

### REST guidance

- RAID and workflow operations are documented via REST endpoints, including legacy and `/api/v1` forms.

## Verification summary

- Tutorial content no longer instructs deprecated direct CLI groups for RAID/workflow.
- Tutorial examples follow the `commands propose/apply` model.
- Touched tutorial files were refreshed with the current timestamp conventions where applicable.

## Traceability

- See GitHub issues created for changed tutorial files in this refresh cycle.

---

**Last Updated:** 2026-02-15
