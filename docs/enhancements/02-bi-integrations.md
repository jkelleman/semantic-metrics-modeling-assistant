# Enhancement 02: BI Tool Integrations (Looker & Tableau)

**Status:** 🔄 In Progress  
**Priority:** High (Tier 2 - Integration)  
**Target Date:** January 2026

---

## Overview

Add export capabilities to integrate metrics with popular BI tools. Users can define metrics once in the assistant and seamlessly export to Looker (LookML) and Tableau (TDS files).

## Problem Solved

**Before:** Analysts define metrics in the assistant, then manually recreate them in Looker/Tableau (error-prone, time-consuming, inconsistent definitions).

**After:** Click export, paste into BI tool. Same metric definition everywhere = single source of truth.

## Implementation Plan

### New MCP Tools

#### 1. `export_to_looker`

**Purpose:** Generate LookML syntax for Looker

**Input:**
```json
{
  "metric_id": "revenue_total",
  "view_name": "transactions",
  "explore": "sales"
}
```

**Output:**
```yaml
# LookML for revenue_total
view: transactions {
  measure: revenue_total {
    label: "Total Revenue"
    description: "Sum of all completed transactions"
    type: sum
    sql: ${amount} ;;
    filters: [status: "completed"]
    
    value_format_name: usd
    drill_fields: [transaction_id, customer_id, amount, created_at]
  }
}
```

**Implementation:**
```python
@mcp.tool()
def export_to_looker(metric_id: str, view_name: str, explore: str = None) -> str:
    """
    Export a metric to LookML format for Looker.
    
    Args:
        metric_id: ID of the metric to export
        view_name: Looker view name to attach the measure to
        explore: Optional explore name for context
        
    Returns:
        LookML formatted string ready to paste into Looker
    """
    db = MetricsDatabase()
    metric = db.get_metric(metric_id)
    
    if not metric:
        return f"Error: Metric '{metric_id}' not found"
    
    # Parse calculation to extract aggregation type
    calc = metric['calculation'].upper()
    measure_type = _determine_looker_type(calc)
    
    # Build LookML
    lookml = f"""view: {view_name} {{
  measure: {metric_id} {{
    label: "{metric['name']}"
    description: "{metric['description']}"
    type: {measure_type}
    sql: {_convert_to_looker_sql(metric['calculation'], view_name)} ;;
"""
    
    # Add tags as hidden field
    if metric.get('tags'):
        lookml += f"    tags: [{', '.join(f'"{tag}"' for tag in metric['tags'])}]\n"
    
    # Add owner as metadata
    if metric.get('owner'):
        lookml += f"    # Owner: {metric['owner']}\n"
    
    # Add trust score as metadata
    lookml += f"    # Trust Score: {metric.get('trust_score', 0):.1f}%\n"
    
    lookml += "  }\n}\n"
    
    db.close()
    return lookml
```

#### 2. `export_to_tableau`

**Purpose:** Generate TDS (Tableau Data Source) XML for Tableau

**Input:**
```json
{
  "metric_id": "revenue_total",
  "connection": "snowflake_prod"
}
```

**Output:**
```xml
<?xml version='1.0' encoding='utf-8' ?>
<datasource>
  <connection class='federated'>
    <named-connections>
      <named-connection name='snowflake_prod' />
    </named-connections>
  </connection>
  
  <column name='revenue_total' datatype='real' role='measure'>
    <calculation class='tableau' formula='SUM([amount])' />
    <desc>Sum of all completed transactions</desc>
    <aliases>
      <alias key='Total Revenue' value='revenue_total' />
    </aliases>
  </column>
</datasource>
```

**Implementation:**
```python
@mcp.tool()
def export_to_tableau(metric_id: str, connection: str) -> str:
    """
    Export a metric to Tableau TDS format.
    
    Args:
        metric_id: ID of the metric to export
        connection: Tableau connection name
        
    Returns:
        TDS XML string ready to import into Tableau
    """
    db = MetricsDatabase()
    metric = db.get_metric(metric_id)
    
    if not metric:
        return f"Error: Metric '{metric_id}' not found"
    
    # Convert calculation to Tableau formula syntax
    tableau_formula = _convert_to_tableau_formula(metric['calculation'])
    
    # Determine data type
    datatype = _determine_tableau_datatype(metric['calculation'])
    
    # Build TDS XML
    tds = f"""<?xml version='1.0' encoding='utf-8' ?>
<datasource>
  <connection class='federated'>
    <named-connections>
      <named-connection name='{connection}' />
    </named-connections>
  </connection>
  
  <column name='{metric_id}' datatype='{datatype}' role='measure'>
    <calculation class='tableau' formula='{tableau_formula}' />
    <desc>{metric['description']}</desc>
    <aliases>
      <alias key='{metric['name']}' value='{metric_id}' />
    </aliases>
"""
    
    # Add tags as metadata
    if metric.get('tags'):
        tds += f"    <!-- Tags: {', '.join(metric['tags'])} -->\n"
    
    # Add owner
    if metric.get('owner'):
        tds += f"    <!-- Owner: {metric['owner']} -->\n"
    
    tds += "  </column>\n</datasource>\n"
    
    db.close()
    return tds
```

### Helper Functions

```python
def _determine_looker_type(calculation: str) -> str:
    """Determine Looker measure type from calculation."""
    calc_upper = calculation.upper()
    if 'SUM(' in calc_upper:
        return 'sum'
    elif 'AVG(' in calc_upper or 'AVERAGE(' in calc_upper:
        return 'average'
    elif 'COUNT(' in calc_upper:
        return 'count'
    elif 'COUNT(DISTINCT' in calc_upper:
        return 'count_distinct'
    elif 'MAX(' in calc_upper:
        return 'max'
    elif 'MIN(' in calc_upper:
        return 'min'
    else:
        return 'number'

def _convert_to_looker_sql(calculation: str, view_name: str) -> str:
    """Convert generic SQL to Looker SQL with ${field} references."""
    # Replace table.column with ${column}
    import re
    sql = calculation
    
    # Extract columns and convert to Looker references
    # e.g., "transactions.amount" -> "${amount}"
    sql = re.sub(r'\b\w+\.(\w+)\b', r'${\1}', sql)
    
    # Extract WHERE conditions as filters
    # This is simplified - real implementation would need full SQL parsing
    return sql

def _convert_to_tableau_formula(calculation: str) -> str:
    """Convert SQL calculation to Tableau formula syntax."""
    # Tableau uses [field] instead of table.column
    import re
    formula = calculation
    
    # Replace table.column with [column]
    formula = re.sub(r'\b\w+\.(\w+)\b', r'[\1]', formula)
    
    # Convert SQL functions to Tableau functions
    formula = formula.replace('AVG(', 'AVG([').replace(')', '])')
    
    # Remove WHERE clauses (Tableau handles these as filters)
    formula = re.sub(r'\s+WHERE\s+.*$', '', formula, flags=re.IGNORECASE)
    
    return formula

def _determine_tableau_datatype(calculation: str) -> str:
    """Determine Tableau data type from calculation."""
    calc_upper = calculation.upper()
    if 'COUNT(' in calc_upper:
        return 'integer'
    elif 'SUM(' in calc_upper or 'AVG(' in calc_upper:
        return 'real'
    elif 'MAX(' in calc_upper or 'MIN(' in calc_upper:
        return 'real'
    else:
        return 'string'
```

## Files to Modify

### 1. `semantic_metrics/server.py`

Add new tools after existing tools:

```python
from semantic_metrics.database import MetricsDatabase

# ... existing tools ...

@mcp.tool()
def export_to_looker(metric_id: str, view_name: str, explore: str = None) -> str:
    # Implementation above
    pass

@mcp.tool()
def export_to_tableau(metric_id: str, connection: str) -> str:
    # Implementation above
    pass
```

### 2. New File: `semantic_metrics/exporters.py`

Extract helper functions to separate module:

```python
"""BI tool export utilities."""
import re
from typing import Dict, Any

def determine_looker_type(calculation: str) -> str:
    """Determine Looker measure type from calculation."""
    # Implementation

def convert_to_looker_sql(calculation: str, view_name: str) -> str:
    """Convert generic SQL to Looker SQL with ${field} references."""
    # Implementation

def convert_to_tableau_formula(calculation: str) -> str:
    """Convert SQL calculation to Tableau formula syntax."""
    # Implementation

def determine_tableau_datatype(calculation: str) -> str:
    """Determine Tableau data type from calculation."""
    # Implementation

def generate_lookml(metric: Dict[str, Any], view_name: str, explore: str = None) -> str:
    """Generate complete LookML for a metric."""
    # Implementation

def generate_tds(metric: Dict[str, Any], connection: str) -> str:
    """Generate complete TDS XML for a metric."""
    # Implementation
```

## Usage Examples

### Looker Export

```python
# Claude Desktop conversation:
User: "Export the revenue_total metric to Looker for the transactions view"

Assistant uses export_to_looker:
{
  "metric_id": "revenue_total",
  "view_name": "transactions",
  "explore": "sales"
}

Returns LookML that user copies into Looker IDE
```

### Tableau Export

```python
# Claude Desktop conversation:
User: "Export churn_rate metric to Tableau using our Snowflake connection"

Assistant uses export_to_tableau:
{
  "metric_id": "churn_rate",
  "connection": "snowflake_prod"
}

Returns TDS XML that user saves and imports into Tableau
```

## Testing Plan

### Unit Tests

```python
def test_determine_looker_type():
    assert determine_looker_type("SUM(amount)") == "sum"
    assert determine_looker_type("COUNT(DISTINCT user_id)") == "count_distinct"
    assert determine_looker_type("AVG(price)") == "average"

def test_convert_to_looker_sql():
    sql = "transactions.amount"
    assert convert_to_looker_sql(sql, "transactions") == "${amount}"

def test_export_to_looker_basic():
    # Create test metric
    db = MetricsDatabase(":memory:")
    db.create_metric({
        "id": "test_metric",
        "name": "Test Metric",
        "description": "Test",
        "calculation": "SUM(transactions.amount)"
    })
    
    # Export
    lookml = export_to_looker("test_metric", "transactions")
    
    # Verify LookML structure
    assert "measure: test_metric" in lookml
    assert "type: sum" in lookml
    assert 'label: "Test Metric"' in lookml
```

### Integration Tests

```python
def test_full_looker_workflow():
    """Test complete workflow: define metric -> export to Looker"""
    # Define metric
    metric_data = {...}
    metric_id = create_metric(metric_data)
    
    # Export
    lookml = export_to_looker(metric_id, "transactions", "sales")
    
    # Verify valid LookML (could use Looker SDK to validate)
    assert "view:" in lookml
    assert "measure:" in lookml
```

## Benefits

✅ **Seamless Integration** - Metrics flow into analysts' existing tools  
✅ **Single Source of Truth** - Same definition across all platforms  
✅ **Reduced Errors** - No manual re-entry or translation  
✅ **Faster Adoption** - Don't force teams to change their workflow  
✅ **Bi-directional Potential** - Future: sync back from BI tools  

## Limitations & Future Work

⚠️ **Current Limitations:**
- Simple SQL parsing (may not handle complex queries)
- No Looker SDK integration (manual paste required)
- No Tableau SDK integration (manual import required)
- Doesn't handle metric dependencies (composite metrics)

🚀 **Future Enhancements:**
- Auto-publish to Looker via API
- Auto-publish to Tableau via REST API
- Support for Power BI (DAX export)
- Support for Sigma (SQL export)
- Validation of exported metrics
- Reverse import from BI tools

## Related Files

- [server.py](../../semantic_metrics/server.py) - Main MCP server (needs tool additions)
- [database.py](../../semantic_metrics/database.py) - Database access for metric retrieval
- [ENHANCEMENT_RATIONALE.md](../../ENHANCEMENT_RATIONALE.md) - Why BI integrations matter

---

*Last updated: January 3, 2026*
