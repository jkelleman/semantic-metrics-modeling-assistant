# Next Steps

##  Priority Tasks

### 1. Complete Database Implementation (HIGH PRIORITY)
**Status:** Minimal version working, needs full CRUD operations

**Current State:**
-  Basic database.py with create_metric() and get_metric()
-  Imports successfully
-  Missing methods needed for tests

**What to Implement:**

```python
# semantic_metrics/database.py

def update_metric(self, metric_id: str, updates: Dict) -> None:
    """Update existing metric and record in history."""
    # Update metrics table
    # Insert into metric_history table
    
def delete_metric(self, metric_id: str) -> None:
    """Delete a metric."""
    # DELETE FROM metrics WHERE id = ?
    
def get_all_metrics(self) -> List[Dict]:
    """Get all metrics."""
    # SELECT * FROM metrics
    
def search_metrics(self, query: str) -> List[Dict]:
    """Search metrics by name or description."""
    # SELECT * WHERE name LIKE ? OR description LIKE ?
    
def get_metrics_by_owner(self, owner: str) -> List[Dict]:
    """Get metrics by owner."""
    # SELECT * WHERE owner = ?
    
def get_metrics_by_tag(self, tag: str) -> List[Dict]:
    """Get metrics with specific tag."""
    # Parse JSON tags column
    
def record_usage(self, metric_id: str) -> None:
    """Record metric usage in metric_usage table."""
    # INSERT INTO metric_usage
    
def get_metric_history(self, metric_id: str) -> List[Dict]:
    """Get change history for a metric."""
    # SELECT * FROM metric_history WHERE metric_id = ?
    
def add_validation_test(self, metric_id: str, test: Dict) -> None:
    """Add validation test to validation_tests table."""
    # INSERT INTO validation_tests
    
def record_trust_score(self, metric_id: str, score: float, breakdown: Dict) -> None:
    """Record trust score in trust_score_history table."""
    # INSERT INTO trust_score_history
    
def get_trust_score_history(self, metric_id: str, from_date: str) -> List[Dict]:
    """Get trust score history."""
    # SELECT * FROM trust_score_history
```

**Estimated Time:** 3-4 hours

**Test After:**
```bash
pytest tests/test_database.py -v
```

---

### 2. Run Full Test Suite (AFTER #1)
**Goal:** Get all 35+ tests passing

```bash
# Should pass after implementing database methods
pytest tests/ -v

# Current status: Some tests pass, many need full database implementation
```

---

### 3. Implement Missing Trust Scoring Features
**File:** `semantic_metrics/trust_scoring.py`

**Current:** File exists but may need enhancements
**Check:** Does it have all the weighted algorithm features?

```python
# Verify these are implemented:
- calculate_trust_score_enhanced()
- check_freshness() 
- check_test_coverage()
- check_usage()
- check_documentation()
- check_ownership()
- calculate_trend()
- generate_sparkline()
- get_recommendations()
```

---

### 4. Implement Missing Exporters Features
**File:** `semantic_metrics/exporters.py`

**Current:** File exists
**Verify:** Looker LookML and Tableau TDS export working

```bash
# Test exports
python -c "from semantic_metrics.exporters import generate_lookml, generate_tds; print('OK')"
```

---

### 5. Run MCP Server (AFTER tests pass)

```bash
python -m semantic_metrics.server
```

**Expected:** Server starts and provides 13 MCP tools

---

##  Optional Enhancements (From Enhancement Docs)

### Task 6: Comprehensive Documentation
**Files to create:**
- `docs/API.md` - Complete function reference
- `docs/ARCHITECTURE.md` - System design
- Enhanced `examples/USAGE.md`

**Time:** 2-3 hours

### Task 7: dbt Cloud API Integration
**New tool:** `sync_from_dbt_cloud()`
**See:** `docs/enhancements/07-dbt-cloud-api.md`

### Task 8: Git Integration
**Features:** YAML storage, auto-commits, rollback
**See:** `docs/enhancements/08-git-integration.md`

### Task 9: PyPI Packaging
**Goal:** Make installable with `pip install semantic-metrics`
**See:** `docs/enhancements/09-packaging.md`

### Task 10: Claude Desktop Setup Guide
**Finalize:** Platform-specific instructions
**See:** `docs/enhancements/10-claude-desktop-setup.md`

---

##  Quick Wins

1. **Fix Achievement Badge Branch**
   ```bash
   git branch -d achievement-badges  # Merged already
   ```

2. **Set Git Identity**
   ```bash
   git config --global user.name "Jen Kelleman"
   git config --global user.email "jenkelleman@microsoft.com"
   ```

3. **Update README Badges**
   - Add "Tests: Passing" badge when tests work
   - Update status from "In Progress" to "Production Ready"

---

##  Immediate Action Plan

**Day 1 (4 hours):**
1.  Implement all missing database methods (3 hours)
2.  Run test suite and fix any issues (1 hour)

**Day 2 (2 hours):**
3.  Test MCP server with all tools
4.  Update README with final status

**Day 3 (optional - 4 hours):**
5. Create API documentation (Task 6)
6. Package for easy installation (Task 9)

---

##  Reference

- **Enhancement Docs:** `docs/enhancements/01-10-*.md`
- **Current Tests:** `tests/test_database.py`, `tests/test_trust_scoring.py`
- **Implementation Summary:** `IMPLEMENTATION_SUMMARY.md`
- **Progress Tracking:** `PROGRESS.md`

---

**Last Updated:** January 3, 2026  
**Status:** Database partially implemented, needs full CRUD operations  
**Priority:** Complete database.py to unlock all functionality
