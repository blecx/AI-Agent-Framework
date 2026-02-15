# GUI Commands and Proposals

This page reflects the current shipped Web UI behavior.

## Available command cards
- `assess_gaps`
- `generate_artifact`
- `generate_plan`

For `generate_artifact`, fill both parameters:
- `artifact_name`
- `artifact_type`

## Workflow
1. Open project in the web UI.
2. In **Commands** tab, pick a command card.
3. Submit proposal.
4. Review diff in modal.
5. Apply to commit changes.
6. Verify in **Artifacts** tab.

## URL consistency
- Docker web UI: `http://localhost:8080`
- Local dev web UI: `http://localhost:5173`

## TUI equivalent

```bash
python apps/tui/main.py commands propose --project TODO-001 --command assess_gaps
python apps/tui/main.py commands apply --project TODO-001 --proposal <proposal-id>
```

---

**Last Updated:** 2026-02-15
