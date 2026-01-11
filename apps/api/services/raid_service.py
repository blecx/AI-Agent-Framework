"""
RAID register service for managing Risks, Assumptions, Issues, and Dependencies.
Aligned with ISO 21500/21502 standards.
"""

import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class RAIDService:
    """Service for handling RAID register items."""

    def __init__(self):
        """Initialize RAID service."""
        pass

    # ========================================================================
    # RAID Item CRUD Operations
    # ========================================================================

    def get_raid_items(self, project_key: str, git_manager) -> List[Dict[str, Any]]:
        """Get all RAID items for a project."""
        content = git_manager.read_file(project_key, "governance/raid_register.json")
        if content is None:
            return []

        data = json.loads(content)
        return data.get("items", [])

    def get_raid_item(
        self, project_key: str, raid_id: str, git_manager
    ) -> Optional[Dict[str, Any]]:
        """Get a specific RAID item by ID."""
        items = self.get_raid_items(project_key, git_manager)
        for item in items:
            if item["id"] == raid_id:
                return item
        return None

    def create_raid_item(
        self, project_key: str, item_data: Dict[str, Any], git_manager
    ) -> Dict[str, Any]:
        """Create a new RAID item."""
        items = self.get_raid_items(project_key, git_manager)

        # Generate unique ID
        raid_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        raid_item = {
            "id": raid_id,
            "type": item_data["type"],
            "title": item_data["title"],
            "description": item_data["description"],
            "status": item_data.get("status", "open"),
            "owner": item_data["owner"],
            "priority": item_data.get("priority", "medium"),
            "impact": item_data.get("impact"),
            "likelihood": item_data.get("likelihood"),
            "mitigation_plan": item_data.get("mitigation_plan", ""),
            "next_actions": item_data.get("next_actions", []),
            "linked_decisions": item_data.get("linked_decisions", []),
            "linked_change_requests": item_data.get("linked_change_requests", []),
            "created_at": now,
            "updated_at": now,
            "created_by": item_data.get("created_by", "system"),
            "updated_by": item_data.get("created_by", "system"),
            "target_resolution_date": item_data.get("target_resolution_date"),
        }

        items.append(raid_item)

        # Write RAID register
        content = json.dumps({"items": items}, indent=2)
        git_manager.write_file(project_key, "governance/raid_register.json", content)

        # Commit changes
        git_manager.commit_changes(
            project_key,
            f"[{project_key}] Add {raid_item['type']}: {raid_item['title']}",
            ["governance/raid_register.json"],
        )

        # Log event
        git_manager.log_event(
            project_key,
            {
                "event_type": "raid_item_created",
                "project_key": project_key,
                "raid_id": raid_id,
                "raid_type": raid_item["type"],
                "created_by": raid_item["created_by"],
            },
        )

        return raid_item

    def update_raid_item(
        self, project_key: str, raid_id: str, updates: Dict[str, Any], git_manager
    ) -> Dict[str, Any]:
        """Update an existing RAID item."""
        items = self.get_raid_items(project_key, git_manager)

        # Find and update the item
        updated_item = None
        for item in items:
            if item["id"] == raid_id:
                now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

                # Update fields
                for key, value in updates.items():
                    if (
                        key not in ["id", "created_at", "created_by"]
                        and value is not None
                    ):
                        item[key] = value

                item["updated_at"] = now
                if "updated_by" in updates:
                    item["updated_by"] = updates["updated_by"]

                updated_item = item
                break

        if updated_item is None:
            raise ValueError(f"RAID item {raid_id} not found")

        # Write updated RAID register
        content = json.dumps({"items": items}, indent=2)
        git_manager.write_file(project_key, "governance/raid_register.json", content)

        # Commit changes
        git_manager.commit_changes(
            project_key,
            f"[{project_key}] Update {updated_item['type']}: {updated_item['title']}",
            ["governance/raid_register.json"],
        )

        # Log event
        git_manager.log_event(
            project_key,
            {
                "event_type": "raid_item_updated",
                "project_key": project_key,
                "raid_id": raid_id,
                "updated_by": updated_item["updated_by"],
            },
        )

        return updated_item

    def delete_raid_item(self, project_key: str, raid_id: str, git_manager) -> bool:
        """Delete a RAID item."""
        items = self.get_raid_items(project_key, git_manager)

        # Find and remove the item
        deleted_item = None
        filtered_items = []
        for item in items:
            if item["id"] == raid_id:
                deleted_item = item
            else:
                filtered_items.append(item)

        if deleted_item is None:
            return False

        # Write updated RAID register
        content = json.dumps({"items": filtered_items}, indent=2)
        git_manager.write_file(project_key, "governance/raid_register.json", content)

        # Commit changes
        git_manager.commit_changes(
            project_key,
            f"[{project_key}] Delete {deleted_item['type']}: {deleted_item['title']}",
            ["governance/raid_register.json"],
        )

        # Log event
        git_manager.log_event(
            project_key,
            {
                "event_type": "raid_item_deleted",
                "project_key": project_key,
                "raid_id": raid_id,
            },
        )

        return True

    # ========================================================================
    # Filtering and Querying
    # ========================================================================

    def filter_raid_items(
        self,
        items: List[Dict[str, Any]],
        raid_type: Optional[str] = None,
        status: Optional[str] = None,
        owner: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Filter RAID items by various criteria."""
        filtered = items

        if raid_type:
            filtered = [item for item in filtered if item["type"] == raid_type]

        if status:
            filtered = [item for item in filtered if item["status"] == status]

        if owner:
            filtered = [item for item in filtered if item["owner"] == owner]

        if priority:
            filtered = [item for item in filtered if item["priority"] == priority]

        return filtered

    # ========================================================================
    # Traceability and Linking
    # ========================================================================

    def link_raid_to_decision(
        self, project_key: str, raid_id: str, decision_id: str, git_manager
    ) -> bool:
        """Link a RAID item to a governance decision."""
        items = self.get_raid_items(project_key, git_manager)

        updated = False
        for item in items:
            if item["id"] == raid_id:
                if decision_id not in item["linked_decisions"]:
                    item["linked_decisions"].append(decision_id)
                    updated = True
                break

        if not updated:
            return False

        # Write updated RAID register
        content = json.dumps({"items": items}, indent=2)
        git_manager.write_file(project_key, "governance/raid_register.json", content)

        # Commit changes
        git_manager.commit_changes(
            project_key,
            f"[{project_key}] Link RAID {raid_id} to decision {decision_id}",
            ["governance/raid_register.json"],
        )

        return True

    def get_raid_items_by_decision(
        self, project_key: str, decision_id: str, git_manager
    ) -> List[Dict[str, Any]]:
        """Get all RAID items linked to a specific decision."""
        items = self.get_raid_items(project_key, git_manager)
        return [
            item for item in items if decision_id in item.get("linked_decisions", [])
        ]
