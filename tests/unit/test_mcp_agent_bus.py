"""Unit tests for AgentBus — mcp-agent-bus SQLite backend.

All tests use in-memory SQLite (':memory:') so no files are created.
Tests cover: create run, write plan, approve, snapshots, validations,
             checkpoints, context packet, status transitions, error cases.
"""

import pytest

from apps.mcp.agent_bus.bus import AgentBus, InvalidStatusTransitionError


@pytest.fixture
def bus() -> AgentBus:
    """Fresh in-memory AgentBus for each test."""
    b = AgentBus(db_path=":memory:")
    yield b
    b.close()


# ---------------------------------------------------------------------------
# Task runs: create and status
# ---------------------------------------------------------------------------


def test_create_run_returns_uuid(bus: AgentBus) -> None:
    run_id = bus.create_run(issue_number=42)
    assert isinstance(run_id, str)
    assert len(run_id) == 36  # UUID format


def test_create_run_sets_initial_status(bus: AgentBus) -> None:
    run_id = bus.create_run(issue_number=42, repo="owner/repo")
    run = bus.get_run(run_id)
    assert run is not None
    assert run["status"] == "created"
    assert run["issue_number"] == 42
    assert run["repo"] == "owner/repo"


def test_get_run_returns_none_for_unknown(bus: AgentBus) -> None:
    assert bus.get_run("nonexistent-run-id") is None


def test_set_status_valid_transition(bus: AgentBus) -> None:
    run_id = bus.create_run(101)
    bus.set_status(run_id, "routing")
    assert bus.get_run(run_id)["status"] == "routing"


def test_set_status_invalid_transition_raises(bus: AgentBus) -> None:
    run_id = bus.create_run(101)
    with pytest.raises(InvalidStatusTransitionError):
        bus.set_status(run_id, "done")  # can't jump from created → done


def test_set_status_unknown_run_raises(bus: AgentBus) -> None:
    with pytest.raises(ValueError, match="Unknown run_id"):
        bus.set_status("bad-id", "routing")


def test_set_status_any_to_failed(bus: AgentBus) -> None:
    run_id = bus.create_run(101)
    bus.set_status(run_id, "failed")
    assert bus.get_run(run_id)["status"] == "failed"


def test_set_status_terminal_state_no_transitions(bus: AgentBus) -> None:
    run_id = bus.create_run(101)
    # Walk to done
    for status in ["routing", "planning", "awaiting_approval", "approved",
                   "coding", "validating", "reviewing", "pr_created", "done"]:
        bus.set_status(run_id, status)
    with pytest.raises(InvalidStatusTransitionError):
        bus.set_status(run_id, "failed")  # terminal — no outgoing transitions


# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------


def test_write_and_get_plan(bus: AgentBus) -> None:
    run_id = bus.create_run(55)
    bus.write_plan(
        run_id=run_id,
        goal="Add template CRUD endpoints",
        files=["apps/api/routers/templates.py", "tests/unit/test_templates.py"],
        acceptance_criteria=["GET /templates returns 200", "POST /templates creates record"],
        validation_cmds=["pytest tests/unit/", "flake8 apps/api/"],
        estimated_minutes=45,
    )

    plan = bus.get_plan(run_id)
    assert plan is not None
    assert plan["goal"] == "Add template CRUD endpoints"
    assert "apps/api/routers/templates.py" in plan["files"]
    assert plan["estimated_minutes"] == 45
    assert isinstance(plan["acceptance_criteria"], list)


def test_write_plan_is_idempotent(bus: AgentBus) -> None:
    run_id = bus.create_run(56)
    bus.write_plan(run_id=run_id, goal="First goal", files=[], acceptance_criteria=[], validation_cmds=[])
    bus.write_plan(run_id=run_id, goal="Updated goal", files=["new_file.py"], acceptance_criteria=[], validation_cmds=[])

    plan = bus.get_plan(run_id)
    assert plan["goal"] == "Updated goal"
    assert "new_file.py" in plan["files"]


def test_get_plan_returns_none_when_not_set(bus: AgentBus) -> None:
    run_id = bus.create_run(57)
    assert bus.get_plan(run_id) is None


def test_approve_run_transitions_status(bus: AgentBus) -> None:
    run_id = bus.create_run(58)
    # Walk to awaiting_approval
    for status in ["routing", "planning", "awaiting_approval"]:
        bus.set_status(run_id, status)
    bus.write_plan(run_id=run_id, goal="Some goal", files=[], acceptance_criteria=[], validation_cmds=[])

    bus.approve_run(run_id=run_id, feedback="LGTM")
    assert bus.get_run(run_id)["status"] == "approved"
    plan = bus.get_plan(run_id)
    assert plan["approved"] == 1
    assert plan["feedback"] == "LGTM"


def test_approve_run_from_wrong_status_raises(bus: AgentBus) -> None:
    run_id = bus.create_run(59)
    with pytest.raises((InvalidStatusTransitionError, ValueError)):
        bus.approve_run(run_id)  # still in 'created' status


# ---------------------------------------------------------------------------
# Pending approval list
# ---------------------------------------------------------------------------


def test_list_pending_approval(bus: AgentBus) -> None:
    run1 = bus.create_run(100)
    run2 = bus.create_run(101)
    run3 = bus.create_run(102)

    # Move run1 and run2 to awaiting_approval
    for run_id in [run1, run2]:
        for status in ["routing", "planning", "awaiting_approval"]:
            bus.set_status(run_id, status)

    pending = bus.list_pending_approval()
    run_ids = [r["run_id"] for r in pending]
    assert run1 in run_ids
    assert run2 in run_ids
    assert run3 not in run_ids


# ---------------------------------------------------------------------------
# File snapshots
# ---------------------------------------------------------------------------


def test_write_and_get_snapshots(bus: AgentBus) -> None:
    run_id = bus.create_run(60)
    bus.write_snapshot(
        run_id=run_id,
        filepath="apps/api/services/template_service.py",
        content_before="# old content",
        content_after="# new content",
    )

    snapshots = bus.get_snapshots(run_id)
    assert len(snapshots) == 1
    assert snapshots[0]["filepath"] == "apps/api/services/template_service.py"
    assert snapshots[0]["content_before"] == "# old content"
    assert snapshots[0]["content_after"] == "# new content"


def test_multiple_snapshots_for_different_files(bus: AgentBus) -> None:
    run_id = bus.create_run(61)
    bus.write_snapshot(run_id, "file_a.py", "before_a", "after_a")
    bus.write_snapshot(run_id, "file_b.py", None, "new file")

    snapshots = bus.get_snapshots(run_id)
    assert len(snapshots) == 2
    filepaths = {s["filepath"] for s in snapshots}
    assert filepaths == {"file_a.py", "file_b.py"}


def test_get_snapshots_empty(bus: AgentBus) -> None:
    run_id = bus.create_run(62)
    assert bus.get_snapshots(run_id) == []


# ---------------------------------------------------------------------------
# Validation results
# ---------------------------------------------------------------------------


def test_write_and_get_validation(bus: AgentBus) -> None:
    run_id = bus.create_run(70)
    bus.write_validation(
        run_id=run_id,
        command="pytest tests/unit/",
        stdout="5 passed",
        stderr="",
        exit_code=0,
        passed=True,
    )

    results = bus.get_validations(run_id)
    assert len(results) == 1
    assert results[0]["command"] == "pytest tests/unit/"
    assert results[0]["exit_code"] == 0
    assert results[0]["passed"] is True


def test_get_validations_respects_limit(bus: AgentBus) -> None:
    run_id = bus.create_run(71)
    for i in range(5):
        bus.write_validation(run_id, f"cmd_{i}", "", "", 0, True)

    results = bus.get_validations(run_id, limit=3)
    assert len(results) == 3


def test_validation_failed_flag(bus: AgentBus) -> None:
    run_id = bus.create_run(72)
    bus.write_validation(run_id, "pytest tests/", "1 failed", "ERROR", 1, False)
    results = bus.get_validations(run_id)
    assert results[0]["passed"] is False
    assert results[0]["exit_code"] == 1


# ---------------------------------------------------------------------------
# Checkpoints
# ---------------------------------------------------------------------------


def test_write_and_get_checkpoints(bus: AgentBus) -> None:
    run_id = bus.create_run(80)
    bus.write_checkpoint(run_id, "plan_generated", {"files_count": 3})
    bus.write_checkpoint(run_id, "coding_complete")

    checkpoints = bus.get_checkpoints(run_id)
    assert len(checkpoints) == 2
    assert checkpoints[0]["label"] == "plan_generated"
    assert checkpoints[0]["metadata"] == {"files_count": 3}
    assert checkpoints[1]["label"] == "coding_complete"


def test_get_checkpoints_empty(bus: AgentBus) -> None:
    run_id = bus.create_run(81)
    assert bus.get_checkpoints(run_id) == []


# ---------------------------------------------------------------------------
# Context packet (the key MAESTRO primitive)
# ---------------------------------------------------------------------------


def test_read_context_packet_full(bus: AgentBus) -> None:
    run_id = bus.create_run(90, repo="owner/repo")
    bus.write_plan(
        run_id=run_id,
        goal="Fix router bug",
        files=["apps/api/routers/templates.py"],
        acceptance_criteria=["GET /templates returns 200"],
        validation_cmds=["pytest"],
    )
    bus.write_snapshot(run_id, "apps/api/routers/templates.py", "old", "new")
    bus.write_validation(run_id, "pytest", "1 passed", "", 0, True)
    bus.write_checkpoint(run_id, "plan_generated")

    packet = bus.read_context_packet(run_id)

    assert packet["run"]["run_id"] == run_id
    assert packet["run"]["issue_number"] == 90
    assert packet["plan"] is not None
    assert packet["plan"]["goal"] == "Fix router bug"
    assert len(packet["file_snapshots"]) == 1
    assert len(packet["validation_results"]) == 1
    assert len(packet["checkpoints"]) == 1


def test_read_context_packet_unknown_run_raises(bus: AgentBus) -> None:
    with pytest.raises(ValueError, match="Unknown run_id"):
        bus.read_context_packet("nonexistent-run-id")


def test_read_context_packet_no_plan_returns_none(bus: AgentBus) -> None:
    run_id = bus.create_run(91)
    packet = bus.read_context_packet(run_id)
    assert packet["plan"] is None
    assert packet["file_snapshots"] == []
    assert packet["validation_results"] == []


def test_context_packet_validation_results_limited_to_3(bus: AgentBus) -> None:
    run_id = bus.create_run(92)
    for i in range(5):
        bus.write_validation(run_id, f"cmd_{i}", "", "", 0, True)

    packet = bus.read_context_packet(run_id)
    assert len(packet["validation_results"]) == 3
