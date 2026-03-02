# Backend Cleanup Plan

**Date:** 2026-03-15
**Status:** Actionable — reviewed after Step 3 completion (all 9 S3R-BE issues closed)

---

## 1. Goals Review — Are All Backend Goals Met?

### Step 3 Requirements (PLAN.md / planning/STEP-3-REQUIREMENTS.md)

| Requirement | Issues | Status |
|---|---|---|
| R1: TUI-Driven E2E Test Suite | S3R-BE-01–04 (#693–#696) | ✅ All merged |
| R2: Cross-Artifact Audit Hardening | S3R-BE-05–06 (#684/#685) | ✅ All merged |
| R3: Diff Determinism | S3R-BE-07 (#686) | ✅ Merged |
| R4: CI Quality Gates (freshness) | S3R-BE-08 (#687) | ✅ Merged |
| R5: CI Quality Gates (wiring) | S3R-BE-09 (#688) | ✅ Merged |

**Conclusion: All Step 3 backend goals are met. Issue queue is empty.**

---

## 2. Outdated Artifacts — Delete

These files are point-in-time session artifacts with no ongoing value.

### Root-level tracking `.md` files (safe to delete)

| File | Reason |
|---|---|
| `AGENT-REVIEW-COMPLETE.md` | Session tracking artifact from Jan 2026 |
| `COPILOT-REVIEW-COMPLETED.md` | Session tracking artifact |
| `ISSUEAGENT-CHAT-COMPLETE.md` | Chat session record |
| `ISSUEAGENT-CHAT-SETUP.md` | Chat session setup doc |
| `STEP-1-IMPLEMENTATION-TRACKING.md` | Step 1 finished, history in `planning/archive/` |
| `STEP-1-STATUS.md` | Step 1 finished |
| `STEP-2-PLANNING.md` | Step 2 finished |
| `TEST-RESULTS.md` | Jan 2026 snapshot, superseded by CI |

**Delete command:**
```bash
rm -f AGENT-REVIEW-COMPLETE.md COPILOT-REVIEW-COMPLETED.md \
  ISSUEAGENT-CHAT-COMPLETE.md ISSUEAGENT-CHAT-SETUP.md \
  STEP-1-IMPLEMENTATION-TRACKING.md STEP-1-STATUS.md \
  STEP-2-PLANNING.md TEST-RESULTS.md
```

---

## 3. Stale Artifacts — Archive or Evaluate

These files may have historical value but clutter root.

| File | Recommendation |
|---|---|
| `LEARNINGS-SUMMARY.md` | Move to `docs/` or `planning/archive/` — contains issue-level learnings |
| `instructions.md` | Documents chat archive workflow — move to `docs/` |
| `E2E_TESTING.md` | Check against `tests/e2e/tui/README.md` for duplication; archive if superseded |
| `usedChats/master_plan_for_solution_merged.md` | Archive to `planning/archive/` or delete |
| `usedChats/tutorial_chat_mvp_quality_20260203_2336.md` | Delete — old chat export |

**Commands:**
```bash
# Move to docs
mv LEARNINGS-SUMMARY.md docs/learnings-summary.md
mv instructions.md docs/chat-archive-instructions.md

# Archive usedChats
mv usedChats/master_plan_for_solution_merged.md planning/archive/
rm -f usedChats/tutorial_chat_mvp_quality_20260203_2336.md
rmdir usedChats 2>/dev/null || true  # only if now empty
```

---

## 4. `__pycache__` — Python 3.11 and 3.13 Stale Bytecode

The project runs Python 3.12, but 13,546 `.pyc` files exist, including orphaned 3.11 and 3.13 bytecode from previous runs on other versions.

**Impact:** No functional harm, but confusing and wastes disk (approx 20MB+).

**Clean command:**
```bash
find . -name "*.pyc" -path "*cpython-311*" -delete
find . -name "*.pyc" -path "*cpython-313*" -delete
find . -name "__pycache__" -empty -delete
```

**Prevent recurrence** — add to `.gitignore` if not already there:
```
__pycache__/
*.py[cod]
```

---

## 5. Tests — Unused / Orphaned Files

### `tests/e2e/backend_e2e_runner.py` (313 lines, not imported anywhere)

This standalone harness script is not referenced by any test file or CI job. It predates the TUI fixture helper infrastructure (`tests/e2e/tui/helpers.py`) introduced in S3R-BE-01.

**Options:**
- **Delete** if functionality is covered by `tests/e2e/tui/helpers.py`
- **Keep** if it's a useful manual debug tool (add a `# Manual use only` header)

**Recommended action:** Review content then delete or add header.

### `tests/unit/test_commands/` — Unusual Split Pattern

The `proposals.py`, `raid.py`, `workflow.py` (non-prefixed) contain the actual test cases. The `test_proposals.py`, `test_raid.py`, `test_workflow.py` files are single-line shims:
```python
from tests.unit.test_commands.proposals import *  # noqa: F401,F403
```
This pattern works but creates confusion about where tests live.

**Recommendation:** Rename the non-prefixed files to `test_proposals_cases.py`, `test_raid_cases.py`, `test_workflow_cases.py` and update their importers, OR consolidate into single `test_*.py` files.

---

## 6. Code Quality — Pydantic Warning

**Location:** `apps/api/domain/templates/models.py:78`

**Warning:** `Field name "schema" in "TemplateUpdate" shadows an attribute in parent "BaseModel"`

**Fix:** Rename the field to `template_schema` (with `alias="schema"` if API backward-compat required):
```python
# Before
schema: Optional[Dict[str, Any]] = None

# After
template_schema: Optional[Dict[str, Any]] = Field(None, alias="schema")
```

---

## 7. Scripts — Stale Step-Specific Helpers

| Script | Status |
|---|---|
| `scripts/create_step1_issues.sh` | Step 1 done — historical only |
| `scripts/update_step1_issues_hybrid.sh` | Step 1 done — historical only |
| `scripts/generate_step_4_roadmap.py` | Step 4 not started — keep until needed |
| `scripts/check_test_docs.py` | Check if superseded by `check_test_docs_freshness.py` |

**Recommended action:** Move `create_step1_issues.sh` and `update_step1_issues_hybrid.sh` to `planning/archive/scripts/`.

---

## 8. Summary — Priority Order

| Priority | Action | Files/Scope |
|---|---|---|
| **P1 - Do now** | Delete stale root .md files | 8 files (see §2) |
| **P1 - Do now** | Clean stale `__pycache__` | All 3.11/3.13 `.pyc` files |
| **P2 - This week** | Fix Pydantic `schema` warning | `apps/api/domain/templates/models.py:78` |
| **P2 - This week** | Archive `usedChats/`, move `LEARNINGS-SUMMARY.md` | 2–3 files |
| **P3 - When time** | Resolve `backend_e2e_runner.py` orphan | `tests/e2e/backend_e2e_runner.py` |
| **P3 - When time** | Archive Step 1 scripts | `scripts/create_step1_issues.sh` etc. |
| **P3 - When time** | Consolidate `test_commands` split pattern | `tests/unit/test_commands/*.py` |

---

## 9. What to Keep As-Is

- `planning/` — all planning docs including `archive/` and `issues/` — valuable history
- `usedChats/master_plan_for_solution_merged.md` — consider archiving, not deleting
- `PLAN.md`, `README.md`, `QUICKSTART.md`, `CONTRIBUTING.md` — core docs
- `agents/training/`, `agents/knowledge/` — live agent learning data
- `configs/` — all configs are active or default references
- All `tests/unit/`, `tests/integration/`, `tests/e2e/` — all actively used in CI
- All `apps/api/`, `apps/mcp/`, `apps/tui/` — production code
