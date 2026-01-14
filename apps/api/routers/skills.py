"""
Skills router for AI agent cognitive capabilities.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import List

from models import (
    MemoryState,
    MemoryStateUpdate,
    PlanRequest,
    PlanResponse,
    LearningRequest,
    LearningResponse,
)
from skills.registry import get_registry
from skills.base import SkillMetadata

router = APIRouter()


@router.get("/skills", response_model=List[SkillMetadata])
async def list_skills():
    """
    List all available skills.
    
    Returns metadata for all registered skills including name, version,
    description, and input/output schemas.
    """
    registry = get_registry()
    return registry.list_skills()


@router.get("/{agent_id}/skills/memory", response_model=MemoryState)
async def get_memory(agent_id: str, request: Request):
    """
    Get agent memory state.
    
    Retrieves both short-term and long-term memory for the specified agent.
    """
    registry = get_registry()
    memory_skill = registry.get_skill("memory")
    
    if not memory_skill:
        raise HTTPException(status_code=500, detail="Memory skill not available")
    
    git_manager = request.app.state.git_manager
    
    try:
        result = await memory_skill.execute(
            agent_id=agent_id,
            input_data={"operation": "get"},
            context={"git_manager": git_manager}
        )
        return MemoryState(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get memory: {str(e)}"
        )


@router.post("/{agent_id}/skills/memory", response_model=MemoryState)
async def update_memory(
    agent_id: str, memory_update: MemoryStateUpdate, request: Request
):
    """
    Update agent memory state.
    
    Merges the provided short-term and long-term memory updates
    with the existing memory state. Returns the updated memory.
    """
    registry = get_registry()
    memory_skill = registry.get_skill("memory")
    
    if not memory_skill:
        raise HTTPException(status_code=500, detail="Memory skill not available")
    
    git_manager = request.app.state.git_manager
    
    try:
        input_data = {
            "operation": "set",
            "short_term": memory_update.short_term,
            "long_term": memory_update.long_term,
        }
        
        result = await memory_skill.execute(
            agent_id=agent_id,
            input_data=input_data,
            context={"git_manager": git_manager}
        )
        return MemoryState(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update memory: {str(e)}"
        )


@router.post("/{agent_id}/skills/plan", response_model=PlanResponse)
async def create_plan(agent_id: str, plan_request: PlanRequest, request: Request):
    """
    Generate a multi-step plan for the given goal.
    
    Creates a structured plan with ordered steps, dependencies,
    and time estimates based on the goal and constraints.
    """
    registry = get_registry()
    planning_skill = registry.get_skill("planning")
    
    if not planning_skill:
        raise HTTPException(status_code=500, detail="Planning skill not available")
    
    llm_service = request.app.state.llm_service
    
    try:
        input_data = {
            "goal": plan_request.goal,
            "constraints": plan_request.constraints or [],
            "context": plan_request.context or {},
        }
        
        result = await planning_skill.execute(
            agent_id=agent_id,
            input_data=input_data,
            context={"llm_service": llm_service}
        )
        return PlanResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create plan: {str(e)}"
        )


@router.post("/{agent_id}/skills/learn", response_model=LearningResponse)
async def record_experience(
    agent_id: str, learning_request: LearningRequest, request: Request
):
    """
    Record a learning experience for the agent.
    
    Stores the input, outcome, and optional feedback for future
    learning and improvement.
    """
    registry = get_registry()
    learning_skill = registry.get_skill("learning")
    
    if not learning_skill:
        raise HTTPException(status_code=500, detail="Learning skill not available")
    
    git_manager = request.app.state.git_manager
    
    try:
        input_data = {
            "experience": {
                "input": learning_request.experience.input,
                "outcome": learning_request.experience.outcome,
                "feedback": learning_request.experience.feedback,
                "context": learning_request.experience.context or {},
            }
        }
        
        result = await learning_skill.execute(
            agent_id=agent_id,
            input_data=input_data,
            context={"git_manager": git_manager}
        )
        return LearningResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to record experience: {str(e)}"
        )
