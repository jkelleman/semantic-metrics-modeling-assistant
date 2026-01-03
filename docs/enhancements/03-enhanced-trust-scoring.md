# Enhancement 03: Enhanced Trust Scoring Algorithm

**Status:** 🔄 In Progress  
**Priority:** Medium (Tier 3 - Polish)  
**Target Date:** January 2026

---

## Overview

Upgrade the trust scoring algorithm from simple equal-weighted factors to a sophisticated system with weighted factors, historical tracking, time-decay for stale metrics, and trend visualization.

## Problem Solved

**Current Algorithm Issues:**
- All factors weighted equally (doesn't reflect real-world importance)
- No time dimension (can't see if metric health is improving/degrading)
- Static scoring (doesn't account for staleness)
- No historical tracking (can't identify trends)

**After Enhancement:**
- Weighted factors based on importance (tests=35%, most critical)
- Historical trust score tracking with trends
- Time-decay function (old metrics without updates lose trust)
- Trend visualization (↗️ improving, → stable, ↘️ degrading)

## Current Implementation

```python
def _calculate_trust_score(metric: Dict) -> int:
    """Calculate trust score (0-100) based on various factors."""
    score = 0
    
    # Freshness (20 points)
    score += _check_freshness(metric)
    
    # Test coverage (25 points)
    score += _check_test_coverage(metric)
    
    # Usage (20 points)
    score += _check_usage(metric)
    
    # Documentation (20 points)
    score += _check_documentation(metric)
    
    # Ownership (15 points)
    score += _check_ownership(metric)
    
    return score
```

**Problems:**
1. All factors equal importance (tests should matter more than docs)
2. No decay over time
3. No trend tracking
4. No history

## Enhanced Implementation

### New Algorithm

```python
def _calculate_trust_score_enhanced(metric: Dict, db: MetricsDatabase = None) -> Dict[str, Any]:
    """
    Calculate enhanced trust score with weights, history, and decay.
    
    Returns:
        Dict with score, breakdown, trend, and recommendations
    """
    # Base scores with new weights
    freshness_score = _check_freshness(metric) * (15/20)  # 15% weight
    test_score = _check_test_coverage(metric) * (35/25)    # 35% weight (increased!)
    usage_score = _check_usage(metric) * 1.0               # 20% weight (same)
    doc_score = _check_documentation(metric) * (15/20)     # 15% weight
    ownership_score = _check_ownership(metric) * 1.0       # 15% weight (same)
    
    base_score = (
        freshness_score +
        test_score +
        usage_score +
        doc_score +
        ownership_score
    )
    
    # Apply multipliers
    final_score = base_score
    
    # Recent activity boost (+10% max)
    days_since_update = (datetime.now() - datetime.fromisoformat(metric['updated_at'])).days
    if days_since_update <= 7:
        final_score += 10  # Used this week
    elif days_since_update <= 30:
        final_score += 5   # Used this month
    
    # Consistency bonus (+5% if regularly updated)
    if db:
        history = db.get_metric_history(metric['id'], limit=10)
        if len(history) >= 5:  # At least 5 updates
            update_dates = [datetime.fromisoformat(h['changed_at']) for h in history]
            gaps = [(update_dates[i] - update_dates[i+1]).days for i in range(len(update_dates)-1)]
            if all(g <= 30 for g in gaps):  # Updated at least monthly
                final_score += 5
    
    # Time decay (older metrics lose trust)
    days_since_creation = (datetime.now() - datetime.fromisoformat(metric['created_at'])).days
    if days_since_creation > 90 and days_since_update > 30:
        # Lose 5% per month of staleness
        decay = min(25, (days_since_update / 30) * 5)
        final_score -= decay
    
    # Clamp to 0-100
    final_score = max(0, min(100, final_score))
    
    # Get trend
    trend = _calculate_trend(metric, db) if db else "→"
    
    # Get recommendations
    recommendations = _get_recommendations(
        final_score, 
        metric, 
        freshness_score, 
        test_score, 
        usage_score, 
        doc_score, 
        ownership_score
    )
    
    return {
        "score": round(final_score, 1),
        "trend": trend,  # "↗️", "→", "↘️"
        "breakdown": {
            "freshness": round(freshness_score, 1),
            "tests": round(test_score, 1),
            "usage": round(usage_score, 1),
            "documentation": round(doc_score, 1),
            "ownership": round(ownership_score, 1)
        },
        "multipliers": {
            "recent_activity": 10 if days_since_update <= 7 else (5 if days_since_update <= 30 else 0),
            "consistency": 5 if (db and len(db.get_metric_history(metric['id'], limit=10)) >= 5) else 0,
            "time_decay": -min(25, (days_since_update / 30) * 5) if days_since_creation > 90 and days_since_update > 30 else 0
        },
        "recommendations": recommendations
    }
```

### Trend Calculation

```python
def _calculate_trend(metric: Dict, db: MetricsDatabase) -> str:
    """
    Calculate trust score trend based on history.
    
    Returns:
        "↗️" (improving), "→" (stable), "↘️" (degrading)
    """
    history = db.get_metric_history(metric['id'], limit=30)
    
    if len(history) < 2:
        return "→"  # Not enough data
    
    # Get scores over time (approximate from activity)
    recent_activity = len([h for h in history[:10] if 
        (datetime.now() - datetime.fromisoformat(h['changed_at'])).days <= 30])
    older_activity = len([h for h in history[10:20] if 
        (datetime.now() - datetime.fromisoformat(h['changed_at'])).days <= 60])
    
    if recent_activity > older_activity + 2:
        return "↗️"  # Improving
    elif recent_activity < older_activity - 2:
        return "↘️"  # Degrading
    else:
        return "→"  # Stable
```

### Historical Tracking

Store trust scores in database:

```python
# In database.py - add new method
def record_trust_score(self, metric_id: str, score: float, breakdown: Dict):
    """Record trust score snapshot for trend analysis."""
    self.cursor.execute("""
        INSERT INTO trust_score_history (metric_id, score, breakdown, recorded_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (metric_id, score, json.dumps(breakdown)))
    self.conn.commit()

def get_trust_score_history(self, metric_id: str, days: int = 90) -> List[Dict]:
    """Get trust score history for trend analysis."""
    self.cursor.execute("""
        SELECT score, breakdown, recorded_at
        FROM trust_score_history
        WHERE metric_id = ? AND recorded_at >= date('now', '-' || ? || ' days')
        ORDER BY recorded_at DESC
    """, (metric_id, days))
    
    return [self._row_to_dict(row) for row in self.cursor.fetchall()]
```

Add new table in schema:

```sql
CREATE TABLE IF NOT EXISTS trust_score_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_id TEXT NOT NULL,
    score REAL NOT NULL,
    breakdown TEXT,  -- JSON
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (metric_id) REFERENCES metrics(id)
);

CREATE INDEX idx_trust_history_metric ON trust_score_history(metric_id, recorded_at);
```

## New Weights Rationale

| Factor | Old Weight | New Weight | Rationale |
|--------|-----------|-----------|-----------|
| **Tests** | 25% | **35%** | Most important - proves metric accuracy |
| **Usage** | 20% | **20%** | High usage = battle-tested, validates usefulness |
| **Freshness** | 20% | **15%** | Important but not critical (some metrics stable) |
| **Documentation** | 20% | **15%** | Helpful but secondary to correctness |
| **Ownership** | 15% | **15%** | Same - accountability matters |

**Why Tests Get 35%?**
- Tests prove the metric calculates correctly
- Tests catch data quality issues
- Tests enable confident changes
- Production-critical metrics MUST have tests

## Usage Examples

### Calculate Enhanced Score

```python
from semantic_metrics.database import MetricsDatabase

db = MetricsDatabase()
metric = db.get_metric("revenue_total")

# Enhanced calculation
score_data = _calculate_trust_score_enhanced(metric, db)

print(f"Trust Score: {score_data['score']}/100 {score_data['trend']}")
print(f"Breakdown:")
for factor, value in score_data['breakdown'].items():
    print(f"  {factor}: {value}")
print(f"\nRecommendations:")
for rec in score_data['recommendations']:
    print(f"  • {rec}")
```

### View Trend Over Time

```python
# Get 90-day history
history = db.get_trust_score_history("revenue_total", days=90)

# Show sparkline
scores = [h['score'] for h in history]
print(f"Trust Score Trend (90 days): {_generate_sparkline(scores)}")
print(f"Current: {scores[0]:.1f}, 90 days ago: {scores[-1]:.1f}")
print(f"Change: {(scores[0] - scores[-1]):+.1f} points")
```

## Modified MCP Tools

### Update `calculate_trust_score` Tool

```python
@mcp.tool()
def calculate_trust_score(metric_name: str, show_history: bool = False) -> str:
    """
    Calculate trust score for a metric with enhanced algorithm.
    
    Args:
        metric_name: Name of the metric
        show_history: Whether to show 90-day trend
        
    Returns:
        Trust score with breakdown, trend, and recommendations
    """
    from semantic_metrics.database import MetricsDatabase
    
    metric_id = metric_name.lower().replace(" ", "_")
    
    if metric_id not in METRICS_STORE:
        return f"❌ Metric '{metric_name}' not found."
    
    metric = METRICS_STORE[metric_id]
    db = MetricsDatabase()
    
    # Calculate enhanced score
    score_data = _calculate_trust_score_enhanced(metric, db)
    
    # Build report
    report = f"""
📊 Trust Score for: {metric['name']}
{'=' * 50}

Overall Score: {score_data['score']}/100 {score_data['trend']}
Grade: {_get_score_label(score_data['score'])}

Factor Breakdown:
  Tests: {score_data['breakdown']['tests']}/35 {_get_check_mark(score_data['breakdown']['tests'], 25)}
  Usage: {score_data['breakdown']['usage']}/20 {_get_check_mark(score_data['breakdown']['usage'], 10)}
  Freshness: {score_data['breakdown']['freshness']}/15 {_get_check_mark(score_data['breakdown']['freshness'], 10)}
  Documentation: {score_data['breakdown']['documentation']}/15 {_get_check_mark(score_data['breakdown']['documentation'], 10)}
  Ownership: {score_data['breakdown']['ownership']}/15 {_get_check_mark(score_data['breakdown']['ownership'], 10)}

Multipliers:
  Recent Activity: {score_data['multipliers']['recent_activity']:+.0f}
  Consistency Bonus: {score_data['multipliers']['consistency']:+.0f}
  Time Decay: {score_data['multipliers']['time_decay']:.1f}

"""
    
    if show_history:
        history = db.get_trust_score_history(metric_id, days=90)
        if history:
            scores = [h['score'] for h in history]
            report += f"""
Historical Trend (90 days):
  {_generate_sparkline(scores)}
  Current: {scores[0]:.1f} | 30d ago: {scores[min(30, len(scores)-1)]:.1f} | 90d ago: {scores[-1]:.1f}
  Change: {(scores[0] - scores[-1]):+.1f} points

"""
    
    if score_data['recommendations']:
        report += "💡 Recommendations:\n"
        for rec in score_data['recommendations']:
            report += f"  • {rec}\n"
    
    db.close()
    return report
```

## Testing Plan

### Unit Tests

```python
def test_enhanced_scoring_weights():
    """Test new weighting system."""
    metric = {
        'id': 'test',
        'name': 'Test',
        'test_count': 3,  # Should get 35% weight
        'usage_count': 10,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'owner': '@team',
        'tags': ['test'],
        'data_source': 'db'
    }
    
    score_data = _calculate_trust_score_enhanced(metric)
    
    # Tests should contribute most
    assert score_data['breakdown']['tests'] > score_data['breakdown']['documentation']
    assert score_data['breakdown']['tests'] > score_data['breakdown']['freshness']

def test_time_decay():
    """Test that old metrics without updates lose trust."""
    old_metric = {
        'created_at': (datetime.now() - timedelta(days=200)).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=60)).isoformat(),
        # ... other fields
    }
    
    score_data = _calculate_trust_score_enhanced(old_metric)
    
    # Should have negative decay multiplier
    assert score_data['multipliers']['time_decay'] < 0

def test_trend_calculation():
    """Test trend detection."""
    db = MetricsDatabase(":memory:")
    # Create metric with increasing activity
    # ... add history records
    
    trend = _calculate_trend(metric, db)
    assert trend == "↗️"
```

## Benefits

✅ **More Accurate** - Weights reflect real importance (tests > docs)  
✅ **Time-Aware** - Accounts for staleness with decay function  
✅ **Trend Visibility** - See if metric health improving/degrading  
✅ **Historical Context** - Track changes over time  
✅ **Better Recommendations** - Prioritize what matters most  

## Future Enhancements

🚀 **Adaptive Weighting** - Learn weights from team behavior  
🚀 **Predictive Scoring** - Predict when metric will need attention  
🚀 **Comparative Analysis** - Compare against team averages  
🚀 **Automated Alerts** - Notify when score drops significantly  

## Related Files

- [server.py](../../semantic_metrics/server.py) - Update calculate_trust_score tool
- [database.py](../../semantic_metrics/database.py) - Add trust_score_history table
- [ENHANCEMENT_RATIONALE.md](../../ENHANCEMENT_RATIONALE.md) - Why enhanced scoring matters

---

*Last updated: January 3, 2026*
