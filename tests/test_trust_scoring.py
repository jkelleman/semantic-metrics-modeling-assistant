"""Tests for trust scoring algorithm."""
import pytest
from datetime import datetime, timedelta
from semantic_metrics.trust_scoring import (
    calculate_trust_score_enhanced,
    check_freshness,
    check_test_coverage,
    check_usage,
    check_documentation,
    check_ownership,
    calculate_trend,
    generate_sparkline
)


class TestTrustScoreComponents:
    """Test individual scoring components."""
    
    def test_freshness_recent(self):
        """Test freshness score for recently updated metric."""
        metric = {"updated_at": datetime.now().isoformat()}
        score = check_freshness(metric)
        assert score == 20  # Max score for today
    
    def test_freshness_old(self):
        """Test freshness score for old metric."""
        old_date = (datetime.now() - timedelta(days=200)).isoformat()
        metric = {"updated_at": old_date}
        score = check_freshness(metric)
        assert score == 0  # Min score for very old
    
    def test_test_coverage_excellent(self):
        """Test score for good test coverage."""
        metric = {"test_count": 5}
        score = check_test_coverage(metric)
        assert score == 25  # Max score for 5+ tests
    
    def test_test_coverage_none(self):
        """Test score for no tests."""
        metric = {"test_count": 0}
        score = check_test_coverage(metric)
        assert score == 0
    
    def test_usage_high(self):
        """Test score for high usage."""
        metric = {"usage_count": 100}
        score = check_usage(metric)
        assert score == 20  # Max score
    
    def test_usage_none(self):
        """Test score for no usage."""
        metric = {"usage_count": 0}
        score = check_usage(metric)
        assert score == 0
    
    def test_documentation_complete(self):
        """Test score for complete documentation."""
        metric = {
            "description": "A very detailed description",
            "data_source": "transactions",
            "tags": ["tag1", "tag2"],
            "dependencies": ["dep1"]
        }
        score = check_documentation(metric)
        assert score == 20  # Max score
    
    def test_ownership_assigned(self):
        """Test score for assigned owner."""
        metric = {"owner": "@data-team"}
        score = check_ownership(metric)
        assert score == 15  # Max score


class TestEnhancedScoring:
    """Test the enhanced scoring algorithm."""
    
    def test_perfect_score(self):
        """Test metric with perfect scores in all areas."""
        metric = {
            "id": "perfect",
            "name": "Perfect Metric",
            "description": "A perfect metric with all qualities",
            "calculation": "SUM(amount) FROM transactions",
            "owner": "@team",
            "tags": ["revenue"],
            "data_source": "transactions",
            "dependencies": ["transactions.amount"],
            "test_count": 5,
            "usage_count": 100,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = calculate_trust_score_enhanced(metric)
        assert result["score"] >= 90  # Should be very high
        assert "breakdown" in result
        assert "trend" in result
    
    def test_poor_score(self):
        """Test metric with poor scores."""
        metric = {
            "id": "poor",
            "name": "Poor Metric",
            "description": "",
            "calculation": "SELECT *",
            "owner": "Unassigned",
            "tags": [],
            "data_source": "",
            "dependencies": [],
            "test_count": 0,
            "usage_count": 0,
            "created_at": (datetime.now() - timedelta(days=200)).isoformat(),
            "updated_at": (datetime.now() - timedelta(days=100)).isoformat()
        }
        
        result = calculate_trust_score_enhanced(metric)
        assert result["score"] < 30  # Should be low
        assert len(result["recommendations"]) > 0
    
    def test_time_decay(self):
        """Test that old metrics without updates lose trust."""
        metric = {
            "id": "stale",
            "name": "Stale Metric",
            "description": "Old metric",
            "calculation": "COUNT(*)",
            "owner": "@team",
            "tags": [],
            "data_source": "table",
            "dependencies": [],
            "test_count": 2,
            "usage_count": 10,
            "created_at": (datetime.now() - timedelta(days=200)).isoformat(),
            "updated_at": (datetime.now() - timedelta(days=90)).isoformat()
        }
        
        result = calculate_trust_score_enhanced(metric)
        assert result["multipliers"]["time_decay"] < 0  # Should have negative decay


class TestTrendCalculation:
    """Test trend analysis."""
    
    def test_improving_trend(self):
        """Test detection of improving metric."""
        history = [
            {"changed_at": (datetime.now() - timedelta(days=i)).isoformat()}
            for i in range(10)  # Many recent changes
        ]
        trend = calculate_trend(history)
        assert trend in ["↗️", "→"]  # Improving or stable
    
    def test_stable_trend(self):
        """Test detection of stable metric."""
        history = [
            {"changed_at": (datetime.now() - timedelta(days=i*10)).isoformat()}
            for i in range(5)  # Evenly spaced changes
        ]
        trend = calculate_trend(history)
        assert trend == "→"
    
    def test_no_history(self):
        """Test trend with no history."""
        trend = calculate_trend([])
        assert trend == "→"  # Default to stable


class TestSparkline:
    """Test sparkline generation."""
    
    def test_sparkline_generation(self):
        """Test generating ASCII sparkline."""
        scores = [50, 60, 70, 80, 90, 85, 75, 80]
        sparkline = generate_sparkline(scores)
        assert len(sparkline) == len(scores)
        assert all(c in "▁▂▃▄▅▆▇█" for c in sparkline)
    
    def test_sparkline_flat(self):
        """Test sparkline with flat data."""
        scores = [75, 75, 75, 75]
        sparkline = generate_sparkline(scores)
        assert len(sparkline) == len(scores)
    
    def test_sparkline_empty(self):
        """Test sparkline with no data."""
        sparkline = generate_sparkline([])
        assert sparkline == "─"
