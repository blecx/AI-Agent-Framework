# PR Review Rubric (AI-Agent-Framework)

Use this rubric for both human and agent-based PR reviews.

## Inputs

- PR description (goal, acceptance criteria, validation steps)
- Diff / changed files list
- CI output (if available)

## Required output format

1. Summary (2-4 bullets)
2. Acceptance Criteria Verification
   - AC1: pass/fail + evidence (file/lines)
   - AC2: pass/fail + evidence
3. Repo Standards & Safety Checks
   - `projectDocs/` not committed: pass/fail
   - `configs/llm.json` not committed: pass/fail
   - Router/service separation: pass/fail + notes
   - Pydantic models used for API contracts: pass/fail + notes
4. Correctness / Edge Cases
   - potential bugs, error handling, status codes
5. Tests
   - tests updated/added? gaps?
6. UX / Navigation Compliance (for UI-affecting diffs)
   - `blecs-ux-authority` consulted: pass/fail + evidence
   - responsive/mobile checks included: pass/fail + evidence
   - navigation/grouping quality: pass/fail + notes
7. Breaking Changes / Client Impact
   - requires client repo change? yes/no + details
8. Recommendation
   - APPROVE / REQUEST CHANGES
   - required changes (max 5), ordered by severity

## Review rules

- Be strict about acceptance criteria and evidence.
- Call out missing validation steps.
- Prefer small diffs (<200 LOC) and one issue per PR.
- If behavior changes without tests, request tests or justification.
