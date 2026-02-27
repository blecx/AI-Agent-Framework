#!/usr/bin/env python3
"""Unit tests for split issue draft generation helpers."""

from scripts.work_issue_split import extract_split_steps, generate_split_issue_stubs


def test_extract_split_steps_reads_bullets_and_numbers():
    text = """
SPLIT_RECOMMENDATION:
- Create issue A for parser setup
2) Create issue B for implementation
* Create issue C for docs
"""

    steps = extract_split_steps(text, max_items=3)

    assert steps == [
        "Create issue A for parser setup",
        "Create issue B for implementation",
        "Create issue C for docs",
    ]


def test_extract_split_steps_respects_limit():
    text = "- one\n- two\n- three\n- four"

    steps = extract_split_steps(text, max_items=2)

    assert steps == ["one", "two"]


def test_generate_split_issue_stubs_uses_recommendations():
    drafts = generate_split_issue_stubs(
        parent_issue_number=402,
        estimated_minutes=35,
        recommendation_text="- first slice\n- second slice",
        max_issues=3,
    )

    assert len(drafts) == 2
    assert drafts[0].title.startswith("split(#402): slice 1")
    assert "first slice" in drafts[0].body
    assert "Parent estimated manual effort: 35 minutes" in drafts[0].body


def test_generate_split_issue_stubs_falls_back_when_empty():
    drafts = generate_split_issue_stubs(
        parent_issue_number=402,
        estimated_minutes=None,
        recommendation_text="",
        max_issues=3,
    )

    assert len(drafts) == 3
    assert "unknown" in drafts[0].body


def test_generate_split_issue_stubs_uses_parent_in_scope_when_recommendation_empty():
    parent_issue_body = """
## Scope
### In Scope
- First PR: Refactor sidebar grouping/order logic, update type/state, and confirm with basic visual distinction.
- Keep implementation and validation within a small, reviewable slice.

### Out of Scope
- Work not directly required for this split slice.
"""

    drafts = generate_split_issue_stubs(
        parent_issue_number=440,
        estimated_minutes=60,
        recommendation_text="",
        parent_issue_body=parent_issue_body,
        max_issues=3,
    )

    assert len(drafts) == 1
    assert "Refactor sidebar grouping/order logic" in drafts[0].title
    assert "First PR: Refactor sidebar grouping/order logic" in drafts[0].body


def test_generate_split_issue_stubs_ignores_estimate_metadata_bullet():
    drafts = generate_split_issue_stubs(
        parent_issue_number=434,
        estimated_minutes=None,
        recommendation_text=(
            "- Current plan estimate: unknown minutes (guardrail max: 20).\n"
            "- Create issue A for planning/spec alignment only (target <= 20 min manual work).\n"
            "- Create issue B for implementation slice 1 with focused validation.\n"
            "- Create issue C for follow-up slice and documentation updates."
        ),
        max_issues=3,
    )

    assert len(drafts) == 3
    assert "Current plan estimate" not in drafts[0].title
    assert "Create issue A" in drafts[0].title
    assert "Current plan estimate" not in drafts[0].body


def test_generate_split_issue_stubs_filters_non_actionable_scope_bullets():
    parent_issue_body = """
## Scope
### In Scope
- Keep implementation and validation within a small, reviewable slice.
- Work not directly required for this split slice.
"""

    drafts = generate_split_issue_stubs(
        parent_issue_number=500,
        estimated_minutes=None,
        recommendation_text="",
        parent_issue_body=parent_issue_body,
        max_issues=3,
    )

    assert len(drafts) == 3
    assert "Create foundational planning/spec split" in drafts[0].title
