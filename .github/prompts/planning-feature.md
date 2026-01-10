# Feature Planning Template

Use this prompt to help plan a new feature following the Plan → Issues → PRs workflow.

## Prompt

```
I need to plan a new feature for the AI-Agent-Framework project.

Feature Description: [DESCRIBE THE FEATURE]

Please help me create:

1. **Feature Spec** including:
   - Goal: What problem does this solve?
   - Scope: What's included and what's not?
   - Acceptance Criteria: How do we know it's done?
   - Constraints: Technical limitations or requirements
   - Dependencies: Related repos, services, or components

2. **Issue Breakdown**: Split the work into small, focused issues that:
   - Can each be completed in a single PR (< 200 lines changed)
   - Have clear acceptance criteria
   - Can be worked on independently when possible
   - Follow a logical implementation order

3. **Cross-Repo Impact**: Identify if this requires changes to:
   - blecx/AI-Agent-Framework (backend API)
   - blecx/AI-Agent-Framework-Client (frontend UI)
   - Both (and coordination strategy)

For each issue, include:
- Title (clear, actionable)
- Description (context, requirements)
- Acceptance Criteria (specific, testable)
- Validation Steps (repo-specific commands)
- Estimated size (S/M/L)

Format output as:
- Feature spec document
- List of GitHub issues (ready to create)
```

## Example Usage

**Input:**
```
Feature Description: Add support for exporting project artifacts as PDF
```

**Expected Output:**
- Complete feature spec with goal, scope, criteria
- 3-5 focused issues (e.g., "Add PDF generation library", "Create export endpoint", "Add export button to UI")
- Cross-repo coordination plan (backend API + frontend button)
- Each issue with validation steps specific to AI-Agent-Framework

## Tips

- Keep features small enough to complete in 1-2 weeks
- Identify MVP vs. nice-to-have features
- Consider backwards compatibility
- Plan for testing and documentation
- Think about error handling and edge cases
