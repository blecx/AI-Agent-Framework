"""
Unit tests for DiffService.
Tests diff generation, application, conflict detection, and determinism.
"""

import pytest
import sys
import os

# Add apps/api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))

from services.diff_service import DiffService  # noqa: E402


class TestDiffService:
    """Test suite for DiffService."""

    @pytest.fixture
    def diff_service(self):
        """Create DiffService instance."""
        return DiffService()

    def test_generate_simple_diff(self, diff_service):
        """Test generating a simple unified diff."""
        old_content = "Line 1\nLine 2\nLine 3\n"
        new_content = "Line 1\nLine 2 Modified\nLine 3\n"

        diff = diff_service.generate_diff(old_content, new_content)

        assert diff
        assert "Line 2 Modified" in diff
        assert "---" in diff
        assert "+++" in diff
        assert "@@" in diff

    def test_apply_simple_diff(self, diff_service):
        """Test applying a simple diff."""
        old_content = "Line 1\nLine 2\nLine 3\n"
        new_content = "Line 1\nLine 2 Modified\nLine 3\n"

        diff = diff_service.generate_diff(old_content, new_content)
        result = diff_service.apply_diff(old_content, diff)

        assert result == new_content

    def test_diff_determinism(self, diff_service):
        """Test that same changes produce identical diffs."""
        old_content = "Line 1\nLine 2\nLine 3\n"
        new_content = "Line 1\nLine 2 Modified\nLine 3\n"

        # Generate diff 100 times
        diffs = [
            diff_service.generate_diff(old_content, new_content) for _ in range(100)
        ]

        # All diffs should be identical
        assert len(set(diffs)) == 1

    def test_whitespace_normalization(self, diff_service):
        """Test whitespace normalization prevents diff noise."""
        old_content = "Line 1  \nLine 2\nLine 3  \n"
        new_content = "Line 1\nLine 2\nLine 3\n"

        diff = diff_service.generate_diff(
            old_content, new_content, normalize_whitespace=True
        )

        # Should produce empty diff (only whitespace changed)
        # Check if diff has no content changes
        diff_lines = [
            line
            for line in diff.splitlines()
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
        ]
        assert len(diff_lines) == 0

    def test_compute_content_hash(self, diff_service):
        """Test content hash computation."""
        content1 = "Line 1\nLine 2\n"
        content2 = "Line 1\nLine 2\n"
        content3 = "Line 1\nLine 3\n"

        hash1 = diff_service.compute_content_hash(content1)
        hash2 = diff_service.compute_content_hash(content2)
        hash3 = diff_service.compute_content_hash(content3)

        assert hash1 == hash2  # Same content
        assert hash1 != hash3  # Different content
        assert len(hash1) == 64  # SHA-256 hex digest

    def test_detect_conflict_no_change(self, diff_service):
        """Test conflict detection when content hasn't changed."""
        content = "Line 1\nLine 2\n"
        expected_hash = diff_service.compute_content_hash(content)

        conflict = diff_service.detect_conflict(expected_hash, content)
        assert not conflict

    def test_detect_conflict_changed(self, diff_service):
        """Test conflict detection when content has changed."""
        old_content = "Line 1\nLine 2\n"
        new_content = "Line 1\nLine 3\n"
        expected_hash = diff_service.compute_content_hash(old_content)

        conflict = diff_service.detect_conflict(expected_hash, new_content)
        assert conflict

    def test_verify_diff_preview_accurate(self, diff_service):
        """Test diff preview verification (matches expected)."""
        old_content = "Line 1\nLine 2\n"
        new_content = "Line 1\nLine 2 Modified\n"

        diff = diff_service.generate_diff(old_content, new_content)
        verification = diff_service.verify_diff_preview(
            old_content, diff, expected_result=new_content
        )

        assert verification["preview_accurate"] is True

    def test_verify_diff_preview_mismatch(self, diff_service):
        """Test diff preview verification (doesn't match expected)."""
        old_content = "Line 1\nLine 2\n"
        new_content = "Line 1\nLine 2 Modified\n"
        wrong_expected = "Line 1\nLine 2 Wrong\n"

        diff = diff_service.generate_diff(old_content, new_content)
        verification = diff_service.verify_diff_preview(
            old_content, diff, expected_result=wrong_expected
        )

        assert verification["preview_accurate"] is False

    def test_apply_diff_multiline(self, diff_service):
        """Test applying diff with multiple changes."""
        old_content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
        new_content = "Line 1\nLine 2 Modified\nLine 3\nLine 4 Changed\nLine 5\n"

        diff = diff_service.generate_diff(old_content, new_content)
        result = diff_service.apply_diff(old_content, diff)

        assert result == new_content

    def test_apply_diff_added_lines(self, diff_service):
        """Test applying diff with added lines."""
        old_content = "Line 1\nLine 2\n"
        new_content = "Line 1\nLine 1.5\nLine 2\n"

        diff = diff_service.generate_diff(old_content, new_content)
        result = diff_service.apply_diff(old_content, diff)

        assert result == new_content

    def test_apply_diff_removed_lines(self, diff_service):
        """Test applying diff with removed lines."""
        old_content = "Line 1\nLine 2\nLine 3\n"
        new_content = "Line 1\nLine 3\n"

        diff = diff_service.generate_diff(old_content, new_content)
        result = diff_service.apply_diff(old_content, diff)

        assert result == new_content

    def test_diff_context_lines(self, diff_service):
        """Test diff generation with custom context lines."""
        old_content = "\n".join([f"Line {i}" for i in range(1, 11)]) + "\n"
        new_content = old_content.replace("Line 5", "Line 5 Modified")

        diff_3_ctx = diff_service.generate_diff(
            old_content, new_content, context_lines=3
        )
        diff_1_ctx = diff_service.generate_diff(
            old_content, new_content, context_lines=1
        )

        # More context lines = larger diff
        assert len(diff_3_ctx) > len(diff_1_ctx)
        assert "Line 5 Modified" in diff_3_ctx
        assert "Line 5 Modified" in diff_1_ctx
