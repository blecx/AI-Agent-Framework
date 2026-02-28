from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .path_guard import RepoPathGuard


@dataclass
class SearchService:
    repo_root: Path

    def __post_init__(self) -> None:
        self.repo_root = self.repo_root.resolve()
        self.path_guard = RepoPathGuard(self.repo_root)

    def _iter_files(self, scope: str, include_glob: str) -> list[Path]:
        resolved_scope = self.path_guard.resolve_relative_path(scope, allow_nonexistent=False)
        if not resolved_scope.is_dir():
            raise ValueError("scope must resolve to a directory")

        files: list[Path] = []
        for path in resolved_scope.rglob("*"):
            if not path.is_file():
                continue

            relative = path.relative_to(self.repo_root).as_posix()
            if fnmatch.fnmatch(relative, include_glob):
                files.append(path)
        return files

    def list_files(self, scope: str = ".", include_glob: str = "**/*", max_results: int = 200) -> dict[str, Any]:
        if max_results <= 0 or max_results > 2000:
            raise ValueError("max_results must be between 1 and 2000")

        files = self._iter_files(scope=scope, include_glob=include_glob)[:max_results]
        return {
            "count": len(files),
            "files": [str(path.relative_to(self.repo_root)) for path in files],
        }

    def search(
        self,
        query: str,
        *,
        is_regexp: bool = False,
        scope: str = ".",
        include_glob: str = "**/*",
        max_results: int = 200,
    ) -> dict[str, Any]:
        query_text = query.strip()
        if not query_text:
            raise ValueError("query is required")
        if max_results <= 0 or max_results > 2000:
            raise ValueError("max_results must be between 1 and 2000")

        files = self._iter_files(scope=scope, include_glob=include_glob)

        if is_regexp:
            matcher = re.compile(query_text, flags=re.IGNORECASE)

            def is_match(line: str) -> bool:
                return bool(matcher.search(line))
        else:
            query_lower = query_text.lower()

            def is_match(line: str) -> bool:
                return query_lower in line.lower()

        matches: list[dict[str, Any]] = []
        for file_path in files:
            if len(matches) >= max_results:
                break

            try:
                text = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            for line_no, line in enumerate(text.splitlines(), start=1):
                if is_match(line):
                    matches.append(
                        {
                            "path": str(file_path.relative_to(self.repo_root)),
                            "line": line_no,
                            "text": line,
                        }
                    )
                    if len(matches) >= max_results:
                        break

        return {
            "query": query_text,
            "is_regexp": is_regexp,
            "count": len(matches),
            "matches": matches,
        }
