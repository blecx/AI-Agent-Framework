"""
Unit tests for Git Manager Service.
"""
import pytest
import tempfile
import shutil
import json
from pathlib import Path
from apps.api.services.git_manager import GitManager


@pytest.fixture
def temp_git_dir():
    """Create a temporary directory for git operations."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def git_manager(temp_git_dir):
    """Create a GitManager instance with temporary directory."""
    manager = GitManager(temp_git_dir)
    manager.ensure_repository()
    return manager


class TestGitManagerInit:
    """Test GitManager initialization."""

    def test_init_creates_path_object(self, temp_git_dir):
        """Test that init creates a Path object for base_path."""
        manager = GitManager(temp_git_dir)
        assert isinstance(manager.base_path, Path)
        assert str(manager.base_path) == temp_git_dir

    def test_init_with_default_path(self):
        """Test initialization with default path."""
        manager = GitManager()
        assert manager.base_path == Path("/projectDocs")


class TestEnsureRepository:
    """Test repository initialization."""

    def test_ensure_repository_creates_directory(self, temp_git_dir):
        """Test that ensure_repository creates the base directory."""
        manager = GitManager(temp_git_dir)
        manager.ensure_repository()
        assert Path(temp_git_dir).exists()
        assert Path(temp_git_dir).is_dir()

    def test_ensure_repository_initializes_git(self, temp_git_dir):
        """Test that ensure_repository initializes a git repo."""
        manager = GitManager(temp_git_dir)
        manager.ensure_repository()
        git_dir = Path(temp_git_dir) / ".git"
        assert git_dir.exists()
        assert manager.repo is not None

    def test_ensure_repository_creates_initial_commit(self, temp_git_dir):
        """Test that ensure_repository creates an initial commit."""
        manager = GitManager(temp_git_dir)
        manager.ensure_repository()
        commits = list(manager.repo.iter_commits())
        assert len(commits) == 1
        assert commits[0].message == "Initial commit"

    def test_ensure_repository_idempotent(self, git_manager):
        """Test that calling ensure_repository multiple times is safe."""
        initial_commits = len(list(git_manager.repo.iter_commits()))
        git_manager.ensure_repository()
        final_commits = len(list(git_manager.repo.iter_commits()))
        assert initial_commits == final_commits


class TestProjectOperations:
    """Test project CRUD operations."""

    def test_create_project(self, git_manager):
        """Test creating a new project."""
        project_data = {"key": "TEST001", "name": "Test Project"}
        result = git_manager.create_project("TEST001", project_data)

        assert result["key"] == "TEST001"
        assert result["name"] == "Test Project"
        assert "created_at" in result
        assert "updated_at" in result

    def test_create_project_creates_directory(self, git_manager):
        """Test that create_project creates project directory."""
        git_manager.create_project("TEST001", {"key": "TEST001", "name": "Test"})
        project_dir = git_manager.base_path / "TEST001"
        assert project_dir.exists()
        assert project_dir.is_dir()

    def test_create_project_creates_json_file(self, git_manager):
        """Test that create_project creates project.json."""
        git_manager.create_project("TEST001", {"key": "TEST001", "name": "Test"})
        json_file = git_manager.base_path / "TEST001" / "project.json"
        assert json_file.exists()

        data = json.loads(json_file.read_text())
        assert data["key"] == "TEST001"
        assert data["name"] == "Test"

    def test_create_project_creates_commit(self, git_manager):
        """Test that create_project creates a git commit."""
        initial_commits = len(list(git_manager.repo.iter_commits()))
        git_manager.create_project("TEST001", {"key": "TEST001", "name": "Test"})
        final_commits = len(list(git_manager.repo.iter_commits()))
        assert final_commits == initial_commits + 1

    def test_read_project_json(self, git_manager):
        """Test reading project data."""
        project_data = {"key": "TEST001", "name": "Test Project"}
        git_manager.create_project("TEST001", project_data)

        result = git_manager.read_project_json("TEST001")
        assert result["key"] == "TEST001"
        assert result["name"] == "Test Project"

    def test_read_nonexistent_project_returns_none(self, git_manager):
        """Test reading nonexistent project returns None."""
        result = git_manager.read_project_json("NONEXISTENT")
        assert result is None


class TestFileOperations:
    """Test file read/write operations."""

    @pytest.fixture
    def test_project(self, git_manager):
        """Create a test project."""
        git_manager.create_project("TEST001", {"key": "TEST001", "name": "Test"})
        return "TEST001"

    def test_write_file(self, git_manager, test_project):
        """Test writing a file."""
        content = "# Test Content\n\nThis is a test file."
        git_manager.write_file(test_project, "test.md", content)

        file_path = git_manager.base_path / test_project / "test.md"
        assert file_path.exists()
        assert file_path.read_text() == content

    def test_write_file_creates_subdirectories(self, git_manager, test_project):
        """Test that write_file creates necessary subdirectories."""
        content = "Test content"
        git_manager.write_file(test_project, "sub/dir/test.md", content)

        file_path = git_manager.base_path / test_project / "sub" / "dir" / "test.md"
        assert file_path.exists()
        assert file_path.read_text() == content

    def test_read_file(self, git_manager, test_project):
        """Test reading a file."""
        content = "# Test Content\n\nThis is a test file."
        git_manager.write_file(test_project, "test.md", content)

        result = git_manager.read_file(test_project, "test.md")
        assert result == content

    def test_read_nonexistent_file_returns_none(self, git_manager, test_project):
        """Test reading nonexistent file returns None."""
        result = git_manager.read_file(test_project, "nonexistent.md")
        assert result is None


class TestArtifactOperations:
    """Test artifact listing and management."""

    @pytest.fixture
    def test_project(self, git_manager):
        """Create a test project with some artifacts."""
        git_manager.create_project("TEST001", {"key": "TEST001", "name": "Test"})
        git_manager.write_file("TEST001", "artifacts/charter.md", "Charter content")
        git_manager.write_file("TEST001", "artifacts/plan.md", "Plan content")
        git_manager.write_file("TEST001", "other.md", "Other content")
        return "TEST001"

    def test_list_artifacts(self, git_manager, test_project):
        """Test listing artifacts."""
        artifacts = git_manager.list_artifacts(test_project)

        # Should only list files in artifacts/ directory
        artifact_names = [a["name"] for a in artifacts]
        assert "charter.md" in artifact_names
        assert "plan.md" in artifact_names
        assert "other.md" not in artifact_names

    def test_list_artifacts_empty_project(self, git_manager):
        """Test listing artifacts for project with no artifacts."""
        git_manager.create_project("EMPTY", {"key": "EMPTY", "name": "Empty"})
        artifacts = git_manager.list_artifacts("EMPTY")
        assert artifacts == []


class TestCommitOperations:
    """Test git commit operations."""

    @pytest.fixture
    def test_project(self, git_manager):
        """Create a test project."""
        git_manager.create_project("TEST001", {"key": "TEST001", "name": "Test"})
        return "TEST001"

    def test_commit_changes(self, git_manager, test_project):
        """Test committing changes."""
        git_manager.write_file(test_project, "test.md", "Test content")

        initial_commits = len(list(git_manager.repo.iter_commits()))
        commit_hash = git_manager.commit_changes(
            test_project, "[TEST001] Add test file", ["test.md"]
        )

        final_commits = len(list(git_manager.repo.iter_commits()))
        assert final_commits == initial_commits + 1
        assert commit_hash is not None
        assert len(commit_hash) == 40  # SHA-1 hash length

    def test_get_last_commit(self, git_manager, test_project):
        """Test getting last commit info."""
        git_manager.write_file(test_project, "test.md", "Test")
        git_manager.commit_changes(test_project, "[TEST001] Test", ["test.md"])

        last_commit = git_manager.get_last_commit(test_project)
        assert last_commit is not None
        assert "hash" in last_commit
        assert "message" in last_commit
        assert "author" in last_commit
        assert "date" in last_commit


class TestDiffOperations:
    """Test diff generation."""

    @pytest.fixture
    def test_project(self, git_manager):
        """Create a test project."""
        git_manager.create_project("TEST001", {"key": "TEST001", "name": "Test"})
        return "TEST001"

    def test_get_diff_new_file(self, git_manager, test_project):
        """Test getting diff for a new file."""
        new_content = "# New File\n\nThis is new content."
        diff = git_manager.get_diff(test_project, "new.md", new_content)

        assert diff is not None
        assert "new.md" in diff or "New File" in diff

    def test_get_diff_existing_file(self, git_manager, test_project):
        """Test getting diff for existing file modification."""
        # Create initial file
        git_manager.write_file(test_project, "test.md", "Original content")
        git_manager.commit_changes(test_project, "[TEST001] Initial", ["test.md"])

        # Get diff for modified content
        new_content = "Modified content"
        diff = git_manager.get_diff(test_project, "test.md", new_content)

        assert diff is not None


class TestEventLogging:
    """Test event logging functionality."""

    @pytest.fixture
    def test_project(self, git_manager):
        """Create a test project."""
        git_manager.create_project("TEST001", {"key": "TEST001", "name": "Test"})
        return "TEST001"

    def test_log_event(self, git_manager, test_project):
        """Test logging an event."""
        event_data = {
            "event_type": "test_event",
            "description": "Test event description",
        }

        git_manager.log_event(test_project, event_data)

        # Verify event log file exists
        log_file = git_manager.base_path / test_project / "events" / "events.ndjson"
        assert log_file.exists()

        # Verify event was written
        lines = log_file.read_text().strip().split("\n")
        last_event = json.loads(lines[-1])
        assert last_event["event_type"] == "test_event"
        assert last_event["description"] == "Test event description"

    def test_log_multiple_events(self, git_manager, test_project):
        """Test logging multiple events."""
        for i in range(3):
            git_manager.log_event(test_project, {"event_type": f"event_{i}"})

        log_file = git_manager.base_path / test_project / "events" / "events.ndjson"
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 3

        # Verify events are in correct order
        for i, line in enumerate(lines):
            event = json.loads(line)
            assert event["event_type"] == f"event_{i}"
