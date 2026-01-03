#!/usr/bin/env python3
"""
Semantic Metrics Modeling Assistant - MCP Server

An MCP agent that helps data teams define, validate, and visualize semantic metrics
with built-in trust indicators and observability.

Demonstrates UX design for:
- Metrics governance
- Trust and transparency
- Cognitive load reduction for technical users
- Complex data system design
"""

import sys
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from semantic_metrics.trust_scoring import calculate_trust_score_enhanced, generate_sparkline, get_score_emoji, get_score_label

# Create the FastMCP server
mcp = FastMCP("semantic-metrics-assistant")

# In-memory metric repository (in production, this would be a database)
METRICS_STORE: Dict[str, Dict[str, Any]] = {}
LINEAGE_GRAPH: Dict[str, List[str]] = defaultdict(list)


@mcp.tool()
def define_metric(
    name: str,
    description: str,
    calculation: str,
    owner: str = "",
    tags: str = "",
    data_source: str = ""
) -> str:
    """
    Define a new semantic metric with conversational input.
    
    Args:
        name: Metric name (e.g., "Active Users", "Revenue per Customer")
        description: Plain language description
        calculation: SQL or formula for calculating the metric
        owner: Team or person responsible (e.g., "@data-team")
        tags: Comma-separated tags (e.g., "engagement,daily")
        data_source: Primary data source (e.g., "raw.users")
        
    Returns:
        Confirmation with metric details and trust score
    """
    if not name or not description or not calculation:
        return "Error: Name, description, and calculation are required"
    
    metric_id = name.lower().replace(" ", "_")
    
    # Check if metric already exists
    if metric_id in METRICS_STORE:
        return f"âš ï¸ Metric '{name}' already exists. Use update_metric() to modify it."
    
    # Parse dependencies from calculation
    dependencies = _extract_dependencies(calculation)
    
    # Create metric definition
    metric = {
        "name": name,
        "id": metric_id,
        "description": description,
        "calculation": calculation,
        "owner": owner or "Unassigned",
        "tags": [t.strip() for t in tags.split(",")] if tags else [],
        "data_source": data_source,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "dependencies": dependencies,
        "usage_count": 0,
        "test_count": 0,
        "documentation_complete": bool(description and calculation and owner)
    }
    
    # Store metric
    METRICS_STORE[metric_id] = metric
    
    # Update lineage graph
    for dep in dependencies:
        LINEAGE_GRAPH[dep].append(metric_id)
    
    # Calculate initial trust score
    trust_score = _calculate_trust_score(metric)
    
    report = f"""
âœ… Metric Created: {name}

ðŸ“Š Definition:
{description}

ðŸ”¢ Calculation:
{calculation}

ðŸ‘¤ Owner: {owner or "âš ï¸ Unassigned - Please assign an owner"}
ðŸ·ï¸ Tags: {', '.join(metric['tags']) if metric['tags'] else "None"}
ðŸ“ Data Source: {data_source or "Not specified"}

ðŸ›¡ï¸ Initial Trust Score: {trust_score}/100
"""
    
    if trust_score < 70:
        report += "\nâš ï¸ Trust score is low. Consider:\n"
        if not owner:
            report += "  â€¢ Assigning an owner\n"
        if not metric['tags']:
            report += "  â€¢ Adding relevant tags\n"
        if not data_source:
            report += "  â€¢ Specifying the data source\n"
        report += "  â€¢ Adding tests with validate_metric()\n"
    
    if dependencies:
        report += f"\nðŸ”— Dependencies detected: {', '.join(dependencies)}\n"
    
    report += f"\nðŸ’¡ Next steps:\n"
    report += f"  â€¢ Add tests: validate_metric('{name}')\n"
    report += f"  â€¢ Check lineage: visualize_lineage('{name}')\n"
    report += f"  â€¢ Export to dbt: export_to_dbt('{name}')\n"
    
    return report


@mcp.tool()
def search_metrics(query: str = "", tags: str = "") -> str:
    """
    Search for existing metrics by name, description, or tags.
    
    Args:
        query: Search term to match in name or description
        tags: Filter by specific tags (comma-separated)
        
    Returns:
        List of matching metrics with trust scores
    """
    if not METRICS_STORE:
        return "No metrics defined yet. Use define_metric() to create your first metric."
    
    query_lower = query.lower() if query else ""
    tag_filter = [t.strip().lower() for t in tags.split(",")] if tags else []
    
    matches = []
    for metric_id, metric in METRICS_STORE.items():
        # Match query in name or description
        query_match = (
            not query or 
            query_lower in metric['name'].lower() or 
            query_lower in metric['description'].lower()
        )
        
        # Match tags
        tag_match = (
            not tag_filter or 
            any(tag in [t.lower() for t in metric['tags']] for tag in tag_filter)
        )
        
        if query_match and tag_match:
            trust_score = _calculate_trust_score(metric)
            matches.append((metric, trust_score))
    
    if not matches:
        return f"No metrics found matching '{query}' with tags '{tags}'"
    
    # Sort by trust score descending
    matches.sort(key=lambda x: x[1], reverse=True)
    
    report = f"""
Search Results ({len(matches)} metrics found)
{'=' * 50}
"""
    
    for metric, trust_score in matches:
        trust_emoji = "ðŸŸ¢" if trust_score >= 80 else "ðŸŸ¡" if trust_score >= 60 else "ðŸ”´"
        report += f"\n{trust_emoji} {metric['name']} (Trust: {trust_score}/100)\n"
        report += f"   {metric['description']}\n"
        report += f"   Owner: {metric['owner']}\n"
        if metric['tags']:
            report += f"   Tags: {', '.join(metric['tags'])}\n"
        report += f"   Usage: {metric['usage_count']} times\n"
    
    return report


@mcp.tool()
def check_trust_score(metric_name: str) -> str:
    """
    Check the trust score and indicators for a metric.
    
    Trust is based on:
    - Freshness: How recently was it updated?
    - Test Coverage: Are there validation tests?
    - Usage: How widely adopted is it?
    - Documentation: Is it well-documented?
    - Ownership: Is there a clear owner?
    
    Args:
        metric_name: Name of the metric to check
        
    Returns:
        Detailed trust score breakdown
    """
    metric_id = metric_name.lower().replace(" ", "_")
    
    if metric_id not in METRICS_STORE:
        similar = _find_similar_metrics(metric_name)
        msg = f"âŒ Metric '{metric_name}' not found."
        if similar:
            msg += f"\n\nDid you mean: {', '.join(similar)}?"
        return msg
    
    metric = METRICS_STORE[metric_id]
    
    # Calculate detailed trust scores
    freshness_score = _check_freshness(metric)
    test_score = _check_test_coverage(metric)
    usage_score = _check_usage(metric)
    doc_score = _check_documentation(metric)
    ownership_score = _check_ownership(metric)
    
    overall_score = _calculate_trust_score(metric)
    
    report = f"""
Trust Score Report: {metric['name']}
{'=' * 50}

Overall Trust Score: {overall_score}/100
{_get_score_emoji(overall_score)} {_get_score_label(overall_score)}

Detailed Breakdown:
-------------------

ðŸ“… Freshness: {freshness_score}/20
{_get_check_mark(freshness_score, 15)} Updated: {_format_relative_time(metric['updated_at'])}
{_get_freshness_recommendation(freshness_score)}

ðŸ§ª Test Coverage: {test_score}/25
{_get_check_mark(test_score, 15)} Tests: {metric['test_count']} passing
{_get_test_recommendation(test_score, metric['test_count'])}

ðŸ“Š Usage: {usage_score}/20
{_get_check_mark(usage_score, 10)} Used {metric['usage_count']} times
{_get_usage_recommendation(usage_score, metric['usage_count'])}

ðŸ“– Documentation: {doc_score}/20
{_get_check_mark(doc_score, 15)} Complete: {metric['documentation_complete']}
{_get_doc_recommendation(doc_score, metric)}

ðŸ‘¤ Ownership: {ownership_score}/15
{_get_check_mark(ownership_score, 10)} Owner: {metric['owner']}
{_get_ownership_recommendation(ownership_score, metric['owner'])}

ðŸ’¡ Recommendations:
"""
    
    recommendations = _generate_recommendations(metric, overall_score)
    for rec in recommendations:
        report += f"  â€¢ {rec}\n"
    
    if overall_score >= 80:
        report += "\nðŸŽ‰ Excellent! This metric is production-ready and trustworthy.\n"
    elif overall_score >= 60:
        report += "\nðŸ‘ Good baseline. Address recommendations to increase trust.\n"
    else:
        report += "\nâš ï¸ Low trust score. Prioritize improvements before widespread use.\n"
    
    return report


@mcp.tool()
def visualize_lineage(metric_name: str, depth: int = 3) -> str:
    """
    Visualize the lineage and dependencies of a metric.
    
    Shows:
    - Upstream dependencies (what this metric depends on)
    - Downstream dependents (what depends on this metric)
    - Data sources
    
    Args:
        metric_name: Name of the metric
        depth: How many levels deep to show (default: 3)
        
    Returns:
        ASCII tree visualization of dependencies
    """
    metric_id = metric_name.lower().replace(" ", "_")
    
    if metric_id not in METRICS_STORE:
        return f"âŒ Metric '{metric_name}' not found."
    
    metric = METRICS_STORE[metric_id]
    
    report = f"""
Lineage for: {metric['name']}
{'=' * 50}

ðŸ“Š This Metric:
   {metric['description']}
   Data Source: {metric['data_source'] or 'Not specified'}

"""
    
    # Show upstream dependencies
    if metric['dependencies']:
        report += "â¬†ï¸ Upstream Dependencies (what this depends on):\n"
        report += _build_dependency_tree(metric['dependencies'], depth, "   ")
    else:
        report += "â¬†ï¸ Upstream Dependencies: None (base metric)\n"
    
    # Show downstream dependents
    report += "\nâ¬‡ï¸ Downstream Dependents (what depends on this):\n"
    downstream = [m for m, deps in LINEAGE_GRAPH.items() if metric_id in deps]
    if downstream:
        for dep in downstream:
            if dep in METRICS_STORE:
                report += f"   â””â”€â”€ {METRICS_STORE[dep]['name']}\n"
    else:
        report += "   None (no metrics depend on this yet)\n"
    
    # Impact analysis
    report += f"\nðŸŽ¯ Impact Analysis:\n"
    report += f"   Direct dependencies: {len(metric['dependencies'])}\n"
    report += f"   Direct dependents: {len(downstream)}\n"
    
    if len(downstream) > 0:
        report += f"\nâš ï¸ Caution: Changes to this metric will affect {len(downstream)} downstream metric(s)\n"
    
    return report


@mcp.tool()
def validate_metric(metric_name: str, test_description: str = "") -> str:
    """
    Validate a metric definition and add test coverage.
    
    Checks:
    - SQL syntax (basic validation)
    - Dependencies exist
    - No circular dependencies
    - Calculation logic makes sense
    
    Args:
        metric_name: Name of the metric to validate
        test_description: Description of what this test validates
        
    Returns:
        Validation results and trust score improvement
    """
    metric_id = metric_name.lower().replace(" ", "_")
    
    if metric_id not in METRICS_STORE:
        return f"âŒ Metric '{metric_name}' not found."
    
    metric = METRICS_STORE[metric_id]
    
    issues = []
    warnings = []
    
    # Check SQL syntax (basic)
    if "SELECT" not in metric['calculation'].upper():
        warnings.append("âš ï¸ Calculation doesn't appear to be SQL - ensure format is correct")
    
    # Check dependencies exist
    for dep in metric['dependencies']:
        if dep not in METRICS_STORE and not _is_table_reference(dep):
            issues.append(f"âŒ Dependency '{dep}' not found - define it first or verify table name")
    
    # Check for circular dependencies
    if _has_circular_dependency(metric_id):
        issues.append(f"âŒ Circular dependency detected!")
    
    # Check ownership
    if metric['owner'] == "Unassigned":
        warnings.append("âš ï¸ No owner assigned")
    
    # Check documentation
    if not metric['data_source']:
        warnings.append("âš ï¸ Data source not specified")
    
    # Add test if description provided
    if test_description:
        metric['test_count'] += 1
        metric['updated_at'] = datetime.now().isoformat()
    
    old_trust = _calculate_trust_score(metric)
    METRICS_STORE[metric_id] = metric
    new_trust = _calculate_trust_score(metric)
    
    report = f"""
Validation Report: {metric['name']}
{'=' * 50}

"""
    
    if not issues:
        report += "âœ… All validation checks passed!\n\n"
    else:
        report += f"âŒ {len(issues)} issue(s) found:\n"
        for issue in issues:
            report += f"   {issue}\n"
        report += "\n"
    
    if warnings:
        report += f"âš ï¸ {len(warnings)} warning(s):\n"
        for warning in warnings:
            report += f"   {warning}\n"
        report += "\n"
    
    if test_description:
        report += f"ðŸ§ª Test Added:\n"
        report += f"   {test_description}\n"
        report += f"   Total tests: {metric['test_count']}\n\n"
    
    report += f"ðŸ›¡ï¸ Trust Score: {old_trust}/100 â†’ {new_trust}/100 "
    if new_trust > old_trust:
        report += f"(+{new_trust - old_trust}) ðŸ“ˆ\n"
    else:
        report += "\n"
    
    if not issues and not warnings:
        report += "\nâœ¨ Metric is validated and ready to use!\n"
    
    return report


@mcp.tool()
def compare_metrics(metric1_name: str, metric2_name: str) -> str:
    """
    Compare two metrics side-by-side.
    
    Useful for:
    - Understanding why metrics show different values
    - Identifying duplicate or similar metrics
    - Choosing between alternative definitions
    
    Args:
        metric1_name: First metric name
        metric2_name: Second metric name
        
    Returns:
        Side-by-side comparison
    """
    metric1_id = metric1_name.lower().replace(" ", "_")
    metric2_id = metric2_name.lower().replace(" ", "_")
    
    if metric1_id not in METRICS_STORE:
        return f"âŒ Metric '{metric1_name}' not found."
    if metric2_id not in METRICS_STORE:
        return f"âŒ Metric '{metric2_name}' not found."
    
    m1 = METRICS_STORE[metric1_id]
    m2 = METRICS_STORE[metric2_id]
    
    trust1 = _calculate_trust_score(m1)
    trust2 = _calculate_trust_score(m2)
    
    report = f"""
Metric Comparison
{'=' * 50}

{m1['name']} vs {m2['name']}

Description:
  1ï¸âƒ£ {m1['description']}
  2ï¸âƒ£ {m2['description']}

Calculation:
  1ï¸âƒ£ {m1['calculation']}
  2ï¸âƒ£ {m2['calculation']}

Owner:
  1ï¸âƒ£ {m1['owner']}
  2ï¸âƒ£ {m2['owner']}

Trust Score:
  1ï¸âƒ£ {trust1}/100 {_get_score_emoji(trust1)}
  2ï¸âƒ£ {trust2}/100 {_get_score_emoji(trust2)}

Usage:
  1ï¸âƒ£ {m1['usage_count']} times
  2ï¸âƒ£ {m2['usage_count']} times

Data Source:
  1ï¸âƒ£ {m1['data_source'] or 'Not specified'}
  2ï¸âƒ£ {m2['data_source'] or 'Not specified'}

"""
    
    # Recommendation
    if trust1 > trust2 + 10:
        report += f"ðŸ’¡ Recommendation: '{m1['name']}' has higher trust - prefer using it\n"
    elif trust2 > trust1 + 10:
        report += f"ðŸ’¡ Recommendation: '{m2['name']}' has higher trust - prefer using it\n"
    elif m1['usage_count'] > m2['usage_count'] * 2:
        report += f"ðŸ’¡ Recommendation: '{m1['name']}' is more widely used\n"
    elif m2['usage_count'] > m1['usage_count'] * 2:
        report += f"ðŸ’¡ Recommendation: '{m2['name']}' is more widely used\n"
    else:
        report += "ðŸ’¡ Both metrics appear similar - review calculations to choose\n"
    
    # Check for potential duplicates
    similarity = _calculate_similarity(m1, m2)
    if similarity > 0.7:
        report += f"\nâš ï¸ Warning: These metrics appear very similar ({int(similarity*100)}% match)\n"
        report += "Consider consolidating them to reduce metric sprawl.\n"
    
    return report


@mcp.tool()
def export_to_dbt(metric_name: str) -> str:
    """
    Export metric definition to dbt YAML format.
    
    Args:
        metric_name: Name of the metric to export
        
    Returns:
        dbt-compatible YAML definition
    """
    metric_id = metric_name.lower().replace(" ", "_")
    
    if metric_id not in METRICS_STORE:
        return f"âŒ Metric '{metric_name}' not found."
    
    metric = METRICS_STORE[metric_id]
    
    # Generate dbt YAML
    yaml_output = f"""
# dbt Semantic Layer Metric
# Generated by Semantic Metrics Modeling Assistant
# Created: {datetime.now().strftime("%Y-%m-%d")}

version: 2

metrics:
  - name: {metric_id}
    label: {metric['name']}
    description: {metric['description']}
    
    calculation_method: derived
    expression: {metric['calculation']}
    
    timestamp: updated_at
    time_grains: [day, week, month, quarter, year]
    
    dimensions:
      {f"- {metric['data_source']}" if metric['data_source'] else "# Add dimensions here"}
    
    meta:
      owner: {metric['owner']}
      tags: {metric['tags']}
      created_at: {metric['created_at']}
      trust_score: {_calculate_trust_score(metric)}
"""
    
    report = f"""
âœ… dbt Export for: {metric['name']}
{'=' * 50}

```yaml{yaml_output}
```

ðŸ’¡ Next steps:
1. Copy the YAML above to your dbt project
2. Place in: models/metrics/{metric_id}.yml
3. Run: dbt compile
4. Run: dbt run --select {metric_id}

ðŸ“š dbt documentation:
https://docs.getdbt.com/docs/build/metrics
"""
    
    return report


# Helper functions

def _extract_dependencies(calculation: str) -> List[str]:
    """Extract metric and table dependencies from calculation."""
    # Simple regex to find potential table references (schema.table)
    pattern = r'\b([a-z_]+\.[a-z_]+)\b'
    matches = re.findall(pattern, calculation.lower())
    return list(set(matches))


def _calculate_trust_score(metric: Dict) -> int:
    """Calculate overall trust score (0-100)."""
    freshness = _check_freshness(metric)
    tests = _check_test_coverage(metric)
    usage = _check_usage(metric)
    docs = _check_documentation(metric)
    ownership = _check_ownership(metric)
    
    return freshness + tests + usage + docs + ownership


def _check_freshness(metric: Dict) -> int:
    """Check how fresh the metric is (0-20 points)."""
    updated = datetime.fromisoformat(metric['updated_at'])
    age_days = (datetime.now() - updated).days
    
    if age_days == 0:
        return 20
    elif age_days <= 7:
        return 18
    elif age_days <= 30:
        return 15
    elif age_days <= 90:
        return 10
    else:
        return 5


def _check_test_coverage(metric: Dict) -> int:
    """Check test coverage (0-25 points)."""
    tests = metric['test_count']
    if tests >= 5:
        return 25
    elif tests >= 3:
        return 20
    elif tests >= 1:
        return 15
    else:
        return 0


def _check_usage(metric: Dict) -> int:
    """Check usage adoption (0-20 points)."""
    usage = metric['usage_count']
    if usage >= 20:
        return 20
    elif usage >= 10:
        return 15
    elif usage >= 5:
        return 10
    elif usage >= 1:
        return 5
    else:
        return 0


def _check_documentation(metric: Dict) -> int:
    """Check documentation completeness (0-20 points)."""
    score = 0
    if metric['description']:
        score += 10
    if metric['data_source']:
        score += 5
    if metric['tags']:
        score += 5
    return score


def _check_ownership(metric: Dict) -> int:
    """Check ownership assignment (0-15 points)."""
    if metric['owner'] and metric['owner'] != "Unassigned":
        return 15
    else:
        return 0


def _get_score_emoji(score: int) -> str:
    """Get emoji for score."""
    if score >= 80:
        return "ðŸŸ¢"
    elif score >= 60:
        return "ðŸŸ¡"
    else:
        return "ðŸ”´"


def _get_score_label(score: int) -> str:
    """Get label for score."""
    if score >= 80:
        return "Excellent - Production Ready"
    elif score >= 60:
        return "Good - Minor Improvements Recommended"
    else:
        return "Needs Improvement"


def _get_check_mark(score: int, threshold: int) -> str:
    """Get check or warning mark."""
    return "âœ…" if score >= threshold else "âš ï¸"


def _format_relative_time(iso_time: str) -> str:
    """Format time as relative."""
    dt = datetime.fromisoformat(iso_time)
    delta = datetime.now() - dt
    
    if delta.days == 0:
        return "today"
    elif delta.days == 1:
        return "yesterday"
    elif delta.days < 7:
        return f"{delta.days} days ago"
    elif delta.days < 30:
        return f"{delta.days // 7} weeks ago"
    else:
        return f"{delta.days // 30} months ago"


def _get_freshness_recommendation(score: int) -> str:
    """Get recommendation for freshness."""
    if score >= 15:
        return ""
    else:
        return "âš ï¸ Consider updating - metrics should be reviewed regularly"


def _get_test_recommendation(score: int, test_count: int) -> str:
    """Get recommendation for tests."""
    if score >= 20:
        return ""
    elif test_count == 0:
        return "â— Add validation tests to verify metric accuracy"
    else:
        return "âš ï¸ Add more tests for comprehensive coverage"


def _get_usage_recommendation(score: int, usage: int) -> str:
    """Get recommendation for usage."""
    if usage == 0:
        return "â„¹ï¸ New metric - promote to increase adoption"
    elif score < 10:
        return "â„¹ï¸ Low usage - ensure metric is discoverable"
    else:
        return ""


def _get_doc_recommendation(score: int, metric: Dict) -> str:
    """Get recommendation for documentation."""
    if score >= 15:
        return ""
    missing = []
    if not metric['data_source']:
        missing.append("data source")
    if not metric['tags']:
        missing.append("tags")
    if missing:
        return f"âš ï¸ Add: {', '.join(missing)}"
    return ""


def _get_ownership_recommendation(score: int, owner: str) -> str:
    """Get recommendation for ownership."""
    if owner == "Unassigned":
        return "â— Assign an owner for governance"
    return ""


def _generate_recommendations(metric: Dict, score: int) -> List[str]:
    """Generate improvement recommendations."""
    recs = []
    
    if metric['test_count'] == 0:
        recs.append("Add validation tests")
    
    if metric['owner'] == "Unassigned":
        recs.append("Assign an owner")
    
    if not metric['data_source']:
        recs.append("Specify the data source")
    
    if not metric['tags']:
        recs.append("Add relevant tags for discoverability")
    
    if metric['usage_count'] == 0:
        recs.append("Promote metric to increase adoption")
    
    if not recs:
        recs.append("Keep metric updated and monitored")
    
    return recs


def _find_similar_metrics(query: str) -> List[str]:
    """Find metrics with similar names."""
    query_lower = query.lower()
    similar = []
    
    for metric_id, metric in METRICS_STORE.items():
        if query_lower in metric['name'].lower():
            similar.append(metric['name'])
    
    return similar[:5]


def _build_dependency_tree(deps: List[str], depth: int, indent: str) -> str:
    """Build ASCII tree of dependencies."""
    if depth == 0 or not deps:
        return ""
    
    tree = ""
    for dep in deps:
        tree += f"{indent}â””â”€â”€ {dep}\n"
        if dep in METRICS_STORE:
            sub_deps = METRICS_STORE[dep]['dependencies']
            tree += _build_dependency_tree(sub_deps, depth - 1, indent + "    ")
    
    return tree


def _is_table_reference(name: str) -> bool:
    """Check if name looks like a table reference."""
    return '.' in name


def _has_circular_dependency(metric_id: str, visited: set = None) -> bool:
    """Check for circular dependencies."""
    if visited is None:
        visited = set()
    
    if metric_id in visited:
        return True
    
    visited.add(metric_id)
    
    if metric_id in METRICS_STORE:
        for dep in METRICS_STORE[metric_id]['dependencies']:
            if dep in METRICS_STORE and _has_circular_dependency(dep, visited.copy()):
                return True
    
    return False


def _calculate_similarity(m1: Dict, m2: Dict) -> float:
    """Calculate similarity between two metrics (0-1)."""
    score = 0.0
    
    # Compare descriptions
    desc1_words = set(m1['description'].lower().split())
    desc2_words = set(m2['description'].lower().split())
    if desc1_words and desc2_words:
        desc_overlap = len(desc1_words & desc2_words) / len(desc1_words | desc2_words)
        score += desc_overlap * 0.4
    
    # Compare tags
    tags1 = set(m1['tags'])
    tags2 = set(m2['tags'])
    if tags1 or tags2:
        tag_overlap = len(tags1 & tags2) / max(len(tags1 | tags2), 1)
        score += tag_overlap * 0.3
    
    # Compare data sources
    if m1['data_source'] == m2['data_source'] and m1['data_source']:
        score += 0.3
    
    return score




@mcp.tool()
def export_to_looker(metric_name: str, view_name: str, explore: str = "") -> str:
    """
    Export metric definition to Looker LookML format.
    
    Args:
        metric_name: Name of the metric to export
        view_name: Looker view name to attach the measure to
        explore: Optional explore name for context
        
    Returns:
        LookML formatted string ready to paste into Looker
    """
    from semantic_metrics.exporters import generate_lookml
    
    metric_id = metric_name.lower().replace(" ", "_")
    
    if metric_id not in METRICS_STORE:
        return f" Metric ''{metric_name}'' not found."
    
    metric = METRICS_STORE[metric_id]
    lookml = generate_lookml(metric, view_name, explore if explore else None)
    
    report = f"""
 Looker LookML Export for: {metric[''name'']}
{''='' * 50}

```lookml
{lookml}
```

 Next steps:
1. Copy the LookML above
2. Paste into your Looker project view file
3. Validate syntax in Looker IDE
4. Deploy to production

 Trust Score: {_calculate_trust_score(metric)}/100
{''ℹ '' if metric[''owner''] else '' Assign an owner before deploying''}
"""
    
    return report


@mcp.tool()
def export_to_tableau(metric_name: str, connection: str) -> str:
    """
    Export metric definition to Tableau TDS format.
    
    Args:
        metric_name: Name of the metric to export
        connection: Tableau connection name
        
    Returns:
        TDS XML string ready to import into Tableau
    """
    from semantic_metrics.exporters import generate_tds
    
    metric_id = metric_name.lower().replace(" ", "_")
    
    if metric_id not in METRICS_STORE:
        return f" Metric ''{metric_name}'' not found."
    
    metric = METRICS_STORE[metric_id]
    tds = generate_tds(metric, connection)
    
    report = f"""
 Tableau TDS Export for: {metric[''name'']}
{''='' * 50}

```xml
{tds}
```

 Next steps:
1. Save the TDS XML above to a .tds file
2. Open Tableau Desktop
3. Data  Connect to Data  More  Other Files (TDS)
4. Select your saved .tds file

 Trust Score: {_calculate_trust_score(metric)}/100
{''ℹ '' if metric[''owner''] else '' Assign an owner before sharing''}
"""
    
    return report





@mcp.tool()
def calculate_trust_score_enhanced_tool(metric_name: str, show_history: bool = False) -> str:
    """
    Calculate enhanced trust score with weighted factors, trends, and recommendations.
    
    Uses improved algorithm with:
    - Weighted scoring (tests=35%, usage=20%, freshness/docs/ownership=15% each)
    - Time-decay for stale metrics
    - Trend analysis from history
    - Detailed recommendations
    
    Args:
        metric_name: Name of the metric
        show_history: Whether to show 90-day trend sparkline
        
    Returns:
        Trust score with breakdown, trend, multipliers, and actionable recommendations
    """
    from semantic_metrics.database import MetricsDatabase
    
    metric_id = metric_name.lower().replace(" ", "_")
    
    if metric_id not in METRICS_STORE:
        return f" Metric ''{metric_name}'' not found."
    
    metric = METRICS_STORE[metric_id]
    
    # Get database for history
    db = MetricsDatabase()
    history = db.get_metric_history(metric_id, limit=30)
    
    # Calculate enhanced score
    score_data = calculate_trust_score_enhanced(metric, history)
    
    # Build report
    report = f"""
 Enhanced Trust Score for: {metric[''name'']}
{''='' * 60}

Overall Score: {get_score_emoji(score_data[''score''])} {score_data[''score'']}/100 {score_data[''trend'']}
Grade: {get_score_label(score_data[''score''])}

 Factor Breakdown (Weighted):
   Tests:         {score_data[''breakdown''][''tests'']}/35  (35% weight - MOST IMPORTANT)
   Usage:         {score_data[''breakdown''][''usage'']}/20  (20% weight)
   Freshness:     {score_data[''breakdown''][''freshness'']}/15  (15% weight)
   Documentation: {score_data[''breakdown''][''documentation'']}/15  (15% weight)
   Ownership:     {score_data[''breakdown''][''ownership'']}/15  (15% weight)

 Multipliers Applied:
  Recent Activity: {score_data[''multipliers''][''recent_activity'']:+.0f} points
  Consistency:     {score_data[''multipliers''][''consistency'']:+.0f} points
  Time Decay:      {score_data[''multipliers''][''time_decay'']:.1f} points
"""
    
    # Show history if requested
    if show_history:
        trust_history = db.get_trust_score_history(metric_id, days=90)
        if trust_history and len(trust_history) >= 2:
            scores = [h[''score''] for h in trust_history]
            report += f"""
 Trust Score Trend (90 days):
  {generate_sparkline(scores[:30])}
  Current: {scores[0]:.1f} | 30d ago: {scores[min(30, len(scores)-1)]:.1f} | 90d ago: {scores[-1]:.1f}
  Change: {(scores[0] - scores[-1]):+.1f} points
"""
        else:
            report += "\n Trust Score Trend: Not enough history data yet\n"
    
    # Add recommendations
    if score_data[''recommendations'']:
        report += "\n Recommendations:\n"
        for rec in score_data[''recommendations'']:
            report += f"  {rec}\n"
    
    # Record this score
    db.record_trust_score(metric_id, score_data[''score''], score_data[''breakdown''])
    db.close()
    
    return report





@mcp.tool()
def generate_mermaid_diagram(metric_name: str, depth: int = 3, include_downstream: bool = False) -> str:
    """
    Generate Mermaid flowchart diagram showing metric dependencies and lineage.
    
    Creates beautiful, interactive diagrams that render in GitHub, Notion, Confluence, and other markdown tools.
    
    Args:
        metric_name: Name of the metric to visualize
        depth: How many dependency levels to traverse (default: 3)
        include_downstream: Also show metrics that depend on this one
        
    Returns:
        Mermaid diagram syntax ready to render in markdown
    """
    metric_id = metric_name.lower().replace(" ", "_")
    
    if metric_id not in METRICS_STORE:
        return f" Metric ''{metric_name}'' not found."
    
    metric = METRICS_STORE[metric_id]
    
    # Build dependency graph
    nodes = {}
    edges = []
    visited = set()
    
    def add_dependencies(mid, current_depth):
        if current_depth > depth or mid in visited:
            return
        visited.add(mid)
        
        if mid in METRICS_STORE:
            m = METRICS_STORE[mid]
            # Create sanitized node ID
            node_id = mid.replace(" ", "_").replace("-", "_")
            nodes[node_id] = {
                ''label'': m[''name''],
                ''type'': ''metric'',
                ''is_root'': mid == metric_id
            }
            
            # Add edges for dependencies
            for dep in m.get(''dependencies'', []):
                dep_id = dep.replace(" ", "_").replace("-", "_").split(''.'')[0]
                
                # Determine if dependency is a table or metric
                if dep_id in METRICS_STORE:
                    nodes[dep_id] = {
                        ''label'': METRICS_STORE[dep_id][''name''],
                        ''type'': ''metric'',
                        ''is_root'': False
                    }
                else:
                    # It''s a table/external source
                    nodes[dep_id] = {
                        ''label'': dep,
                        ''type'': ''table'',
                        ''is_root'': False
                    }
                
                edges.append((node_id, dep_id))
                
                # Recurse for metrics only
                if dep_id in METRICS_STORE:
                    add_dependencies(dep_id, current_depth + 1)
    
    # Build upstream dependencies
    add_dependencies(metric_id, 0)
    
    # Build downstream dependencies if requested
    if include_downstream:
        for mid, m in METRICS_STORE.items():
            if metric_id in m.get(''dependencies'', []) or metric[''name''] in m.get(''dependencies'', []):
                node_id = mid.replace(" ", "_").replace("-", "_")
                nodes[node_id] = {
                    ''label'': m[''name''],
                    ''type'': ''metric'',
                    ''is_root'': False
                }
                edges.append((node_id, metric_id.replace(" ", "_").replace("-", "_")))
    
    # Generate Mermaid syntax
    mermaid = "```mermaid\ngraph TD\n"
    
    # Add nodes with labels
    for node_id, node_data in nodes.items():
        label = node_data[''label'']
        if node_data[''type''] == ''table'':
            mermaid += f"    {node_id}[({label})]\n"  # Cylinder for tables
        else:
            mermaid += f"    {node_id}[{label}]\n"
    
    # Add edges
    for source, target in edges:
        mermaid += f"    {source} --> {target}\n"
    
    # Add styling
    mermaid += "\n    %% Styling\n"
    for node_id, node_data in nodes.items():
        if node_data[''is_root'']:
            mermaid += f"    style {node_id} fill:#4CAF50,color:#fff\n"  # Green for root
        elif node_data[''type''] == ''metric'':
            mermaid += f"    style {node_id} fill:#2196F3,color:#fff\n"  # Blue for metrics
        else:
            mermaid += f"    style {node_id} fill:#9E9E9E,color:#fff\n"  # Gray for tables
    
    mermaid += "```\n"
    
    report = f"""
 Dependency Diagram for: {metric[''name'']}
{''='' * 60}

{mermaid}

 How to use:
1. Copy the Mermaid diagram above
2. Paste into:
   - GitHub README.md or issues
   - Notion pages
   - Confluence
   - VS Code with Mermaid preview
   - Any markdown renderer with Mermaid support

 Legend:
   Green = Target metric
   Blue = Dependent metrics
   Gray = Tables/Data sources

 Depth: {depth} levels | Nodes: {len(nodes)} | Edges: {len(edges)}
"""
    
    return report



@mcp.prompt()
def metric_definition_guide() -> str:
    """
    Guide for defining high-quality metrics.
    
    Returns best practices and examples for metric definitions.
    """
    return """
# Guide to Defining High-Quality Metrics

## Best Practices

### 1. Clear Naming
âœ… Good: "Active Users", "Revenue per Customer", "Churn Rate"
âŒ Bad: "metric_1", "users_v2", "the_thing"

### 2. Descriptive Explanations
âœ… Good: "Daily unique user logins, counting users who authenticate at least once per 24-hour period"
âŒ Bad: "User count"

### 3. Explicit Calculations
âœ… Good: "COUNT(DISTINCT user_id) WHERE login_date = CURRENT_DATE"
âŒ Bad: "count users today"

### 4. Assign Ownership
Always specify who's responsible: "@data-team", "@analytics", "@product"

### 5. Add Context
- Tags: ["engagement", "daily", "key-metric"]
- Data source: "raw.user_events"
- Dependencies: Related metrics and tables

## Example: Excellent Metric Definition

```
Name: Monthly Recurring Revenue
Description: Sum of all recurring subscription revenue normalized to a monthly amount
Calculation: SUM(CASE 
  WHEN billing_frequency = 'monthly' THEN amount
  WHEN billing_frequency = 'annual' THEN amount / 12
  ELSE 0 END)
FROM subscriptions.active
WHERE status = 'active'
Owner: @revenue-team
Tags: revenue, subscription, monthly, key-metric
Data Source: subscriptions.active
```

## Trust Indicators

Metrics with high trust scores have:
- âœ… 3+ validation tests
- âœ… Clear ownership
- âœ… Complete documentation
- âœ… Regular usage (10+ times)
- âœ… Recent updates (< 30 days)

Use validate_metric() to add tests and increase trust.
"""


def main():
    """
    Main entry point for the Semantic Metrics Modeling Assistant.
    Starts the server with STDIO transport.
    """
    try:
        print("Starting Semantic Metrics Modeling Assistant...", file=sys.stderr)
        print("Ready to help with metrics governance and observability", file=sys.stderr)
        
        # Run the server
        mcp.run()
        
    except Exception as e:
        print(f"Failed to start Semantic Metrics Assistant: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()




