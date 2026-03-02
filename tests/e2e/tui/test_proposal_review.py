"""
TUI E2E Test: Proposal Review/Apply

Deterministic scenario: project creation → propose command → list proposals
(pending state) → apply proposal → verify accepted state transition.

No arbitrary sleep() calls — all assertions check observable API/CLI state.

Scenario
--------
1. Create project
2. Propose an assess_gaps command → capture proposal ID from output
3. List proposals filtered by "pending" → assert proposal is present
4. Apply proposal → assert success message
5. List proposals filtered by "pending" → assert proposal is absent (transitioned)
6. List proposals filtered by "accepted" → assert proposal appears (visible)

These tests are marked @pytest.mark.tui and @pytest.mark.e2e.  They are
intentionally excluded from the default pytest run (addopts = -m "not e2e") and
must be run explicitly::

    pytest tests/e2e/tui -k proposal_review -m tui -q

The `tui` fixture in conftest.py skips automatically when the TUI binary is
unavailable so that CI does not fail on environments lacking the CLI.
"""

from __future__ import annotations

import re

import pytest


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _extract_proposal_id(output: str) -> str:
    """Extract the first proposal UUID from CLI output.

    The ``commands propose`` command prints the proposal ID via Rich with markup,
    which may introduce ANSI escape sequences.  Both formats are handled:

    - ``Proposal ID:  <uuid>``
    - any standalone ``<uuid>`` elsewhere in the output (fallback)
    """
    # Primary: look after "Proposal ID" label (tolerates ANSI / Rich markup)
    match = re.search(
        r"Proposal\s+ID[^\w-]*([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
        output,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)

    # Fallback: any UUID in the output
    match = re.search(
        r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
        output,
        re.IGNORECASE,
    )
    assert match, (
        f"Could not extract a proposal UUID from propose output:\n{output}"
    )
    return match.group(1)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.tui
@pytest.mark.e2e
def test_proposal_review_deterministic_cycle(tui, unique_project_key):
    """Deterministic proposal review/apply cycle.

    State transitions verified:
      create project → propose → pending → apply → no longer pending
    """
    # Step 1: Create project
    result = tui.create_project(
        key=unique_project_key, name="Proposal Review Test"
    )
    assert result.success, f"Project creation failed:\n{result.stderr}"
    assert unique_project_key in result.stdout

    # Step 2: Propose a command; capture proposal ID
    result = tui.execute_command(
        [
            "commands",
            "propose",
            "--project",
            unique_project_key,
            "--command",
            "assess_gaps",
        ]
    )
    assert result.success, f"Propose command failed:\n{result.stderr}"
    assert "proposed successfully" in result.stdout.lower(), (
        f"Expected 'proposed successfully' in output:\n{result.stdout}"
    )

    proposal_id = _extract_proposal_id(result.stdout)
    assert proposal_id, "Proposal ID must be non-empty after propose"

    # Step 3: Pending list must contain the new proposal
    result = tui.execute_command(
        [
            "proposals",
            "list",
            "--project",
            unique_project_key,
            "--status",
            "pending",
        ]
    )
    assert result.success, f"List pending proposals failed:\n{result.stderr}"
    assert proposal_id in result.stdout, (
        f"Proposal {proposal_id} not found in pending list:\n{result.stdout}"
    )
    assert "pending" in result.stdout.lower(), (
        f"Expected status 'pending' in listing output:\n{result.stdout}"
    )

    # Step 4: Apply the proposal
    result = tui.execute_command(
        [
            "proposals",
            "apply",
            "--project",
            unique_project_key,
            "--id",
            proposal_id,
        ]
    )
    assert result.success, f"Apply proposal failed:\n{result.stderr}"
    assert "applied successfully" in result.stdout.lower(), (
        f"Expected 'applied successfully' in output:\n{result.stdout}"
    )
    assert proposal_id in result.stdout, (
        f"Expected proposal ID {proposal_id} in apply output:\n{result.stdout}"
    )

    # Step 5: Proposal must no longer appear in the pending list
    result = tui.execute_command(
        [
            "proposals",
            "list",
            "--project",
            unique_project_key,
            "--status",
            "pending",
        ]
    )
    assert result.success, f"Final pending list failed:\n{result.stderr}"
    assert proposal_id not in result.stdout, (
        f"Proposal {proposal_id} is still in pending state after apply:\n{result.stdout}"
    )

    print(
        f"✓ Proposal {proposal_id} transitioned pending→accepted for project {unique_project_key}"
    )


@pytest.mark.tui
@pytest.mark.e2e
def test_proposal_accepted_state_visible(tui, unique_project_key):
    """After apply, proposal must appear in the accepted-filtered list."""
    # Create project
    result = tui.create_project(
        key=unique_project_key, name="Proposal Accepted State Test"
    )
    assert result.success, f"Project creation failed:\n{result.stderr}"

    # Propose
    result = tui.execute_command(
        [
            "commands",
            "propose",
            "--project",
            unique_project_key,
            "--command",
            "assess_gaps",
        ]
    )
    assert result.success, f"Propose failed:\n{result.stderr}"
    proposal_id = _extract_proposal_id(result.stdout)

    # Apply
    result = tui.execute_command(
        [
            "proposals",
            "apply",
            "--project",
            unique_project_key,
            "--id",
            proposal_id,
        ]
    )
    assert result.success, f"Apply failed:\n{result.stderr}"

    # Accepted list must contain the proposal
    result = tui.execute_command(
        [
            "proposals",
            "list",
            "--project",
            unique_project_key,
            "--status",
            "accepted",
        ]
    )
    assert result.success, f"List accepted proposals failed:\n{result.stderr}"
    assert proposal_id in result.stdout, (
        f"Proposal {proposal_id} missing from accepted list:\n{result.stdout}"
    )
    assert "accepted" in result.stdout.lower(), (
        f"Expected status 'accepted' in listing output:\n{result.stdout}"
    )

    print(
        f"✓ Proposal {proposal_id} visible in accepted list for {unique_project_key}"
    )
