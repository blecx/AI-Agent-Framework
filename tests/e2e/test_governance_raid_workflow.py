"""
End-to-end tests for ISO 21500/21502 Governance and RAID workflows.

These tests validate complete project governance and RAID management workflows,
ensuring all components work together correctly in realistic scenarios.
"""

import pytest
from fastapi.testclient import TestClient
import tempfile
import shutil
import sys
import os

# Add apps/api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))


@pytest.fixture(scope="function")
def temp_project_dir():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def client(temp_project_dir):
    """Create a test client with temporary project directory."""
    # Override the PROJECT_DOCS_PATH environment variable
    os.environ["PROJECT_DOCS_PATH"] = temp_project_dir

    # Create a new app instance for this test to avoid state sharing
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    test_app = FastAPI(title="Test App")
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import and register routers
    from routers import projects, commands, artifacts, governance, raid

    test_app.include_router(projects.router, prefix="/projects", tags=["projects"])
    test_app.include_router(
        commands.router, prefix="/projects/{project_key}/commands", tags=["commands"]
    )
    test_app.include_router(
        artifacts.router,
        prefix="/projects/{project_key}/artifacts",
        tags=["artifacts"],
    )
    test_app.include_router(
        governance.router,
        prefix="/projects/{project_key}/governance",
        tags=["governance"],
    )
    test_app.include_router(
        raid.router, prefix="/projects/{project_key}/raid", tags=["raid"]
    )

    # Initialize services
    from services.git_manager import GitManager
    from services.llm_service import LLMService

    git_manager = GitManager(temp_project_dir)
    git_manager.ensure_repository()
    test_app.state.git_manager = git_manager
    test_app.state.llm_service = LLMService()

    with TestClient(test_app) as test_client:
        yield test_client


class TestCompleteGovernanceWorkflow:
    """Test end-to-end governance workflow."""

    def test_complete_governance_lifecycle(self, client):
        """
        Test complete governance workflow:
        1. Create project
        2. Set up governance metadata
        3. Record decisions
        4. Link decisions to RAID items
        5. Query and verify traceability
        """
        # Step 1: Create a project
        project_response = client.post(
            "/projects", json={"key": "E2E_GOV", "name": "E2E Governance Test Project"}
        )
        assert project_response.status_code == 201
        project = project_response.json()
        assert project["key"] == "E2E_GOV"

        # Step 2: Set up governance metadata
        governance_metadata = {
            "objectives": [
                "Deliver high-quality software",
                "Maintain ISO 21500 compliance",
                "Manage risks effectively",
            ],
            "scope": "End-to-end testing of governance and RAID integration",
            "stakeholders": [
                {
                    "name": "Alice Johnson",
                    "role": "Project Manager",
                    "responsibilities": "Overall project delivery and governance",
                },
                {
                    "name": "Bob Smith",
                    "role": "Tech Lead",
                    "responsibilities": "Technical decisions and architecture",
                },
                {
                    "name": "Carol Davis",
                    "role": "Risk Manager",
                    "responsibilities": "Risk identification and mitigation",
                },
            ],
            "decision_rights": {
                "architecture": "Tech Lead",
                "budget": "Project Manager",
                "scope_changes": "Steering Committee",
                "risk_acceptance": "Risk Manager",
            },
            "stage_gates": [
                {
                    "name": "Requirements Review",
                    "date": "2026-02-01",
                    "status": "pending",
                    "criteria": "All requirements documented and approved",
                },
                {
                    "name": "Design Approval",
                    "date": "2026-03-01",
                    "status": "pending",
                    "criteria": "Architecture reviewed and approved by stakeholders",
                },
            ],
            "approvals": [
                {"type": "budget", "approver": "CFO", "status": "pending"},
                {"type": "technical", "approver": "CTO", "status": "pending"},
            ],
            "created_by": "e2e_test",
        }

        metadata_response = client.post(
            "/projects/E2E_GOV/governance/metadata", json=governance_metadata
        )
        assert metadata_response.status_code == 201
        metadata = metadata_response.json()
        assert len(metadata["objectives"]) == 3
        assert len(metadata["stakeholders"]) == 3
        assert metadata["created_by"] == "e2e_test"

        # Step 3: Record governance decisions
        decision1_data = {
            "title": "Adopt microservices architecture",
            "description": "Decision to use microservices architecture for better scalability",
            "decision_maker": "Tech Lead",
            "rationale": "Microservices provide better scalability and independent deployment",
            "impact": "Requires additional infrastructure setup and team training",
            "status": "approved",
            "created_by": "e2e_test",
        }

        decision1_response = client.post(
            "/projects/E2E_GOV/governance/decisions", json=decision1_data
        )
        assert decision1_response.status_code == 201
        decision1 = decision1_response.json()
        assert decision1["title"] == "Adopt microservices architecture"
        decision1_id = decision1["id"]

        decision2_data = {
            "title": "Implement comprehensive testing strategy",
            "description": "Decision to implement unit, integration, and e2e tests",
            "decision_maker": "Tech Lead",
            "rationale": "Comprehensive testing ensures quality and reduces bugs",
            "impact": "Increases development time but reduces post-release issues",
            "status": "approved",
            "created_by": "e2e_test",
        }

        decision2_response = client.post(
            "/projects/E2E_GOV/governance/decisions", json=decision2_data
        )
        assert decision2_response.status_code == 201
        decision2 = decision2_response.json()
        decision2_id = decision2["id"]

        # Step 4: Create RAID items related to decisions
        raid1_data = {
            "type": "risk",
            "title": "Microservices complexity risk",
            "description": "Team lacks experience with microservices architecture",
            "owner": "Tech Lead",
            "priority": "high",
            "impact": "high",
            "likelihood": "possible",
            "mitigation_plan": "Provide training and hire experienced architect",
            "next_actions": ["Schedule training sessions", "Recruit senior architect"],
            "created_by": "e2e_test",
        }

        raid1_response = client.post("/projects/E2E_GOV/raid", json=raid1_data)
        assert raid1_response.status_code == 201
        raid1 = raid1_response.json()
        raid1_id = raid1["id"]

        # Step 5: Link decision to RAID item (bidirectional)
        # Link from decision side
        link_response1 = client.post(
            f"/projects/E2E_GOV/governance/decisions/{decision1_id}/link-raid/{raid1_id}"
        )
        assert link_response1.status_code == 200

        # Link from RAID side (for bidirectional traceability)
        link_response2 = client.post(
            f"/projects/E2E_GOV/raid/{raid1_id}/link-decision/{decision1_id}"
        )
        assert link_response2.status_code == 200

        # Step 6: Verify traceability - check decision has RAID link
        decision_check = client.get(
            f"/projects/E2E_GOV/governance/decisions/{decision1_id}"
        )
        assert decision_check.status_code == 200
        decision_data = decision_check.json()
        assert raid1_id in decision_data["linked_raid_ids"]

        # Step 7: Query RAID items by decision
        raid_by_decision = client.get(
            f"/projects/E2E_GOV/raid/by-decision/{decision1_id}"
        )
        assert raid_by_decision.status_code == 200
        raid_items = raid_by_decision.json()
        assert raid_items["total"] == 1
        assert raid_items["items"][0]["id"] == raid1_id

        # Step 8: List all decisions
        all_decisions = client.get("/projects/E2E_GOV/governance/decisions")
        assert all_decisions.status_code == 200
        decisions_list = all_decisions.json()
        assert len(decisions_list) == 2
        decision_ids = {decision["id"] for decision in decisions_list}
        assert decision1_id in decision_ids
        assert decision2_id in decision_ids

        # Step 9: List all RAID items
        all_raid = client.get("/projects/E2E_GOV/raid")
        assert all_raid.status_code == 200
        raid_list = all_raid.json()
        assert raid_list["total"] == 1


class TestCompleteRAIDWorkflow:
    """Test end-to-end RAID register workflow."""

    def test_complete_raid_lifecycle(self, client):
        """
        Test complete RAID workflow:
        1. Create project
        2. Create multiple RAID items of different types
        3. Update RAID items through their lifecycle
        4. Filter and query RAID items
        5. Link RAID items to decisions
        6. Verify audit trail
        """
        # Step 1: Create project
        project_response = client.post(
            "/projects", json={"key": "E2E_RAID", "name": "E2E RAID Test Project"}
        )
        assert project_response.status_code == 201

        # Step 2: Create RAID items of all types
        # Risk
        risk_data = {
            "type": "risk",
            "title": "Database migration failure risk",
            "description": "Migration from MySQL to PostgreSQL may encounter data integrity issues",
            "owner": "Database Admin",
            "priority": "critical",
            "impact": "very_high",
            "likelihood": "possible",
            "mitigation_plan": "Comprehensive testing, rollback plan, staged migration",
            "next_actions": [
                "Create test environment",
                "Document rollback procedure",
                "Perform dry run",
            ],
            "created_by": "e2e_test",
            "target_resolution_date": "2026-02-15",
        }
        risk_response = client.post("/projects/E2E_RAID/raid", json=risk_data)
        assert risk_response.status_code == 201
        risk = risk_response.json()
        risk_id = risk["id"]
        assert risk["type"] == "risk"
        assert risk["status"] == "open"

        # Assumption
        assumption_data = {
            "type": "assumption",
            "title": "Third-party API availability",
            "description": "Assuming payment gateway API will be available 99.9% uptime",
            "owner": "Integration Lead",
            "priority": "high",
            "mitigation_plan": "Implement fallback payment method and retry logic",
            "next_actions": ["Verify SLA with vendor", "Implement circuit breaker"],
            "created_by": "e2e_test",
        }
        assumption_response = client.post(
            "/projects/E2E_RAID/raid", json=assumption_data
        )
        assert assumption_response.status_code == 201
        assumption = assumption_response.json()
        assert assumption["type"] == "assumption"

        # Issue
        issue_data = {
            "type": "issue",
            "title": "Production deployment failed",
            "description": "Latest release deployment failed due to configuration error",
            "owner": "DevOps Lead",
            "priority": "critical",
            "status": "in_progress",
            "mitigation_plan": "Rollback to previous version, fix configuration, redeploy",
            "next_actions": [
                "Rollback completed",
                "Root cause analysis in progress",
                "Configuration fix being tested",
            ],
            "created_by": "e2e_test",
            "target_resolution_date": "2026-01-12",
        }
        issue_response = client.post("/projects/E2E_RAID/raid", json=issue_data)
        assert issue_response.status_code == 201
        issue = issue_response.json()
        issue_id = issue["id"]
        assert issue["type"] == "issue"
        assert issue["status"] == "in_progress"

        # Dependency
        dependency_data = {
            "type": "dependency",
            "title": "API integration depends on vendor timeline",
            "description": "Payment gateway integration requires vendor to complete API v2",
            "owner": "Integration Lead",
            "priority": "high",
            "mitigation_plan": "Weekly check-ins with vendor, fallback to API v1 if delayed",
            "next_actions": [
                "Schedule vendor status meeting",
                "Document API v1 fallback approach",
            ],
            "created_by": "e2e_test",
            "target_resolution_date": "2026-02-28",
        }
        dependency_response = client.post(
            "/projects/E2E_RAID/raid", json=dependency_data
        )
        assert dependency_response.status_code == 201
        dependency = dependency_response.json()
        assert dependency["type"] == "dependency"

        # Step 3: Update RAID items through lifecycle
        # Update risk from open to in_progress
        risk_update = {
            "status": "in_progress",
            "next_actions": [
                "Test environment created ✓",
                "Rollback procedure documented ✓",
                "Dry run scheduled for next week",
            ],
            "updated_by": "e2e_test",
        }
        risk_update_response = client.put(
            f"/projects/E2E_RAID/raid/{risk_id}", json=risk_update
        )
        assert risk_update_response.status_code == 200
        updated_risk = risk_update_response.json()
        assert updated_risk["status"] == "in_progress"

        # Update issue to closed
        issue_update = {
            "status": "closed",
            "mitigation_plan": "Issue resolved - deployment successful after configuration fix",
            "updated_by": "e2e_test",
        }
        issue_update_response = client.put(
            f"/projects/E2E_RAID/raid/{issue_id}", json=issue_update
        )
        assert issue_update_response.status_code == 200
        updated_issue = issue_update_response.json()
        assert updated_issue["status"] == "closed"

        # Step 4: Filter and query RAID items
        # Filter by type=risk
        risks_response = client.get("/projects/E2E_RAID/raid?type=risk")
        assert risks_response.status_code == 200
        risks_data = risks_response.json()
        assert risks_data["total"] == 1
        assert all(item["type"] == "risk" for item in risks_data["items"])

        # Filter by status=in_progress
        in_progress_response = client.get("/projects/E2E_RAID/raid?status=in_progress")
        assert in_progress_response.status_code == 200
        in_progress_data = in_progress_response.json()
        assert in_progress_data["total"] == 1

        # Filter by priority=critical
        critical_response = client.get("/projects/E2E_RAID/raid?priority=critical")
        assert critical_response.status_code == 200
        critical_data = critical_response.json()
        assert critical_data["total"] >= 1

        # Filter by owner
        owner_response = client.get("/projects/E2E_RAID/raid?owner=Integration%20Lead")
        assert owner_response.status_code == 200
        owner_data = owner_response.json()
        assert owner_data["total"] == 2  # assumption and dependency

        # Step 5: Create decision and link RAID items
        decision_data = {
            "title": "Approve database migration with enhanced safeguards",
            "description": "Decision to proceed with migration using staged approach",
            "decision_maker": "CTO",
            "rationale": "Benefits outweigh risks with proper safeguards",
            "impact": "Improved performance and scalability",
            "status": "approved",
            "created_by": "e2e_test",
        }
        decision_response = client.post(
            "/projects/E2E_RAID/governance/decisions", json=decision_data
        )
        assert decision_response.status_code == 201
        decision = decision_response.json()
        decision_id = decision["id"]

        # Link decision to risk (bidirectional)
        link_response1 = client.post(
            f"/projects/E2E_RAID/raid/{risk_id}/link-decision/{decision_id}"
        )
        assert link_response1.status_code == 200

        link_response2 = client.post(
            f"/projects/E2E_RAID/governance/decisions/{decision_id}/link-raid/{risk_id}"
        )
        assert link_response2.status_code == 200

        # Verify link
        risk_check = client.get(f"/projects/E2E_RAID/raid/{risk_id}")
        assert risk_check.status_code == 200
        risk_data = risk_check.json()
        assert decision_id in risk_data["linked_decisions"]

        # Step 6: List all RAID items and verify count
        all_raid_response = client.get("/projects/E2E_RAID/raid")
        assert all_raid_response.status_code == 200
        all_raid = all_raid_response.json()
        assert all_raid["total"] == 4  # risk, assumption, issue, dependency


class TestIntegratedGovernanceRAIDWorkflow:
    """Test integrated governance and RAID workflow."""

    def test_project_lifecycle_with_governance_and_raid(self, client):
        """
        Test realistic project lifecycle integrating governance and RAID:
        1. Create project with governance setup
        2. Identify and record risks
        3. Make governance decisions to address risks
        4. Track issues that arise
        5. Update RAID items as project progresses
        6. Maintain traceability throughout
        """
        # Step 1: Create project
        project_response = client.post(
            "/projects",
            json={"key": "E2E_INT", "name": "E2E Integrated Workflow Test"},
        )
        assert project_response.status_code == 201

        # Step 2: Set up governance
        governance_data = {
            "objectives": ["Deliver on time", "Maintain quality", "Control costs"],
            "scope": "Integrated project with full governance and risk management",
            "stakeholders": [
                {"name": "PM", "role": "Manager", "responsibilities": "Delivery"}
            ],
            "decision_rights": {"technical": "Tech Lead", "budget": "PM"},
            "stage_gates": [{"name": "Milestone 1", "status": "pending"}],
            "created_by": "e2e_test",
        }
        gov_response = client.post(
            "/projects/E2E_INT/governance/metadata", json=governance_data
        )
        assert gov_response.status_code == 201

        # Step 3: Identify initial risks
        risk1 = {
            "type": "risk",
            "title": "Resource availability risk",
            "description": "Key team member may leave",
            "owner": "PM",
            "priority": "high",
            "impact": "high",
            "likelihood": "possible",
            "mitigation_plan": "Cross-training and knowledge transfer",
            "created_by": "e2e_test",
        }
        risk1_response = client.post("/projects/E2E_INT/raid", json=risk1)
        assert risk1_response.status_code == 201
        risk1_id = risk1_response.json()["id"]

        # Step 4: Make decision to address risk
        decision1 = {
            "title": "Approve retention bonus",
            "description": "Decision to offer retention bonus to key team member",
            "decision_maker": "PM",
            "rationale": "Retention is critical to project success",
            "impact": "Budget increase but reduced risk",
            "status": "approved",
            "created_by": "e2e_test",
        }
        decision1_response = client.post(
            "/projects/E2E_INT/governance/decisions", json=decision1
        )
        assert decision1_response.status_code == 201
        decision1_id = decision1_response.json()["id"]

        # Link decision to risk (bidirectional)
        client.post(
            f"/projects/E2E_INT/governance/decisions/{decision1_id}/link-raid/{risk1_id}"
        )
        client.post(f"/projects/E2E_INT/raid/{risk1_id}/link-decision/{decision1_id}")

        # Step 5: Track progress - risk mitigated
        risk_update = {
            "status": "mitigated",
            "mitigation_plan": "Retention bonus accepted, knowledge transfer 80% complete",
            "updated_by": "e2e_test",
        }
        client.put(f"/projects/E2E_INT/raid/{risk1_id}", json=risk_update)

        # Step 6: New issue arises
        issue = {
            "type": "issue",
            "title": "Integration test failures",
            "description": "Recent code changes broke integration tests",
            "owner": "Tech Lead",
            "priority": "high",
            "status": "open",
            "mitigation_plan": "Investigate and fix, add regression tests",
            "created_by": "e2e_test",
        }
        issue_response = client.post("/projects/E2E_INT/raid", json=issue)
        assert issue_response.status_code == 201
        issue_id = issue_response.json()["id"]

        # Step 7: Make decision on issue resolution approach
        decision2 = {
            "title": "Rollback breaking changes",
            "description": "Decision to rollback changes and fix properly",
            "decision_maker": "Tech Lead",
            "rationale": "Maintain test suite integrity",
            "impact": "Short delay but better quality",
            "status": "approved",
            "created_by": "e2e_test",
        }
        decision2_response = client.post(
            "/projects/E2E_INT/governance/decisions", json=decision2
        )
        assert decision2_response.status_code == 201
        decision2_id = decision2_response.json()["id"]

        # Link decision to issue (bidirectional)
        client.post(f"/projects/E2E_INT/raid/{issue_id}/link-decision/{decision2_id}")
        client.post(
            f"/projects/E2E_INT/governance/decisions/{decision2_id}/link-raid/{issue_id}"
        )

        # Step 8: Update issue to closed
        issue_update = {
            "status": "closed",
            "mitigation_plan": "Changes rolled back, fixes applied, tests passing",
            "updated_by": "e2e_test",
        }
        client.put(f"/projects/E2E_INT/raid/{issue_id}", json=issue_update)

        # Step 9: Verify final state
        # All decisions
        decisions = client.get("/projects/E2E_INT/governance/decisions").json()
        assert len(decisions) == 2

        # All RAID items
        raid_items = client.get("/projects/E2E_INT/raid").json()
        assert raid_items["total"] == 2

        # Check traceability - both RAID items should be linked to decisions
        risk_final = client.get(f"/projects/E2E_INT/raid/{risk1_id}").json()
        assert len(risk_final["linked_decisions"]) == 1

        issue_final = client.get(f"/projects/E2E_INT/raid/{issue_id}").json()
        assert len(issue_final["linked_decisions"]) == 1

        # Verify both RAID items are in non-open status (workflow completed)
        assert risk_final["status"] == "mitigated"
        assert issue_final["status"] == "closed"


class TestRAIDFilteringAndQuerying:
    """Test comprehensive RAID filtering and querying scenarios."""

    def test_complex_raid_filtering(self, client):
        """Test complex filtering scenarios for RAID items."""
        # Create project
        client.post("/projects", json={"key": "E2E_FLT", "name": "E2E Filtering Test"})

        # Create diverse RAID items for filtering
        raid_items = [
            {
                "type": "risk",
                "title": "Risk A",
                "description": "Test",
                "owner": "Alice",
                "priority": "critical",
                "status": "open",
                "created_by": "test",
            },
            {
                "type": "risk",
                "title": "Risk B",
                "description": "Test",
                "owner": "Bob",
                "priority": "high",
                "status": "in_progress",
                "created_by": "test",
            },
            {
                "type": "issue",
                "title": "Issue A",
                "description": "Test",
                "owner": "Alice",
                "priority": "critical",
                "status": "open",
                "created_by": "test",
            },
            {
                "type": "issue",
                "title": "Issue B",
                "description": "Test",
                "owner": "Bob",
                "priority": "medium",
                "status": "closed",
                "created_by": "test",
            },
            {
                "type": "assumption",
                "title": "Assumption A",
                "description": "Test",
                "owner": "Alice",
                "priority": "low",
                "status": "open",
                "created_by": "test",
            },
        ]

        for item in raid_items:
            response = client.post("/projects/E2E_FLT/raid", json=item)
            assert response.status_code == 201

        # Test various filtering combinations
        # Filter by type
        risks = client.get("/projects/E2E_FLT/raid?type=risk").json()
        assert risks["total"] == 2

        # Filter by status
        open_items = client.get("/projects/E2E_FLT/raid?status=open").json()
        assert open_items["total"] == 3

        # Filter by owner
        alice_items = client.get("/projects/E2E_FLT/raid?owner=Alice").json()
        assert alice_items["total"] == 3

        # Filter by priority
        critical_items = client.get("/projects/E2E_FLT/raid?priority=critical").json()
        assert critical_items["total"] == 2

        # Multiple filters - type=risk AND owner=Alice
        alice_risks = client.get("/projects/E2E_FLT/raid?type=risk&owner=Alice").json()
        assert alice_risks["total"] == 1
        assert alice_risks["items"][0]["title"] == "Risk A"

        # Multiple filters - status=open AND priority=critical
        open_critical = client.get(
            "/projects/E2E_FLT/raid?status=open&priority=critical"
        ).json()
        assert open_critical["total"] == 2

        # Complex filter - type=issue AND status=closed AND owner=Bob
        bob_closed_issues = client.get(
            "/projects/E2E_FLT/raid?type=issue&status=closed&owner=Bob"
        ).json()
        assert bob_closed_issues["total"] == 1
        assert bob_closed_issues["items"][0]["title"] == "Issue B"
