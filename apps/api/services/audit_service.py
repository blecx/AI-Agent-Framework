"""
Audit service - backward-compatible facade for refactored audit subsystem.
Delegates to focused services: AuditEventLogger, AuditRulesEngine, AuditOrchestrator.

DEPRECATED FACADE: Prefer using focused services directly for new code:
- AuditEventLogger for event logging/retrieval
- AuditRulesEngine for validation rules
- AuditOrchestrator for history and coordination
"""

from typing import Dict, Any, Optional, List

from domain.audit.constants import DEFAULT_QUERY_LIMIT
from .audit.event_logger import AuditEventLogger
from .audit.rules_engine import AuditRulesEngine
from .audit.orchestrator import AuditOrchestrator


class AuditService:
    """
    Backward-compatible facade for audit operations.

    This class maintains API compatibility while delegating to focused services.
    For new code, prefer using the focused services directly.
    """

    def __init__(self):
        """Initialize audit service with focused service instances."""
        self.event_logger = AuditEventLogger()
        self.rules_engine = AuditRulesEngine()
        self.orchestrator = AuditOrchestrator(self.event_logger, self.rules_engine)

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
        """Delegate to AuditEventLogger."""
        return self.event_logger.log_audit_event(
            project_key=project_key,
            event_type=event_type,
            actor=actor,
            payload_summary=payload_summary,
            resource_hash=resource_hash,
            git_manager=git_manager,
            correlation_id=correlation_id,
        )

    def get_audit_events(
        self,
        project_key: str,
        git_manager,
        event_type: Optional[str] = None,
        actor: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        limit: int = DEFAULT_QUERY_LIMIT,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Delegate to AuditEventLogger."""
        return self.event_logger.get_audit_events(
            project_key=project_key,
            git_manager=git_manager,
            event_type=event_type,
            actor=actor,
            since=since,
            until=until,
            limit=limit,
            offset=offset,
        )

    def run_audit_rules(
        self,
        project_key: str,
        git_manager,
        rule_set: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Delegate to AuditRulesEngine."""
        return self.rules_engine.run_audit_rules(
            project_key=project_key,
            git_manager=git_manager,
            rule_set=rule_set,
        )

    def compute_resource_hash(self, content: str) -> str:
        """Delegate to AuditRulesEngine."""
        return self.rules_engine.compute_resource_hash(content)

    def save_audit_history(
        self,
        project_key: str,
        audit_result: Dict[str, Any],
        git_manager,
    ) -> None:
        """Delegate to AuditOrchestrator."""
        return self.orchestrator.save_audit_history(
            project_key=project_key,
            audit_result=audit_result,
            git_manager=git_manager,
        )

    def get_audit_history(
        self,
        project_key: str,
        git_manager,
        limit: int = DEFAULT_QUERY_LIMIT,
    ) -> List[Dict[str, Any]]:
        """Delegate to AuditOrchestrator."""
        return self.orchestrator.get_audit_history(
            project_key=project_key,
            git_manager=git_manager,
            limit=limit,
        )

    def _calculate_completeness_score(self, project_key: str, git_manager) -> float:
        """Delegate to AuditRulesEngine (for backward compatibility with tests)."""
        return self.rules_engine._calculate_completeness_score(
            project_key=project_key,
            git_manager=git_manager,
        )
