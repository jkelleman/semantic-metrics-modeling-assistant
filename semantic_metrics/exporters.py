"""BI tool export utilities for Looker and Tableau."""
import re
from typing import Dict, Any, Optional


def determine_looker_type(calculation: str) -> str:
    """
    Determine Looker measure type from SQL calculation.
    
    Args:
        calculation: SQL calculation string
        
    Returns:
        Looker measure type (sum, average, count, etc.)
    """
    calc_upper = calculation.upper()
    if 'SUM(' in calc_upper:
        return 'sum'
    elif 'AVG(' in calc_upper or 'AVERAGE(' in calc_upper:
        return 'average'
    elif 'COUNT(DISTINCT' in calc_upper:
        return 'count_distinct'
    elif 'COUNT(' in calc_upper:
        return 'count'
    elif 'MAX(' in calc_upper:
        return 'max'
    elif 'MIN(' in calc_upper:
        return 'min'
    else:
        return 'number'


def convert_to_looker_sql(calculation: str, view_name: str) -> str:
    """
    Convert generic SQL to Looker SQL with ${field} references.
    
    Args:
        calculation: SQL calculation string
        view_name: Looker view name for context
        
    Returns:
        Looker-formatted SQL string
    """
    sql = calculation
    
    # Replace table.column with ${column}
    # e.g., "transactions.amount" -> "${amount}"
    sql = re.sub(r'\b\w+\.(\w+)\b', r'${\1}', sql)
    
    # Remove table references from FROM clause
    sql = re.sub(r'\s+FROM\s+\w+', '', sql, flags=re.IGNORECASE)
    
    # Convert WHERE to Looker filters (simplified)
    # Full implementation would need SQL parser
    if 'WHERE' in sql.upper():
        # Extract WHERE clause for documentation
        where_match = re.search(r'WHERE\s+(.+)', sql, flags=re.IGNORECASE)
        if where_match:
            # Add as comment for now
            sql = sql.replace(where_match.group(0), f'\n    # Filter: {where_match.group(1)}')
    
    return sql.strip()


def convert_to_tableau_formula(calculation: str) -> str:
    """
    Convert SQL calculation to Tableau formula syntax.
    
    Args:
        calculation: SQL calculation string
        
    Returns:
        Tableau-formatted formula string
    """
    formula = calculation
    
    # Replace table.column with [column]
    # e.g., "transactions.amount" -> "[amount]"
    formula = re.sub(r'\b\w+\.(\w+)\b', r'[\1]', formula)
    
    # Remove FROM clauses
    formula = re.sub(r'\s+FROM\s+\w+', '', formula, flags=re.IGNORECASE)
    
    # Remove WHERE clauses (Tableau handles these as filters)
    formula = re.sub(r'\s+WHERE\s+.*$', '', formula, flags=re.IGNORECASE)
    
    return formula.strip()


def determine_tableau_datatype(calculation: str) -> str:
    """
    Determine Tableau data type from calculation.
    
    Args:
        calculation: SQL calculation string
        
    Returns:
        Tableau data type (integer, real, string, etc.)
    """
    calc_upper = calculation.upper()
    if 'COUNT(' in calc_upper:
        return 'integer'
    elif 'SUM(' in calc_upper or 'AVG(' in calc_upper or 'AVERAGE(' in calc_upper:
        return 'real'
    elif 'MAX(' in calc_upper or 'MIN(' in calc_upper:
        return 'real'
    else:
        return 'string'


def generate_lookml(
    metric: Dict[str, Any],
    view_name: str,
    explore: Optional[str] = None
) -> str:
    """
    Generate complete LookML for a metric.
    
    Args:
        metric: Metric dictionary from database
        view_name: Looker view name to attach measure to
        explore: Optional explore name for context
        
    Returns:
        Complete LookML string
    """
    measure_type = determine_looker_type(metric['calculation'])
    looker_sql = convert_to_looker_sql(metric['calculation'], view_name)
    
    # Build LookML
    lookml = f"""view: {view_name} {{
  measure: {metric['id']} {{
    label: "{metric['name']}"
    description: "{metric.get('description', '')}"
    type: {measure_type}
    sql: {looker_sql} ;;
"""
    
    # Add tags as metadata
    if metric.get('tags'):
        tags_str = ', '.join(f'"{tag}"' for tag in metric['tags'])
        lookml += f"    tags: [{tags_str}]\n"
    
    # Add owner as comment
    if metric.get('owner'):
        lookml += f"    # Owner: {metric['owner']}\n"
    
    # Add trust score as comment
    if metric.get('trust_score') is not None:
        lookml += f"    # Trust Score: {metric['trust_score']:.1f}%\n"
    
    # Add dependencies as comment
    if metric.get('dependencies'):
        deps_str = ', '.join(metric['dependencies'])
        lookml += f"    # Dependencies: {deps_str}\n"
    
    lookml += "  }\n}\n"
    
    # Add explore context if provided
    if explore:
        lookml += f"\n# Use in explore: {explore}\n"
    
    return lookml


def generate_tds(metric: Dict[str, Any], connection: str) -> str:
    """
    Generate complete TDS XML for a metric.
    
    Args:
        metric: Metric dictionary from database
        connection: Tableau connection name
        
    Returns:
        Complete TDS XML string
    """
    tableau_formula = convert_to_tableau_formula(metric['calculation'])
    datatype = determine_tableau_datatype(metric['calculation'])
    
    # Build TDS XML
    tds = f"""<?xml version='1.0' encoding='utf-8' ?>
<datasource>
  <connection class='federated'>
    <named-connections>
      <named-connection name='{connection}' />
    </named-connections>
  </connection>
  
  <column name='{metric['id']}' datatype='{datatype}' role='measure'>
    <calculation class='tableau' formula='{tableau_formula}' />
    <desc>{metric.get('description', '')}</desc>
    <aliases>
      <alias key='{metric['name']}' value='{metric['id']}' />
    </aliases>
"""
    
    # Add metadata as XML comments
    if metric.get('tags'):
        tags_str = ', '.join(metric['tags'])
        tds += f"    <!-- Tags: {tags_str} -->\n"
    
    if metric.get('owner'):
        tds += f"    <!-- Owner: {metric['owner']} -->\n"
    
    if metric.get('trust_score') is not None:
        tds += f"    <!-- Trust Score: {metric['trust_score']:.1f}% -->\n"
    
    if metric.get('dependencies'):
        deps_str = ', '.join(metric['dependencies'])
        tds += f"    <!-- Dependencies: {deps_str} -->\n"
    
    tds += "  </column>\n</datasource>\n"
    
    return tds


def export_to_power_bi(metric: Dict[str, Any]) -> str:
    """
    Generate DAX formula for Power BI (future enhancement).
    
    Args:
        metric: Metric dictionary from database
        
    Returns:
        DAX formula string
    """
    # Placeholder for future Power BI support
    # Would convert SQL to DAX syntax
    return f"-- Power BI export not yet implemented\n-- Metric: {metric['name']}\n-- Calculation: {metric['calculation']}"
