"""
Integration tests for diff stability and determinism.
Tests that diffs are consistent across multiple runs and handle edge cases.
"""

import pytest
import sys
import os

# Add apps/api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))

from services.diff_service import DiffService  # noqa: E402


class TestDiffStability:
    """Integration tests for diff stability."""

    @pytest.fixture
    def diff_service(self):
        """Create DiffService instance."""
        return DiffService()

    def test_diff_determinism_1000_iterations(self, diff_service):
        """
        Test that same changes produce identical diffs over 1000 iterations.

        This property-based test ensures diff generation is truly deterministic.
        """
        old_content = """# Project Management Plan

## Overview
This is a sample project management plan.

## Scope
- Deliverable 1
- Deliverable 2
- Deliverable 3

## Timeline
Start: 2026-03-01
End: 2026-06-01
"""

        new_content = """# Project Management Plan

## Overview
This is a sample project management plan with updates.

## Scope
- Deliverable 1 (Updated)
- Deliverable 2
- Deliverable 3
- Deliverable 4 (New)

## Timeline
Start: 2026-03-01
End: 2026-08-01
"""

        # Generate diff 1000 times
        diffs = []
        for _ in range(1000):
            diff = diff_service.generate_diff(old_content, new_content)
            diffs.append(diff)

        # All diffs must be identical
        unique_diffs = set(diffs)
        assert (
            len(unique_diffs) == 1
        ), f"Found {len(unique_diffs)} unique diffs (expected 1)"

        # Verify diff can be applied
        result = diff_service.apply_diff(old_content, diffs[0])
        assert result == new_content

    def test_whitespace_only_changes_no_noise(self, diff_service):
        """Test that whitespace-only changes don't create diff noise."""
        old_content = "Line 1  \nLine 2\t\nLine 3   \n"
        new_content = "Line 1\nLine 2\nLine 3\n"

        # With normalization
        diff_normalized = diff_service.generate_diff(
            old_content, new_content, normalize_whitespace=True
        )

        # Should not show content changes (only header lines)
        content_lines = [
            line
            for line in diff_normalized.splitlines()
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
        ]
        assert len(content_lines) == 0, "Whitespace-only changes created diff noise"

    def test_diff_preview_matches_apply_result(self, diff_service):
        """Test that diff preview exactly matches actual apply result."""
        old_content = """Function: calculate_total
Args: items (list), tax_rate (float)
Returns: float

Description:
Calculates the total cost including tax.
"""

        new_content = """Function: calculate_total
Args: items (list), tax_rate (float), discount (float)
Returns: float

Description:
Calculates the total cost including tax and discount.
Supports percentage-based discounts.
"""

        # Generate diff
        diff = diff_service.generate_diff(old_content, new_content)

        # Apply diff
        actual_result = diff_service.apply_diff(old_content, diff)

        # Verify byte-for-byte match
        verification = diff_service.verify_diff_preview(
            old_content, diff, expected_result=new_content
        )

        assert verification["preview_accurate"] is True
        assert actual_result == new_content
        assert verification["actual_hash"] == verification["expected_hash"]

    def test_concurrent_proposals_conflict_detection(self, diff_service):
        """Test detecting conflicts when artifact has changed."""
        # Original artifact
        original_content = """# Artifact
Version: 1.0
Status: Draft
"""

        # User A's version (proposal 1)
        version_a = """# Artifact
Version: 1.1
Status: Draft
"""

        # Proposal 1 applied first
        original_hash = diff_service.compute_content_hash(original_content)

        # Proposal 2 tries to apply, but artifact has changed
        current_content = version_a
        conflict = diff_service.detect_conflict(original_hash, current_content)

        assert conflict is True, "Failed to detect concurrent proposal conflict"

    def test_line_numbers_accurate(self, diff_service):
        """Test that line numbers in diffs are accurate (no off-by-one errors)."""
        lines = [f"Line {i}\n" for i in range(1, 21)]
        old_content = "".join(lines)

        # Modify line 10
        new_lines = lines.copy()
        new_lines[9] = "Line 10 MODIFIED\n"
        new_content = "".join(new_lines)

        diff = diff_service.generate_diff(old_content, new_content, context_lines=3)

        # Parse diff to find line numbers
        for line in diff.splitlines():
            if line.startswith("@@"):
                # Extract line numbers from hunk header
                # Format: @@ -old_start,old_count +new_start,new_count @@
                assert (
                    "-7," in line or "-8," in line
                ), "Line numbers inaccurate in hunk header"
                break

    def test_context_lines_included(self, diff_service):
        """Test that context lines (3 before/after) are included in unified diff."""
        lines = [f"Line {i}\n" for i in range(1, 11)]
        old_content = "".join(lines)

        # Modify line 5
        new_lines = lines.copy()
        new_lines[4] = "Line 5 MODIFIED\n"
        new_content = "".join(new_lines)

        diff = diff_service.generate_diff(old_content, new_content, context_lines=3)

        # Check context lines are present
        diff_content = diff.splitlines()
        context_count = sum(1 for line in diff_content if line.startswith(" "))

        # Should have 3 lines before and 3 lines after (6 total context)
        assert context_count >= 6, f"Expected >= 6 context lines, got {context_count}"

    def test_large_diff_performance(self, diff_service):
        """Test diff generation and application with large content."""
        import time

        # Generate large content (100 lines)
        old_lines = [f"Line {i}: {'x' * 50}\n" for i in range(1, 101)]
        old_content = "".join(old_lines)

        # Modify 10 random lines
        new_lines = old_lines.copy()
        for i in [10, 25, 40, 55, 70, 85]:
            new_lines[i] = f"Line {i+1}: MODIFIED {'y' * 40}\n"
        new_content = "".join(new_lines)

        # Time diff generation
        start = time.time()
        diff = diff_service.generate_diff(old_content, new_content)
        gen_time = time.time() - start

        # Time diff application
        start = time.time()
        result = diff_service.apply_diff(old_content, diff)
        apply_time = time.time() - start

        # Verify correctness
        assert result == new_content

        # Performance check (should be fast)
        assert gen_time < 1.0, f"Diff generation too slow: {gen_time:.3f}s"
        assert apply_time < 1.0, f"Diff application too slow: {apply_time:.3f}s"

    def test_empty_content_edge_case(self, diff_service):
        """Test diff with empty content (edge case)."""
        old_content = ""
        new_content = "New content\n"

        diff = diff_service.generate_diff(old_content, new_content)
        result = diff_service.apply_diff(old_content, diff)

        assert result == new_content

    def test_no_changes_edge_case(self, diff_service):
        """Test diff when content hasn't changed (edge case)."""
        content = "Line 1\nLine 2\nLine 3\n"

        diff = diff_service.generate_diff(content, content)
        result = diff_service.apply_diff(content, diff)

        # Empty diff should still work
        assert result == content
