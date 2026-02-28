from pathlib import Path

import scripts.check_prompt_quality as mod


def test_detects_legacy_ux_authority_naming(tmp_path):
    agents_dir = tmp_path / ".github" / "agents"
    prompts_dir = tmp_path / ".github" / "prompts"
    agents_dir.mkdir(parents=True)
    prompts_dir.mkdir(parents=True)

    bad_file = agents_dir / "bad.agent.md"
    bad_file.write_text("You are the blecx UX Authority Agent.", encoding="utf-8")

    original_root = mod.ROOT
    try:
        mod.ROOT = tmp_path
        errors: list[str] = []
        mod._check_ux_authority_naming_drift(errors)
        assert errors
        assert "legacy UX authority naming" in errors[0]
    finally:
        mod.ROOT = original_root


def test_accepts_blecs_ux_authority_naming(tmp_path):
    prompts_dir = tmp_path / ".github" / "prompts"
    prompts_dir.mkdir(parents=True)

    good_file = prompts_dir / "good.md"
    good_file.write_text("Consult blecs-ux-authority before final UX decisions.", encoding="utf-8")

    original_root = mod.ROOT
    try:
        mod.ROOT = tmp_path
        errors: list[str] = []
        mod._check_ux_authority_naming_drift(errors)
        assert errors == []
    finally:
        mod.ROOT = original_root
