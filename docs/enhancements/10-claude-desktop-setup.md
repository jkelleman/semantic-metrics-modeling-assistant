# Enhancement 10: Claude Desktop Setup Guide

**Status:** 📝 Documented  
**Priority:** Medium (Tier 2 - Integration)  
**Target Date:** January 2026

---

## Overview

Comprehensive guide for connecting the semantic metrics assistant to Claude Desktop, enabling conversational metric management through AI chat interface.

## Setup Guide Structure

### 1. Platform-Specific Instructions

#### Windows
```json
// %APPDATA%\Claude\claude_desktop_config.json
{
  "mcpServers": {
    "semantic-metrics": {
      "command": "python",
      "args": [
        "-m",
        "semantic_metrics.server"
      ],
      "env": {
        "METRICS_DB": "C:\\Users\\YourName\\metrics.db"
      }
    }
  }
}
```

#### macOS
```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "semantic-metrics": {
      "command": "python3",
      "args": [
        "-m",
        "semantic_metrics.server"
      ],
      "env": {
        "METRICS_DB": "/Users/yourname/metrics.db"
      }
    }
  }
}
```

#### Linux
```json
// ~/.config/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "semantic-metrics": {
      "command": "python3",
      "args": [
        "-m",
        "semantic_metrics.server"
      ],
      "env": {
        "METRICS_DB": "/home/yourname/metrics.db"
      }
    }
  }
}
```

### 2. Step-by-Step Setup

1. **Install Claude Desktop**
   - Download from https://claude.ai/download
   - Install and sign in

2. **Install Semantic Metrics**
   ```bash
   pip install semantic-metrics
   ```

3. **Find Config File Location**
   - Windows: Open `%APPDATA%\Claude`
   - Mac: Open `~/Library/Application Support/Claude`
   - Linux: Open `~/.config/Claude`

4. **Edit claude_desktop_config.json**
   - Copy platform-specific config above
   - Update paths to match your system
   - Save file

5. **Restart Claude Desktop**
   - Quit completely
   - Relaunch

6. **Verify Connection**
   - Open Claude Desktop
   - Type: "List all metrics"
   - Should see MCP tool response

### 3. Usage Examples

**Define a metric conversationally:**
```
User: "Define a metric called Active Users that counts distinct user IDs who logged in the last 30 days from the users table"

Claude: [Uses define_metric tool]
✅ Created metric: Active Users
Trust Score: 45/100
📝 Recommendations:
  - Add validation tests
  - Assign an owner
```

**Check trust score:**
```
User: "What's the trust score for Active Users?"

Claude: [Uses calculate_trust_score_enhanced_tool]
📊 Enhanced Trust Score: 🟡 65/100 →
...detailed breakdown...
```

**Export to Looker:**
```
User: "Export Active Users to Looker for the users view"

Claude: [Uses export_to_looker]
✅ Here's the LookML...
[Copy-paste ready output]
```

### 4. Troubleshooting

**Problem:** "MCP server not connecting"
- ✅ Check Python path is correct (`which python` or `where python`)
- ✅ Verify semantic-metrics is installed (`pip list | grep semantic`)
- ✅ Check JSON syntax in config file (use JSON validator)
- ✅ Look at Claude Desktop logs

**Problem:** "Permission denied"
- ✅ Ensure database path is writable
- ✅ Run `chmod 755` on database directory (Mac/Linux)

**Problem:** "Module not found"
- ✅ Use full path to Python: `/usr/bin/python3`
- ✅ Or activate virtual environment in config

### 5. Advanced Configuration

**Use virtual environment:**
```json
{
  "mcpServers": {
    "semantic-metrics": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "semantic_metrics.server"]
    }
  }
}
```

**Custom database location:**
```json
{
  "env": {
    "METRICS_DB": "/shared/team/metrics.db"
  }
}
```

**Enable debug logging:**
```json
{
  "env": {
    "METRICS_DB": "metrics.db",
    "LOG_LEVEL": "DEBUG"
  }
}
```

### 6. Test Scenarios

**Test 1: Basic Connection**
```
In Claude: "Are there any metrics defined?"
Expected: List of metrics or "No metrics found"
```

**Test 2: Create Metric**
```
In Claude: "Define a test metric"
Expected: Metric created with ID and trust score
```

**Test 3: Trust Score**
```
In Claude: "Calculate trust score for [metric name]"
Expected: Detailed score breakdown
```

**Test 4: Export**
```
In Claude: "Export [metric name] to Looker"
Expected: LookML syntax output
```

## Benefits

✅ **Conversational UX** - Define metrics in natural language  
✅ **AI-Assisted** - Claude helps write calculations  
✅ **Iterative Refinement** - "Actually, change the owner to..."  
✅ **Context Aware** - Claude understands your metric ecosystem  
✅ **Faster** - No switching between tools  

## Video Walkthrough (Future)

- [ ] Record 5-minute setup video
- [ ] Add to README and docs site
- [ ] Show common workflows

---

*Last updated: January 3, 2026*
