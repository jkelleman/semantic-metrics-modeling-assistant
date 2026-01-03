# Enhancement 07: dbt Cloud API Integration

**Status:** 📝 Documented  
**Priority:** Medium (Tier 2 - Integration)  
**Target Date:** January 2026

---

## Overview

Integrate with dbt Cloud REST API to fetch existing metric definitions, enabling bidirectional sync and eliminating manual re-entry of metrics already defined in dbt.

## Implementation Plan

### New MCP Tool: `sync_from_dbt_cloud`

```python
@mcp.tool()
def sync_from_dbt_cloud(
    api_token: str,
    account_id: str,
    project_id: str,
    sync_mode: str = "import"
) -> str:
    """
    Sync metrics with dbt Cloud.
    
    Args:
        api_token: dbt Cloud API token
        account_id: dbt Cloud account ID
        project_id: dbt Cloud project ID
        sync_mode: "import" (fetch from dbt), "export" (push to dbt), or "bidirectional"
        
    Returns:
        Sync report with imported/exported metrics
    """
```

### Features

- **Import from dbt Cloud** - Fetch all metric definitions
- **Export to dbt Cloud** - Push new metrics back
- **Conflict Detection** - Handle metrics defined in both places
- **Merge Strategies** - Choose dbt-wins, assistant-wins, or manual merge
- **Incremental Sync** - Only sync changes since last run
- **Audit Trail** - Log all sync operations

### dbt Cloud API Endpoints

```python
# Get metrics from dbt Cloud
GET https://cloud.getdbt.com/api/v2/accounts/{account_id}/projects/{project_id}/metrics

# Create/update metric
POST https://cloud.getdbt.com/api/v2/accounts/{account_id}/projects/{project_id}/metrics
```

## Usage Example

```python
# Import metrics from dbt Cloud
sync_from_dbt_cloud(
    api_token="dbt_abc123...",
    account_id="12345",
    project_id="67890",
    sync_mode="import"
)

# Output:
✅ Synced 42 metrics from dbt Cloud
📊 Trust scores calculated for all imported metrics
⚠️ 3 conflicts detected (use merge tool to resolve)
```

## Benefits

✅ **Don't Rebuild** - Import 100+ existing metrics instantly  
✅ **Single Source of Truth** - dbt remains authoritative  
✅ **Continuous Sync** - Keep definitions in sync  
✅ **ROI** - Leverage existing dbt investment  

---

*Last updated: January 3, 2026*
