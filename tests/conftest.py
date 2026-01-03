"""Test configuration and shared fixtures."""
import pytest
import sqlite3
from datetime import datetime, timedelta
from semantic_metrics.database import MetricsDatabase


@pytest.fixture
def test_db():
    """Create a test database in memory."""
    db = MetricsDatabase(":memory:")
    yield db
    db.close()


@pytest.fixture
def sample_metric():
    """Sample metric data for testing."""
    return {
        "id": "test_revenue",
        "name": "Test Revenue",
        "description": "Total revenue from all completed transactions",
        "calculation": "SUM(amount) FROM transactions WHERE status='completed'",
        "owner": "@revenue-team",
        "tags": ["revenue", "financial", "key-metric"],
        "data_source": "transactions",
        "dependencies": ["transactions.amount"],
        "test_count": 3,
        "usage_count": 25,
        "trust_score": 85.0
    }


@pytest.fixture
def multiple_metrics(test_db):
    """Create multiple test metrics in database."""
    metrics = [
        {
            "id": "metric_1",
            "name": "Metric One",
            "description": "First test metric",
            "calculation": "COUNT(*) FROM table1",
            "owner": "@team-a",
            "tags": ["tag1", "tag2"],
            "data_source": "table1",
            "dependencies": [],
            "test_count": 2,
            "usage_count": 10
        },
        {
            "id": "metric_2",
            "name": "Metric Two",
            "description": "Second test metric",
            "calculation": "SUM(value) FROM table2",
            "owner": "@team-b",
            "tags": ["tag2", "tag3"],
            "data_source": "table2",
            "dependencies": ["metric_1"],
            "test_count": 5,
            "usage_count": 50
        },
        {
            "id": "metric_3",
            "name": "Metric Three",
            "description": "Third test metric",
            "calculation": "AVG(score) FROM table3",
            "owner": "@team-a",
            "tags": ["tag1"],
            "data_source": "table3",
            "dependencies": ["metric_1", "metric_2"],
            "test_count": 0,
            "usage_count": 5
        }
    ]
    
    for metric in metrics:
        test_db.create_metric(metric)
    
    return metrics


@pytest.fixture
def metric_with_history(test_db, sample_metric):
    """Create metric with change history."""
    metric_id = test_db.create_metric(sample_metric)
    
    # Add some history
    test_db.update_metric(metric_id, {"description": "Updated description"}, "user1")
    test_db.update_metric(metric_id, {"owner": "@new-team"}, "user2")
    test_db.update_metric(metric_id, {"tags": ["revenue", "updated"]}, "user3")
    
    return metric_id
