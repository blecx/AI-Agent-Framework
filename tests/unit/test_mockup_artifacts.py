from pathlib import Path

import pytest

from agents.tooling.mockup_artifacts import (
    get_mockup_dir,
    list_mockup_images,
    write_mockup_index_html,
)


def test_get_mockup_dir_is_deterministic(tmp_path: Path):
    assert get_mockup_dir(123, base_dir=tmp_path) == tmp_path / "issue-123"


def test_list_mockup_images_empty(tmp_path: Path):
    assert list_mockup_images(tmp_path) == []


def test_write_mockup_index_html_no_images(tmp_path: Path):
    out = write_mockup_index_html(tmp_path)
    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "No images found" in html


def test_write_mockup_index_html_with_images(tmp_path: Path):
    (tmp_path / "b.png").write_bytes(b"fake")
    (tmp_path / "a.jpg").write_bytes(b"fake")

    out = write_mockup_index_html(tmp_path)
    html = out.read_text(encoding="utf-8")

    assert "Previous" in html
    assert "Next" in html
    assert "Return to list" in html

    # Sorted by filename
    assert "a.jpg" in html
    assert "b.png" in html


def test_write_mockup_index_html_ignores_non_images(tmp_path: Path):
    (tmp_path / "note.txt").write_text("hi", encoding="utf-8")
    out = write_mockup_index_html(tmp_path)
    html = out.read_text(encoding="utf-8")
    assert "note.txt" not in html
