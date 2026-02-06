"""
Unit tests for agents.coverage_analyzer

Tests the CoverageAnalyzer class that enforces coverage quality gates.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from agents.coverage_analyzer import (
    CoverageAnalyzer,
    CoverageDiff,
    CoverageFile,
    CoverageReport,
    get_coverage_analyzer,
)


class TestCoverageFile:
    """Test CoverageFile dataclass."""

    def test_coverage_file_creation(self):
        """Test creating a CoverageFile."""
        cov_file = CoverageFile(
            path="apps/api/main.py",
            percent_covered=85.5,
            covered_lines=100,
            missing_lines=17,
            total_lines=117,
        )

        assert cov_file.path == "apps/api/main.py"
        assert cov_file.percent_covered == 85.5
        assert cov_file.covered_lines == 100
        assert cov_file.missing_lines == 17
        assert cov_file.total_lines == 117


class TestCoverageReport:
    """Test CoverageReport dataclass."""

    def test_coverage_report_creation(self):
        """Test creating a CoverageReport."""
        files = {
            "file1.py": CoverageFile("file1.py", 90.0, 90, 10, 100),
            "file2.py": CoverageFile("file2.py", 80.0, 80, 20, 100),
        }

        report = CoverageReport(total_percent=85.0, files=files)

        assert report.total_percent == 85.0
        assert len(report.files) == 2

    def test_total_covered_calculation(self):
        """Test total_covered property sums covered lines."""
        files = {
            "file1.py": CoverageFile("file1.py", 90.0, 90, 10, 100),
            "file2.py": CoverageFile("file2.py", 80.0, 80, 20, 100),
        }

        report = CoverageReport(total_percent=85.0, files=files)

        assert report.total_covered == 170  # 90 + 80

    def test_total_uncovered_calculation(self):
        """Test total_uncovered property sums missing lines."""
        files = {
            "file1.py": CoverageFile("file1.py", 90.0, 90, 10, 100),
            "file2.py": CoverageFile("file2.py", 80.0, 80, 20, 100),
        }

        report = CoverageReport(total_percent=85.0, files=files)

        assert report.total_uncovered == 30  # 10 + 20


class TestCoverageDiff:
    """Test CoverageDiff dataclass."""

    def test_coverage_diff_creation(self):
        """Test creating a CoverageDiff."""
        diff = CoverageDiff(
            total_delta=2.5,
            new_lines_covered=50,
            new_lines_uncovered=25,
            affected_files=["file1.py", "file2.py"],
            low_coverage_files=[],
            regressions=[],
        )

        assert diff.total_delta == 2.5
        assert diff.new_lines_covered == 50
        assert diff.new_lines_uncovered == 25
        assert len(diff.affected_files) == 2


class TestCoverageAnalyzer:
    """Test CoverageAnalyzer class."""

    def test_initialization_with_defaults(self):
        """Test analyzer initializes with default values."""
        analyzer = CoverageAnalyzer()

        assert analyzer.coverage_threshold == 80.0
        assert analyzer.working_directory == Path(".")
        assert analyzer.metrics["coverage_regressions_prevented"] == 0
        assert analyzer.metrics["average_coverage_delta"] == 0.0

    def test_initialization_with_custom_values(self):
        """Test analyzer initializes with custom values."""
        analyzer = CoverageAnalyzer(coverage_threshold=85.0, working_directory="/tmp")

        assert analyzer.coverage_threshold == 85.0
        assert analyzer.working_directory == Path("/tmp")

    @patch("subprocess.run")
    def test_run_coverage_success(self, mock_run):
        """Test running coverage successfully."""
        mock_run.return_value = Mock(returncode=0)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            coverage_file = tmpdir_path / "coverage.json"
            coverage_file.write_text('{"totals": {"percent_covered": 90.0}}')

            analyzer = CoverageAnalyzer(working_directory=tmpdir)
            result = analyzer._run_coverage()

            assert result == coverage_file
            assert result.exists()

    @patch("subprocess.run")
    def test_run_coverage_failure(self, mock_run):
        """Test handling coverage run failure."""
        mock_run.side_effect = Exception("Command failed")

        analyzer = CoverageAnalyzer()
        result = analyzer._run_coverage()

        assert result is None

    def test_parse_coverage_file_success(self):
        """Test parsing valid coverage.json."""
        coverage_data = {
            "totals": {"percent_covered": 85.5},
            "files": {
                "apps/api/main.py": {
                    "summary": {
                        "percent_covered": 90.0,
                        "covered_lines": 90,
                        "missing_lines": 10,
                        "num_statements": 100,
                    }
                },
                "apps/api/models.py": {
                    "summary": {
                        "percent_covered": 80.0,
                        "covered_lines": 80,
                        "missing_lines": 20,
                        "num_statements": 100,
                    }
                },
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            coverage_file = Path(tmpdir) / "coverage.json"
            coverage_file.write_text(json.dumps(coverage_data))

            analyzer = CoverageAnalyzer()
            report = analyzer._parse_coverage_file(coverage_file)

            assert report is not None
            assert report.total_percent == 85.5
            assert len(report.files) == 2
            assert "apps/api/main.py" in report.files
            assert report.files["apps/api/main.py"].percent_covered == 90.0

    def test_parse_coverage_file_invalid(self):
        """Test handling invalid coverage.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            coverage_file = Path(tmpdir) / "coverage.json"
            coverage_file.write_text("invalid json")

            analyzer = CoverageAnalyzer()
            report = analyzer._parse_coverage_file(coverage_file)

            assert report is None

    def test_analyze_coverage_impact_improvement(self):
        """Test analyzing coverage when it improves."""
        before = CoverageReport(
            total_percent=80.0,
            files={
                "file1.py": CoverageFile("file1.py", 80.0, 80, 20, 100),
            },
        )

        after = CoverageReport(
            total_percent=85.0,
            files={
                "file1.py": CoverageFile("file1.py", 90.0, 90, 10, 100),
            },
        )

        analyzer = CoverageAnalyzer()
        diff = analyzer.analyze_coverage_impact(before, after, ["file1.py"])

        assert diff.total_delta == 5.0  # 85.0 - 80.0
        assert diff.new_lines_covered == 10  # 90 - 80
        assert diff.new_lines_uncovered == -10  # 10 - 20
        assert len(diff.affected_files) == 1
        assert len(diff.low_coverage_files) == 0
        assert len(diff.regressions) == 0

    def test_analyze_coverage_impact_regression(self):
        """Test analyzing coverage when it decreases."""
        before = CoverageReport(
            total_percent=85.0,
            files={
                "file1.py": CoverageFile("file1.py", 90.0, 90, 10, 100),
            },
        )

        after = CoverageReport(
            total_percent=80.0,
            files={
                "file1.py": CoverageFile("file1.py", 80.0, 80, 20, 100),
            },
        )

        analyzer = CoverageAnalyzer()
        diff = analyzer.analyze_coverage_impact(before, after, ["file1.py"])

        assert diff.total_delta == -5.0
        assert len(diff.regressions) == 1
        assert "file1.py" in diff.regressions

    def test_analyze_coverage_impact_low_coverage(self):
        """Test detecting files below coverage threshold."""
        before = CoverageReport(total_percent=80.0, files={})

        after = CoverageReport(
            total_percent=75.0,
            files={
                "file1.py": CoverageFile("file1.py", 70.0, 70, 30, 100),
                "file2.py": CoverageFile("file2.py", 85.0, 85, 15, 100),
            },
        )

        analyzer = CoverageAnalyzer(coverage_threshold=80.0)
        diff = analyzer.analyze_coverage_impact(before, after, ["file1.py", "file2.py"])

        assert len(diff.low_coverage_files) == 1
        assert diff.low_coverage_files[0].path == "file1.py"

    def test_analyze_coverage_impact_updates_metrics(self):
        """Test that analysis updates metrics."""
        before = CoverageReport(
            total_percent=80.0,
            files={"file1.py": CoverageFile("file1.py", 80.0, 80, 20, 100)},
        )

        after = CoverageReport(
            total_percent=85.0,
            files={"file1.py": CoverageFile("file1.py", 90.0, 90, 10, 100)},
        )

        analyzer = CoverageAnalyzer()
        analyzer.analyze_coverage_impact(before, after, ["file1.py"])

        metrics = analyzer.get_metrics()
        assert metrics["files_analyzed"] == 1
        assert metrics["average_coverage_delta"] == 5.0
        assert metrics["coverage_regressions_prevented"] == 0
        assert metrics["warnings_issued"] == 0

    def test_enforce_coverage_rules_pass(self):
        """Test coverage rules pass with no violations."""
        diff = CoverageDiff(
            total_delta=5.0,
            new_lines_covered=10,
            new_lines_uncovered=0,
            affected_files=["file1.py"],
            low_coverage_files=[],
            regressions=[],
        )

        analyzer = CoverageAnalyzer()
        result = analyzer.enforce_coverage_rules(diff)

        assert result is True

    def test_enforce_coverage_rules_fail_regression(self):
        """Test coverage rules fail with regression."""
        diff = CoverageDiff(
            total_delta=-5.0,
            new_lines_covered=0,
            new_lines_uncovered=10,
            affected_files=["file1.py"],
            low_coverage_files=[],
            regressions=["file1.py"],
        )

        analyzer = CoverageAnalyzer()
        result = analyzer.enforce_coverage_rules(diff)

        assert result is False

    def test_enforce_coverage_rules_fail_low_coverage(self):
        """Test coverage rules fail with low coverage files."""
        low_cov_file = CoverageFile("file1.py", 70.0, 70, 30, 100)

        diff = CoverageDiff(
            total_delta=0.0,
            new_lines_covered=0,
            new_lines_uncovered=0,
            affected_files=["file1.py"],
            low_coverage_files=[low_cov_file],
            regressions=[],
        )

        analyzer = CoverageAnalyzer(coverage_threshold=80.0)
        result = analyzer.enforce_coverage_rules(diff)

        assert result is False

    def test_get_metrics(self):
        """Test getting coverage metrics."""
        analyzer = CoverageAnalyzer()
        metrics = analyzer.get_metrics()

        assert "coverage_regressions_prevented" in metrics
        assert "average_coverage_delta" in metrics
        assert "files_analyzed" in metrics
        assert "warnings_issued" in metrics
        assert isinstance(metrics, dict)

    def test_get_metrics_returns_copy(self):
        """Test that get_metrics returns a copy, not reference."""
        analyzer = CoverageAnalyzer()
        metrics1 = analyzer.get_metrics()
        metrics2 = analyzer.get_metrics()

        metrics1["coverage_regressions_prevented"] = 999

        assert metrics2["coverage_regressions_prevented"] == 0


class TestGetCoverageAnalyzer:
    """Test get_coverage_analyzer factory function."""

    def test_get_coverage_analyzer_defaults(self):
        """Test factory creates analyzer with defaults."""
        analyzer = get_coverage_analyzer()

        assert isinstance(analyzer, CoverageAnalyzer)
        assert analyzer.coverage_threshold == 80.0
        assert analyzer.working_directory == Path(".")

    def test_get_coverage_analyzer_custom_values(self):
        """Test factory creates analyzer with custom values."""
        analyzer = get_coverage_analyzer(
            coverage_threshold=85.0, working_directory="/tmp"
        )

        assert analyzer.coverage_threshold == 85.0
        assert analyzer.working_directory == Path("/tmp")
