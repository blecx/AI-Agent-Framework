import re

from apps.api.skills.coder_change_plan_skill import CoderChangePlanSkill
from apps.api.skills.design_guidelines_skill import DesignGuidelinesSkill


def test_design_guidelines_skill_returns_skill_result_envelope():
    skill = DesignGuidelinesSkill()
    result = skill.execute(
        "agent-1",
        {
            "context": "Approved mockup for Step 4",
            "platform": "web",
            "constraints": ["Use existing components only"],
        },
    )

    assert result.success is True
    assert result.message
    assert isinstance(result.data, dict)
    assert "markdown" in result.data
    assert "Design Guidelines" in result.data["markdown"]


def test_coder_change_plan_includes_yaml_block():
    skill = CoderChangePlanSkill()
    result = skill.execute(
        "agent-1",
        {
            "feature": "Mockup implementation",
            "goal": "Implement approved mockups",
            "touched_files": ["client/src/App.tsx"],
        },
    )

    assert result.success is True
    assert isinstance(result.data, dict)
    markdown = result.data["markdown"]
    assert "```yaml" in markdown
    assert "```" in markdown
    assert isinstance(result.data.get("yaml"), str)
    assert result.data["yaml"].startswith("issues:\n")

    # Ensure YAML block is clearly delimited and contains the stub keys.
    assert re.search(r"```yaml\n[\s\S]+\n```", markdown)
    assert "acceptance_criteria" in result.data["yaml"]


def test_global_registry_lists_new_skills(monkeypatch):
    import apps.api.skills.registry as registry_mod

    # Force a fresh global registry to ensure built-in registration runs.
    monkeypatch.setattr(registry_mod, "_global_registry", None)
    registry = registry_mod.get_global_registry()

    names = {s["name"] for s in registry.list_available()}
    assert "design_guidelines" in names
    assert "coder_change_plan" in names
