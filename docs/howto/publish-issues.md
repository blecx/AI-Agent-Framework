# Publish planning issues

Use the deterministic publisher to create/update issue mappings from `planning/issues/*.yml`.

## Prerequisites

- GitHub CLI authenticated (`gh auth status`)
- Valid planning specs (`./scripts/validate_issue_specs.sh`)

## Dry run (safe default)

- `./scripts/publish_issues.py --paths "planning/issues/*.yml"`

This prints what would be published and performs duplicate checks by title.

## Apply mode (creates issues)

- `./scripts/publish_issues.py --paths "planning/issues/*.yml" --apply`

Results are persisted to:

- `planning/issues/.published-map.json`

The mapping stores source ID, repository, issue URL, and issue number for idempotent reruns.

## Optional repo filter

- `./scripts/publish_issues.py --repo blecx/AI-Agent-Framework --apply`
- `./scripts/publish_issues.py --repo blecx/AI-Agent-Framework-Client --apply`

## Failure recovery

- Re-run in dry-run mode first.
- If a run partially succeeds, rerun with `--apply`; existing mapping entries are skipped.
- Duplicate title detection maps to existing issues instead of creating duplicates.
