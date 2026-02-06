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

8. **Create PR**
   ```bash
   # Use PR template from recent successful PR
   gh pr view <recent-pr> --json body --jq .body | head -60 > .tmp/pr-template.md
   
   # Create PR body from template
   cat > .tmp/pr-body-<issue-number>.md <<EOF
   ... (fill template with issue details)
   EOF
   
   gh pr create --title "feat: <title> (Issue #<issue-number>)" --body-file .tmp/pr-body-<issue-number>.md
   ```

9. **CI validation** (optional, check once)
   ```bash
   sleep 30  # Wait for CI to start
   gh pr checks <PR>  # Single check, no --watch
   ```
   - **Optimization:** Don't poll CI in loops
   - **Early exit:** If checks passing, done. If failing, report and exit.

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
