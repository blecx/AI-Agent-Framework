# TUI + GUI Hybrid Workflows

Use each interface where it is strongest.

## Recommended split
- **TUI**: quick command execution and artifact reads.
- **GUI**: visual proposal review and artifact browsing.
- **REST**: RAID and workflow state management.

## Example hybrid flow
1. TUI create project:
   - `python apps/tui/main.py projects create --key HYB-001 --name "Hybrid Demo"`
2. TUI propose/apply:
   - `python apps/tui/main.py commands propose --project HYB-001 --command generate_plan`
   - `python apps/tui/main.py commands apply --project HYB-001 --proposal <proposal-id>`
3. GUI verify in **Artifacts** tab.
4. REST update workflow state:
   - `PATCH /projects/HYB-001/workflow/state`
5. REST manage RAID entries:
   - `/projects/HYB-001/raid`

## URLs
- Docker UI: `http://localhost:8080`
- Local dev UI: `http://localhost:5173`

---

**Last Updated:** 2026-02-16
