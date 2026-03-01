"""Unit tests for ArtifactGenerationService."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from apps.api.services.artifact_generation_service import (
    ArtifactGenerationError,
    ArtifactGenerationService,
    ValidationError,
)


def _build_service(template=None, blueprint=None):
    template_service = Mock()
    template_service.get_template.return_value = template

    blueprint_service = Mock()
    blueprint_service.get_blueprint.return_value = blueprint

    git_manager = Mock()

    service = ArtifactGenerationService(
        template_service=template_service,
        blueprint_service=blueprint_service,
        git_manager=git_manager,
    )
    return service, template_service, blueprint_service, git_manager


def test_generate_from_template_pmp_success():
    template = SimpleNamespace(
        id="tpl-pmp",
        artifact_type="pmp",
        schema={
            "type": "object",
            "properties": {
                "project_name": {"type": "string"},
                "owner": {"type": "string"},
            },
            "required": ["project_name", "owner"],
        },
        markdown_template="# {{ project_name }}\nOwner: {{ owner }}\nProject: {{ project_key }}",
    )
    service, _, _, git_manager = _build_service(template=template)

    result = service.generate_from_template(
        template_id="tpl-pmp",
        project_key="TEST001",
        context={"project_name": "Phoenix", "owner": "Alex"},
    )

    assert result["artifact_path"] == "artifacts/pmp.md"
    assert result["artifact_type"] == "pmp"
    assert "Phoenix" in result["content"]
    assert "Alex" in result["content"]
    assert "TEST001" in result["content"]
    git_manager.write_file.assert_called_once_with(
        "TEST001", "artifacts/pmp.md", result["content"]
    )
    git_manager.commit_changes.assert_called_once()


def test_generate_from_template_missing_template_raises():
    service, _, _, _ = _build_service(template=None)

    with pytest.raises(ArtifactGenerationError, match="Template not found"):
        service.generate_from_template("missing", "TEST001", {})


def test_generate_from_template_schema_validation_error():
    template = SimpleNamespace(
        id="tpl-raid",
        artifact_type="raid",
        schema={
            "type": "object",
            "properties": {"project_name": {"type": "string"}},
            "required": ["project_name"],
        },
        markdown_template="# {{ project_name }}",
    )
    service, _, _, _ = _build_service(template=template)

    with pytest.raises(ValidationError, match="Context validation failed"):
        service.generate_from_template("tpl-raid", "TEST001", {})


def test_generate_from_blueprint_missing_blueprint_raises():
    service, _, _, _ = _build_service(blueprint=None)

    with pytest.raises(ArtifactGenerationError, match="Blueprint not found"):
        service.generate_from_blueprint("missing-blueprint", "TEST001")


def test_generate_from_blueprint_partial_failure_returns_error_entry():
    blueprint = SimpleNamespace(required_templates=["tpl-ok", "tpl-fail"])
    service, _, _, _ = _build_service(blueprint=blueprint)

    def _fake_generate(template_id, project_key, context):
        if template_id == "tpl-fail":
            raise ArtifactGenerationError("Template not found: tpl-fail")
        return {
            "artifact_path": "artifacts/pmp.md",
            "template_id": template_id,
            "artifact_type": "pmp",
            "content": "ok",
        }

    service.generate_from_template = _fake_generate  # type: ignore[method-assign]

    results = service.generate_from_blueprint("bp-1", "TEST001", base_context={})

    assert len(results) == 2
    assert any(item.get("template_id") == "tpl-ok" for item in results)
    failed = next(item for item in results if item.get("template_id") == "tpl-fail")
    assert failed["success"] is False
    assert "Template not found" in failed["error"]


def test_sanitize_context_strips_private_keys():
    template = SimpleNamespace(
        id="tpl-pmp",
        artifact_type="pmp",
        schema={
            "type": "object",
            "properties": {"project_name": {"type": "string"}},
            "required": ["project_name"],
        },
        markdown_template="# {{ project_name }}",
    )
    service, _, _, _ = _build_service(template=template)

    sanitized = service._sanitize_context(
        {
            "project_name": "Phoenix",
            "_private": "drop",
            "nested": {"ok": "yes", "_skip": "drop"},
        }
    )

    assert "_private" not in sanitized
    assert "_skip" not in sanitized["nested"]
    assert sanitized["project_name"] == "Phoenix"
