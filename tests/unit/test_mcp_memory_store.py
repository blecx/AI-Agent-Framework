"""Unit tests for MemoryStore — mcp-memory SQLite backend.

All tests use in-memory SQLite (':memory:') so no files are created.
Tests cover: lessons CRUD, keyword search, recent query, knowledge graph.
"""

import pytest

from apps.mcp.memory.store import MemoryStore


@pytest.fixture
def store() -> MemoryStore:
    """Fresh in-memory MemoryStore for each test."""
    s = MemoryStore(db_path=":memory:")
    yield s
    s.close()


# ---------------------------------------------------------------------------
# Lessons: store and retrieve
# ---------------------------------------------------------------------------


def test_store_and_get_lesson(store: MemoryStore) -> None:
    lesson_id = store.store_lesson(
        issue_number=42,
        outcome="success",
        summary="Fixed the template service bug",
        learnings=["Always check null path", "Run integration tests first"],
        repo="blecx/AI-Agent-Framework",
    )
    assert isinstance(lesson_id, int)
    assert lesson_id > 0

    lessons = store.get_lessons(42)
    assert len(lessons) == 1
    assert lessons[0]["issue_number"] == 42
    assert lessons[0]["outcome"] == "success"
    assert lessons[0]["summary"] == "Fixed the template service bug"
    assert "Always check null path" in lessons[0]["learnings"]


def test_get_lessons_returns_empty_for_unknown_issue(store: MemoryStore) -> None:
    assert store.get_lessons(9999) == []


def test_multiple_lessons_for_same_issue(store: MemoryStore) -> None:
    store.store_lesson(101, "failure", "First attempt failed", ["lesson A"])
    store.store_lesson(101, "success", "Second attempt succeeded", ["lesson B"])

    lessons = store.get_lessons(101)
    assert len(lessons) == 2
    outcomes = {l["outcome"] for l in lessons}
    assert outcomes == {"failure", "success"}


def test_store_lesson_default_repo(store: MemoryStore) -> None:
    store.store_lesson(5, "partial", "Partial fix", [])
    lessons = store.get_lessons(5)
    assert lessons[0]["repo"] == ""


# ---------------------------------------------------------------------------
# Lessons: keyword search
# ---------------------------------------------------------------------------


def test_search_similar_finds_matching_lesson(store: MemoryStore) -> None:
    store.store_lesson(10, "success", "Refactored template router code", ["use DDD"])
    store.store_lesson(11, "failure", "Broke the audit service", ["check rollback"])

    results = store.search_similar("template router")
    assert len(results) == 1
    assert results[0]["issue_number"] == 10


def test_search_similar_returns_empty_when_no_match(store: MemoryStore) -> None:
    store.store_lesson(20, "success", "Fixed widget layout", ["use flexbox"])
    results = store.search_similar("completely unrelated xyz123")
    assert results == []


def test_search_similar_respects_limit(store: MemoryStore) -> None:
    for i in range(10):
        store.store_lesson(i, "success", f"common keyword fix number {i}", [])

    results = store.search_similar("common keyword", limit=3)
    assert len(results) == 3


def test_search_similar_empty_query(store: MemoryStore) -> None:
    store.store_lesson(1, "success", "something", [])
    results = store.search_similar("")
    assert results == []


# ---------------------------------------------------------------------------
# Recent lessons
# ---------------------------------------------------------------------------


def test_get_recent_lessons_returns_latest_first(store: MemoryStore) -> None:
    store.store_lesson(1, "success", "first", [])
    store.store_lesson(2, "success", "second", [])
    store.store_lesson(3, "success", "third", [])

    recent = store.get_recent_lessons(limit=2)
    assert len(recent) == 2
    # Most recent should be issue 3
    assert recent[0]["issue_number"] == 3


def test_get_recent_lessons_default_limit(store: MemoryStore) -> None:
    for i in range(15):
        store.store_lesson(i, "success", f"lesson {i}", [])

    recent = store.get_recent_lessons()
    assert len(recent) == 10  # default limit


def test_get_recent_lessons_empty_store(store: MemoryStore) -> None:
    assert store.get_recent_lessons() == []


# ---------------------------------------------------------------------------
# Knowledge graph
# ---------------------------------------------------------------------------


def test_upsert_entity_and_get_related(store: MemoryStore) -> None:
    store.upsert_entity("apps/api/services/template_service.py", "file")
    store.upsert_entity("templates", "domain")
    store.add_relationship(
        "apps/api/services/template_service.py", "belongs_to", "templates"
    )

    related = store.get_related("apps/api/services/template_service.py")
    assert len(related) == 1
    assert related[0]["relation"] == "belongs_to"
    assert related[0]["to_entity"] == "templates"


def test_upsert_entity_is_idempotent(store: MemoryStore) -> None:
    store.upsert_entity("myfile.py", "file", {"lines": 100})
    store.upsert_entity("myfile.py", "file", {"lines": 200})  # update

    # Should still be one entity (no duplicate)
    related = store.get_related("myfile.py")
    assert related == []  # no relationships, just checking no error


def test_add_relationship_is_idempotent(store: MemoryStore) -> None:
    store.upsert_entity("service_a.py", "file")
    store.upsert_entity("domain_x", "domain")
    store.add_relationship("service_a.py", "belongs_to", "domain_x")
    store.add_relationship("service_a.py", "belongs_to", "domain_x")  # duplicate

    related = store.get_related("service_a.py")
    assert len(related) == 1  # idempotent


def test_get_related_filtered_by_relation(store: MemoryStore) -> None:
    store.upsert_entity("service.py", "file")
    store.upsert_entity("domain_a", "domain")
    store.upsert_entity("issue_99", "issue")
    store.add_relationship("service.py", "belongs_to", "domain_a")
    store.add_relationship("service.py", "changed_by", "issue_99")

    belongs = store.get_related("service.py", relation="belongs_to")
    assert len(belongs) == 1
    assert belongs[0]["to_entity"] == "domain_a"

    changed = store.get_related("service.py", relation="changed_by")
    assert len(changed) == 1
    assert changed[0]["to_entity"] == "issue_99"


def test_get_related_unknown_entity(store: MemoryStore) -> None:
    assert store.get_related("nonexistent_entity") == []
