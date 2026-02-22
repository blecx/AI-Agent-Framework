# Agent: close-issue

**Purpose:** Close a GitHub issue with a consistent resolution comment and traceability to the merged PR/commit.

**Inputs:**
- Issue number (required)
- PR number or commit SHA (optional but recommended)

**Workflow:**

1. **Validate issue exists and is open**
   ```bash
   gh issue view <issue-number> --json state,title
   ```
   - **Early exit:** If already closed, log "Already closed" and exit 0

2. **Construct resolution comment**
   - If PR provided: "Resolved in #<PR>"
   - If commit SHA: "Resolved in <commit>"
   - Else: "Resolved"

3. **Close issue**
   ```bash
   gh issue close <issue-number> --comment "<resolution-comment>"
   ```

   - For UI/UX-affecting issues, ensure closure comment references completed `blecs-ux-authority` consultation outcome.

4. **Verify closure**
   ```bash
   gh issue view <issue-number> --json state | grep -q "CLOSED" && echo "✓ Issue closed" || echo "✗ Failed"
   ```

**Success Criteria:** Issue state = CLOSED with resolution comment posted.

**Optimization Notes:**
- Single state check (no polling)
- Early exit for already-closed issues
- No redundant validations
- Use `.github/prompts/modules/ux/delegation-policy.md` for UX ownership rules
