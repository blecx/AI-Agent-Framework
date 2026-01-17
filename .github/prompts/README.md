# Copilot Prompt Templates

This directory contains reusable prompt templates to help standardize GitHub Copilot interactions and enforce the **Plan → Issues → PRs** workflow.

## Available Templates

### 1. [planning-feature.md](./planning-feature.md)

**Purpose:** Create a comprehensive feature plan with spec and issue breakdown.

**When to use:**

- Starting a new feature
- Need to break down complex work
- Planning cross-repo changes
- Scoping a large task

**Output:**

- Feature specification (goal, scope, criteria, constraints)
- List of small, focused issues
- Cross-repo impact analysis

---

### 2. [drafting-issue.md](./drafting-issue.md)

**Purpose:** Draft a complete, actionable implementation issue.

**When to use:**

- Creating an issue from a feature plan
- Documenting a bug fix task
- Defining work for a single PR

**Output:**

- Clear issue title and description
- Specific acceptance criteria
- Validation steps (repo-specific commands)
- Implementation notes and estimates

---

### 3. [drafting-pr.md](./drafting-pr.md)

**Purpose:** Write a comprehensive PR description with validation steps.

**When to use:**

- Submitting a PR for review
- Documenting changes made
- Providing reviewer validation steps

**Output:**

- PR title and summary
- Detailed change list
- Testing performed
- Copy-pasteable validation commands
- Checklist for reviewers

---

### 4. [cross-repo-coordination.md](./cross-repo-coordination.md)

**Purpose:** Coordinate changes between backend and frontend repositories.

**When to use:**

- API changes that affect the client
- Breaking changes requiring coordination
- New features spanning both repos
- Deprecating or versioning APIs

**Output:**

- Impact analysis (backend + frontend)
- Implementation order and strategy
- API contract documentation
- Testing and deployment plan
- Communication checklist

---

### 5. [pr-review-rubric.md](./pr-review-rubric.md)

**Purpose:** Standardize PR review quality and ensure acceptance criteria are actually met.

**When to use:**

- Reviewing a PR manually
- Running a review agent against a PR diff

**Output:**

- Pass/fail against acceptance criteria with evidence
- Standards/safety checks (repo hygiene)
- Clear approve vs request-changes recommendation

---

## How to Use These Templates

### Method 1: Direct Copy-Paste

1. Open the template file
2. Copy the prompt section
3. Replace `[PLACEHOLDERS]` with your specifics
4. Paste into GitHub Copilot Chat or issue/PR description

### Method 2: Reference in Copilot Chat

```text
@workspace Follow the template in .github/prompts/planning-feature.md
to help me plan [YOUR FEATURE]
```

### Method 3: As Issue/PR Template

Use the structure as a checklist when creating issues or PRs manually.

## Workflow Integration

These templates support the standard workflow:

```text
1. PLAN
   ↓ (use planning-feature.md)
2. CREATE ISSUES
   ↓ (use drafting-issue.md for each)
3. IMPLEMENT
   ↓ (one issue per PR)
4. CREATE PR
   ↓ (use drafting-pr.md)
5. REVIEW & MERGE
   ↓ (squash merge preferred)
6. CLOSE ISSUE
```

For cross-repo work, use `cross-repo-coordination.md` at the planning stage.

## Customization

Feel free to adapt these templates for your specific needs:

- Add project-specific validation steps
- Include additional sections
- Adjust format to match team preferences

## Related Documentation

- [../.copilot-instructions.md](../copilot-instructions.md) - Main Copilot guidance
- [../../README.md](../../README.md) - Project overview
- [../../docs/development.md](../../docs/development.md) - Development guide

## Contributing

When adding new templates:

1. Follow existing template structure
2. Include clear examples
3. Add repo-specific validation steps
4. Update this README with the new template
5. Test with GitHub Copilot to ensure clarity
