from __future__ import annotations

from pathlib import Path

import pytest

from apps.mcp.repo_fundamentals.filesystem_service import FilesystemService
from apps.mcp.repo_fundamentals.path_guard import PathGuardError


def test_write_read_and_list_dir(tmp_path: Path) -> None:
    service = FilesystemService(repo_root=tmp_path)

    write_result = service.write_text("src/test.txt", "hello")
    assert write_result["path"] == "src/test.txt"

    read_result = service.read_text("src/test.txt")
    assert read_result["content"] == "hello"

    list_result = service.list_dir("src")
    assert "src/test.txt" in list_result["entries"]


def test_move_and_copy_path(tmp_path: Path) -> None:
    service = FilesystemService(repo_root=tmp_path)
    service.write_text("a.txt", "a")

    move_result = service.move_path("a.txt", "nested/b.txt")
    assert move_result["moved_to"] == "nested/b.txt"

    copy_result = service.copy_path("nested/b.txt", "nested/c.txt")
    assert copy_result["copied_to"] == "nested/c.txt"

    assert (tmp_path / "nested" / "b.txt").exists()
    assert (tmp_path / "nested" / "c.txt").exists()


def test_delete_dir_requires_recursive(tmp_path: Path) -> None:
    service = FilesystemService(repo_root=tmp_path)
    service.write_text("dir/file.txt", "x")

    with pytest.raises(ValueError):
        service.delete_path("dir", recursive=False)

    service.delete_path("dir", recursive=True)
    assert not (tmp_path / "dir").exists()


def test_blocks_forbidden_project_docs(tmp_path: Path) -> None:
    service = FilesystemService(repo_root=tmp_path)
    with pytest.raises(PathGuardError):
        service.write_text("projectDocs/secret.md", "x")


def test_blocks_forbidden_llm_config(tmp_path: Path) -> None:
    service = FilesystemService(repo_root=tmp_path)
    with pytest.raises(PathGuardError):
        service.write_text("configs/llm.json", "{}")


def test_blocks_traversal(tmp_path: Path) -> None:
    service = FilesystemService(repo_root=tmp_path)
    with pytest.raises(PathGuardError):
        service.read_text("../outside.txt")
