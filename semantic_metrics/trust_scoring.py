"""Enhanced trust scoring with weighted factors, time-decay, and trend analysis."""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


def calculate_trust_score_enhanced(metric: Dict, history: List[Dict] = None) -> Dict[str, Any]:
    """
    Calculate enhanced trust score with weights, history, and decay.
    
    New algorithm uses:
    - Weighted factors (tests=35%, usage=20%, freshness/docs/ownership=15% each)
    - Time decay for stale metrics
    - Activity multipliers
    - Trend analysis from history
    
    Args:
        metric: Metric dictionary from database
        history: Optional metric history for trend calculation
        
    Returns:
        Dict with score, breakdown, trend, multipliers, and recommendations
    """
    # Calculate base component scores with new weights
    freshness_score = check_freshness(metric) * (15/20)  # 15% weight
    test_score = check_test_coverage(metric) * (35/25)    # 35% weight (increased!)
    usage_score = check_usage(metric) * 1.0               # 20% weight (same)
    doc_score = check_documentation(metric) * (15/20)     # 15% weight
    ownership_score = check_ownership(metric) * 1.0       # 15% weight (same)
    
    base_score = (
        freshness_score +
        test_score +
        usage_score +
        doc_score +
        ownership_score
    )
    
    # Apply multipliers
    final_score = base_score
    multipliers = {}
    
    # Recent activity boost (+10% max)
    days_since_update = (datetime.now() - datetime.fromisoformat(metric['updated_at'])).days
    if days_since_update <= 7:
        multipliers['recent_activity'] = 10  # Used this week
        final_score += 10
    elif days_since_update <= 30:
        multipliers['recent_activity'] = 5   # Used this month
        final_score += 5
    else:
        multipliers['recent_activity'] = 0
    
    # Consistency bonus (+5% if regularly updated)
    if history and len(history) >= 5:
        update_dates = [datetime.fromisoformat(h['changed_at']) for h in history[:10]]
        if len(update_dates) > 1:
            gaps = [(update_dates[i] - update_dates[i+1]).days for i in range(len(update_dates)-1)]
            if all(g <= 30 for g in gaps):  # Updated at least monthly
                multipliers['consistency'] = 5
                final_score += 5
            else:
                multipliers['consistency'] = 0
        else:
            multipliers['consistency'] = 0
    else:
        multipliers['consistency'] = 0
    
    # Time decay (older metrics lose trust)
    days_since_creation = (datetime.now() - datetime.fromisoformat(metric['created_at'])).days
    if days_since_creation > 90 and days_since_update > 30:
        # Lose 5% per month of staleness
        decay = min(25, (days_since_update / 30) * 5)
        multipliers['time_decay'] = -decay
        final_score -= decay
    else:
        multipliers['time_decay'] = 0
    
    # Clamp to 0-100
    final_score = max(0, min(100, final_score))
    
    # Get trend
    trend = calculate_trend(history) if history else "→"
    
    # Get recommendations
    recommendations = get_recommendations(
        final_score, 
        metric, 
        freshness_score, 
        test_score, 
        usage_score, 
        doc_score, 
        ownership_score,
        days_since_update
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
        "multipliers": multipliers,
        "recommendations": recommendations
    }


def check_freshness(metric: Dict) -> float:
    """Check freshness (0-20 points, weighted to 15)."""
    days_old = (datetime.now() - datetime.fromisoformat(metric['updated_at'])).days
    
    if days_old <= 7:
        return 20
    elif days_old <= 30:
        return 15
    elif days_old <= 90:
        return 10
    elif days_old <= 180:
        return 5
    else:
        return 0


def check_test_coverage(metric: Dict) -> float:
    """Check test coverage (0-25 points, weighted to 35)."""
    test_count = metric.get('test_count', 0)
    
    if test_count >= 5:
        return 25
    elif test_count >= 3:
        return 20
    elif test_count >= 1:
        return 15
    else:
        return 0


def check_usage(metric: Dict) -> float:
    """Check usage (0-20 points, stays at 20)."""
    usage = metric.get('usage_count', 0)
    
    if usage >= 50:
        return 20
    elif usage >= 20:
        return 15
    elif usage >= 10:
        return 10
    elif usage >= 1:
        return 5
    else:
        return 0


def check_documentation(metric: Dict) -> float:
    """Check documentation quality (0-20 points, weighted to 15)."""
    score = 0
    
    # Description present and meaningful
    if metric.get('description') and len(metric['description']) > 20:
        score += 5
    
    # Data source specified
    if metric.get('data_source'):
        score += 5
    
    # Tags present
    if metric.get('tags') and len(metric['tags']) > 0:
        score += 5
    
    # Dependencies documented
    if metric.get('dependencies'):
        score += 5
    
    return score


def check_ownership(metric: Dict) -> float:
    """Check ownership assignment (0-15 points, stays at 15)."""
    if metric.get('owner') and metric['owner'] != "Unassigned":
        return 15
    else:
        return 0


def calculate_trend(history: List[Dict]) -> str:
    """
    Calculate trust score trend based on history.
    
    Args:
        history: List of metric_history records
        
    Returns:
        "↗️" (improving), "→" (stable), "↘️" (degrading)
    """
    if not history or len(history) < 2:
        return "→"  # Not enough data
    
    # Count recent vs older activity as proxy for metric health
    now = datetime.now()
    recent_changes = len([h for h in history if 
        (now - datetime.fromisoformat(h['changed_at'])).days <= 30])
    older_changes = len([h for h in history if 
        30 < (now - datetime.fromisoformat(h['changed_at'])).days <= 60])
    
    if recent_changes > older_changes + 2:
        return "↗️"  # Improving - more recent activity
    elif recent_changes < older_changes - 2:
        return "↘️"  # Degrading - less recent activity
    else:
        return "→"  # Stable


def get_recommendations(
    final_score: float,
    metric: Dict,
    freshness_score: float,
    test_score: float,
    usage_score: float,
    doc_score: float,
    ownership_score: float,
    days_since_update: int
) -> List[str]:
    """Generate actionable recommendations based on score breakdown."""
    recommendations = []
    
    # Prioritize tests (most important)
    if test_score < 15:
        if metric.get('test_count', 0) == 0:
            recommendations.append("🔴 CRITICAL: Add validation tests to verify metric accuracy")
        else:
            recommendations.append("🟡 Add more tests for comprehensive coverage (target: 3+ tests)")
    
    # Usage recommendations
    if usage_score < 10:
        if metric.get('usage_count', 0) == 0:
            recommendations.append("💡 New metric - promote to stakeholders to increase adoption")
        else:
            recommendations.append("💡 Low usage - ensure metric is discoverable and well-documented")
    
    # Freshness recommendations
    if days_since_update > 90:
        recommendations.append("⚠️ Stale metric - review and update to maintain trust")
    elif days_since_update > 30:
        recommendations.append("ℹ️ Consider reviewing - metrics should be validated regularly")
    
    # Documentation recommendations
    if doc_score < 10:
        missing = []
        if not metric.get('data_source'):
            missing.append("data source")
        if not metric.get('tags') or len(metric['tags']) == 0:
            missing.append("tags")
        if not metric.get('description') or len(metric['description']) < 20:
            missing.append("detailed description")
        if missing:
            recommendations.append(f"📝 Improve documentation: Add {', '.join(missing)}")
    
    # Ownership recommendation
    if ownership_score < 10:
        recommendations.append("👤 Assign an owner for accountability and governance")
    
    # Overall assessment
    if final_score >= 80:
        recommendations.insert(0, "✅ Excellent - This metric is production-ready")
    elif final_score < 50:
        recommendations.insert(0, "⚠️ Action required - Address critical issues before using in production")
    
    return recommendations


def generate_sparkline(scores: List[float]) -> str:
    """Generate ASCII sparkline from score history."""
    if not scores or len(scores) < 2:
        return "─"
    
    # Normalize scores to 0-8 range for 8 sparkline characters
    min_score = min(scores)
    max_score = max(scores)
    
    if max_score == min_score:
        return "▄" * len(scores)
    
    sparkline_chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    
    sparkline = ""
    for score in scores:
        normalized = (score - min_score) / (max_score - min_score)
        char_index = min(7, int(normalized * 8))
        sparkline += sparkline_chars[char_index]
    
    return sparkline


def get_score_emoji(score: float) -> str:
    """Get emoji indicator for score."""
    if score >= 80:
        return "🟢"
    elif score >= 60:
        return "🟡"
    else:
        return "🔴"


def get_score_label(score: float) -> str:
    """Get descriptive label for score."""
    if score >= 80:
        return "Excellent - Production Ready"
    elif score >= 60:
        return "Good - Minor Improvements Recommended"
    elif score >= 40:
        return "Fair - Several Issues to Address"
    else:
        return "Poor - Needs Significant Work"
