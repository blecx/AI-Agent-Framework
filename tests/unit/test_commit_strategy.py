"""Unit tests for agents.commit_strategy module."""

from pathlib import Path
from unittest.mock import MagicMock, patch, call

from agents.commit_strategy import (
    CommitStage,
    CommitMetrics,
    CommitStrategy,
    get_commit_strategy,
)


class TestCommitStage:
    """Tests for CommitStage dataclass."""

    def test_commit_stage_creation(self):
        """Test creating a CommitStage."""
        stage = CommitStage(
            name="tests",
            description="Add tests",
            file_patterns=["test_", "/tests/"],
            commit_message_prefix="test:",
        )
        assert stage.name == "tests"
        assert stage.description == "Add tests"
        assert len(stage.file_patterns) == 2
        assert stage.commit_message_prefix == "test:"
        assert stage.files == []

    def test_matches_file_positive(self):
        """Test file pattern matching returns True for matching files."""
        stage = CommitStage(
            name="tests",
            description="Tests",
            file_patterns=["test_", "/tests/"],
            commit_message_prefix="test:",
        )
        assert stage.matches_file("test_example.py") is True
        assert stage.matches_file("/tests/test_unit.py") is True

    def test_matches_file_negative(self):
        """Test file pattern matching returns False for non-matching files."""
        stage = CommitStage(
            name="tests",
            description="Tests",
            file_patterns=["test_", "/tests/"],
            commit_message_prefix="test:",
        )
        assert stage.matches_file("main.py") is False
        assert stage.matches_file("README.md") is False


class TestCommitMetrics:
    """Tests for CommitMetrics dataclass."""

    def test_commit_metrics_defaults(self):
        """Test CommitMetrics default values."""
        metrics = CommitMetrics()
        assert metrics.commits_per_pr == 0
        assert metrics.pr_review_time_minutes == 0.0
        assert metrics.stages_completed == 0
        assert metrics.total_files_staged == 0

    def test_commit_metrics_custom_values(self):
        """Test CommitMetrics with custom values."""
        metrics = CommitMetrics(
            commits_per_pr=3,
            pr_review_time_minutes=15.5,
            stages_completed=3,
            total_files_staged=10,
        )
        assert metrics.commits_per_pr == 3
        assert metrics.pr_review_time_minutes == 15.5
        assert metrics.stages_completed == 3
        assert metrics.total_files_staged == 10


class TestCommitStrategy:
    """Tests for CommitStrategy class."""

    def test_init_defaults(self):
        """Test CommitStrategy initialization with defaults."""
        strategy = CommitStrategy()
        assert strategy.working_directory == Path(".")
        assert isinstance(strategy.metrics, CommitMetrics)
        assert len(strategy.stages) == 4
        assert strategy.stages[0].name == "tests"
        assert strategy.stages[1].name == "implementation"
        assert strategy.stages[2].name == "documentation"
        assert strategy.stages[3].name == "refactoring"

    def test_init_custom_directory(self):
        """Test CommitStrategy with custom directory."""
        strategy = CommitStrategy(working_directory="/tmp/repo")
        assert strategy.working_directory == Path("/tmp/repo")

    @patch("subprocess.run")
    def test_get_changed_files_success(self, mock_run):
        """Test getting changed files successfully."""
        mock_run.return_value = MagicMock(
            stdout="file1.py\nfile2.py\ntest_file.py\n", returncode=0
        )

        strategy = CommitStrategy()
        files = strategy.get_changed_files()

        assert files == ["file1.py", "file2.py", "test_file.py"]
        mock_run.assert_called_once_with(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=str(Path(".")),
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_get_changed_files_empty(self, mock_run):
        """Test getting changed files when none exist."""
        mock_run.return_value = MagicMock(stdout="", returncode=0)

        strategy = CommitStrategy()
        files = strategy.get_changed_files()

        assert files == []

    @patch("subprocess.run")
    def test_get_staged_files_success(self, mock_run):
        """Test getting staged files successfully."""
        mock_run.return_value = MagicMock(
            stdout="staged1.py\nstaged2.py\n", returncode=0
        )

        strategy = CommitStrategy()
        files = strategy.get_staged_files()

        assert files == ["staged1.py", "staged2.py"]
        mock_run.assert_called_once_with(
            ["git", "diff", "--cached", "--name-only"],
            cwd=str(Path(".")),
            capture_output=True,
            text=True,
            check=True,
        )

    def test_classify_files_tests(self):
        """Test file classification for test files."""
        strategy = CommitStrategy()
        files = ["test_example.py", "tests/test_unit.py"]

        classified = strategy.classify_files(files)

        assert "test_example.py" in classified["tests"]
        assert "tests/test_unit.py" in classified["tests"]
        assert len(classified["tests"]) == 2

    def test_classify_files_documentation(self):
        """Test file classification for documentation files."""
        strategy = CommitStrategy()
        files = ["README.md", "docs/guide.md", "CHANGELOG.md"]

        classified = strategy.classify_files(files)

        assert "README.md" in classified["documentation"]
        assert "docs/guide.md" in classified["documentation"]
        assert "CHANGELOG.md" in classified["documentation"]
        assert len(classified["documentation"]) == 3

    def test_classify_files_implementation(self):
        """Test file classification for implementation files."""
        strategy = CommitStrategy()
        files = ["main.py", "service.py", "utils.py"]

        classified = strategy.classify_files(files)

        assert "main.py" in classified["implementation"]
        assert "service.py" in classified["implementation"]
        assert "utils.py" in classified["implementation"]
        assert len(classified["implementation"]) == 3

    def test_classify_files_mixed(self):
        """Test file classification with mixed file types."""
        strategy = CommitStrategy()
        files = [
            "test_main.py",
            "main.py",
            "README.md",
            "tests/test_service.py",
            "service.py",
            "docs/api.md",
        ]

        classified = strategy.classify_files(files)

        assert len(classified["tests"]) == 2
        assert len(classified["implementation"]) == 2
        assert len(classified["documentation"]) == 2

    @patch("subprocess.run")
    def test_create_stage_commit_dry_run(self, mock_run, capsys):
        """Test create_stage_commit in dry-run mode."""
        strategy = CommitStrategy()
        files = ["test_example.py", "test_unit.py"]

        result = strategy.create_stage_commit(
            stage_name="tests", files=files, message="Add tests", dry_run=True
        )

        assert result is True
        mock_run.assert_not_called()

        captured = capsys.readouterr()
        assert "[DRY RUN]" in captured.out
        assert "2 files" in captured.out
        assert "tests" in captured.out

    @patch("subprocess.run")
    def test_create_stage_commit_success(self, mock_run):
        """Test creating stage commit successfully."""
        mock_run.return_value = MagicMock(returncode=0)

        strategy = CommitStrategy()
        files = ["test_example.py"]

        result = strategy.create_stage_commit(
            stage_name="tests", files=files, message="Add tests", dry_run=False
        )

        assert result is True
        assert strategy.metrics.commits_per_pr == 1
        assert strategy.metrics.stages_completed == 1
        assert strategy.metrics.total_files_staged == 1

        # Verify git add and commit were called
        assert mock_run.call_count == 2
        add_call = call(
            ["git", "add", "test_example.py"], cwd=str(Path(".")), check=True
        )
        assert add_call in mock_run.call_args_list

    def test_create_stage_commit_no_files(self):
        """Test create_stage_commit with no files returns False."""
        strategy = CommitStrategy()

        result = strategy.create_stage_commit(
            stage_name="tests", files=[], message="Add tests", dry_run=False
        )

        assert result is False

    def test_create_stage_commit_invalid_stage(self):
        """Test create_stage_commit with invalid stage name raises error."""
        strategy = CommitStrategy()

        try:
            strategy.create_stage_commit(
                stage_name="invalid_stage",
                files=["file.py"],
                message="Test",
                dry_run=False,
            )
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unknown stage" in str(e)

    @patch("subprocess.run")
    def test_execute_strategy_no_files(self, mock_run):
        """Test execute_strategy with no changed files."""
        mock_run.return_value = MagicMock(stdout="", returncode=0)

        strategy = CommitStrategy()
        result = strategy.execute_strategy()

        assert result["success"] is False
        assert "No changed files" in result["message"]
        assert result["commits_created"] == 0

    @patch.object(CommitStrategy, "get_changed_files")
    @patch.object(CommitStrategy, "create_stage_commit")
    def test_execute_strategy_with_files(self, mock_create, mock_get):
        """Test execute_strategy with mixed file types."""
        mock_get.return_value = ["test_main.py", "main.py", "README.md"]
        mock_create.return_value = True

        strategy = CommitStrategy()
        result = strategy.execute_strategy(
            message_template="Implement feature", dry_run=False
        )

        assert result["success"] is True
        assert result["commits_created"] == 3
        assert len(result["stages_executed"]) == 3
        assert "tests" in result["stages_executed"]
        assert "implementation" in result["stages_executed"]
        assert "documentation" in result["stages_executed"]

    def test_get_metrics(self):
        """Test get_metrics returns correct dictionary."""
        strategy = CommitStrategy()
        strategy.metrics.commits_per_pr = 3
        strategy.metrics.pr_review_time_minutes = 15.0
        strategy.metrics.stages_completed = 3
        strategy.metrics.total_files_staged = 10

        metrics = strategy.get_metrics()

        assert metrics["commits_per_pr"] == 3
        assert metrics["pr_review_time_minutes"] == 15.0
        assert metrics["stages_completed"] == 3
        assert metrics["total_files_staged"] == 10


class TestGetCommitStrategy:
    """Tests for get_commit_strategy factory function."""

    def test_get_commit_strategy_defaults(self):
        """Test factory function with defaults."""
        strategy = get_commit_strategy()
        assert isinstance(strategy, CommitStrategy)
        assert strategy.working_directory == Path(".")

    def test_get_commit_strategy_custom_directory(self):
        """Test factory function with custom directory."""
        strategy = get_commit_strategy(working_directory="/tmp/repo")
        assert isinstance(strategy, CommitStrategy)
        assert strategy.working_directory == Path("/tmp/repo")
