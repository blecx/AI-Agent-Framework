# Issue Drafting Template

Use this prompt to help draft a well-structured implementation issue following best practices.

## Prompt

```
I need to create an implementation issue for the AI-Agent-Framework project.

Issue Context: [DESCRIBE THE WORK TO BE DONE]

Related Feature/Plan: [LINK TO FEATURE SPEC OR PARENT ISSUE IF APPLICABLE]

Please help me draft a complete issue including:

1. **Title**: Clear, actionable, starts with verb (e.g., "Add", "Fix", "Update")

2. **Description** with:
   - Context: Why is this needed?
   - Requirements: What needs to be done?
   - Technical approach: How should it be implemented?
   - Related issues/PRs: Links to dependencies

3. **Acceptance Criteria**: Specific, testable conditions that must be met
   - Use checklist format (- [ ] criterion)
   - Include both functional and non-functional criteria
   - Consider edge cases and error handling

4. **Validation Steps**: Commands to verify the changes work
   For AI-Agent-Framework backend:
   - Python environment setup
   - Linting (black, flake8)
   - API health check
   - Manual testing steps
   - Docker build verification (if applicable)

5. **Implementation Notes**:
   - Files likely to change
   - Key components to modify
   - Potential gotchas or tricky areas
   - References to similar existing code

6. **Docs Grounding (MCP + Context7)**:
   - List framework/library versions in scope (e.g., FastAPI 0.109.1, Pydantic 2.5.3)
   - Require Context7-backed doc retrieval for API/SDK behavior questions
   - Specify explicitly: “Use repo conventions for architecture and internal implementation details; use Context7 for external API/library correctness”
   - Include a short note for any unresolved version ambiguity

7. **Estimated Size**: S (< 50 lines) / M (50-200 lines) / L (> 200 lines)

Format as a GitHub issue ready to copy-paste.
```

## Example Usage

**Input:**
```
Issue Context: Add a new /api/projects/{id}/export endpoint that returns project artifacts as JSON
Related Feature/Plan: Export feature #123
```

**Expected Output:**
```markdown
## Title
Add JSON export endpoint for project artifacts

## Description
Users need to export project artifacts programmatically. This issue adds a REST endpoint to retrieve all artifacts for a project in JSON format.

### Context
Part of the export feature (#123). This backend endpoint will be consumed by the UI export functionality.

### Requirements
- Add GET /api/projects/{id}/export endpoint
- Return all artifacts as structured JSON
- Include metadata (project info, timestamps)
- Handle missing project gracefully (404)

### Related
- Parent: #123 (Export Feature)
- Depends on: blecx/AI-Agent-Framework-Client#45 (UI export button)

## Acceptance Criteria
- [ ] Endpoint returns 200 with JSON on success
- [ ] Returns 404 if project doesn't exist
- [ ] JSON includes all artifacts from projectDocs/
- [ ] Response includes project metadata
- [ ] Endpoint documented in OpenAPI schema
- [ ] No changes to existing endpoints

## Validation Steps
```bash
# Setup
./setup.sh && source .venv/bin/activate
mkdir -p projectDocs

# Run API
cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Test endpoint
curl http://localhost:8000/api/projects/TEST-001/export
# Should return JSON with artifacts

# Verify OpenAPI docs
# Visit http://localhost:8000/docs
# Check new endpoint is documented

# Lint
python -m black apps/api/
python -m flake8 apps/api/
```

## Docs Grounding (MCP + Context7)
- Libraries in scope: FastAPI 0.109.1, Pydantic 2.5.3, GitPython 3.1.41
- External API behavior must be validated against Context7-provided docs
- Repo architecture decisions must follow DDD and local project conventions
- If docs are ambiguous across versions, capture assumptions in issue notes

## Implementation Notes
- Add new route in `apps/api/routers/projects.py`
- Use existing `GitManager` to read artifacts
- Follow pattern from `/projects/{id}` endpoint
- Add response model in `models.py`

**Files to change:**
- `apps/api/routers/projects.py` (new endpoint)
- `apps/api/models.py` (new response model)
- `apps/api/services/git_manager.py` (if new methods needed)

**Estimated Size:** M (100-150 lines)
```

## Tips

- One issue = one PR (keep scope small)
- Be specific about what changes and what doesn't
- Include both happy path and error cases
- Make validation steps copy-pasteable
- Add a Context7 docs-grounding note for any non-trivial framework/API behavior
- Link to related issues for context
- Consider backwards compatibility
- Note any environment variables or config needed
