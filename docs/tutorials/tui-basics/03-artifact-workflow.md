# TUI Artifact Workflow

This workflow uses the current `commands propose/apply` model.

## Supported propose commands
- `assess_gaps`
- `generate_artifact` (requires `--artifact-name` and `--artifact-type`)
- `generate_plan`

## 1) Propose gap assessment

```bash
python apps/tui/main.py commands propose --project TODO-001 --command assess_gaps
```

## 2) Propose artifact generation

```bash
python apps/tui/main.py commands propose \
  --project TODO-001 \
  --command generate_artifact \
  --artifact-name "project-charter.md" \
  --artifact-type "project_charter"
```

## 3) Apply a proposal

```bash
python apps/tui/main.py commands apply --project TODO-001 --proposal <proposal-id>
```

## 4) List artifacts

```bash
python apps/tui/main.py artifacts list --project TODO-001
```

## 5) Read artifact content

```bash
python apps/tui/main.py artifacts get --project TODO-001 --path artifacts/project-charter.md
```

## Notes

- TUI currently supports proposal creation and apply operations.
- TUI currently supports artifact list/get operations.

---

**Last Updated:** 2026-02-15
