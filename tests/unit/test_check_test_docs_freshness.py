"""
tests/unit/test_check_test_docs_freshness.py

Unit tests for scripts/check_test_docs_freshness.py freshness checker.
Covers: extract_headings, check_file, and end-to-end main() behaviour.
"""

import sys
import textwrap
from pathlib import Path

import pytest

# Ensure the scripts directory is on the path so we can import the module.
SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from check_test_docs_freshness import (  # noqa: E402
    REQUIRED_SECTIONS,
    check_file,
    extract_headings,
    main,
)


# ---------------------------------------------------------------------------
# extract_headings
# ---------------------------------------------------------------------------

class TestExtractHeadings:
    def test_finds_h2_headings(self):
        text = "## Architecture\n## Fixtures\n"
        result = extract_headings(text)
        assert "## Architecture" in result
        assert "## Fixtures" in result

    def test_finds_mixed_levels(self):
        text = "# Title\n## Section\n### Sub\n"
        result = extract_headings(text)
        assert "# Title" in result
        assert "## Section" in result
        assert "### Sub" in result

    def test_returns_sorted(self):
        text = "## Zebra\n## Apple\n## Mango\n"
        result = extract_headings(text)
        assert result == sorted(result)

    def test_empty_text(self):
        assert extract_headings("") == []

    def test_ignores_inline_hashes(self):
        text = "Some text with # in the middle\n"
        assert extract_headings(text) == []


# ---------------------------------------------------------------------------
# check_file
# ---------------------------------------------------------------------------

class TestCheckFile:
    def test_all_sections_present(self, tmp_path):
        doc = tmp_path / "tests" / "e2e" / "tui" / "README.md"
        doc.parent.mkdir(parents=True)
        doc.write_text(
            textwrap.dedent("""\
                ## Architecture
                some content

                ## Fixtures
                some content

                ## Running Tests
                some content
            """),
            encoding="utf-8",
        )
        errors = check_file(tmp_path, "tests/e2e/tui/README.md", ["## Architecture", "## Fixtures", "## Running Tests"])
        assert errors == []

    def test_missing_section_reported(self, tmp_path):
        doc = tmp_path / "tests" / "e2e" / "tui" / "README.md"
        doc.parent.mkdir(parents=True)
        doc.write_text("## Architecture\n## Fixtures\n", encoding="utf-8")
        errors = check_file(tmp_path, "tests/e2e/tui/README.md", ["## Architecture", "## Fixtures", "## Running Tests"])
        assert len(errors) == 1
        assert "## Running Tests" in errors[0]
        assert "tests/e2e/tui/README.md" in errors[0]

    def test_missing_file_reported(self, tmp_path):
        errors = check_file(tmp_path, "tests/nonexistent/README.md", ["## Foo"])
        assert len(errors) == 1
        assert "MISSING FILE" in errors[0]

    def test_multiple_missing_sections(self, tmp_path):
        doc = tmp_path / "tests" / "README.md"
        doc.parent.mkdir(parents=True)
        doc.write_text("# Just a title\n", encoding="utf-8")
        errors = check_file(tmp_path, "tests/README.md", ["## Running tests locally", "## TUI E2E notes"])
        assert len(errors) == 2

    def test_errors_sorted_by_section(self, tmp_path):
        doc = tmp_path / "tests" / "README.md"
        doc.parent.mkdir(parents=True)
        doc.write_text("# Title\n", encoding="utf-8")
        required = ["## Zebra", "## Apple", "## Mango"]
        errors = check_file(tmp_path, "tests/README.md", required)
        # Errors should mention sections in sorted order
        sections_in_errors = [e.split('"')[1] for e in errors]
        assert sections_in_errors == sorted(sections_in_errors)


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------

class TestMainIntegration:
    """Run main() against the actual repo docs — they must pass."""

    def test_main_passes_on_current_docs(self, capsys):
        """Current repo docs contain all required sections → exit 0."""
        result = main()
        assert result == 0

    def test_required_sections_config_non_empty(self):
        assert len(REQUIRED_SECTIONS) >= 2

    def test_each_file_has_required_sections(self):
        for path, sections in REQUIRED_SECTIONS.items():
            assert len(sections) >= 1, f"{path} has no required sections defined"
