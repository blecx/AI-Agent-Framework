# Agent: Plan

**Purpose:** Research and outline a multi-step implementation plan for a goal or problem.

**Inputs:**
- Goal or problem description (required)
- Optional: --repo flag to specify repository context

**Workflow:**

1. **Analyze goal** (quick assessment)
   - Identify affected components
   - Check for existing patterns (limit to 5 most relevant files)
   - List dependencies and constraints

2. **Search relevant files** (LIMIT TO 5 RESULTS)
   ```bash
   rg -l "<relevant-keyword>" --type py --max-count 5
   ```
   - **Optimization:** Stop at 5 matches, don't scan entire codebase
   - **Optimization:** Use specific keywords, not broad searches

3. **Review architecture patterns** (reference only, no deep dive)
   - Backend: domain/ → services/ → routers/ (DDD)
   - Frontend: domain clients → components
   - Check `.github/copilot-instructions.md` for standards
   - **Optimization:** Shallow reference, not exhaustive analysis

4. **Create step-by-step plan**
   - Break into issues (S/M/L sizing)
   - Identify parallel work opportunities
   - List acceptance criteria per step
   - Document cross-repo dependencies

5. **Output plan**
   - Markdown format with sections: Goal, Analysis, Steps, Dependencies
   - Save to `.tmp/plan-<timestamp>.md`
   - Print summary to stdout

**Success Criteria:** Clear, actionable plan with sized steps and dependencies identified.

**Optimization Notes:**
- Limit file searches to 5 results max
- Prefer shallow analysis over deep dives
- No exhaustive codebase scans
- Focus on essential patterns only
- Early exit if goal is ambiguous (request clarification)

**Plan Template:**

```markdown
# Plan: <Goal Title>

## Goal
[One sentence description]

## Analysis
[Affected components, existing patterns found]

## Steps
1. **Step 1 Title** (Size: S/M/L, Est: Xh)
   - Acceptance criteria
   - Files to modify
   
2. **Step 2 Title** (Size: S/M/L, Est: Xh)
   - Acceptance criteria
   - Dependencies: Step 1

## Cross-repo Dependencies
[If any]

## Risks
[If any]
```
