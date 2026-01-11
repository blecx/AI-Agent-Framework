"""
Audit service for managing audit events in NDJSON format.
Provides event logging and retrieval with filtering capabilities.
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
