"""
Unit tests for Command Service.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from apps.api.services.command_service import CommandService


class TestCommandServiceInit:
    """Test command service initialization."""

    def test_init_creates_empty_proposals(self):
        """Test that initialization creates empty proposals dict."""
        service = CommandService()
        assert service.proposals == {}
        assert isinstance(service.proposals, dict)


class TestProposeCommand:
    """Test command proposal functionality."""

    @pytest.fixture
    def command_service(self):
        """Create a command service instance."""
        return CommandService()

    @pytest.fixture
    def mock_git_manager(self):
        """Create a mock git manager."""
        mock = Mock()
        mock.read_project_json.return_value = {"key": "TEST001", "name": "Test Project"}
        mock.list_artifacts.return_value = []
        mock.get_diff.return_value = "--- test diff ---"
        return mock

    @pytest.fixture
    def mock_llm_service(self):
        """Create a mock LLM service."""
        mock = Mock()
        mock.render_prompt.return_value = "test prompt"
        mock.chat_completion = AsyncMock(return_value="LLM response")
        mock.render_output.return_value = "rendered output"
        return mock

    @pytest.mark.asyncio
    async def test_propose_unknown_command_raises_error(
        self, command_service, mock_git_manager, mock_llm_service
    ):
        """Test that unknown command raises ValueError."""
        with pytest.raises(ValueError, match="Unknown command: invalid_command"):
            await command_service.propose_command(
                "TEST001", "invalid_command", {}, mock_llm_service, mock_git_manager
            )

    @pytest.mark.asyncio
    async def test_propose_command_nonexistent_project(
        self, command_service, mock_llm_service
    ):
        """Test proposing command for nonexistent project."""
        mock_git = Mock()
        mock_git.read_project_json.return_value = None

        with pytest.raises(ValueError, match="Project TEST001 not found"):
            await command_service.propose_command(
                "TEST001", "assess_gaps", {}, mock_llm_service, mock_git
            )

    @pytest.mark.asyncio
    async def test_propose_assess_gaps(
        self, command_service, mock_git_manager, mock_llm_service
    ):
        """Test proposing gap assessment command."""
        result = await command_service.propose_command(
            "TEST001", "assess_gaps", {}, mock_llm_service, mock_git_manager
        )

        assert "proposal_id" in result
        assert result["project_key"] == "TEST001"
        assert result["command"] == "assess_gaps"
        assert "assistant_message" in result
        assert "file_changes" in result
        assert "draft_commit_message" in result
        assert len(result["file_changes"]) == 1
        assert result["file_changes"][0]["path"] == "reports/gap_assessment.md"

        # Verify proposal was stored
        assert result["proposal_id"] in command_service.proposals

    @pytest.mark.asyncio
    async def test_propose_generate_artifact(
        self, command_service, mock_git_manager, mock_llm_service
    ):
        """Test proposing artifact generation command."""
        params = {"artifact_name": "project_charter.md", "artifact_type": "project_charter"}

        result = await command_service.propose_command(
            "TEST001", "generate_artifact", params, mock_llm_service, mock_git_manager
        )

        assert "proposal_id" in result
        assert result["project_key"] == "TEST001"
        assert result["command"] == "generate_artifact"
        assert len(result["file_changes"]) == 1
        assert result["file_changes"][0]["path"] == "artifacts/project_charter.md"

    @pytest.mark.asyncio
    async def test_propose_generate_plan(
        self, command_service, mock_git_manager, mock_llm_service
    ):
        """Test proposing plan generation command."""
        result = await command_service.propose_command(
            "TEST001", "generate_plan", {}, mock_llm_service, mock_git_manager
        )

        assert "proposal_id" in result
        assert result["project_key"] == "TEST001"
        assert result["command"] == "generate_plan"
        assert len(result["file_changes"]) == 1
        assert result["file_changes"][0]["path"] == "artifacts/schedule.md"


class TestApplyProposal:
    """Test proposal application functionality."""

    @pytest.fixture
    def command_service(self):
        """Create a command service with a stored proposal."""
        service = CommandService()
        # Pre-populate with a test proposal
        service.proposals["test-proposal-id"] = {
            "proposal_id": "test-proposal-id",
            "project_key": "TEST001",
            "command": "assess_gaps",
            "params": {},
            "assistant_message": "Test message",
            "draft_commit_message": "[TEST001] Test commit",
            "file_changes": [
                {
                    "path": "test.md",
                    "content": "test content",
                    "operation": "create",
                }
            ],
        }
        return service

    @pytest.fixture
    def mock_git_manager(self):
        """Create a mock git manager for apply operations."""
        mock = Mock()
        mock.write_file.return_value = None
        mock.commit_changes.return_value = "abc123"
        mock.log_event.return_value = None
        return mock

    @pytest.mark.asyncio
    async def test_apply_nonexistent_proposal_raises_error(self, mock_git_manager):
        """Test that applying nonexistent proposal raises ValueError."""
        service = CommandService()

        with pytest.raises(ValueError, match="Proposal nonexistent not found"):
            await service.apply_proposal("nonexistent", mock_git_manager)

    @pytest.mark.asyncio
    async def test_apply_proposal_success(self, command_service, mock_git_manager):
        """Test successfully applying a proposal."""
        result = await command_service.apply_proposal(
            "test-proposal-id", mock_git_manager, log_content=False
        )

        assert result["commit_hash"] == "abc123"
        assert result["changed_files"] == ["test.md"]
        assert "message" in result

        # Verify git operations were called
        mock_git_manager.write_file.assert_called_once_with(
            "TEST001", "test.md", "test content"
        )
        mock_git_manager.commit_changes.assert_called_once_with(
            "TEST001", "[TEST001] Test commit", ["test.md"]
        )
        mock_git_manager.log_event.assert_called_once()

        # Verify proposal was removed
        assert "test-proposal-id" not in command_service.proposals

    @pytest.mark.asyncio
    async def test_apply_proposal_with_content_logging(
        self, command_service, mock_git_manager
    ):
        """Test applying proposal with content logging enabled."""
        result = await command_service.apply_proposal(
            "test-proposal-id", mock_git_manager, log_content=True
        )

        assert result["commit_hash"] == "abc123"

        # Verify log_event was called with params and message (not hashes)
        log_call_args = mock_git_manager.log_event.call_args[0][1]
        assert "params" in log_call_args
        assert "message" in log_call_args
        assert "params_hash" not in log_call_args
        assert "message_hash" not in log_call_args

    @pytest.mark.asyncio
    async def test_apply_proposal_without_content_logging(
        self, command_service, mock_git_manager
    ):
        """Test applying proposal with content logging disabled (hashes only)."""
        result = await command_service.apply_proposal(
            "test-proposal-id", mock_git_manager, log_content=False
        )

        assert result["commit_hash"] == "abc123"

        # Verify log_event was called with hashes (not params/message)
        log_call_args = mock_git_manager.log_event.call_args[0][1]
        assert "params_hash" in log_call_args
        assert "message_hash" in log_call_args
        assert "params" not in log_call_args
        assert "message" not in log_call_args

    @pytest.mark.asyncio
    async def test_apply_proposal_multiple_files(self, mock_git_manager):
        """Test applying proposal with multiple file changes."""
        service = CommandService()
        service.proposals["multi-file"] = {
            "proposal_id": "multi-file",
            "project_key": "TEST001",
            "command": "test",
            "params": {},
            "assistant_message": "Test",
            "draft_commit_message": "[TEST001] Multi-file",
            "file_changes": [
                {"path": "file1.md", "content": "content1"},
                {"path": "file2.md", "content": "content2"},
                {"path": "file3.md", "content": "content3"},
            ],
        }

        result = await service.apply_proposal("multi-file", mock_git_manager)

        assert result["commit_hash"] == "abc123"
        assert len(result["changed_files"]) == 3
        assert result["changed_files"] == ["file1.md", "file2.md", "file3.md"]

        # Verify all files were written
        assert mock_git_manager.write_file.call_count == 3
