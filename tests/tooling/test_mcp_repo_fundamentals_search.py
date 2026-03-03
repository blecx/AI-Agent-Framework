from __future__ import annotations

from pathlib import Path

import pytest

from apps.mcp.repo_fundamentals.path_guard import PathGuardError
from apps.mcp.repo_fundamentals.search_service import SearchService


def test_list_files_finds_matches(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("print('a')\n", encoding="utf-8")
    (tmp_path / "src" / "b.txt").write_text("b\n", encoding="utf-8")

    service = SearchService(repo_root=tmp_path)
    result = service.list_files(scope="src", include_glob="**/*.py")

    assert result["count"] == 1
    assert result["files"] == ["src/a.py"]


def test_search_literal_case_insensitive(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "note.md").write_text("Hello MCP\nsecond line\n", encoding="utf-8")

    service = SearchService(repo_root=tmp_path)
    result = service.search("hello", scope="docs", include_glob="**/*.md")

    assert result["count"] == 1
    assert result["matches"][0]["path"] == "docs/note.md"
    assert result["matches"][0]["line"] == 1


def test_search_regex(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "module.py").write_text("token_123\ntoken_456\n", encoding="utf-8")

    service = SearchService(repo_root=tmp_path)
    result = service.search(r"token_\d{3}", is_regexp=True, scope="src", include_glob="**/*.py")

    assert result["count"] == 2


def test_scope_forbidden_project_docs(tmp_path: Path) -> None:
    (tmp_path / "projectDocs").mkdir()
    service = SearchService(repo_root=tmp_path)

    with pytest.raises(PathGuardError):
        service.list_files(scope="projectDocs", include_glob="**/*")


def test_scope_blocks_traversal(tmp_path: Path) -> None:
    service = SearchService(repo_root=tmp_path)
    with pytest.raises(PathGuardError):
        service.search("x", scope="../")


def test_search_excludes_forbidden_subtrees_when_scope_is_repo_root(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "visible.md").write_text("needle\n", encoding="utf-8")

    (tmp_path / "projectDocs").mkdir()
    (tmp_path / "projectDocs" / "hidden.md").write_text("needle\n", encoding="utf-8")

    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "llm.json").write_text('{"token":"needle"}\n', encoding="utf-8")

    service = SearchService(repo_root=tmp_path)
    result = service.search("needle", scope=".", include_glob="**/*")

    assert result["count"] == 1
    assert result["matches"][0]["path"] == "docs/visible.md"


def test_list_files_excludes_forbidden_subtrees_when_scope_is_repo_root(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "visible.md").write_text("ok\n", encoding="utf-8")

    (tmp_path / "projectDocs").mkdir()
    (tmp_path / "projectDocs" / "hidden.md").write_text("ok\n", encoding="utf-8")

    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "llm.json").write_text('{"model":"x"}\n', encoding="utf-8")

    service = SearchService(repo_root=tmp_path)
    result = service.list_files(scope=".", include_glob="**/*")

    assert "docs/visible.md" in result["files"]
    assert "projectDocs/hidden.md" not in result["files"]
    assert "configs/llm.json" not in result["files"]
