"""
Planning skill for AI agent multi-step planning capabilities.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone

from .base import SkillMetadata


class PlanningSkill:
    """
    Planning skill providing multi-step plan generation.
    
    For Phase 1, this provides a deterministic planning algorithm.
    Future versions can integrate with LLM for more sophisticated planning.
    """

    def get_metadata(self) -> SkillMetadata:
        """Get planning skill metadata."""
        return SkillMetadata(
            name="planning",
            version="1.0.0",
            description="Generate multi-step plans from goals and constraints",
            input_schema={
                "type": "object",
                "properties": {
                    "goal": {
                        "type": "string",
                        "description": "Goal to achieve",
                        "minLength": 1
                    },
                    "constraints": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Constraints to consider"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context"
                    }
                },
                "required": ["goal"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "goal": {"type": "string"},
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "step_number": {"type": "integer"},
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "estimated_duration": {"type": "string"},
                                "dependencies": {"type": "array"},
                                "status": {"type": "string"}
                            }
                        }
                    },
                    "estimated_total_duration": {"type": "string"},
                    "created_at": {"type": "string"}
                }
            }
        )

    async def execute(
        self, agent_id: str, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute planning operation.
        
        Args:
            agent_id: Agent identifier
            input_data: Contains goal, constraints, and context
            context: Execution context (may contain llm_service for future enhancement)
            
        Returns:
            Generated plan with steps
        """
        goal = input_data.get("goal")
        if not goal:
            raise ValueError("goal is required")

        constraints = input_data.get("constraints", [])
        plan_context = input_data.get("context", {})

        # Generate plan (deterministic for Phase 1)
        steps = self._generate_plan_steps(goal, constraints, plan_context)

        # Calculate total duration
        total_duration = self._estimate_total_duration(steps)

        return {
            "agent_id": agent_id,
            "goal": goal,
            "steps": steps,
            "estimated_total_duration": total_duration,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

    def _generate_plan_steps(
        self, goal: str, constraints: List[str], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate plan steps based on goal and constraints.
        
        Phase 1: Deterministic decomposition
        Future: Could use LLM for intelligent planning
        """
        # Deterministic plan generation based on common patterns
        steps = []
        
        # Step 1: Analyze requirements
        steps.append({
            "step_number": 1,
            "title": "Analyze Requirements",
            "description": f"Analyze and clarify requirements for: {goal}",
            "estimated_duration": "30m",
            "dependencies": [],
            "status": "pending"
        })
        
        # Step 2: Design approach
        steps.append({
            "step_number": 2,
            "title": "Design Approach",
            "description": "Design solution approach considering constraints",
            "estimated_duration": "1h",
            "dependencies": [1],
            "status": "pending"
        })
        
        # Step 3: Implement
        steps.append({
            "step_number": 3,
            "title": "Implement Solution",
            "description": f"Implement solution for: {goal}",
            "estimated_duration": "2h",
            "dependencies": [2],
            "status": "pending"
        })
        
        # Step 4: Test and validate
        steps.append({
            "step_number": 4,
            "title": "Test and Validate",
            "description": "Test implementation and validate against requirements",
            "estimated_duration": "1h",
            "dependencies": [3],
            "status": "pending"
        })
        
        # Add constraint-specific steps if needed
        if constraints:
            steps.append({
                "step_number": 5,
                "title": "Verify Constraints",
                "description": f"Verify all constraints are met: {', '.join(constraints[:3])}",
                "estimated_duration": "30m",
                "dependencies": [4],
                "status": "pending"
            })
        
        return steps

    def _estimate_total_duration(self, steps: List[Dict[str, Any]]) -> str:
        """Estimate total duration from step durations."""
        total_minutes = self._parse_duration_to_minutes(steps)
        return self._format_duration(total_minutes)
    
    def _parse_duration_to_minutes(self, steps: List[Dict[str, Any]]) -> int:
        """Parse step durations and sum to total minutes."""
        total_minutes = 0
        
        for step in steps:
            duration = step.get("estimated_duration", "0m")
            total_minutes += self._parse_single_duration(duration)
        
        return total_minutes
    
    def _parse_single_duration(self, duration: str) -> int:
        """Parse a single duration string (e.g., '1h 30m', '2h', '45m') to minutes."""
        if not duration or not isinstance(duration, str):
            return 0
        
        minutes = 0
        duration = duration.strip()
        
        try:
            # Parse hours
            if 'h' in duration:
                hours_part = duration.split('h')[0].strip()
                if hours_part:
                    minutes += int(hours_part) * 60
            
            # Parse minutes
            if 'm' in duration:
                minutes_part = duration.split('h')[-1] if 'h' in duration else duration
                minutes_part = minutes_part.replace('m', '').strip()
                if minutes_part:
                    minutes += int(minutes_part)
        except (ValueError, AttributeError):
            # Malformed duration, return 0
            pass
        
        return minutes
    
    def _format_duration(self, total_minutes: int) -> str:
        """Format minutes into duration string (e.g., '2h 30m')."""
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        return f"{minutes}m"
