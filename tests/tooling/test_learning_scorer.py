"""Unit tests for agents.learning_scorer module."""

from datetime import datetime, timedelta

from agents.learning_scorer import (
    Learning,
    ScoredLearning,
    ScoringMetrics,
    LearningScorer,
    get_learning_scorer,
)


class TestLearning:
    """Tests for Learning dataclass."""

    def test_learning_creation(self):
        """Test creating a Learning."""
        learning = Learning(
            content="Always use pytest for testing",
            timestamp=datetime(2026, 1, 1),
            domain="backend",
            repository="AI-Agent-Framework",
            success_rate=0.9,
            application_count=5,
            issue_number=123,
        )
        assert learning.content == "Always use pytest for testing"
        assert learning.domain == "backend"
        assert learning.repository == "AI-Agent-Framework"
        assert learning.success_rate == 0.9
        assert learning.application_count == 5
        assert learning.issue_number == 123

    def test_learning_defaults(self):
        """Test Learning default values."""
        learning = Learning(
            content="Test content",
            timestamp=datetime.now(),
            domain="backend",
            repository="test-repo",
        )
        assert learning.success_rate == 1.0
        assert learning.application_count == 0
        assert learning.issue_number is None


class TestScoredLearning:
    """Tests for ScoredLearning dataclass."""

    def test_scored_learning_creation(self):
        """Test creating a ScoredLearning."""
        learning = Learning(
            content="Test",
            timestamp=datetime.now(),
            domain="backend",
            repository="test-repo",
        )
        scored = ScoredLearning(
            learning=learning,
            score=0.85,
            score_breakdown={"recency": 0.9, "domain": 1.0},
        )
        assert scored.score == 0.85
        assert scored.learning == learning
        assert scored.score_breakdown["recency"] == 0.9


class TestScoringMetrics:
    """Tests for ScoringMetrics dataclass."""

    def test_metrics_defaults(self):
        """Test ScoringMetrics default values."""
        metrics = ScoringMetrics()
        assert metrics.learning_relevance_score_avg == 0.0
        assert metrics.irrelevant_learnings_filtered == 0
        assert metrics.total_learnings_scored == 0
        assert metrics.top_score == 0.0


class TestLearningScorer:
    """Tests for LearningScorer class."""

    def test_init_defaults(self):
        """Test LearningScorer initialization with defaults."""
        scorer = LearningScorer()
        assert scorer.recency_half_life_days == 90
        assert scorer.relevance_threshold == 0.3
        assert scorer.weights["recency"] == 0.3
        assert scorer.weights["domain"] == 0.25
        assert sum(scorer.weights.values()) == 1.0

    def test_init_custom_values(self):
        """Test LearningScorer with custom values."""
        weights = {
            "recency": 0.4,
            "domain": 0.3,
            "repository": 0.2,
            "success_rate": 0.05,
            "frequency": 0.05,
        }
        scorer = LearningScorer(
            recency_half_life_days=60, relevance_threshold=0.5, weights=weights
        )
        assert scorer.recency_half_life_days == 60
        assert scorer.relevance_threshold == 0.5
        assert scorer.weights["recency"] == 0.4

    def test_init_invalid_weights(self):
        """Test LearningScorer raises error for invalid weights."""
        weights = {"recency": 0.5, "domain": 0.3}  # Sum = 0.8, not 1.0
        try:
            LearningScorer(weights=weights)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Weights must sum to 1.0" in str(e)

    def test_compute_recency_score_fresh(self):
        """Test recency score for fresh learning (today)."""
        scorer = LearningScorer(recency_half_life_days=90)
        learning = Learning(
            content="Test",
            timestamp=datetime.now(),
            domain="backend",
            repository="test-repo",
        )
        score = scorer.compute_recency_score(learning, datetime.now())
        assert score >= 0.99  # Very fresh

    def test_compute_recency_score_half_life(self):
        """Test recency score at exactly half-life."""
        scorer = LearningScorer(recency_half_life_days=90)
        now = datetime(2026, 2, 6)
        past = now - timedelta(days=90)
        learning = Learning(
            content="Test", timestamp=past, domain="backend", repository="test-repo"
        )
        score = scorer.compute_recency_score(learning, now)
        assert abs(score - 0.5) < 0.01  # Should be ~0.5

    def test_compute_recency_score_old(self):
        """Test recency score for old learning (180 days)."""
        scorer = LearningScorer(recency_half_life_days=90)
        now = datetime(2026, 2, 6)
        past = now - timedelta(days=180)
        learning = Learning(
            content="Test", timestamp=past, domain="backend", repository="test-repo"
        )
        score = scorer.compute_recency_score(learning, now)
        assert abs(score - 0.25) < 0.01  # Two half-lives = 0.5^2 = 0.25

    def test_compute_domain_score_match(self):
        """Test domain score for exact match."""
        scorer = LearningScorer()
        learning = Learning(
            content="Test",
            timestamp=datetime.now(),
            domain="backend",
            repository="test-repo",
        )
        score = scorer.compute_domain_score(learning, "backend")
        assert score == 1.0

    def test_compute_domain_score_mismatch(self):
        """Test domain score for mismatch."""
        scorer = LearningScorer()
        learning = Learning(
            content="Test",
            timestamp=datetime.now(),
            domain="frontend",
            repository="test-repo",
        )
        score = scorer.compute_domain_score(learning, "backend")
        assert score == 0.3

    def test_compute_repository_score_match(self):
        """Test repository score for exact match."""
        scorer = LearningScorer()
        learning = Learning(
            content="Test",
            timestamp=datetime.now(),
            domain="backend",
            repository="AI-Agent-Framework",
        )
        score = scorer.compute_repository_score(learning, "AI-Agent-Framework")
        assert score == 1.0

    def test_compute_repository_score_mismatch(self):
        """Test repository score for mismatch."""
        scorer = LearningScorer()
        learning = Learning(
            content="Test",
            timestamp=datetime.now(),
            domain="backend",
            repository="AI-Agent-Framework-Client",
        )
        score = scorer.compute_repository_score(learning, "AI-Agent-Framework")
        assert score == 0.5

    def test_compute_success_score_high(self):
        """Test success score for high success rate."""
        scorer = LearningScorer()
        learning = Learning(
            content="Test",
            timestamp=datetime.now(),
            domain="backend",
            repository="test-repo",
            success_rate=0.95,
        )
        score = scorer.compute_success_score(learning)
        assert score == 0.95

    def test_compute_success_score_low(self):
        """Test success score for low success rate."""
        scorer = LearningScorer()
        learning = Learning(
            content="Test",
            timestamp=datetime.now(),
            domain="backend",
            repository="test-repo",
            success_rate=0.3,
        )
        score = scorer.compute_success_score(learning)
        assert score == 0.3

    def test_compute_frequency_score_zero(self):
        """Test frequency score for never applied."""
        scorer = LearningScorer()
        learning = Learning(
            content="Test",
            timestamp=datetime.now(),
            domain="backend",
            repository="test-repo",
            application_count=0,
        )
        score = scorer.compute_frequency_score(learning)
        assert score == 0.0

    def test_compute_frequency_score_high(self):
        """Test frequency score for frequently applied."""
        scorer = LearningScorer()
        learning = Learning(
            content="Test",
            timestamp=datetime.now(),
            domain="backend",
            repository="test-repo",
            application_count=10,
        )
        score = scorer.compute_frequency_score(learning)
        assert score > 0.5  # Should be significant

    def test_score_learning_comprehensive(self):
        """Test scoring a learning with all factors."""
        scorer = LearningScorer()
        now = datetime(2026, 2, 6)
        learning = Learning(
            content="Use pytest",
            timestamp=now - timedelta(days=30),  # Recent
            domain="backend",
            repository="AI-Agent-Framework",
            success_rate=0.9,
            application_count=5,
        )
        scored = scorer.score_learning(learning, "backend", "AI-Agent-Framework", now)

        assert scored.score > 0.7  # Should be high score
        assert "recency" in scored.score_breakdown
        assert "domain" in scored.score_breakdown
        assert "repository" in scored.score_breakdown
        assert scored.score_breakdown["domain"] == 1.0  # Exact match
        assert scored.score_breakdown["repository"] == 1.0  # Exact match

    def test_score_learning_low_relevance(self):
        """Test scoring a low-relevance learning."""
        scorer = LearningScorer()
        now = datetime(2026, 2, 6)
        learning = Learning(
            content="Old learning",
            timestamp=now - timedelta(days=365),  # Very old
            domain="frontend",
            repository="other-repo",
            success_rate=0.4,
            application_count=1,
        )
        scored = scorer.score_learning(learning, "backend", "AI-Agent-Framework", now)

        assert scored.score < 0.4  # Should be low score
        assert scored.score_breakdown["domain"] == 0.3  # Mismatch
        assert scored.score_breakdown["repository"] == 0.5  # Mismatch

    def test_get_relevant_learnings_filters_threshold(self):
        """Test get_relevant_learnings filters by threshold."""
        scorer = LearningScorer(relevance_threshold=0.5)
        now = datetime(2026, 2, 6)

        learnings = [
            Learning(
                content="High relevance",
                timestamp=now,
                domain="backend",
                repository="AI-Agent-Framework",
                success_rate=1.0,
                application_count=10,
            ),
            Learning(
                content="Low relevance",
                timestamp=now - timedelta(days=365),
                domain="frontend",
                repository="other-repo",
                success_rate=0.2,
                application_count=0,
            ),
        ]

        relevant = scorer.get_relevant_learnings(
            learnings, "backend", "AI-Agent-Framework", now
        )

        assert len(relevant) == 1
        assert relevant[0].learning.content == "High relevance"
        assert scorer.metrics.irrelevant_learnings_filtered == 1

    def test_get_relevant_learnings_sorts_by_score(self):
        """Test get_relevant_learnings sorts by score descending."""
        scorer = LearningScorer()
        now = datetime(2026, 2, 6)

        learnings = [
            Learning(
                content="Medium",
                timestamp=now - timedelta(days=60),
                domain="backend",
                repository="AI-Agent-Framework",
            ),
            Learning(
                content="High",
                timestamp=now,
                domain="backend",
                repository="AI-Agent-Framework",
                application_count=10,
            ),
            Learning(
                content="Low",
                timestamp=now - timedelta(days=120),
                domain="frontend",
                repository="other-repo",
            ),
        ]

        relevant = scorer.get_relevant_learnings(
            learnings, "backend", "AI-Agent-Framework", now
        )

        assert len(relevant) >= 2
        assert relevant[0].learning.content == "High"
        assert relevant[0].score > relevant[1].score

    def test_get_relevant_learnings_updates_metrics(self):
        """Test get_relevant_learnings updates metrics correctly."""
        scorer = LearningScorer(relevance_threshold=0.5)
        now = datetime(2026, 2, 6)

        learnings = [
            Learning(
                content="Relevant 1",
                timestamp=now,
                domain="backend",
                repository="AI-Agent-Framework",
            ),
            Learning(
                content="Relevant 2",
                timestamp=now - timedelta(days=30),
                domain="backend",
                repository="AI-Agent-Framework",
            ),
            Learning(
                content="Irrelevant",
                timestamp=now - timedelta(days=365),
                domain="other",
                repository="other-repo",
            ),
        ]

        relevant = scorer.get_relevant_learnings(
            learnings, "backend", "AI-Agent-Framework", now
        )

        assert scorer.metrics.total_learnings_scored == 3
        assert scorer.metrics.irrelevant_learnings_filtered >= 1
        assert scorer.metrics.learning_relevance_score_avg > 0.5
        assert scorer.metrics.top_score == relevant[0].score

    def test_get_metrics(self):
        """Test get_metrics returns correct dictionary."""
        scorer = LearningScorer()
        scorer.metrics.learning_relevance_score_avg = 0.75
        scorer.metrics.irrelevant_learnings_filtered = 5
        scorer.metrics.total_learnings_scored = 10
        scorer.metrics.top_score = 0.95

        metrics = scorer.get_metrics()

        assert metrics["learning_relevance_score_avg"] == 0.75
        assert metrics["irrelevant_learnings_filtered"] == 5
        assert metrics["total_learnings_scored"] == 10
        assert metrics["top_score"] == 0.95


class TestGetLearningScorer:
    """Tests for get_learning_scorer factory function."""

    def test_get_learning_scorer_defaults(self):
        """Test factory function with defaults."""
        scorer = get_learning_scorer()
        assert isinstance(scorer, LearningScorer)
        assert scorer.recency_half_life_days == 90
        assert scorer.relevance_threshold == 0.3

    def test_get_learning_scorer_custom(self):
        """Test factory function with custom values."""
        weights = {
            "recency": 0.5,
            "domain": 0.2,
            "repository": 0.15,
            "success_rate": 0.1,
            "frequency": 0.05,
        }
        scorer = get_learning_scorer(
            recency_half_life_days=60, relevance_threshold=0.4, weights=weights
        )
        assert scorer.recency_half_life_days == 60
        assert scorer.relevance_threshold == 0.4
        assert scorer.weights["recency"] == 0.5
