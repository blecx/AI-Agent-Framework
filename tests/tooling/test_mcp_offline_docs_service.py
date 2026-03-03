from __future__ import annotations

from pathlib import Path

from apps.mcp.offline_docs.service import OfflineDocsService


def _service(tmp_path: Path) -> OfflineDocsService:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "guide.md").write_text("alpha line\nbeta line\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("project intro\n", encoding="utf-8")

    return OfflineDocsService(
        repo_root=tmp_path,
        index_db_path=tmp_path / ".tmp" / "mcp-offline-docs" / "docs_index.db",
        source_paths=["docs", "README.md"],
    )


def test_rebuild_and_stats(tmp_path: Path) -> None:
    service = _service(tmp_path)
    result = service.rebuild_index()

    assert result["indexed_files"] >= 2
    stats = service.stats()
    assert stats["doc_count"] >= 2


def test_search_and_read(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.rebuild_index()

    found = service.search("beta", max_results=5)
    assert found["count"] >= 1
    assert found["matches"][0]["path"] == "docs/guide.md"

    excerpt = service.read_document("docs/guide.md", start_line=2, end_line=2)
    assert excerpt["content"] == "beta line"


def test_index_auto_rebuilds_after_docs_change(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.rebuild_index()

    docs_file = tmp_path / "docs" / "guide.md"
    docs_file.write_text("alpha line\ngamma line\n", encoding="utf-8")

    found = service.search("gamma", max_results=5)
    assert found["count"] >= 1
    assert found["matches"][0]["path"] == "docs/guide.md"
