"""
Audit service for managing audit events in NDJSON format.
Provides event logging and retrieval with filtering capabilities.
Enhanced with cross-artifact validation rules.
"""

import json
import uuid
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path


class AuditService:
    """Service for handling audit events."""

    def __init__(self):
        """Initialize audit service."""
        pass

    def log_audit_event(
        self,
        project_key: str,
        event_type: str,
        actor: str = "system",
        payload_summary: Optional[Dict[str, Any]] = None,
        resource_hash: Optional[str] = None,
        git_manager=None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Log an audit event to NDJSON file.

        Args:
            project_key: Project key
            event_type: Type of event
            actor: User/actor that triggered event
            payload_summary: Summary of event payload
            resource_hash: Optional hash of affected resource
            git_manager: Git manager instance
            correlation_id: Optional correlation ID for request tracing

        Returns:
            The created audit event
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        event = {
            "event_id": event_id,
            "event_type": event_type,
            "timestamp": timestamp,
            "actor": actor,
            "correlation_id": correlation_id,
            "project_key": project_key,
            "payload_summary": payload_summary or {},
            "resource_hash": resource_hash,
        }

        # Append to NDJSON file
        events_path = (
            git_manager.get_project_path(project_key) / "events" / "audit.ndjson"
        )
        events_path.parent.mkdir(parents=True, exist_ok=True)

        event_line = json.dumps(event)
        with events_path.open("a") as f:
            f.write(event_line + "\n")

        return event

    def get_audit_events(
        self,
        project_key: str,
        git_manager,
        event_type: Optional[str] = None,
        actor: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Retrieve audit events with optional filtering and pagination.

        Args:
            project_key: Project key
            git_manager: Git manager instance
            event_type: Filter by event type
            actor: Filter by actor
            since: Filter events since timestamp (ISO 8601)
            until: Filter events until timestamp (ISO 8601)
            limit: Maximum number of events to return
            offset: Number of events to skip

        Returns:
            Dictionary with events list and metadata
        """
        events_path = (
            git_manager.get_project_path(project_key) / "events" / "audit.ndjson"
        )

        if not events_path.exists():
            return {
                "events": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "filtered_by": self._build_filter_summary(
                    event_type, actor, since, until
                ),
            }

        # Read all events from NDJSON
        events = []
        with events_path.open("r") as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line)
                        events.append(event)
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue

        # Apply filters
        filtered_events = self._filter_events(events, event_type, actor, since, until)

        # Apply pagination
        total = len(filtered_events)
        paginated_events = filtered_events[offset : offset + limit]

        return {
            "events": paginated_events,
            "total": total,
            "limit": limit,
            "offset": offset,
            "filtered_by": self._build_filter_summary(event_type, actor, since, until),
        }

    def _filter_events(
        self,
        events: List[Dict[str, Any]],
        event_type: Optional[str] = None,
        actor: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Apply filters to events list."""
        filtered = events

        # Filter by event type
        if event_type:
            filtered = [e for e in filtered if e.get("event_type") == event_type]

        # Filter by actor
        if actor:
            filtered = [e for e in filtered if e.get("actor") == actor]

        # Filter by time range
        if since:
            filtered = [e for e in filtered if e.get("timestamp", "") >= since]

        if until:
            filtered = [e for e in filtered if e.get("timestamp", "") <= until]

        return filtered

    def _build_filter_summary(
        self,
        event_type: Optional[str],
        actor: Optional[str],
        since: Optional[str],
        until: Optional[str],
    ) -> Dict[str, Any]:
        """Build filter summary for response."""
        filters = {}
        if event_type:
            filters["event_type"] = event_type
        if actor:
            filters["actor"] = actor
        if since:
            filters["since"] = since
        if until:
            filters["until"] = until
        return filters if filters else None

    def compute_resource_hash(self, content: str) -> str:
        """Compute SHA-256 hash of resource content for compliance tracking."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    # ========================
    # Enhanced Audit Rules
    # ========================

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

    def _audit_cross_references(
        self, project_key: str, git_manager
    ) -> List[Dict[str, Any]]:
        """
        Audit Rule 1: Validate cross-references between RAID items and PMP deliverables/milestones.

        Returns:
            List of issue dictionaries
        """
        issues = []
        project_path = git_manager.get_project_path(project_key)

        # Load RAID items
        raid_path = project_path / "artifacts" / "raid.json"
        if raid_path.exists():
            try:
                raid_data = json.loads(raid_path.read_text())
                raid_items = raid_data.get("items", [])

                # Check if referenced deliverables exist
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
        """
        Audit Rule 2: Check date consistency (milestone dates vs. project dates).

        Returns:
            List of issue dictionaries
        """
        issues = []
        project_path = git_manager.get_project_path(project_key)

        # Load project metadata
        metadata_path = project_path / "metadata.json"
        if not metadata_path.exists():
            return issues

        try:
            metadata = json.loads(metadata_path.read_text())
            project_start = metadata.get("start_date")
            project_end = metadata.get("end_date")

            # Load milestones from PMP
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
        """
        Audit Rule 3: Validate that referenced owners/users exist.

        Returns:
            List of issue dictionaries
        """
        issues = []
        project_path = git_manager.get_project_path(project_key)

        # Load team members from governance
        governance_path = project_path / "artifacts" / "governance.json"
        valid_users = set()

        if governance_path.exists():
            try:
                governance_data = json.loads(governance_path.read_text())
                team = governance_data.get("team", [])
                valid_users = {member.get("id") for member in team if "id" in member}
            except (json.JSONDecodeError, KeyError):
                pass

        # Check RAID item owners
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
        """
        Audit Rule 4: Detect dependency cycles in deliverables/tasks.

        Returns:
            List of issue dictionaries
        """
        issues = []
        project_path = git_manager.get_project_path(project_key)

        # Load PMP deliverables
        pmp_path = project_path / "artifacts" / "pmp.json"
        if not pmp_path.exists():
            return issues

        try:
            pmp_data = json.loads(pmp_path.read_text())
            deliverables = pmp_data.get("deliverables", [])

            # Build dependency graph
            graph = {}
            for deliverable in deliverables:
                deliverable_id = deliverable.get("id")
                dependencies = deliverable.get("dependencies", [])
                graph[deliverable_id] = dependencies

            # Detect cycles using DFS
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
        """
        Audit Rule 5: Calculate completeness scoring (% of required fields filled).

        Returns:
            List of issue dictionaries (warnings for incomplete artifacts)
        """
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
        """
        Audit Rule 6: Validate required fields are present.

        Returns:
            List of issue dictionaries
        """
        issues = []
        project_path = git_manager.get_project_path(project_key)

        # Check metadata required fields
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
        """
        Audit Rule 7: Validate artifact relationships are consistent.

        Returns:
            List of issue dictionaries
        """
        issues = []
        project_path = git_manager.get_project_path(project_key)

        # Check if RAID items reference valid milestones
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
        """
        Audit Rule 8: Validate workflow states are valid.

        Returns:
            List of issue dictionaries
        """
        issues = []
        project_path = git_manager.get_project_path(project_key)

        # Check workflow state validity
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
        """
        Audit Rule 9: Validate project complies with its blueprint.

        Returns:
            List of issue dictionaries
        """
        issues = []
        project_path = git_manager.get_project_path(project_key)

        # Load project metadata to get blueprint
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

            # Check if required artifacts exist (based on blueprint)
            # For now, just check core artifacts exist
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

    # Helper methods for audit rules

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
        """
        Detect cycles in a dependency graph using DFS.

        Args:
            graph: Dictionary mapping node ID to list of dependency IDs

        Returns:
            List of cycles (each cycle is a list of node IDs)
        """
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
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def _calculate_completeness_score(self, project_key: str, git_manager) -> float:
        """
        Calculate project completeness score (0-100%).

        Args:
            project_key: Project key
            git_manager: Git manager instance

        Returns:
            Completeness score as percentage
        """
        project_path = git_manager.get_project_path(project_key)

        # Define expected artifacts and fields
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
            total_items += 1  # Count artifact existence

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

    def save_audit_history(
        self,
        project_key: str,
        audit_result: Dict[str, Any],
        git_manager,
    ) -> None:
        """
        Save audit result to history.

        Args:
            project_key: Project key
            audit_result: Audit result dictionary
            git_manager: Git manager instance
        """
        project_path = git_manager.get_project_path(project_key)
        history_path = project_path / "audit" / "history.ndjson"
        history_path.parent.mkdir(parents=True, exist_ok=True)

        # Create history entry
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "total_issues": audit_result.get("total_issues", 0),
            "completeness_score": audit_result.get("completeness_score", 0.0),
            "rule_violations": audit_result.get("rule_violations", {}),
        }

        # Append to NDJSON
        entry_line = json.dumps(entry)
        with history_path.open("a") as f:
            f.write(entry_line + "\n")

    def get_audit_history(
        self,
        project_key: str,
        git_manager,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit history for a project.

        Args:
            project_key: Project key
            git_manager: Git manager instance
            limit: Maximum number of entries to return

        Returns:
            List of audit history entries (newest first)
        """
        project_path = git_manager.get_project_path(project_key)
        history_path = project_path / "audit" / "history.ndjson"

        if not history_path.exists():
            return []

        entries = []
        with history_path.open("r") as f:
            for line in f:
                if line.strip():
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue

        # Return newest first
        entries.reverse()
        return entries[:limit]
