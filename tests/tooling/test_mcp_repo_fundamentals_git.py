from __future__ import annotations

from pathlib import Path

import pytest

from apps.mcp.repo_fundamentals.git_service import GitService
from apps.mcp.repo_fundamentals.path_guard import PathGuardError, RepoPathGuard


def test_path_guard_blocks_forbidden_targets(tmp_path: Path) -> None:
    guard = RepoPathGuard(tmp_path)

    with pytest.raises(PathGuardError):
        guard.resolve_relative_path("projectDocs/test.md")

    with pytest.raises(PathGuardError):
        guard.resolve_relative_path("configs/llm.json")


def test_path_guard_blocks_traversal(tmp_path: Path) -> None:
    guard = RepoPathGuard(tmp_path)

    with pytest.raises(PathGuardError):
        guard.resolve_relative_path("../outside.txt")


def test_path_guard_blocks_symlink_escape(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside"
    outside.mkdir(parents=True, exist_ok=True)
    (outside / "secret.txt").write_text("x", encoding="utf-8")

    link = tmp_path / "linked"
    link.symlink_to(outside, target_is_directory=True)

    guard = RepoPathGuard(tmp_path)
    with pytest.raises(PathGuardError):
        guard.resolve_relative_path("linked/secret.txt")


def test_git_service_validated_paths_block_forbidden(tmp_path: Path) -> None:
    service = GitService(repo_root=tmp_path)
    with pytest.raises(PathGuardError):
        service._validated_paths(["projectDocs/a.md"])


def test_git_service_add_uses_validated_relative_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    file_path = tmp_path / "README.md"
    file_path.write_text("ok", encoding="utf-8")

    service = GitService(repo_root=tmp_path)

    captured: dict[str, list[str]] = {}

    def fake_run(args: list[str]) -> str:
        captured["args"] = args
        return ""

    monkeypatch.setattr(service, "_run_git", fake_run)
    result = service.add(paths=["README.md"])

    assert result["added"] == ["README.md"]
    assert captured["args"] == ["add", "--", "README.md"]


def test_git_service_branch_current(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service = GitService(repo_root=tmp_path)

    def fake_run(args: list[str]) -> str:
        assert args == ["branch", "--show-current"]
        return "main\n"

    monkeypatch.setattr(service, "_run_git", fake_run)
    result = service.branch_current()

    assert result == {"branch": "main"}


def test_git_service_branch_list(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service = GitService(repo_root=tmp_path)

    def fake_run(args: list[str]) -> str:
        assert args == ["branch", "--list", "--format=%(refname:short)"]
        return "main\nfeature/a\n"

    monkeypatch.setattr(service, "_run_git", fake_run)
    result = service.branch_list()

    assert result["branches"] == ["main", "feature/a"]
    assert result["count"] == 2


def test_git_service_blame_validates_range_and_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "README.md").write_text("line1\nline2\n", encoding="utf-8")
    service = GitService(repo_root=tmp_path)

    captured: dict[str, list[str]] = {}

    def fake_run(args: list[str]) -> str:
        captured["args"] = args
        return "author Test\n"

    monkeypatch.setattr(service, "_run_git", fake_run)
    result = service.blame(path="README.md", line_start=1, line_end=2)

    assert result["path"] == "README.md"
    assert captured["args"] == ["blame", "--line-porcelain", "-L", "1,2", "--", "README.md"]


def test_git_service_blame_rejects_partial_range(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("line1\n", encoding="utf-8")
    service = GitService(repo_root=tmp_path)

    with pytest.raises(ValueError):
        service.blame(path="README.md", line_start=1)
