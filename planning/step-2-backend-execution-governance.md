# Step 2 Backend Execution Governance

This document captures the governance model for the Step 2 backend issue track in `blecx/AI-Agent-Framework`.

## Tracker

- Primary tracker issue: https://github.com/blecx/AI-Agent-Framework/issues/623

## Ordered Queue (strict)

1. #613 — Step 2.01 (closed)
2. #614 — Step 2.02
3. #615 — Step 2.03
4. #616 — Step 2.04
5. #617 — Step 2.05
6. #618 — Step 2.06
7. #619 — Step 2.07
8. #620 — Step 2.08
9. #621 — Step 2.09
10. #622 — Step 2.17

## Status Labels

- `status:ready`: exactly one issue that can be actively worked
- `status:blocked`: all queued issues not yet unblocked
- `track:step2-backend`: all Step 2 backend issues and tracker

## Current State

- `#614` is labeled `status:ready`
- `#615`–`#622` are labeled `status:blocked`
- `#613` is already closed

## Operational Rule

When the current `status:ready` issue closes:

1. Remove `status:blocked` from the next issue in the ordered queue
2. Add `status:ready` to that next issue
3. Keep all remaining future issues as `status:blocked`
4. Update tracker checklist in issue #623

## Automation

Use the queue helper to enforce labels and tracker consistency:

- Dry run (no writes):
	- `./step2-backend-queue --dry-run --sync-tracker`
- Apply changes:
	- `./step2-backend-queue --apply --sync-tracker`

The command enforces:

- exactly one open issue with `status:ready` (first open in queue)
- all later open queue issues as `status:blocked`
- `track:step2-backend` on all queue issues and tracker #623
- checklist sync in tracker #623 based on real issue open/closed state

## Required Quality Gates per Issue

- Respect issue body acceptance criteria
- Run testing commands from issue body before PR
- Keep issue/PR traceability (`Fixes #<issue>`) and evidence in PR description

## Non-Goals

- This governance does not implement issue code changes
- This governance does not bypass CI or review requirements
