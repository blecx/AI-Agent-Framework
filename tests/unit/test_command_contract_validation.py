from agents.validation_profiles import (
    validate_contract_markers,
    validate_namespace_collision,
)


def test_namespace_shadowing_detected_for_same_suffix():
    command_ids = [
        "speckit.plan",
        "blecs.plan",
        "speckit.specify",
        "blecs.ux.plan",
    ]

    errors = validate_namespace_collision(command_ids)

    assert len(errors) == 1
    assert "speckit.plan conflicts with blecs.plan" in errors[0]


def test_namespace_shadowing_not_detected_when_suffixes_differ():
    command_ids = [
        "speckit.plan",
        "speckit.specify",
        "blecs.ux.plan",
        "blecs.workflow.sync",
    ]

    errors = validate_namespace_collision(command_ids)

    assert errors == []


def test_contract_markers_detects_missing_markers():
    content = "---\ndescription: test\n---\nMissing user request section"

    missing = validate_contract_markers(content)

    assert missing == ["User request:"]


def test_contract_markers_accepts_complete_contract_text():
    content = "---\ndescription: test\n---\n\nUser request:\n$ARGUMENTS\n"

    missing = validate_contract_markers(content)

    assert missing == []
