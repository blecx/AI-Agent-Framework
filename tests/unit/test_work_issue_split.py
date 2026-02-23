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
