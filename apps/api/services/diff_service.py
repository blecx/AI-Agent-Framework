"""
Diff service for generating deterministic, stable diffs.
Handles conflict detection and ensures diff preview accuracy.
"""

import difflib
import hashlib
from typing import Dict, Any, List, Optional, Tuple


class DiffService:
    """Service for deterministic diff generation and conflict detection."""

    def __init__(self):
        """Initialize diff service."""
        pass

    def generate_diff(
        self,
        old_content: str,
        new_content: str,
        context_lines: int = 3,
        normalize_whitespace: bool = True,
    ) -> str:
        """
        Generate deterministic unified diff between two content versions.

        Args:
            old_content: Original content
            new_content: Modified content
            context_lines: Number of context lines (default 3)
            normalize_whitespace: Strip trailing whitespace (default True)

        Returns:
            Unified diff string (deterministic)
        """
        # Normalize whitespace if requested (prevents diff noise)
        if normalize_whitespace:
            old_content = self._normalize_whitespace(old_content)
            new_content = self._normalize_whitespace(new_content)

        # Generate unified diff with consistent parameters
        # Use keepends=False to avoid newline issues
        old_lines = old_content.splitlines(keepends=False)
        new_lines = new_content.splitlines(keepends=False)

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile="a/artifact",
            tofile="b/artifact",
            lineterm="",  # Don't add extra lineterm
            n=context_lines,
        )

        return "\n".join(diff)

    def generate_proposal_diff(
        self,
        changes: Dict[str, Tuple[str, str]],
        context_lines: int = 3,
        normalize_whitespace: bool = True,
    ) -> str:
        """
        Generate a deterministic multi-file unified diff for proposal previews.

        Entries are sorted by file path (lexicographic) before assembly,
        ensuring identical output for identical input regardless of dict
        insertion order or runtime environment.

        Args:
            changes: Mapping of ``{file_path: (old_content, new_content)}``
            context_lines: Number of context lines per hunk (default 3)
            normalize_whitespace: Strip trailing whitespace (default True)

        Returns:
            Concatenated unified diff string, sections ordered by file path.
        """
        if not changes:
            return ""

        # Sort by file path for stable, deterministic ordering
        sorted_paths: List[str] = sorted(changes.keys())

        sections: List[str] = []
        for file_path in sorted_paths:
            old_content, new_content = changes[file_path]
            section = self.generate_diff(
                old_content,
                new_content,
                context_lines=context_lines,
                normalize_whitespace=normalize_whitespace,
            )
            if section:
                # Replace generic filenames with the actual file path
                section = section.replace(
                    "--- a/artifact", f"--- a/{file_path}", 1
                ).replace("+++ b/artifact", f"+++ b/{file_path}", 1)
                sections.append(section)

        return "\n".join(sections)

    def normalize_diff_sections(self, diff_str: str) -> str:
        """
        Normalize an existing multi-file unified diff for stable ordering.

        Splits the diff into per-file sections and re-joins them sorted by
        the ``--- a/<path>`` filename header.  Within each section the hunk
        order (ascending line numbers) is preserved as produced by
        ``difflib.unified_diff``.

        Args:
            diff_str: Existing unified diff string (may be multi-file)

        Returns:
            Normalized diff string with sections sorted by file path.
        """
        if not diff_str:
            return diff_str

        # Split into per-file sections on the "--- " boundary
        raw_sections: List[str] = []
        current: List[str] = []
        for line in diff_str.splitlines():
            if line.startswith("--- ") and current:
                raw_sections.append("\n".join(current))
                current = [line]
            else:
                current.append(line)
        if current:
            raw_sections.append("\n".join(current))

        # Sort sections by the filename extracted from the "--- a/<path>" header
        def _section_key(section: str) -> str:
            first_line = section.splitlines()[0] if section else ""
            # Handles "--- a/path" and "--- path" formats
            return first_line.replace("--- a/", "").replace("--- ", "").strip()

        raw_sections.sort(key=_section_key)
        return "\n".join(raw_sections)

    def apply_diff(self, old_content: str, diff_str: str) -> str:
        """
        Apply a unified diff to content using patch-style application.

        Args:
            old_content: Original content
            diff_str: Unified diff string

        Returns:
            New content after applying diff

        Raises:
            ValueError: If diff cannot be applied
        """
        # Use difflib to generate expected result from diff
        # This is a simple implementation; production might use subprocess/patch
        old_lines = old_content.splitlines(keepends=False)
        diff_lines = diff_str.splitlines()

        # Parse the diff to rebuild the new content
        result_lines = []
        old_line_idx = 0
        in_hunk = False
        hunk_old_start = 0

        for line in diff_lines:
            # Skip file headers
            if line.startswith("---") or line.startswith("+++"):
                continue

            # Parse hunk header @@ -old_start,old_count +new_start,new_count @@
            if line.startswith("@@"):
                in_hunk = True
                # Extract old start position
                parts = line.split()
                if len(parts) >= 2:
                    old_range = parts[1]  # -old_start,old_count
                    hunk_old_start = int(old_range.split(",")[0][1:]) - 1  # 0-indexed

                # Copy unchanged lines before this hunk
                while old_line_idx < hunk_old_start and old_line_idx < len(old_lines):
                    result_lines.append(old_lines[old_line_idx])
                    old_line_idx += 1
                continue

            if not in_hunk:
                continue

            # Process hunk lines
            if line.startswith(" "):  # Context line (unchanged)
                result_lines.append(line[1:])
                old_line_idx += 1
            elif line.startswith("-"):  # Removed line
                # Skip this line in old content
                old_line_idx += 1
            elif line.startswith("+"):  # Added line
                # Add this new line to result
                result_lines.append(line[1:])

        # Append any remaining unchanged lines from old content
        while old_line_idx < len(old_lines):
            result_lines.append(old_lines[old_line_idx])
            old_line_idx += 1

        # Join lines with newlines (handle empty result)
        if result_lines:
            return "\n".join(result_lines) + "\n"
        return ""

    def compute_content_hash(self, content: str) -> str:
        """
        Compute SHA-256 hash of content for conflict detection.

        Args:
            content: Content to hash

        Returns:
            Hex digest of SHA-256 hash
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def detect_conflict(
        self,
        expected_hash: str,
        current_content: str,
    ) -> bool:
        """
        Detect if content has changed since proposal was created.

        Args:
            expected_hash: Expected content hash from proposal
            current_content: Current artifact content

        Returns:
            True if conflict detected (hashes don't match)
        """
        current_hash = self.compute_content_hash(current_content)
        return current_hash != expected_hash

    def verify_diff_preview(
        self,
        old_content: str,
        diff_str: str,
        expected_result: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Verify diff preview matches actual apply result.

        Args:
            old_content: Original content
            diff_str: Diff to apply
            expected_result: Optional expected result (for testing)

        Returns:
            Dictionary with verification status and details
        """
        try:
            actual_result = self.apply_diff(old_content, diff_str)

            if expected_result is not None:
                matches = actual_result == expected_result
                return {
                    "preview_accurate": matches,
                    "actual_hash": self.compute_content_hash(actual_result),
                    "expected_hash": self.compute_content_hash(expected_result),
                }
            else:
                return {
                    "preview_accurate": True,
                    "actual_hash": self.compute_content_hash(actual_result),
                }

        except ValueError as e:
            return {
                "preview_accurate": False,
                "error": str(e),
            }

    def _normalize_whitespace(self, content: str) -> str:
        """
        Normalize whitespace in content to prevent diff noise.

        Args:
            content: Content to normalize

        Returns:
            Normalized content with trailing whitespace stripped
        """
        lines = content.splitlines(keepends=True)
        normalized = [
            line.rstrip() + "\n" if line.endswith("\n") else line.rstrip()
            for line in lines
        ]
        return "".join(normalized)
