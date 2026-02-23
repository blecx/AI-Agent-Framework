"""
Audit Rules Engine - validates cross-artifact consistency.
Single Responsibility: Execute validation rules and calculate completeness.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from pathlib import Path


class AuditRulesEngine:
    """Service for running audit rules on project artifacts."""

    def __init__(self):
        """Initialize audit rules engine."""
        pass

    def run_audit_rules(
        self,
        project_key: str,
        git_manager,
        rule_set: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run enhanced audit rules on a project.

        Args:
            project_key: Project key
            git_manager: Git manager instance
            rule_set: Optional list of specific rules to run (default: all)

        Returns:
            Dictionary with issues, completeness score, and rule violations
        """
        available_rules = {
            "cross_reference": self._audit_cross_references,
            "date_consistency": self._audit_date_consistency,
            "owner_validation": self._audit_owner_validation,
            "dependency_cycles": self._audit_dependency_cycles,
            "completeness": self._audit_completeness,
            "required_fields": self._audit_required_fields,
            "relationship_consistency": self._audit_relationship_consistency,
            "workflow_state": self._audit_workflow_state,
            "blueprint_compliance": self._audit_blueprint_compliance,
        }

        # Use all rules if none specified
        rules_to_run = rule_set or list(available_rules.keys())

        issues = []
        rule_violations = {}

        for rule_name in rules_to_run:
            if rule_name in available_rules:
                rule_func = available_rules[rule_name]
                rule_issues = rule_func(project_key, git_manager)
                issues.extend(rule_issues)
                rule_violations[rule_name] = len(rule_issues)

        issues = self._sort_issues(issues)

        # Calculate completeness score
        completeness_score = self._calculate_completeness_score(
            project_key, git_manager
        )

        return {
            "issues": issues,
            "completeness_score": completeness_score,
            "rule_violations": rule_violations,
            "total_issues": len(issues),
        }

    def _sort_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return issues in deterministic order for stable outputs."""

        def sort_key(issue: Dict[str, Any]) -> tuple:
            return (
                str(issue.get("rule", "")),
                str(issue.get("severity", "")),
                str(issue.get("artifact", "")),
                str(issue.get("item_id", issue.get("milestone_id", ""))),
                str(issue.get("message", "")),
            )

        return sorted(issues, key=sort_key)

    def compute_resource_hash(self, content: str) -> str:
        """Compute SHA-256 hash of resource content for compliance tracking."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _audit_cross_references(
        self, project_key: str, git_manager
    ) -> List[Dict[str, Any]]:
        """Validate cross-references between RAID items and deliverables."""
        issues = []
        project_path = git_manager.get_project_path(project_key)

        raid_path = project_path / "artifacts" / "raid.json"
        if raid_path.exists():
            try:
                raid_data = json.loads(raid_path.read_text())
                raid_items = raid_data.get("items", [])

                for item in raid_items:
                    related_deliverables = item.get("related_deliverables", [])
                    for deliverable_id in related_deliverables:
                        if not self._deliverable_exists(project_path, deliverable_id):
                            issues.append(
                                {
                                    "rule": "cross_reference",
                                    "severity": "error",
                                    "message": f"RAID item {item.get('id', 'unknown')} references non-existent deliverable {deliverable_id}",
                                    "artifact": "artifacts/raid.json",
                                    "item_id": item.get("id"),
                                }
                            )
            except (json.JSONDecodeError, KeyError) as e:
                issues.append(
                    {
                        "rule": "cross_reference",
                        "severity": "error",
                        "message": f"Failed to parse RAID data: {str(e)}",
                        "artifact": "artifacts/raid.json",
                    }
                )

        return issues

    def _audit_date_consistency(
        self, project_key: str, git_manager
    ) -> List[Dict[str, Any]]:
        """Check date consistency (milestone dates vs. project dates)."""
        issues = []
        project_path = git_manager.get_project_path(project_key)

        metadata_path = project_path / "metadata.json"
        if not metadata_path.exists():
            return issues

        try:
            metadata = json.loads(metadata_path.read_text())
            project_start = metadata.get("start_date")
            project_end = metadata.get("end_date")

            pmp_path = project_path / "artifacts" / "pmp.json"
            if pmp_path.exists():
                pmp_data = json.loads(pmp_path.read_text())
                milestones = pmp_data.get("milestones", [])

                for milestone in milestones:
                    milestone_date = milestone.get("due_date")
                    milestone_id = milestone.get("id", "unknown")

                    if (
                        project_start
                        and milestone_date
                        and milestone_date < project_start
                    ):
                        issues.append(
                            {
                                "rule": "date_consistency",
                                "severity": "error",
                                "message": f"Milestone {milestone_id} date ({milestone_date}) is before project start ({project_start})",
                                "artifact": "artifacts/pmp.json",
                                "milestone_id": milestone_id,
                            }
                        )

                    if project_end and milestone_date and milestone_date > project_end:
                        issues.append(
                            {
                                "rule": "date_consistency",
                                "severity": "warning",
                                "message": f"Milestone {milestone_id} date ({milestone_date}) is after project end ({project_end})",
                                "artifact": "artifacts/pmp.json",
                                "milestone_id": milestone_id,
                            }
                        )

        except (json.JSONDecodeError, KeyError) as e:
            issues.append(
                {
                    "rule": "date_consistency",
                    "severity": "error",
                    "message": f"Failed to validate dates: {str(e)}",
                }
            )

        return issues

    def _audit_owner_validation(
        self, project_key: str, git_manager
    ) -> List[Dict[str, Any]]:
        """Validate that referenced owners/users exist."""
        issues = []
        project_path = git_manager.get_project_path(project_key)

        governance_path = project_path / "artifacts" / "governance.json"
        valid_users = set()

        if governance_path.exists():
            try:
                governance_data = json.loads(governance_path.read_text())
                team = governance_data.get("team", [])
                valid_users = {member.get("id") for member in team if "id" in member}
            except (json.JSONDecodeError, KeyError):
                pass

        raid_path = project_path / "artifacts" / "raid.json"
        if raid_path.exists():
            try:
                raid_data = json.loads(raid_path.read_text())
                raid_items = raid_data.get("items", [])

                for item in raid_items:
                    owner = item.get("owner")
                    if owner and owner not in valid_users:
                        issues.append(
                            {
                                "rule": "owner_validation",
                                "severity": "warning",
                                "message": f"RAID item {item.get('id', 'unknown')} owner '{owner}' not found in team",
                                "artifact": "artifacts/raid.json",
                                "item_id": item.get("id"),
                            }
                        )
            except (json.JSONDecodeError, KeyError):
                pass

        return issues

    def _audit_dependency_cycles(
        self, project_key: str, git_manager
    ) -> List[Dict[str, Any]]:
        """Detect dependency cycles in deliverables/tasks."""
        issues = []
        project_path = git_manager.get_project_path(project_key)

        pmp_path = project_path / "artifacts" / "pmp.json"
        if not pmp_path.exists():
            return issues

        try:
            pmp_data = json.loads(pmp_path.read_text())
            deliverables = pmp_data.get("deliverables", [])

            graph = {}
            for deliverable in deliverables:
                deliverable_id = deliverable.get("id")
                dependencies = deliverable.get("dependencies", [])
                graph[deliverable_id] = dependencies

            cycles = self._detect_cycles_in_graph(graph)
            for cycle in cycles:
                issues.append(
                    {
                        "rule": "dependency_cycles",
                        "severity": "error",
                        "message": f"Dependency cycle detected: {' -> '.join(cycle)}",
                        "artifact": "artifacts/pmp.json",
                        "cycle": cycle,
                    }
                )

        except (json.JSONDecodeError, KeyError) as e:
            issues.append(
                {
                    "rule": "dependency_cycles",
                    "severity": "error",
                    "message": f"Failed to analyze dependencies: {str(e)}",
                }
            )

        return issues

    def _audit_completeness(
        self, project_key: str, git_manager
    ) -> List[Dict[str, Any]]:
        """Calculate completeness scoring."""
        issues = []
        completeness = self._calculate_completeness_score(project_key, git_manager)

        if completeness < 70.0:
            issues.append(
                {
                    "rule": "completeness",
                    "severity": "warning",
                    "message": f"Project completeness is low: {completeness:.1f}% (target: 70%+)",
                    "completeness_score": completeness,
                }
            )

        return issues

    def _audit_required_fields(
        self, project_key: str, git_manager
    ) -> List[Dict[str, Any]]:
        """Validate required fields are present."""
        issues = []
        project_path = git_manager.get_project_path(project_key)

        metadata_path = project_path / "metadata.json"
        if metadata_path.exists():
            try:
                metadata = json.loads(metadata_path.read_text())
                required_fields = ["key", "name", "description", "start_date"]
                for field in required_fields:
                    if not metadata.get(field):
                        issues.append(
                            {
                                "rule": "required_fields",
                                "severity": "error",
                                "message": f"Required metadata field '{field}' is missing or empty",
                                "artifact": "metadata.json",
                                "field": field,
                            }
                        )
            except (json.JSONDecodeError, KeyError):
                pass

        return issues

    def _audit_relationship_consistency(
        self, project_key: str, git_manager
    ) -> List[Dict[str, Any]]:
        """Validate artifact relationships are consistent."""
        issues = []
        project_path = git_manager.get_project_path(project_key)

        raid_path = project_path / "artifacts" / "raid.json"
        pmp_path = project_path / "artifacts" / "pmp.json"

        if raid_path.exists() and pmp_path.exists():
            try:
                raid_data = json.loads(raid_path.read_text())
                pmp_data = json.loads(pmp_path.read_text())

                milestone_ids = {m.get("id") for m in pmp_data.get("milestones", [])}
                raid_items = raid_data.get("items", [])

                for item in raid_items:
                    related_milestones = item.get("related_milestones", [])
                    for milestone_id in related_milestones:
                        if milestone_id not in milestone_ids:
                            issues.append(
                                {
                                    "rule": "relationship_consistency",
                                    "severity": "error",
                                    "message": f"RAID item {item.get('id', 'unknown')} references non-existent milestone {milestone_id}",
                                    "artifact": "artifacts/raid.json",
                                    "item_id": item.get("id"),
                                }
                            )

            except (json.JSONDecodeError, KeyError):
                pass

        return issues

    def _audit_workflow_state(
        self, project_key: str, git_manager
    ) -> List[Dict[str, Any]]:
        """Validate workflow states are valid."""
        issues = []
        project_path = git_manager.get_project_path(project_key)

        workflow_path = project_path / "workflow" / "state.json"
        if workflow_path.exists():
            try:
                workflow_data = json.loads(workflow_path.read_text())
                current_phase = workflow_data.get("current_phase")
                valid_phases = [
                    "initiation",
                    "planning",
                    "execution",
                    "monitoring",
                    "closing",
                ]

                if current_phase and current_phase not in valid_phases:
                    issues.append(
                        {
                            "rule": "workflow_state",
                            "severity": "error",
                            "message": f"Invalid workflow phase '{current_phase}' (valid: {', '.join(valid_phases)})",
                            "artifact": "workflow/state.json",
                            "current_phase": current_phase,
                        }
                    )

            except (json.JSONDecodeError, KeyError):
                pass

        return issues

    def _audit_blueprint_compliance(
        self, project_key: str, git_manager
    ) -> List[Dict[str, Any]]:
        """Validate project complies with its blueprint."""
        issues = []
        project_path = git_manager.get_project_path(project_key)

        metadata_path = project_path / "metadata.json"
        if not metadata_path.exists():
            return issues

        try:
            metadata = json.loads(metadata_path.read_text())
            blueprint_id = metadata.get("blueprint")

            if not blueprint_id:
                issues.append(
                    {
                        "rule": "blueprint_compliance",
                        "severity": "warning",
                        "message": "Project has no associated blueprint",
                        "artifact": "metadata.json",
                    }
                )

            core_artifacts = ["pmp.json", "raid.json", "governance.json"]
            artifacts_path = project_path / "artifacts"

            if artifacts_path.exists():
                for artifact_name in core_artifacts:
                    artifact_path = artifacts_path / artifact_name
                    if not artifact_path.exists():
                        issues.append(
                            {
                                "rule": "blueprint_compliance",
                                "severity": "warning",
                                "message": f"Core artifact '{artifact_name}' is missing",
                                "artifact": f"artifacts/{artifact_name}",
                            }
                        )

        except (json.JSONDecodeError, KeyError):
            pass

        return issues

    # Helper methods

    def _deliverable_exists(self, project_path: Path, deliverable_id: str) -> bool:
        """Check if a deliverable exists in PMP."""
        pmp_path = project_path / "artifacts" / "pmp.json"
        if not pmp_path.exists():
            return False

        try:
            pmp_data = json.loads(pmp_path.read_text())
            deliverables = pmp_data.get("deliverables", [])
            return any(d.get("id") == deliverable_id for d in deliverables)
        except (json.JSONDecodeError, KeyError):
            return False

    def _detect_cycles_in_graph(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Detect cycles in a dependency graph using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def _calculate_completeness_score(self, project_key: str, git_manager) -> float:
        """Calculate project completeness score (0-100%)."""
        project_path = git_manager.get_project_path(project_key)

        expected_artifacts = {
            "metadata.json": ["key", "name", "description", "start_date"],
            "artifacts/pmp.json": ["deliverables", "milestones"],
            "artifacts/raid.json": ["items"],
            "artifacts/governance.json": ["team", "roles"],
            "workflow/state.json": ["current_phase"],
        }

        total_items = 0
        completed_items = 0

        for artifact_path, required_fields in expected_artifacts.items():
            full_path = project_path / artifact_path
            total_items += 1

            if full_path.exists():
                completed_items += 1
                try:
                    data = json.loads(full_path.read_text())
                    for field in required_fields:
                        total_items += 1
                        if data.get(field):
                            completed_items += 1
                except (json.JSONDecodeError, KeyError):
                    total_items += len(required_fields)
            else:
                total_items += len(required_fields)

        if total_items == 0:
            return 0.0

        return (completed_items / total_items) * 100.0
