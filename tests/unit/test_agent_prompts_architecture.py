import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_no_legacy_agent_extensions():
    """Ensure no .agent.md files re-enter the repository."""
    agents_dir = ROOT / ".github" / "agents"
    legacy_files = list(agents_dir.glob("*.agent.md"))
    assert not legacy_files, f"Found legacy .agent.md extensions: {legacy_files}"

def test_no_legacy_prompts_agents_directory():
    """Ensure the legacy overlapping prompts/agents directory stays deleted."""
    legacy_dir = ROOT / ".github" / "prompts" / "agents"
    assert not legacy_dir.exists(), f"Legacy directory {legacy_dir} has returned! This violates Phase 1 consolidation."

def test_skills_directory_exists():
    """Ensure the dynamic skills architecture is intact."""
    skills_dir = ROOT / ".copilot" / "skills"
    assert skills_dir.exists(), "Dynamic skills directory is missing!"
    
    ux_skill = skills_dir / "blecs-ux-authority" / "SKILL.md"
    workflow_skill = skills_dir / "blecs-workflow-authority" / "SKILL.md"
    assert ux_skill.exists(), "UX Authority Skill missing"
    assert workflow_skill.exists(), "Workflow Authority Skill missing"

def test_prompt_quality_script_passes():
    """Run the strict prompt quality checks natively."""
    script_path = ROOT / "scripts" / "check_prompt_quality.py"
    result = subprocess.run([sys.executable, str(script_path), "--strict"], capture_output=True, text=True)
    assert result.returncode == 0, f"Prompt quality checks failed!\n{result.stdout}\n{result.stderr}"

def test_autoapprove_validation_passes():
    """Ensure settings.json auto-approvals map successfully to existing agents."""
    script_path = ROOT / "scripts" / "check_subagent_autoapprove.py"
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    assert result.returncode == 0, f"Auto-approve validation failed!\n{result.stdout}\n{result.stderr}"
