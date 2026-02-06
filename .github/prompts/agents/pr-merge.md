# Agent: pr-merge

**Purpose:** Merge PR after validation, capture metrics, close linked issue, clean workspace.

**Inputs:**
- PR number (required)
- Linked issue number (optional, auto-detected from PR body)
- Optional: --admin flag to bypass CI (use when CI has pre-existing failures)

**Workflow:**

1. **Check PR state**
   ```bash
   gh pr view <PR> --json state,mergeable
   ```
   - **Early exit:** If already merged, skip to step 5 (cleanup)

2. **Check CI status** (skip if --admin flag)
   ```bash
   gh pr checks <PR> --required
   ```
   - If required checks passing: proceed
   - If failing: use --admin flag or wait for fixes

3. **Merge PR**
   ```bash
   gh pr merge <PR> --squash --delete-branch [--admin]
   ```
   - **Optimization:** Use --admin to bypass non-blocking CI waits
   - **Optimization:** --delete-branch in single command (no separate git branch -D)

4. **Extract and close linked issue**
   ```bash
   # Auto-detect from PR body
   ISSUE=$(gh pr view <PR> --json body | grep -oP '(?:Fixes|Closes|Resolves): #\K\d+' | head -1)
   
   # Close issue (will auto-close on merge, but add comment for traceability)
   if [ -n "$ISSUE" ]; then
     gh issue comment $ISSUE --body "✓ Resolved in #<PR> (commit $(git rev-parse HEAD))"
   fi
   ```

5. **Cleanup workspace** (MANDATORY)
   ```bash
   rm -f .tmp/pr-body-<issue-number>.md .tmp/issue-<issue-number>-*.md
   ls -la .tmp/*<issue-number>* 2>/dev/null || echo "✓ Cleanup verified"
   ```

6. **Update main**
   ```bash
   git switch main && git pull
   ```

**Success Criteria:** PR merged, branch deleted, issue closed, workspace cleaned, main updated.

**Optimization Notes:**
- No CI polling loops (check once, then merge or skip)
- Use --admin flag to bypass non-blocking waits
- Batch cleanup operations
- Early exit for already-merged PRs
- Auto-detect issue from PR body (no manual lookup)
