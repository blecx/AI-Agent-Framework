# PR Description Template

Use this prompt to help draft a comprehensive PR description that includes validation steps and traceability.

## Prompt

```
I need to create a PR description for the AI-Agent-Framework project.

Changes Summary: [DESCRIBE WHAT WAS CHANGED]

Related Issue: [ISSUE NUMBER AND LINK]

Please help me draft a complete PR description including:

1. **Title**: Clear, references issue (e.g., "Add JSON export endpoint (fixes #123)")

2. **Summary**: Brief description of what changed and why

3. **Changes Made**: Bullet list of specific changes
   - New files added
   - Modified files
   - Deleted files (if any)
   - Configuration changes
   - Dependency updates

4. **Related Issues**: Links with keywords
   - "Fixes #123" (auto-closes on merge)
   - "Related to #456"
   - "Depends on blecx/AI-Agent-Framework-Client#789"

5. **Testing Done**: What you verified works
   For AI-Agent-Framework backend:
   - Python environment setup
   - Linting results
   - API health check
   - Manual testing performed
   - Docker build (if applicable)

6. **Validation Steps** for reviewers:
   Copy-pasteable commands to verify the changes
   
   ```bash
   # Setup
   ./setup.sh && source .venv/bin/activate
   mkdir -p projectDocs
   
   # Run API
   cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
   
   # Test the changes
   [SPECIFIC COMMANDS]
   
   # Lint
   python -m black apps/api/
   python -m flake8 apps/api/
   ```

7. **Breaking Changes**: Call out any breaking changes (or note "None")

8. **Checklist**:
   - [ ] Code follows project conventions
   - [ ] Linting passes
   - [ ] Manual testing completed
   - [ ] No projectDocs/ or configs/llm.json committed
   - [ ] Documentation updated (if needed)
   - [ ] Cross-repo changes coordinated (if applicable)

Format as a GitHub PR description ready to copy-paste.
```

## Example Usage

**Input:**
```
Changes Summary: Added GET /api/projects/{id}/export endpoint that returns project artifacts as JSON
Related Issue: #123
```

**Expected Output:**
```markdown
## Add JSON export endpoint for project artifacts

Fixes #123

### Summary
Adds a new REST endpoint to export all project artifacts as structured JSON. This enables programmatic access to project data and supports the export feature.

### Changes Made
- Added `GET /api/projects/{id}/export` endpoint in `apps/api/routers/projects.py`
- Added `ProjectExportResponse` model in `apps/api/models.py`
- Added `get_all_artifacts()` method in `apps/api/services/git_manager.py`
- Updated OpenAPI documentation

**Files changed:**
- `apps/api/routers/projects.py` (+45 lines)
- `apps/api/models.py` (+12 lines)
- `apps/api/services/git_manager.py` (+23 lines)

### Related Issues
- Fixes #123 (Add JSON export endpoint)
- Related to blecx/AI-Agent-Framework-Client#45 (UI needs to consume this)

### Testing Done
✅ Python environment setup and activation
✅ Linting with black and flake8 (no issues)
✅ API starts successfully with PROJECT_DOCS_PATH set
✅ Health check returns healthy status
✅ Export endpoint returns 200 for existing projects
✅ Export endpoint returns 404 for missing projects
✅ JSON structure matches expected schema
✅ OpenAPI docs updated and accessible

### Validation Steps for Reviewers

```bash
# Setup environment
./setup.sh && source .venv/bin/activate
mkdir -p projectDocs

# Create a test project (if needed)
# [Add specific setup commands if needed]

# Run API
cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Test the new endpoint
curl http://localhost:8000/api/projects/TEST-001/export | jq .
# Should return JSON with project artifacts

# Test 404 handling
curl -i http://localhost:8000/api/projects/NONEXISTENT/export
# Should return 404

# Verify OpenAPI docs
# Visit http://localhost:8000/docs
# Check /api/projects/{id}/export endpoint is documented

# Run linting
python -m black apps/api/
python -m flake8 apps/api/
```

### Breaking Changes
None. This adds a new endpoint without modifying existing functionality.

### Checklist
- [x] Code follows project conventions (FastAPI patterns, Pydantic models)
- [x] Linting passes (black, flake8)
- [x] Manual testing completed (see Testing Done section)
- [x] No projectDocs/ or configs/llm.json committed (verified with git status)
- [x] Documentation updated (OpenAPI schema auto-generated)
- [x] Cross-repo changes coordinated (client team notified in #45)

### Notes for Reviewers
- This endpoint reads from projectDocs/ git repository
- Returns empty list if project has no artifacts yet
- Consider adding pagination in future for large projects
```

## Tips

- Use "Fixes #123" to auto-close issue on merge
- Be specific about what was tested
- Make validation steps easy to copy-paste
- Call out any tricky or non-obvious changes
- Mention performance impact if relevant
- Note any follow-up work needed
- Keep PRs small (prefer < 200 lines changed)
- Include screenshots for UI changes
- Link to related PRs in other repos
