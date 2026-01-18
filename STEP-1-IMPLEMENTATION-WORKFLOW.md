# Step 1 Implementation Workflow - STRICT PROTOCOL

**Version:** 1.0  
**Date:** 2026-01-18  
**Status:** 🔴 **ACTIVE ENFORCEMENT**

---

## 🎯 Purpose

This document defines the **STRICT PROTOCOL** for implementing all 36 Step 1 issues in the correct order with mandatory review cycles and CI validation.

**Quick Start:**

```bash
# Select next issue to work on (intelligent selection with learning)
./next-issue

# After completing an issue, record actual time spent
./scripts/record-completion.py <issue_number> <actual_hours> [notes]
```

**Critical Rules:**

1. ✅ **ONLY ONE ISSUE AT A TIME** - No parallel work on issues
2. ✅ **DEPENDENCIES MUST BE MERGED** - Cannot start issue until blockers are merged
3. ✅ **COPILOT REVIEW IS ABSOLUTELY MANDATORY** - Step 7 CANNOT be skipped under any circumstances
4. ✅ **SOLO DEVELOPER + COPILOT APPROVAL = SUFFICIENT** - No human reviewer required, but Copilot approval is mandatory
5. ✅ **CI MUST PASS** - Make 3 attempts to fix CI before asking user
6. ✅ **NO GOAL REDUCTION** - Cannot reduce issue scope to pass CI
7. ✅ **PLAN MUST BE UPDATED** - Every PR updates the tracking plan

---

## 🚨 CRITICAL: Step 7 (Copilot Review) Is MANDATORY Quality Gate

**⚠️ QUALITY POLICY: Solo Developer + Copilot Approval = Sufficient for Merge**

**This project uses GitHub Copilot as the mandatory reviewer for all PRs. This ensures quality while maintaining solo development velocity.**

**Why This Works:**

- ✅ **AI-Powered Quality** - Copilot catches issues that solo developers might miss
- ✅ **No Blocking** - No waiting for human reviewers
- ✅ **Consistent Standards** - Copilot applies the same standards to every PR
- ✅ **Learning Tool** - Copilot feedback improves your skills over time

**Step 7 (Copilot Review) MUST be completed and result in APPROVAL before merging.**

**Consequences of skipping Step 7:**

- Implementation may be incomplete
- Code quality issues may slip through
- Technical debt accumulates
- Future issues become harder to implement

**Step 7 Mandatory Checklist (Copilot MUST verify ALL):**

- [ ] **All acceptance criteria implemented** - No partial completion
- [ ] **Code quality verified** - No code smells, proper patterns, DRY principle
- [ ] **Test coverage complete** - Unit tests (80%+), integration tests, edge cases
- [ ] **Documentation complete** - README updates, inline comments, JSDoc
- [ ] **TypeScript types verified** - No `any` abuse, proper type safety
- [ ] **Error handling verified** - Try/catch blocks, user-friendly messages
- [ ] **Loading states verified** - All async operations show loading UI
- [ ] **Accessibility verified** - ARIA labels, keyboard navigation, screen reader support
- [ ] **Responsive design verified** - Works on mobile, tablet, desktop
- [ ] **Performance validated** - No unnecessary re-renders, proper memoization

**Copilot MUST explicitly state "APPROVED" or "Ready to merge" after completing checklist.**

**IF you are about to merge a PR and have NOT received Copilot APPROVAL, STOP and request review first.**

---

## 📋 The 9-Step Protocol (Solo Developer + Copilot Workflow)

**Every issue MUST follow these 9 steps in exact order:**

1. **Pre-work Validation** - Check blockers merged
2. **Create Feature Branch** - Clean branch from main
3. **Implementation** - Build the feature
4. **Self-Review** - Lint, type, build, test
5. **Update Tracking Plan** - Document progress
6. **Create Pull Request** - Push to GitHub
7. **🔴 COPILOT REVIEW & APPROVAL** ← **MANDATORY QUALITY GATE**
8. **CI Validation** - 3 fix attempts, then merge
9. **Post-Merge Validation** - Verify + update tracking

**Step 7 is THE quality gate. Copilot approval is required before merge.**

---

## 📋 Issue Dependency Order

### **Phase 1: Infrastructure (Week 1)**

**MUST BE COMPLETED IN EXACT ORDER:**

1. **Issue #24** - API Service Layer Infrastructure 🔴 **START HERE**
   - **Blockers:** None
   - **Blocks:** ALL other issues
   - **Estimated:** 8-10 hours
   - **Priority:** CRITICAL

2. **Issue #25** - Routing and Navigation Setup
   - **Blockers:** Issue #24
   - **Blocks:** #26, #27, #28, #29
   - **Estimated:** 4-6 hours
   - **Priority:** High

3. **Issue #26** - Project Context Provider
   - **Blockers:** Issue #24, #25
   - **Blocks:** All UI components (#32-#45)
   - **Estimated:** 3-4 hours
   - **Priority:** High

4. **Issue #27** - State Management Setup
   - **Blockers:** Issue #24, #25, #26
   - **Blocks:** All UI components (#32-#45)
   - **Estimated:** 4-6 hours
   - **Priority:** High

5. **Issue #28** - Error Handling System
   - **Blockers:** Issue #24, #27
   - **Blocks:** All UI components (error display)
   - **Estimated:** 3-4 hours
   - **Priority:** High

6. **Issue #29** - UI Component Library Setup
   - **Blockers:** Issue #27, #28
   - **Blocks:** All UI components
   - **Estimated:** 4-6 hours
   - **Priority:** High

---

### **Phase 2: Chat Integration (Week 2)**

**MUST START AFTER PHASE 1 COMPLETE:**

7. **Issue #59** - Chat-to-Backend Integration Layer 🔴 **CRITICAL BLOCKER**
   - **Blockers:** Issue #24 (API service)
   - **Blocks:** Primary chat-based workflow
   - **Estimated:** 8-12 hours
   - **Priority:** CRITICAL

---

### **Phase 3: RAID Components (Week 2-3)**

**MUST START AFTER ISSUE #59 COMPLETE:**

8. **Issue #30** - RAID TypeScript Types
   - **Blockers:** Issue #24
   - **Blocks:** #31-#36
   - **Estimated:** 2-3 hours
   - **Priority:** High

9. **Issue #31** - RAID API Service
   - **Blockers:** Issue #24, #30
   - **Blocks:** #32-#36
   - **Estimated:** 4-6 hours
   - **Priority:** High

10. **Issue #32** - RAID List View
    - **Blockers:** Issue #26, #27, #29, #31
    - **Blocks:** #33, #34
    - **Estimated:** 4-6 hours
    - **Priority:** High

11. **Issue #33** - RAID Filter Panel
    - **Blockers:** Issue #32
    - **Blocks:** None
    - **Estimated:** 3-4 hours
    - **Priority:** Medium

12. **Issue #34** - RAID Detail/Edit View
    - **Blockers:** Issue #31, #32
    - **Blocks:** None
    - **Estimated:** 5-7 hours
    - **Priority:** High

13. **Issue #35** - Optional RAID Create Modal
    - **Blockers:** Issue #31, #29
    - **Blocks:** None
    - **Estimated:** 4-6 hours
    - **Priority:** Medium (optional feature)

14. **Issue #36** - RAID Badges Component
    - **Blockers:** Issue #30, #29
    - **Blocks:** #32, #34
    - **Estimated:** 2-3 hours
    - **Priority:** Medium

---

### **Phase 4: Workflow Components (Week 3)**

**MUST START AFTER RAID COMPONENTS COMPLETE:**

15. **Issue #37** - Workflow TypeScript Types
    - **Blockers:** Issue #24
    - **Blocks:** #38-#42
    - **Estimated:** 2-3 hours
    - **Priority:** High

16. **Issue #38** - Workflow API Service
    - **Blockers:** Issue #24, #37
    - **Blocks:** #39-#42
    - **Estimated:** 3-4 hours
    - **Priority:** High

17. **Issue #39** - Workflow Stage Indicator
    - **Blockers:** Issue #26, #29, #38
    - **Blocks:** None
    - **Estimated:** 4-5 hours
    - **Priority:** High

18. **Issue #40** - Workflow Transition UI
    - **Blockers:** Issue #38, #39
    - **Blocks:** None
    - **Estimated:** 4-6 hours
    - **Priority:** High

19. **Issue #41** - Audit Trail Viewer
    - **Blockers:** Issue #24, #26, #29
    - **Blocks:** None
    - **Estimated:** 4-6 hours
    - **Priority:** High

20. **Issue #42** - Clarify WorkflowPanel Purpose
    - **Blockers:** Issue #39 (need separate indicator)
    - **Blocks:** None
    - **Estimated:** 1-2 hours
    - **Priority:** Low (documentation)

---

### **Phase 5: Project Management (Week 4)**

**MUST START AFTER WORKFLOW COMPONENTS COMPLETE:**

21. **Issue #43** - Project List View
    - **Blockers:** Issue #24, #26, #27, #29
    - **Blocks:** #44, #45
    - **Estimated:** 4-6 hours
    - **Priority:** High

22. **Issue #44** - Optional Project Creation Flow
    - **Blockers:** Issue #24, #26, #29
    - **Blocks:** None
    - **Estimated:** 6-8 hours
    - **Priority:** Low (optional feature)

23. **Issue #45** - Project Dashboard
    - **Blockers:** Issue #26, #29, #32, #39, #41, #43
    - **Blocks:** None
    - **Estimated:** 6-8 hours
    - **Priority:** High

---

### **Phase 6: UX & Polish (Week 5)**

**CAN START AFTER COMPONENTS EXIST:**

24. **Issue #46** - Responsive Design
25. **Issue #47** - Accessibility Improvements
26. **Issue #48** - Empty States
27. **Issue #49** - Loading States
28. **Issue #50** - Toast Notifications
29. **Issue #51** - Keyboard Shortcuts

---

### **Phase 7: Testing (Week 5-6)**

**MUST START AFTER ALL COMPONENTS COMPLETE:**

30. **Issue #52** - E2E Tests (Chat + UI flows)
31. **Issue #53** - E2E Tests (Error scenarios)
32. **Issue #54** - Integration Tests
33. **Issue #55** - Performance Tests

---

### **Phase 8: Documentation (Week 6)**

**FINAL PHASE:**

34. **Issue #56** - Update Client README
35. **Issue #57** - Update PLAN.md
36. **Issue #58** - API Integration Guide

---

## 🔒 STRICT PROTOCOL FOR EACH ISSUE

### **Step 1: Pre-Work Validation** ✅

**BEFORE starting ANY work, verify:**

```bash
# 1. Check all blocker issues are MERGED (not just closed)
gh issue view <blocker-issue-number> --repo blecx/AI-Agent-Framework-Client
# Status must be: "State: CLOSED" AND has merged PR

# 2. Update local repository
git checkout main
git pull origin main

# 3. Read issue description completely
gh issue view <issue-number> --repo blecx/AI-Agent-Framework-Client

# 4. Update tracking plan
# (See STEP-1-IMPLEMENTATION-TRACKING.md)
```

**❌ STOP if:**

- Any blocker issue is not merged
- Local repository is not up-to-date
- Issue description is unclear

---

### **Step 2: Create Feature Branch** ✅

```bash
# Branch naming convention: issue/<number>-<slug>
git checkout -b issue/<number>-short-description

# Examples:
# git checkout -b issue/24-api-service-layer
# git checkout -b issue/32-raid-list-view
```

---

### **Step 3: Implementation** ✅

**MUST implement ALL acceptance criteria from issue:**

1. Read acceptance criteria completely
2. Implement functionality (no shortcuts)
3. Add TypeScript types (no `any` types)
4. Add error handling (try/catch, error states)
5. Add loading states (no blank screens)
6. Add unit tests (minimum 80% coverage)
7. Add integration tests (API calls)
8. Update or create documentation

**Code Quality Requirements:**

- ✅ TypeScript strict mode enabled
- ✅ No ESLint errors
- ✅ No console.log statements (use proper logging)
- ✅ All imports organized
- ✅ No unused variables
- ✅ All functions have JSDoc comments
- ✅ Components have PropTypes or TypeScript interfaces

---

### **Step 4: Self-Review (Pre-PR)** ✅

**Run ALL checks locally BEFORE creating PR:**

```bash
# 1. Lint check
npm run lint
# MUST show: No errors, warnings acceptable if documented

# 2. Type check
npm run type-check  # or tsc --noEmit
# MUST show: No errors

# 3. Build check
npm run build
# MUST complete successfully

# 4. Unit tests
npm test
# MUST show: All tests passing

# 5. Integration tests (if applicable)
npm run test:integration
# MUST show: All tests passing

# 6. Visual review
npm run dev
# MUST manually test all functionality
```

**❌ DO NOT create PR if:**

- Lint has errors (warnings OK if documented in PR)
- Type check fails
- Build fails
- Any test fails
- Functionality doesn't work

---

### **Step 5: Update Tracking Plan** ✅

**BEFORE creating PR, update tracking plan:**

```bash
# Edit STEP-1-IMPLEMENTATION-TRACKING.md
# Update issue status: "Not Started" → "In Review"
# Add PR link when created
# Add notes about implementation decisions
# Commit tracking plan update
git add STEP-1-IMPLEMENTATION-TRACKING.md
git commit -m "Update tracking: Issue #<number> in review"
git push origin issue/<number>-description
```

---

### **Step 6: Create Pull Request** ✅

**PR Title Format:**

```
[Issue #<number>] <Short description>

Examples:
[Issue #24] Add API service layer infrastructure
[Issue #32] Implement RAID list view with filters
```

**PR Description Template:**

```markdown
## Issue

Fixes #<number>

## Description

<1-2 sentence summary of what this PR does>

## Changes

- Added <feature/component>
- Implemented <functionality>
- Added tests for <scenarios>
- Updated documentation in <files>

## Acceptance Criteria

- [x] <Copy each acceptance criterion from issue>
- [x] <Mark each as complete>

## Testing

**Unit Tests:**

- `<test file>` - <number> tests
- Coverage: <percentage>%

**Integration Tests:**

- `<test file>` - <number> tests

**Manual Testing:**

- Tested in Chrome, Firefox, Safari
- Tested responsive breakpoints
- Tested error scenarios
- Tested loading states

## Documentation

- [x] Updated README.md (if needed)
- [x] Added JSDoc comments
- [x] Updated STEP-1-IMPLEMENTATION-TRACKING.md

## Screenshots/Videos

<Add screenshots of UI changes>
<Add video of workflow if complex>

## Checklist

- [x] All acceptance criteria met
- [x] Lint passes (no errors)
- [x] Type check passes
- [x] Build succeeds
- [x] All tests pass
- [x] Self-reviewed code
- [x] Documentation updated
- [x] Tracking plan updated

## Notes

<Any implementation decisions, trade-offs, or future considerations>
```

**Create PR:**

```bash
gh pr create --repo blecx/AI-Agent-Framework-Client \
  --title "[Issue #<number>] <description>" \
  --body-file pr-template.md \
  --base main
```

---

### **Step 7: Copilot Self-Review** 🔴 **ABSOLUTELY MANDATORY - NEVER SKIP THIS STEP**

**⚠️ THIS STEP IS MATURE AND CRITICAL - IT HAS SAVED ISSUES FROM BEING INCOMPLETE**

**WHEN TO PERFORM THIS STEP:**

- AFTER Step 6 (code committed to branch)
- BEFORE asking user for review
- BEFORE creating PR for user inspection
- BEFORE proceeding to Step 8 (CI validation)

**🚨 SELF-CHECK BEFORE PROCEEDING: Have you completed this step?**

```
[ ] Have I performed a comprehensive Copilot self-review?
[ ] Have I verified ALL acceptance criteria are implemented?
[ ] Have I checked code quality, tests, documentation?
[ ] Have I explicitly stated "APPROVED" or "Ready for user review"?

IF ANY BOX IS UNCHECKED, STOP AND COMPLETE STEP 7 NOW.
```

---

**MANDATORY SELF-REVIEW PROCESS:**

**1. Perform Comprehensive Code Review:**

```bash
# As Copilot, review your own implementation:
# "I will now perform a comprehensive self-review of Issue #<number>."
```

**2. Verify All Acceptance Criteria:**

For EACH acceptance criterion from the issue:

- [ ] Read the criterion
- [ ] Locate the code that implements it
- [ ] Verify it works correctly
- [ ] Check for edge cases
- [ ] Document verification in review

**3. Check Code Quality:**

- [ ] **Architecture:** Modular? Clean separation of concerns?
- [ ] **TypeScript:** All types defined? No `any` abuse?
- [ ] **Error Handling:** Comprehensive? User-friendly messages?
- [ ] **Loading States:** Present for all async operations?
- [ ] **Code Smells:** Any duplicated code? Complex functions?
- [ ] **Conventions:** Follows project patterns?

**4. Validate Test Coverage:**

- [ ] **Unit Tests:** All functions tested? Edge cases covered?
- [ ] **Integration Tests:** API integration tested?
- [ ] **Test Quality:** Tests are deterministic? No flaky tests?
- [ ] **Coverage:** Meets or exceeds project standards?

**5. Verify Documentation:**

- [ ] **JSDoc Comments:** All public functions documented?
- [ ] **README Updates:** If applicable, updated?
- [ ] **Tracking Plan:** Updated with progress?
- [ ] **PR Description:** Complete and accurate?

**6. Build & Runtime Validation:**

- [ ] **Lint:** No errors (warnings OK if documented)
- [ ] **Type Check:** No errors
- [ ] **Build:** Completes successfully
- [ ] **Tests:** All passing (100%)
- [ ] **Dev Server:** Runs without errors

**7. Review Cycle Iteration:**

```bash
# If you find issues during self-review:

# a. Create checklist of required changes
# b. Implement ALL changes
git add <files>
git commit -m "Self-review: <summary of changes>"
git push origin issue/<number>-description

# c. REPEAT Step 7 (perform self-review again)
# d. Continue until no issues found
```

**8. Explicit Approval Required:**

Once all checks pass, you MUST state explicitly:

```
✅ COPILOT SELF-REVIEW: APPROVED

Issue #<number> implementation is complete and meets all requirements:
- All acceptance criteria implemented and verified
- Code quality is high (no smells, proper patterns)
- Test coverage is comprehensive (X/X tests passing)
- Documentation is complete
- Build and runtime validation passed

RECOMMENDATION: Ready for user review (Step 8).
```

---

**❌ ABSOLUTELY DO NOT PROCEED TO USER REVIEW UNTIL:**

- ✅ You have performed comprehensive self-review
- ✅ All acceptance criteria verified as implemented
- ✅ All code quality checks passed
- ✅ All tests passing (100%)
- ✅ Documentation complete
- ✅ You have explicitly stated "APPROVED"
- ✅ You have written "Ready for user review"

**IF YOU ARE ABOUT TO ASK USER "Ready for review?" BUT HAVE NOT COMPLETED THIS STEP:**

🚨 **STOP IMMEDIATELY** 🚨

**Go back and perform Step 7 now. This step is NEVER optional.**

---

### **Step 8: CI Validation (3 Attempts)** ✅

**Wait for CI to run:**

```bash
# Check CI status
gh pr checks <pr-number> --repo blecx/AI-Agent-Framework-Client

# If CI PASSES:
# → Proceed to Step 9 (Merge)

# If CI FAILS:
# → Analyze failure
# → Fix root cause (no goal reduction!)
# → Push fix
# → Repeat (max 3 attempts)
```

**CI Failure Analysis:**

```bash
# 1. View CI logs
gh pr checks <pr-number> --repo blecx/AI-Agent-Framework-Client --watch

# 2. Common failures and fixes:

# Lint failure:
npm run lint -- --fix
git add .
git commit -m "Fix linting errors"
git push

# Type errors:
npm run type-check
# Fix TypeScript errors
git add .
git commit -m "Fix type errors"
git push

# Test failures:
npm test -- --verbose
# Fix failing tests (no skipping!)
git add .
git commit -m "Fix failing tests"
git push

# Build failure:
npm run build
# Fix build errors
git add .
git commit -m "Fix build errors"
git push

# 3. Push fix and wait for CI
# ATTEMPT 1: First fix
# ATTEMPT 2: Second fix
# ATTEMPT 3: Third fix

# If 3 attempts fail:
# → Ask user for help (do NOT reduce goals)
```

**CRITICAL RULE:**

❌ **NEVER reduce issue goals to pass CI**
❌ **NEVER skip tests to pass CI**
❌ **NEVER disable lint rules to pass CI**

✅ **FIX the root cause**
✅ **Make 3 genuine attempts**
✅ **Ask user after 3 failures**

---

### **Step 9: Merge Pull Request** ✅

**ONLY merge if:**

- ✅ Copilot approved PR
- ✅ CI passes (all checks green)
- ✅ All acceptance criteria met
- ✅ No unresolved review comments
- ✅ Tracking plan updated

**Merge command:**

```bash
# Use SQUASH merge to keep history clean
gh pr merge <pr-number> --squash --delete-branch \
  --repo blecx/AI-Agent-Framework-Client

# PR title becomes commit message
```

**After merge:**

```bash
# 1. Update local main
git checkout main
git pull origin main

# 2. Update tracking plan
# Edit STEP-1-IMPLEMENTATION-TRACKING.md
# Update issue status: "In Review" → "Complete"
# Add completion date

git add STEP-1-IMPLEMENTATION-TRACKING.md
git commit -m "Update tracking: Issue #<number> complete"
git push origin main

# 3. Close issue (auto-closed by PR merge)
# Verify: gh issue view <number> --repo blecx/AI-Agent-Framework-Client
```

---

### **Step 10: Post-Merge Validation** ✅

**Verify merge was successful:**

```bash
# 1. Confirm issue is closed
gh issue view <number> --repo blecx/AI-Agent-Framework-Client
# State: CLOSED

# 2. Confirm PR is merged
gh pr view <pr-number> --repo blecx/AI-Agent-Framework-Client
# State: MERGED

# 3. Confirm branch is deleted
git branch -r | grep issue/<number>
# Should return nothing

# 4. Pull latest main
git checkout main
git pull origin main

# 5. Build and test main
npm install
npm run build
npm test

# 6. Update tracking plan with completion
# (Already done in Step 9)
```

---

## 📊 Progress Tracking

**ALWAYS maintain [STEP-1-IMPLEMENTATION-TRACKING.md](STEP-1-IMPLEMENTATION-TRACKING.md)**

**Update tracking plan:**

- ✅ Before starting issue: "Not Started" → "In Progress"
- ✅ After creating PR: "In Progress" → "In Review" + PR link
- ✅ After merge: "In Review" → "Complete" + completion date

**Weekly tracking updates:**

```bash
# Every Friday, update progress summary
# Add notes about blockers, decisions, risks
# Commit and push tracking plan updates
```

---

## 🚫 VIOLATIONS AND RECOVERY

### **Violation: Started issue without blockers merged**

**Recovery:**

1. Stop all work immediately
2. Close current PR (do not merge)
3. Wait for blocker PRs to merge
4. Restart issue implementation

### **Violation: Created PR without self-review**

**Recovery:**

1. Run all checks locally
2. Fix all issues found
3. Push fixes to PR
4. Document in PR: "Added missing self-review checks"

### **Violation: Merged PR without Copilot approval**

**Recovery:**

1. Create follow-up issue for review feedback
2. Implement feedback in new PR
3. Document lesson learned in tracking plan

### **Violation: Reduced issue goals to pass CI**

**Recovery:**

1. Revert PR merge
2. Re-implement with full goals
3. Fix CI properly
4. Re-submit PR

---

## ✅ Success Criteria

**Step 1 is COMPLETE when:**

- ✅ All 36 issues closed
- ✅ All 36 PRs merged
- ✅ All CI checks passing
- ✅ Tracking plan shows 100% complete
- ✅ No open blockers
- ✅ Documentation updated (README, PLAN, guides)
- ✅ E2E tests passing (chat + UI flows)
- ✅ Manual smoke test successful

---

## 🎯 Current Status

**See:** [STEP-1-IMPLEMENTATION-TRACKING.md](STEP-1-IMPLEMENTATION-TRACKING.md)

**Quick Stats:**

- Issues Complete: 0/36
- PRs Merged: 0/36
- Current Phase: Phase 1 (Infrastructure)
- Next Issue: #24 (API Service Layer) 🔴 **START HERE**

---

## 📞 When to Ask User for Help

**Ask user ONLY when:**

1. ❌ CI fails 3 times (made genuine fix attempts)
2. ❌ Issue description is ambiguous (cannot determine requirements)
3. ❌ Technical blocker (external service, library incompatibility)
4. ❌ Architectural decision needed (impacts multiple issues)
5. ❌ Discovered new dependency not in original plan

**DO NOT ask user for:**

- ✅ Standard implementation questions (solve them)
- ✅ Copilot review feedback (iterate until approved)
- ✅ CI failures 1-2 times (keep trying)
- ✅ How to implement feature (research and implement)

---

## 📚 Reference Documents

**MUST read before starting any issue:**

1. [STEP-1-HYBRID-APPROACH-UPDATE.md](STEP-1-HYBRID-APPROACH-UPDATE.md) - Chat-first paradigm
2. [STEP-1-IMPLEMENTATION-TRACKING.md](STEP-1-IMPLEMENTATION-TRACKING.md) - Live progress tracker
3. [.github/copilot-instructions.md](.github/copilot-instructions.md) - Project conventions
4. Individual issue in GitHub (acceptance criteria)

---

## 🔄 Workflow Summary

```
┌─────────────────────────────────────────────────────┐
│ 1. Pre-Work Validation (blockers merged?)          │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│ 2. Create Feature Branch                            │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│ 3. Implementation (ALL acceptance criteria)         │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│ 4. Self-Review (lint, type, build, test)           │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│ 5. Update Tracking Plan                             │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│ 6. Create Pull Request (detailed description)       │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│ 7. Copilot Review Cycle                             │
│    ↓                                                 │
│    Issues Found? → Fix → Push → Review Again        │
│    ↓                                                 │
│    Approved? → Continue                              │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│ 8. CI Validation (3 attempts)                       │
│    ↓                                                 │
│    Fails? → Analyze → Fix → Push → Retry            │
│    ↓                                                 │
│    Passes? → Continue                                │
│    ↓                                                 │
│    3 Failures? → Ask User                            │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│ 9. Merge Pull Request (squash merge)                │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│ 10. Post-Merge Validation & Update Tracking         │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│ NEXT ISSUE (repeat workflow)                        │
└─────────────────────────────────────────────────────┘
```

---

**END OF STRICT PROTOCOL**

**Remember:** This is a ZERO-TOLERANCE workflow. Follow EVERY step, EVERY time, for EVERY issue.

**Success = Discipline + Process + Quality**
