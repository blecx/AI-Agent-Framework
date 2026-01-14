"""
Skills API router for cognitive skills.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import os

from models import (
    SkillListResponse,
    SkillInfo,
    MemoryGetRequest,
    MemorySetRequest,
    MemoryResponse,
    PlanRequest,
    PlanResponse,
    LearnRequest,
    LearnResponse,
)
from skills.registry import get_global_registry

router = APIRouter()


def get_docs_path(request: Request) -> str:
    """Get the docs path from app state or environment."""
    if hasattr(request.app.state, "git_manager"):
        return str(request.app.state.git_manager.base_path)
    return os.getenv("PROJECT_DOCS_PATH", "/projectDocs")


@router.get("/{agent_id}/skills", response_model=SkillListResponse)
async def list_skills(agent_id: str):
    """
    List all available skills for an agent.

    Args:
        agent_id: Unique identifier for the agent

    Returns:
        List of available skills
    """
    registry = get_global_registry()
    skills = registry.list_available()

    return SkillListResponse(
        skills=[SkillInfo(**skill) for skill in skills], total=len(skills)
    )


@router.get("/{agent_id}/skills/memory", response_model=MemoryResponse)
async def get_memory(agent_id: str, memory_type: str, request: Request):
    """
    Get memory for an agent.

    Args:
        agent_id: Unique identifier for the agent
        memory_type: Type of memory ('short_term' or 'long_term')
        request: FastAPI request object

    Returns:
        Memory data
    """
    registry = get_global_registry()
    skill = registry.get("memory")

    if not skill:
        raise HTTPException(status_code=404, detail="Memory skill not available")

    docs_path = get_docs_path(request)

    result = skill.execute(
        agent_id,
        {"operation": "get", "memory_type": memory_type},
        docs_path=docs_path,
    )

    return MemoryResponse(
        success=result.success,
        data=result.data,
        message=result.message,
        timestamp=result.timestamp,
    )


@router.post("/{agent_id}/skills/memory", response_model=MemoryResponse)
async def set_memory(agent_id: str, body: MemorySetRequest, request: Request):
    """
    Set memory for an agent.

    Args:
        agent_id: Unique identifier for the agent
        body: Memory set request with memory_type and data
        request: FastAPI request object

    Returns:
        Operation result with updated memory
    """
    registry = get_global_registry()
    skill = registry.get("memory")

    if not skill:
        raise HTTPException(status_code=404, detail="Memory skill not available")

    docs_path = get_docs_path(request)

    result = skill.execute(
        agent_id,
        {
            "operation": "set",
            "memory_type": body.memory_type,
            "data": body.data,
        },
        docs_path=docs_path,
    )

    return MemoryResponse(
        success=result.success,
        data=result.data,
        message=result.message,
        timestamp=result.timestamp,
    )


@router.post("/{agent_id}/skills/plan", response_model=PlanResponse)
async def create_plan(agent_id: str, body: PlanRequest, request: Request):
    """
    Generate a multi-step plan for achieving a goal.

    Args:
        agent_id: Unique identifier for the agent
        body: Plan request with goal, constraints, and context
        request: FastAPI request object

    Returns:
        Generated plan with steps
    """
    registry = get_global_registry()
    skill = registry.get("planning")

    if not skill:
        raise HTTPException(status_code=404, detail="Planning skill not available")

    docs_path = get_docs_path(request)

    result = skill.execute(
        agent_id,
        {
            "goal": body.goal,
            "constraints": body.constraints or [],
            "context": body.context or {},
        },
        docs_path=docs_path,
    )

    return PlanResponse(
        success=result.success,
        data=result.data,
        message=result.message,
        timestamp=result.timestamp,
        metadata=result.metadata,
    )


@router.post("/{agent_id}/skills/learn", response_model=LearnResponse)
async def log_experience(agent_id: str, body: LearnRequest, request: Request):
    """
    Log an experience event for learning.

    Args:
        agent_id: Unique identifier for the agent
        body: Learning request with experience details
        request: FastAPI request object

    Returns:
        Operation result
    """
    registry = get_global_registry()
    skill = registry.get("learning")

    if not skill:
        raise HTTPException(status_code=404, detail="Learning skill not available")

    docs_path = get_docs_path(request)

    result = skill.execute(
        agent_id,
        {
            "operation": "log",
            "context": body.context,
            "action": body.action,
            "outcome": body.outcome,
            "feedback": body.feedback or "",
            "tags": body.tags or [],
        },
        docs_path=docs_path,
    )

    return LearnResponse(
        success=result.success,
        data=result.data,
        message=result.message,
        timestamp=result.timestamp,
    )


@router.get("/{agent_id}/skills/learn/summary", response_model=LearnResponse)
async def get_learning_summary(agent_id: str, request: Request):
    """
    Get a summary of learning experiences.

    Args:
        agent_id: Unique identifier for the agent
        request: FastAPI request object

    Returns:
        Summary of experiences
    """
    registry = get_global_registry()
    skill = registry.get("learning")

    if not skill:
        raise HTTPException(status_code=404, detail="Learning skill not available")

    docs_path = get_docs_path(request)

    result = skill.execute(
        agent_id,
        {"operation": "summary"},
        docs_path=docs_path,
    )

    return LearnResponse(
        success=result.success,
        data=result.data,
        message=result.message,
        timestamp=result.timestamp,
    )
