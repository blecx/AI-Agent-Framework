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
