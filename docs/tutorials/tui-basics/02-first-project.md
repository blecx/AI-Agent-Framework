# TUI First Project

Create and inspect your first project with currently supported commands.

## Create project

```bash
python apps/tui/main.py projects create --key TODO-001 --name "Todo Application MVP"
```

## List projects

```bash
python apps/tui/main.py projects list
```

## Get project details + artifacts + last commit

```bash
python apps/tui/main.py projects get --key TODO-001
```

## Notes

- TUI currently supports project create/list/get only.
- Use API routes or repository tools for lifecycle actions outside current TUI scope.

---

**Last Updated:** 2026-02-16
