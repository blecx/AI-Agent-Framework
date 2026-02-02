"""
Audit Orchestrator - coordinates audit operations and history.
Single Responsibility: Coordinate event logging, rule execution, and history tracking.
"""

import json
from typing import Dict, Any, List
from datetime import datetime, timezone

from domain.audit.constants import DEFAULT_QUERY_LIMIT
from .event_logger import AuditEventLogger
from .rules_engine import AuditRulesEngine


class AuditOrchestrator:
    """Service for orchestrating audit operations."""

    def __init__(
        self,
        event_logger: AuditEventLogger = None,
        rules_engine: AuditRulesEngine = None,
    ):
        """
        Initialize audit orchestrator.

        Args:
            event_logger: Event logger instance (creates new if None)
            rules_engine: Rules engine instance (creates new if None)
        """
        self.event_logger = event_logger or AuditEventLogger()
        self.rules_engine = rules_engine or AuditRulesEngine()

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

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "total_issues": audit_result.get("total_issues", 0),
            "completeness_score": audit_result.get("completeness_score", 0.0),
            "rule_violations": audit_result.get("rule_violations", {}),
        }

        entry_line = json.dumps(entry)
        with history_path.open("a") as f:
            f.write(entry_line + "\n")

    def get_audit_history(
        self,
        project_key: str,
        git_manager,
        limit: int = DEFAULT_QUERY_LIMIT,
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

        entries.reverse()
        return entries[:limit]
