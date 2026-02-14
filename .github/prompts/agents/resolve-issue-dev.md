# Agent: resolve-issue-dev

**Purpose:** Implement and validate a solution for a GitHub issue following DDD architecture and workflow standards.

**Inputs:**
- Issue number (required)
- Optional: --plan flag to generate implementation plan first

**Priority Order (MANDATORY):**
1. **Backend/TUI/CLI issues** (blecx/AI-Agent-Framework) - lowest issue number first
2. **Client/UX issues** (blecx/AI-Agent-Framework-Client) - only after backend complete

**Workflow:**

1. **Select next issue** (if not specified)
   ```bash
   # Backend first (priority 1)
   gh issue list --repo blecx/AI-Agent-Framework --state open --json number,title --jq 'sort_by(.number) | .[0]'
   
   # Client second (priority 2) - only if backend has no open issues
   gh issue list --repo blecx/AI-Agent-Framework-Client --state open --json number,title --jq 'sort_by(.number) | .[0]'
   ```

2. **Fetch issue details** (single call, no loops)
   ```bash
   gh issue view <issue-number> --json title,body,labels
   ```

3. **Create feature branch**
   ```bash
   git switch -c feature/issue-<issue-number>-<slug>
   ```
   - **Early exit:** If branch exists, prompt to reuse or abort

4. **Generate plan** (optional, for M/L size issues)
   - Use DDD patterns: domain → service → router layers
   - Identify files to modify/create
   - List validation steps
   - Save to `.tmp/issue-<issue-number>-plan.md`

5. **Implement solution**
   - Follow DDD architecture (domain/ → services/ → routers/)
   - Keep files small (< 200 lines target)
   - Use relative imports in backend
   - Add docstrings to public functions
   - **Optimization:** Batch file creation/edits, avoid sequential creates

6. **Validate locally** (run once per implementation, not repeatedly)
   ```bash
   # Backend validation (single pass)
   source .venv/bin/activate
   python -m black apps/api/
   python -m flake8 apps/api/ --max-line-length=100
   
   # API health check (quick validation, no extended runs)
   cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload &
   sleep 3
   curl http://localhost:8000/health
   kill %1
   ```
   - **Optimization:** Run tests only if code changed since last validation
   - **Optimization:** Skip re-running linting if no Python files changed

7. **Commit and push** (batch operations)
   ```bash
   git add -A && git commit -m "feat: <title from issue>

Fixes #<issue-number>" && git push -u origin HEAD
   ```

8. **Create PR** (with template compliance)
   
   a. **Learn template format from recent successful PR**:

   ```bash
   # Get exact template format from recent merged PR
   gh pr list --state merged --limit 5 --json number,title
   gh pr view <recent-pr-number> --json body --jq .body | head -80 > .tmp/pr-template-ref.md
   ```

   b. **Create PR body with ALL required sections**:

   ```bash
   cat > .tmp/pr-body-<issue-number>.md <<'EOF'
   # Summary
   
   [2-6 sentence description of what changed and why]
   
   ## Goal / Acceptance Criteria (required)
   
   - [x] AC1: [Copy from issue, mark complete]
   - [x] AC2: [Copy from issue, mark complete]
   - [x] AC3: [Copy from issue, mark complete]
   
   ## Issue / Tracking Link (required)
   
   Fixes: #<issue-number>
   
   ## Validation (required)
   
   ### Automated checks
   
   - [x] Lint passes (attach output or CI link):
     - Command(s): `npm run lint` (or `black`/`flake8`)
     - Evidence (CI link or pasted summary): [PASTE ACTUAL OUTPUT]
   - [x] Build passes (attach output or CI link):
     - Command(s): `npm run build` (or backend commands)
     - Evidence (CI link or pasted summary): [PASTE ACTUAL OUTPUT]
   - [x] Tests pass (if applicable):
     - Command(s): `npm test -- --run` (or `pytest`)
     - Evidence (CI link or pasted summary): [PASTE ACTUAL OUTPUT]
   
   ### Manual test evidence (required)
   
   - [x] Manual test entry #1
     - Scenario: [Describe what was tested]
     - Steps:
       1. [Step 1]
       2. [Step 2]
       3. [Step 3]
     - Expected result: [What should happen]
     - Actual result / Evidence: [Screenshots, logs, or terminal output]
   
   ## Cross-repo / Downstream impact (always include)
   
   - Related repos/services impacted: [List or "None"]
   - Required coordinated releases/PRs: [List or "None"]
   - Follow-up issues/PRs needed: [List or "None"]
   EOF
   ```

   c. **Create PR**:

   ```bash
   gh pr create --title "feat: <title> (Issue #<issue-number>)" --body-file .tmp/pr-body-<issue-number>.md
   ```

   d. **Key principle: Create first, fix if needed**

- Don't block on potential template issues
- Let CI validate the template
- Fix and re-trigger if CI catches missing sections
- This maintains momentum while ensuring quality

1. **CI validation** (check once, fix if needed)

   ```bash
   sleep 30  # Wait for CI to start
   gh pr checks <PR>  # Check status
   ```

   **If CI fails on PR template validation:**

   a. Get CI logs to identify missing sections:

   ```bash
   # Find the failed run and get logs
   gh run list --workflow=ci.yml --limit 3
   gh run view <RUN_ID> --log-failed | grep "MISSING\|required"
   ```

   b. Fix PR body with missing sections:

   ```bash
   # Update the PR body file with correct sections
   cat > .tmp/pr-body-<issue-number>.md <<'EOF'
   [... corrected body with ALL required sections ...]
   EOF
   ```

   c. Update PR via REST API (avoids deprecated GraphQL):

   ```bash
   gh api -X PATCH repos/<owner>/<repo>/pulls/<PR_NUMBER> --field body=@.tmp/pr-body-<issue-number>.md
   ```

   d. **CRITICAL: Trigger fresh CI run** (template updates don't auto-trigger):

   ```bash
   git commit --allow-empty -m "chore: trigger CI re-run with updated PR description"
   git push
   ```

   e. Wait and verify fix:

   ```bash
   sleep 30
   gh pr checks <PR>
   ```

   **If checks pass:** PR is ready for review/merge
   **If checks still fail:** Review logs and repeat steps b-e with corrections

**Success Criteria:** PR created, locally validated, CI checks initiated.

**Optimization Notes:**

- Priority order ensures backend-first dependency management
- Single issue fetch (no repeated API calls)
- Batch git operations (add + commit + push in one line)
- Validate once (not in loops)
- Skip redundant work (tests when no code changed)
- No CI polling (check once, then exit)
- Early exit conditions at every decision point

**Architecture Requirements:**

- Backend: domain/ → services/ → routers/ (DDD)
- Frontend: domain clients → components (SRP)
- File size targets: < 200 lines per file
- Use relative imports in backend
