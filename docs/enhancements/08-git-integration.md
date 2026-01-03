# Enhancement 08: Git Integration for Version Control

**Status:** 📝 Documented  
**Priority:** Medium (Tier 3 - Polish)  
**Target Date:** January 2026

---

## Overview

Store metrics as YAML files in a Git repository with automatic commits, enabling version control, code review workflows, and rollback capabilities.

## Implementation Plan

### Storage Format

Store each metric as a YAML file:

```yaml
# metrics/revenue_total.yaml
id: revenue_total
name: Total Revenue
description: Sum of all completed transactions
calculation: SUM(amount) FROM transactions WHERE status='completed'
owner: "@revenue-team"
tags:
  - revenue
  - financial
  - key-metric
data_source: transactions
dependencies:
  - transactions.amount
metadata:
  created_at: 2026-01-03T10:00:00Z
  updated_at: 2026-01-03T15:30:00Z
  trust_score: 85.0
```

### New MCP Tools

#### 1. `init_git_repo`
```python
@mcp.tool()
def init_git_repo(repo_path: str, remote_url: str = "") -> str:
    """Initialize Git repository for metrics storage."""
```

#### 2. `commit_metric_changes`
```python
@mcp.tool()
def commit_metric_changes(metric_id: str, message: str = "") -> str:
    """Commit metric changes to Git with automatic message."""
```

#### 3. `view_metric_history`
```python
@mcp.tool()
def view_metric_history(metric_id: str, limit: int = 10) -> str:
    """Show Git history for a metric."""
```

#### 4. `rollback_metric`
```python
@mcp.tool()
def rollback_metric(metric_id: str, commit_hash: str) -> str:
    """Rollback metric to a previous version."""
```

### Features

- **Automatic Commits** - Every metric change creates a Git commit
- **Meaningful Messages** - Auto-generated commit messages: "Update revenue_total: Changed owner from @team-a to @team-b"
- **Branch Support** - Create feature branches for metric changes
- **PR Workflow** - Metrics go through code review
- **Git Blame** - See who changed what and when
- **Rollback** - Undo bad changes easily
- **Remote Sync** - Push to GitHub/GitLab/Bitbucket

### Git Workflow

```bash
# User updates metric via MCP tool
update_metric("revenue_total", {"owner": "@new-team"})

# Automatic Git operations:
# 1. Update metrics/revenue_total.yaml
# 2. git add metrics/revenue_total.yaml
# 3. git commit -m "Update revenue_total: Changed owner"
# 4. Optionally: git push origin main
```

## Benefits

✅ **Full Version History** - See all changes with git log  
✅ **Code Review** - PR workflow for governance  
✅ **Rollback** - Undo mistakes easily  
✅ **Audit Trail** - Compliance-ready history  
✅ **Collaboration** - Use Git workflows teams know  
✅ **Diff Visualization** - Rich diffs in GitHub/GitLab  

---

*Last updated: January 3, 2026*
