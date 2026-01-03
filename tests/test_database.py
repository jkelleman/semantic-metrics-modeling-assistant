"""Tests for database operations."""
import pytest
from datetime import datetime
from semantic_metrics.database import MetricsDatabase


class TestDatabaseCRUD:
    """Test Create, Read, Update, Delete operations."""
    
    def test_create_metric(self, test_db, sample_metric):
        """Test creating a new metric."""
        metric_id = test_db.create_metric(sample_metric)
        assert metric_id == sample_metric["id"]
        
        # Verify it was created
        retrieved = test_db.get_metric(metric_id)
        assert retrieved is not None
        assert retrieved["name"] == sample_metric["name"]
    
    def test_get_metric(self, test_db, sample_metric):
        """Test retrieving a metric by ID."""
        metric_id = test_db.create_metric(sample_metric)
        metric = test_db.get_metric(metric_id)
        
        assert metric["id"] == metric_id
        assert metric["name"] == sample_metric["name"]
        assert metric["description"] == sample_metric["description"]
        assert metric["tags"] == sample_metric["tags"]
    
    def test_get_nonexistent_metric(self, test_db):
        """Test getting a metric that doesn't exist."""
        metric = test_db.get_metric("nonexistent")
        assert metric is None
    
    def test_get_all_metrics(self, test_db, multiple_metrics):
        """Test listing all metrics."""
        all_metrics = test_db.get_all_metrics()
        assert len(all_metrics) == 3
        assert all(m["id"] in ["metric_1", "metric_2", "metric_3"] for m in all_metrics)
    
    def test_update_metric(self, test_db, sample_metric):
        """Test updating a metric."""
        metric_id = test_db.create_metric(sample_metric)
        
        updates = {
            "description": "Updated description",
            "owner": "@new-team"
        }
        test_db.update_metric(metric_id, updates, "test_user")
        
        updated = test_db.get_metric(metric_id)
        assert updated["description"] == updates["description"]
        assert updated["owner"] == updates["owner"]
    
    def test_update_creates_history(self, test_db, sample_metric):
        """Test that updates create history records."""
        metric_id = test_db.create_metric(sample_metric)
        test_db.update_metric(metric_id, {"description": "New desc"}, "user1")
        
        history = test_db.get_metric_history(metric_id)
        assert len(history) >= 1
        assert history[0]["field_name"] == "description"
        assert history[0]["changed_by"] == "user1"
    
    def test_delete_metric(self, test_db, sample_metric):
        """Test deleting a metric."""
        metric_id = test_db.create_metric(sample_metric)
        test_db.delete_metric(metric_id)
        
        # Verify it's gone
        metric = test_db.get_metric(metric_id)
        assert metric is None


class TestDatabaseSearch:
    """Test search and filter functionality."""
    
    def test_search_metrics_by_name(self, test_db, multiple_metrics):
        """Test searching metrics by name."""
        results = test_db.search_metrics("Metric One")
        assert len(results) == 1
        assert results[0]["id"] == "metric_1"
    
    def test_search_metrics_by_description(self, test_db, multiple_metrics):
        """Test searching in descriptions."""
        results = test_db.search_metrics("Second")
        assert len(results) == 1
        assert results[0]["id"] == "metric_2"
    
    def test_search_no_results(self, test_db, multiple_metrics):
        """Test search with no matches."""
        results = test_db.search_metrics("nonexistent term")
        assert len(results) == 0
    
    def test_get_metrics_by_owner(self, test_db, multiple_metrics):
        """Test filtering by owner."""
        results = test_db.get_metrics_by_owner("@team-a")
        assert len(results) == 2
        assert all(m["owner"] == "@team-a" for m in results)
    
    def test_get_metrics_by_tag(self, test_db, multiple_metrics):
        """Test filtering by tag."""
        results = test_db.get_metrics_by_tag("tag2")
        assert len(results) == 2


class TestDatabaseTracking:
    """Test history and usage tracking."""
    
    def test_record_usage(self, test_db, sample_metric):
        """Test recording metric usage."""
        metric_id = test_db.create_metric(sample_metric)
        test_db.record_usage(metric_id, "dashboard_1", "revenue_dashboard")
        
        stats = test_db.get_usage_stats(metric_id)
        assert stats["total_uses"] >= 1
    
    def test_get_metric_history(self, test_db, metric_with_history):
        """Test retrieving metric change history."""
        history = test_db.get_metric_history(metric_with_history)
        assert len(history) >= 3
        assert all("field_name" in h for h in history)
        assert all("changed_by" in h for h in history)
    
    def test_add_validation_test(self, test_db, sample_metric):
        """Test adding validation test results."""
        metric_id = test_db.create_metric(sample_metric)
        test_db.add_validation_test(
            metric_id,
            {
                "test_type": "range_check",
                "test_query": "SELECT * FROM transactions WHERE amount < 0",
                "expected_result": "0 rows",
                "status": "passed"
            }
        )
        
        metric = test_db.get_metric(metric_id)
        # Validation tests are stored separately, just verify no error


class TestTrustScoreHistory:
    """Test trust score tracking."""
    
    def test_record_trust_score(self, test_db, sample_metric):
        """Test recording trust score."""
        metric_id = test_db.create_metric(sample_metric)
        breakdown = {
            "tests": 35,
            "usage": 20,
            "freshness": 15,
            "documentation": 15,
            "ownership": 15
        }
        
        test_db.record_trust_score(metric_id, 85.0, breakdown)
        
        history = test_db.get_trust_score_history(metric_id)
        assert len(history) == 1
        assert history[0]["score"] == 85.0
        assert history[0]["breakdown"] == breakdown
    
    def test_get_trust_score_history(self, test_db, sample_metric):
        """Test retrieving trust score history."""
        metric_id = test_db.create_metric(sample_metric)
        
        # Record multiple scores
        for score in [70.0, 75.0, 80.0, 85.0]:
            test_db.record_trust_score(metric_id, score, {})
        
        history = test_db.get_trust_score_history(metric_id, days=90)
        assert len(history) == 4
        assert history[0]["score"] == 85.0  # Most recent first
