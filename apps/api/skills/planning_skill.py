"""
Planning skill for multi-step plan generation.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from .base import SkillResult


class PlanningSkill:
    """Skill for generating and managing multi-step plans."""

    name = "planning"
    version = "1.0.0"
    description = "Generate and manage multi-step plans for goal achievement"

    def execute(self, agent_id: str, params: Dict[str, Any], **kwargs) -> SkillResult:
        """
        Execute planning operations.

        Args:
            agent_id: Unique identifier for the agent
            params: {
                "goal": str - The goal to achieve,
                "constraints": Optional[List[str]] - Constraints to consider,
                "context": Optional[Dict[str, Any]] - Additional context
            }
            **kwargs: Must include "docs_path" - base path for document storage

        Returns:
            SkillResult with generated plan
        """
        docs_path = kwargs.get("docs_path")
        if not docs_path:
            return SkillResult(
                success=False, message="docs_path required in kwargs"
            )

        goal = params.get("goal")
        if not goal:
            return SkillResult(success=False, message="goal is required")

        constraints = params.get("constraints", [])
        context = params.get("context", {})

        # Generate plan using deterministic algorithm
        plan = self._generate_plan(goal, constraints, context)

        # Persist plan
        plan_id = str(uuid.uuid4())
        plans_dir = os.path.join(docs_path, "agents", agent_id, "plans")
        plan_file = os.path.join(plans_dir, f"{plan_id}.json")

        try:
            os.makedirs(plans_dir, exist_ok=True)

            plan_data = {
                "plan_id": plan_id,
                "goal": goal,
                "constraints": constraints,
                "context": context,
                "steps": plan,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "pending",
            }

            with open(plan_file, "w") as f:
                json.dump(plan_data, f, indent=2)

            return SkillResult(
                success=True,
                data=plan_data,
                message=f"Plan generated with {len(plan)} steps",
                metadata={"plan_id": plan_id},
            )
        except Exception as e:
            return SkillResult(
                success=False, message=f"Error persisting plan: {str(e)}"
            )

    def _generate_plan(
        self, goal: str, constraints: List[str], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate a deterministic multi-step plan.

        This is a simple algorithmic planner for MVP.
        Future versions can integrate with LLM or advanced planning algorithms.

        Args:
            goal: The goal to achieve
            constraints: List of constraints
            context: Additional context

        Returns:
            List of plan steps
        """
        # Simple decomposition based on goal keywords
        steps = []

        # Step 1: Always start with analysis
        steps.append({
            "step": 1,
            "action": "analyze",
            "description": f"Analyze requirements for: {goal}",
            "status": "pending",
            "dependencies": [],
        })

        # Step 2: Identify resources/constraints
        if constraints:
            steps.append({
                "step": 2,
                "action": "assess_constraints",
                "description": f"Assess constraints: {', '.join(constraints)}",
                "status": "pending",
                "dependencies": [1],
            })
            next_step = 3
        else:
            next_step = 2

        # Step 3: Break down into subtasks based on goal complexity
        goal_lower = goal.lower()
        if any(word in goal_lower for word in ["create", "build", "develop", "implement"]):
            steps.append({
                "step": next_step,
                "action": "design",
                "description": "Design solution architecture",
                "status": "pending",
                "dependencies": [next_step - 1],
            })
            next_step += 1

            steps.append({
                "step": next_step,
                "action": "implement",
                "description": "Implement solution",
                "status": "pending",
                "dependencies": [next_step - 1],
            })
            next_step += 1

        elif any(word in goal_lower for word in ["fix", "resolve", "debug"]):
            steps.append({
                "step": next_step,
                "action": "diagnose",
                "description": "Diagnose the issue",
                "status": "pending",
                "dependencies": [next_step - 1],
            })
            next_step += 1

            steps.append({
                "step": next_step,
                "action": "resolve",
                "description": "Implement fix",
                "status": "pending",
                "dependencies": [next_step - 1],
            })
            next_step += 1

        else:
            # Generic execution step
            steps.append({
                "step": next_step,
                "action": "execute",
                "description": f"Execute: {goal}",
                "status": "pending",
                "dependencies": [next_step - 1],
            })
            next_step += 1

        # Final step: Verify/validate
        steps.append({
            "step": next_step,
            "action": "verify",
            "description": "Verify goal achievement",
            "status": "pending",
            "dependencies": [next_step - 1],
        })

        return steps
