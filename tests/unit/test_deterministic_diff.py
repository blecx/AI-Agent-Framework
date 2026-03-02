"""
Unit tests for deterministic diff ordering and normalization.

Verifies that identical input produces identical diff output across
repeated calls — addressing issue #686.
"""

import pytest
from apps.api.services.diff_service import DiffService


@pytest.fixture
def svc() -> DiffService:
    return DiffService()


# ---------------------------------------------------------------------------
# generate_diff — single-file determinism
# ---------------------------------------------------------------------------


def test_generate_diff_deterministic_across_three_calls(svc: DiffService) -> None:
    """Same single-file diff must be byte-for-byte identical on every call."""
    old = "line one\nline two\nline three\n"
    new = "line one\nline TWO\nline three\nline four\n"

    results = [svc.generate_diff(old, new) for _ in range(3)]
    assert results[0] == results[1] == results[2]


def test_generate_diff_empty_inputs_deterministic(svc: DiffService) -> None:
    """Empty-to-empty diff must be stable and empty."""
    results = [svc.generate_diff("", "") for _ in range(3)]
    assert all(r == "" for r in results)


def test_generate_diff_whitespace_normalization_stable(svc: DiffService) -> None:
    """Trailing-whitespace normalization must yield the same result every call."""
    old = "hello   \nworld  \n"
    new = "hello\nworld\nuniverse\n"

    r1 = svc.generate_diff(old, new, normalize_whitespace=True)
    r2 = svc.generate_diff(old, new, normalize_whitespace=True)
    r3 = svc.generate_diff(old, new, normalize_whitespace=True)
    assert r1 == r2 == r3


# ---------------------------------------------------------------------------
# generate_proposal_diff — multi-file determinism
# ---------------------------------------------------------------------------


def _make_changes() -> dict:
    """Return a dict with deliberately unordered keys."""
    return {
        "z_module.md": ("z old\n", "z new\n"),
        "a_module.md": ("a old\n", "a new\n"),
        "m_module.md": ("m old\n", "m new\n"),
    }


def test_proposal_diff_deterministic_across_three_calls(svc: DiffService) -> None:
    """generate_proposal_diff must return identical output on every call."""
    changes = _make_changes()
    results = [svc.generate_proposal_diff(changes) for _ in range(3)]
    assert results[0] == results[1] == results[2]


def test_proposal_diff_ordered_by_path(svc: DiffService) -> None:
    """Sections in the proposal diff must appear in lexicographic path order."""
    changes = _make_changes()
    diff = svc.generate_proposal_diff(changes)

    # Extract the positions of each file header
    pos_a = diff.find("a_module.md")
    pos_m = diff.find("m_module.md")
    pos_z = diff.find("z_module.md")

    # All must be present
    assert pos_a != -1 and pos_m != -1 and pos_z != -1
    # Must appear in alphabetical order
    assert pos_a < pos_m < pos_z


def test_proposal_diff_insertion_order_does_not_matter(svc: DiffService) -> None:
    """Dict insertion order must not affect the diff output."""
    changes_fwd = {
        "alpha.md": ("old alpha\n", "new alpha\n"),
        "beta.md": ("old beta\n", "new beta\n"),
        "gamma.md": ("old gamma\n", "new gamma\n"),
    }
    changes_rev = {
        "gamma.md": ("old gamma\n", "new gamma\n"),
        "beta.md": ("old beta\n", "new beta\n"),
        "alpha.md": ("old alpha\n", "new alpha\n"),
    }

    assert svc.generate_proposal_diff(changes_fwd) == svc.generate_proposal_diff(
        changes_rev
    )


def test_proposal_diff_empty_changes(svc: DiffService) -> None:
    """Empty changes dict must return empty string."""
    assert svc.generate_proposal_diff({}) == ""


def test_proposal_diff_unchanged_file_omitted(svc: DiffService) -> None:
    """Files with no changes must not appear in the output."""
    changes = {
        "changed.md": ("old\n", "new\n"),
        "unchanged.md": ("same\n", "same\n"),
    }
    diff = svc.generate_proposal_diff(changes)
    assert "changed.md" in diff
    assert "unchanged.md" not in diff


# ---------------------------------------------------------------------------
# normalize_diff_sections — re-ordering an existing diff string
# ---------------------------------------------------------------------------


def test_normalize_diff_sections_sorts_by_path(svc: DiffService) -> None:
    """normalize_diff_sections must sort multi-file diff sections by path."""
    # Build a multi-file diff with sections in reversed order
    changes_rev = {
        "z_file.md": ("z old\n", "z new\n"),
        "a_file.md": ("a old\n", "a new\n"),
    }
    diff_reversed = svc.generate_proposal_diff(changes_rev)

    # Already sorted by generate_proposal_diff, but let's force reverse order
    sections = diff_reversed.split("--- a/")
    header = sections[0]
    part_a = "--- a/" + sections[1] if len(sections) > 1 else ""
    part_z = "--- a/" + sections[2] if len(sections) > 2 else ""

    # Build a "wrong-order" diff manually (z before a)
    wrong_order = part_z + "\n" + part_a

    normalized = svc.normalize_diff_sections(wrong_order)
    pos_a = normalized.find("a_file.md")
    pos_z = normalized.find("z_file.md")

    assert pos_a != -1 and pos_z != -1
    assert pos_a < pos_z


def test_normalize_diff_empty_string(svc: DiffService) -> None:
    """normalize_diff_sections on empty string must return empty string."""
    assert svc.normalize_diff_sections("") == ""


def test_normalize_diff_sections_deterministic_three_calls(svc: DiffService) -> None:
    """normalize_diff_sections must return identical output on every call."""
    changes = _make_changes()
    diff = svc.generate_proposal_diff(changes)

    results = [svc.normalize_diff_sections(diff) for _ in range(3)]
    assert results[0] == results[1] == results[2]
