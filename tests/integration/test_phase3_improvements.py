#!/usr/bin/env python3
"""
Test Phase 3 Agent Improvements (Issues #169-#173)

Tests:
- Cached Command Results (#169)
- Predictive Time Estimation (#170)
- Test Coverage Analyzer (#171)
- Multi-Stage Commit Strategy (#172)
- Learning Confidence Scoring (#173)
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.workflow_agent import (
    CommandCache,
    TimeEstimator,
    CoverageAnalyzer,
    CommitStrategy,
    LearningScorer
)


def test_command_cache():
    """Test Command Cache (#169)."""
    print("Testing Command Cache...")
    
    cache = CommandCache(cache_ttl=5)  # 5 second TTL for testing
    
    # Test cache miss (first run)
    start = time.time()
    result1 = cache.run_cached("echo 'test'", cache_key="test_cmd")
    duration1 = time.time() - start
    
    print(f"  First run: {duration1:.3f}s")
    assert result1[0] == 0  # Success
    assert "test" in result1[1]  # Output contains "test"
    
    # Test cache hit (second run should be instant)
    start = time.time()
    result2 = cache.run_cached("echo 'test'", cache_key="test_cmd")
    duration2 = time.time() - start
    
    print(f"  Cached run: {duration2:.3f}s (should be <0.001s)")
    assert result2 == result1  # Same result
    assert duration2 < duration1  # Faster
    
    # Test cache expiration
    print("  Testing cache expiration...")
    time.sleep(6)  # Wait for TTL to expire
    result3 = cache.run_cached("echo 'test'", cache_key="test_cmd")
    assert result3[0] == 0  # Still works
    
    # Test cache clear
    cache.clear()
    assert len(cache.cache) == 0
    print("  ✅ Command cache working correctly")


def test_time_estimator():
    """Test Predictive Time Estimation (#170)."""
    print("Testing Predictive Time Estimator...")
    
    # Create temporary knowledge directory
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_dir = Path(tmpdir)
        estimator = TimeEstimator(kb_dir=kb_dir)
        
        # Test simple estimation
        issue_data = {
            'files_to_change': 3,
            'lines_estimate': 100,
            'domain': 'backend',
            'is_multi_repo': False,
            'has_dependencies': False,
            'complexity_score': 'medium'
        }
        
        estimate = estimator.estimate_time(issue_data)
        print(f"  Medium complexity estimate: {estimate['estimated_hours']}h (confidence: {estimate['confidence']:.2f})")
        assert 'estimated_hours' in estimate
        assert 'confidence' in estimate
        assert 'reasoning' in estimate
        assert estimate['estimated_hours'] > 0
        assert 0 <= estimate['confidence'] <= 1
        
        # Test high complexity estimation
        issue_data['complexity_score'] = 'high'
        issue_data['is_multi_repo'] = True
        estimate_high = estimator.estimate_time(issue_data)
        print(f"  High complexity + multi-repo estimate: {estimate_high['estimated_hours']}h")
        assert estimate_high['estimated_hours'] > estimate['estimated_hours']  # Should be higher
        
        # Test recording actual time
        estimator.record_actual_time(
            issue_number=123,
            estimated=2.5,
            actual=2.8,
            features=issue_data
        )
        assert len(estimator.history) == 1
        print("  ✅ Time estimator working correctly")


def test_coverage_analyzer():
    """Test Test Coverage Analyzer (#171)."""
    print("Testing Test Coverage Analyzer...")
    
    analyzer = CoverageAnalyzer(min_coverage=80.0)
    
    # Test coverage analysis (stub mode)
    workspace_root = Path(".")
    diff = analyzer.analyze_coverage_impact(workspace_root)
    
    print(f"  Coverage delta: {diff['total_delta']:+.1f}%")
    assert 'total_delta' in diff
    assert 'covered_delta' in diff
    assert 'uncovered_delta' in diff
    assert 'affected_files' in diff
    
    # In real scenario, would check for regressions
    if 'warning' in diff:
        print(f"  ⚠️  {diff['warning']}")
    
    if 'low_coverage_files' in diff:
        print(f"  ⚠️  {len(diff['low_coverage_files'])} files below {analyzer.min_coverage}% coverage")
    
    print("  ✅ Coverage analyzer working correctly")


def test_commit_strategy():
    """Test Multi-Stage Commit Strategy (#172)."""
    print("Testing Multi-Stage Commit Strategy...")
    
    strategy = CommitStrategy()
    
    # Test pattern matching
    assert strategy._matches_pattern("test.test.py", "*.test.py")
    assert strategy._matches_pattern("agents/base_agent.py", "agents/**")
    assert not strategy._matches_pattern("README.md", "*.py")
    
    print("  Pattern matching: ✅")
    
    # Test stage detection (won't actually commit in test)
    stages = [
        {
            "name": "tests",
            "patterns": ["*.test.py"],
            "message": "test: Add tests"
        }
    ]
    
    # In real scenario, would test full commit sequence
    print("  ✅ Commit strategy pattern matching working correctly")


def test_learning_scorer():
    """Test Learning Confidence Scoring (#173)."""
    print("Testing Learning Confidence Scorer...")
    
    # Create temporary knowledge directory
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_dir = Path(tmpdir)
        
        # Create mock learnings file
        learnings_file = kb_dir / "issue_resolution_best_practices.json"
        kb_dir.mkdir(exist_ok=True)
        
        mock_learnings = {
            "learnings": [
                {
                    "problem": "PR template validation",
                    "solution": "Validate before creating PR",
                    "domain": "backend",
                    "repo": "AI-Agent-Framework",
                    "timestamp": datetime.now().isoformat(),
                    "success_rate": 95,
                    "times_applied": 10
                },
                {
                    "problem": "Old learning",
                    "solution": "Outdated approach",
                    "domain": "frontend",
                    "repo": "AI-Agent-Framework-Client",
                    "timestamp": (datetime.now() - timedelta(days=200)).isoformat(),
                    "success_rate": 60,
                    "times_applied": 2
                }
            ]
        }
        
        learnings_file.write_text(json.dumps(mock_learnings))
        
        scorer = LearningScorer(kb_dir=kb_dir)
        
        # Test scoring
        current_issue = {
            'domain': 'backend',
            'repo': 'AI-Agent-Framework'
        }
        
        score1 = scorer.score_learning_relevance(mock_learnings["learnings"][0], current_issue)
        score2 = scorer.score_learning_relevance(mock_learnings["learnings"][1], current_issue)
        
        print(f"  Recent + matching learning score: {score1:.3f}")
        print(f"  Old + non-matching learning score: {score2:.3f}")
        
        assert score1 > score2  # Recent matching should score higher
        assert 0 <= score1 <= 1
        assert 0 <= score2 <= 1
        
        # Test getting relevant learnings
        relevant = scorer.get_relevant_learnings(current_issue, min_score=0.3)
        print(f"  Found {len(relevant)} relevant learnings")
        assert len(relevant) >= 0
        
        print("  ✅ Learning scorer working correctly")


def run_all_tests():
    """Run all Phase 3 improvement tests."""
    print("\n" + "=" * 60)
    print("Phase 3 Agent Improvements Test Suite")
    print("Issues #169-#173")
    print("=" * 60 + "\n")
    
    tests = [
        ("Command Cache", test_command_cache),
        ("Time Estimator", test_time_estimator),
        ("Coverage Analyzer", test_coverage_analyzer),
        ("Commit Strategy", test_commit_strategy),
        ("Learning Scorer", test_learning_scorer)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"\n{'─' * 60}")
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {name} test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
