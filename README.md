# Semantic Metrics Modeling Assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io)
[![FastMCP](https://img.shields.io/badge/FastMCP-latest-orange.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-35%2B%20passing-success.svg)](https://github.com/jkelleman/semantic-metrics-modeling-assistant)

**A production-ready MCP agent that helps data teams define, validate, and visualize semantic metrics with enterprise-grade persistence, trust scoring, and BI integrations.**

---

## Overview

The Semantic Metrics Modeling Assistant is a Model Context Protocol (MCP) agent designed to reduce cognitive load for data teams working with semantic layers. It provides a conversational interface for defining metrics, visual feedback on lineage and dependencies, and sophisticated trust indicators with persistent storage that help teams build confidence in their data.

## Key Features

### 🗄️ Enterprise Data Persistence
- **SQLite Database** - Persistent storage with full audit trails
- **5-Table Schema** - Metrics, history, tests, usage, and trust scores
- **Change Tracking** - Complete history of all metric modifications
- **Version Control Ready** - Designed for Git integration and rollback

### 💬 Conversational Metric Definition
Define metrics naturally through conversation:
```
"Define 'Active Users' as daily unique logins"
"Create a metric for revenue per customer"
"What's the definition of our churn rate metric?"
```

### 📊 BI Tool Integrations
Export metrics to industry-standard platforms:
- **Looker (LookML)** - Generate production-ready LookML files
- **Tableau (TDS)** - Export as Tableau Data Source XML
- **dbt** - Create dbt metric YAML definitions

### 🎯 Enhanced Trust Scoring
Sophisticated quality assessment with weighted algorithms:
- **Tests** (35% weight) - Validation test coverage and pass rates
- **Usage** (20% weight) - Adoption across teams and dashboards
- **Freshness** (15% weight) - Data staleness with time-decay
- **Documentation** (15% weight) - Completeness and clarity
- **Ownership** (15% weight) - Clear accountability
- **Trend Analysis** - Track quality changes over time with sparklines

### 🎨 Visual Lineage & Dependencies
Modern visualization options for understanding metric relationships:
- **Mermaid Diagrams** - Beautiful flowcharts for GitHub/Notion/Confluence
- **ASCII Trees** - Terminal-friendly dependency visualization
- **Impact Analysis** - Understand downstream effects before changes
- **Circular Dependency Detection** - Identify and resolve conflicts

### ✅ Comprehensive Testing
Production-ready test coverage:
- **35+ Tests** - Database, trust scoring, exporters, and tools
- **pytest Framework** - Industry-standard testing with fixtures
- **90%+ Coverage** - Core functionality thoroughly validated
- **CI/CD Ready** - Automated testing for continuous integration

## Why This Matters

### The Problem
Data teams face systemic challenges:
- **Metric proliferation** - Multiple conflicting definitions for core business metrics
- **Trust deficits** - Lack of quality signals leads to metric shopping and inconsistent reporting
- **Cognitive overhead** - Complex dependency chains and lineage are difficult to reason about
- **Governance fragmentation** - Ownership and validation processes are ad-hoc or non-existent

### The Solution
This assistant addresses these challenges through:
- **Abstraction layers** - Natural language interface abstracts YAML configuration complexity
- **Transparency mechanisms** - Multi-dimensional trust scores make quality visible
- **Governance automation** - Built-in prompts for ownership, testing, and documentation
- **Observability instrumentation** - Usage tracking and freshness monitoring

## Architecture

```
┌─────────────────────────────────────────┐
│  Conversational Interface (MCP Tools)   │
├─────────────────────────────────────────┤
│  • define_metric()                      │
│  • validate_metric()                    │
│  • visualize_lineage()                  │
│  • check_trust_score()                  │
│  • search_metrics()                     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Metric Repository                      │
├─────────────────────────────────────────┤
│  • Stores metric definitions            │
│  • Tracks lineage and dependencies      │
│  • Collects usage and quality metadata  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Data Source Integrations               │
├─────────────────────────────────────────┤
│  • dbt project files                    │
│  • LookML models                        │
│  • YAML metric specs                    │
│  • SQL queries                          │
└─────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/jkelleman/semantic-metrics-modeling-assistant.git
cd semantic-metrics-modeling-assistant

# Install dependencies
pip install -e .

# Run the MCP server
python -m semantic_metrics.server

# Or run tests
pytest tests/
```

### Database Setup

The agent automatically creates a SQLite database (`metrics.db`) on first run with:
- Metrics definitions table
- Change history tracking
- Validation test results
- Usage statistics
- Trust score evolution

### Usage Examples

**Define a new metric:**
```python
define_metric(
    name="Active Users",
    description="Daily unique user logins",
    calculation="COUNT(DISTINCT user_id) WHERE login_date = CURRENT_DATE",
    owner="@data-team",
    tags=["engagement", "daily"]
)
```

**Check enhanced trust score:**
```python
check_trust_score("Active Users")

# Returns:
# Trust Score: 87/100 ↗️
# Tests: 4 passing (35/35 points) ✅
# Usage: 12 dashboards, 8 users (18/20 points)
# Freshness: Updated 2 hours ago (14/15 points)
# Documentation: Complete with examples (15/15 points)
# Ownership: @data-team (15/15 points)
#
# Trend: ▂▄▆█ (improving over 30 days)
# Recommendations: Add integration tests for edge cases
```

**Visualize lineage:**
```python
visualize_lineage("Revenue per Customer")

# Returns ASCII tree:
# Revenue per Customer
#   ├── Total Revenue
#   │   ├── Order Amount (raw.orders)
#   │   └── Refunds (raw.refunds)
#   └── Customer Count
#       └── Unique Customers (raw.users)
```

**Generate Mermaid diagram:**
```python
generate_mermaid_diagram("Revenue per Customer")

# Returns:
# ```mermaid
# flowchart TD
#     A[Revenue per Customer] --> B[Total Revenue]
#     A --> C[Customer Count]
#     B --> D[Order Amount]
#     B --> E[Refunds]
#     C --> F[Unique Customers]
# ```
```

**Export to BI tools:**
```python
# Export to Looker
export_to_looker("Active Users")
# Generates: active_users.lkml

# Export to Tableau
export_to_tableau("Active Users")
# Generates: active_users.tds (XML)

# Export to dbt
export_to_dbt("Active Users")
# Generates: active_users.yml
```

## Design Principles

### 1. Conversational First
Abstract complex YAML configurations through natural language interfaces. Reduce the learning curve by prioritizing conversational interaction over syntax memorization.

### 2. Show, Don't Tell
Prioritize visual representations over text descriptions. Render lineage as directed acyclic graphs (DAGs) to make dependency relationships immediately parseable.

### 3. Trust Through Transparency
Expose quality indicators as first-class attributes. Multi-dimensional trust scores provide actionable signals about metric reliability.

### 4. Progressive Disclosure
Implement information hierarchy that surfaces high-level summaries by default while maintaining drill-down access to detailed metadata.

### 5. Governance by Default
Design interfaces that make governance the path of least resistance. Use prompts, validation, and required fields to enforce best practices without adding friction.

## Use Cases

### Data Team Member
"I need to create a metric for customer lifetime value that everyone can trust."

**Assistant helps:**
- Define the metric in plain language
- Validate SQL logic
- Check for similar existing metrics
- Set up ownership and documentation
- Add to metric catalog

### Analytics Engineer
"Why is my dashboard showing different revenue numbers than finance?"

**Assistant helps:**
- Compare revenue metric definitions
- Show lineage and data sources
- Identify where definitions diverge
- Recommend canonical metric

### Data Leader
"Which metrics are most critical and need better governance?"

**Assistant helps:**
- Show metrics by usage and trust score
- Identify high-usage, low-trust metrics
- Track governance coverage
- Monitor metric health over time

## Technical Stack

- **Python 3.10+** - Core language
- **FastMCP** - MCP protocol implementation  
- **SQLite** - Persistent database storage
- **pytest** - Test framework with 35+ tests
- **YAML/JSON** - Metric definitions and exports
- **Mermaid** - Modern diagram generation

## MCP Tools (13 Total)

### Metric Management

| Tool | Purpose | Returns |
|------|---------|---------|  
| `define_metric()` | Create or update metric definitions | Confirmation + trust score |
| `search_metrics()` | Find metrics by name, tag, or owner | List of matching metrics |
| `validate_metric()` | Check SQL syntax and logic | Validation results + suggestions |

### Quality & Trust

| Tool | Purpose | Returns |
|------|---------|---------|  
| `check_trust_score()` | Calculate weighted quality score | Score breakdown + trends + recommendations |
| `suggest_improvements()` | Get actionable quality recommendations | Prioritized improvement list |

### Visualization

| Tool | Purpose | Returns |
|------|---------|---------|  
| `visualize_lineage()` | Show ASCII dependency tree | Formatted tree diagram |
| `generate_mermaid_diagram()` | Create modern flowchart | Mermaid markdown syntax |
| `compare_metrics()` | Side-by-side comparison | Differences highlighted |

### Export & Integration  

| Tool | Purpose | Returns |
|------|---------|---------|  
| `export_to_looker()` | Generate LookML files | Production-ready .lkml |
| `export_to_tableau()` | Create Tableau data source | TDS XML format |
| `export_to_dbt()` | Generate dbt metric YAML | dbt-compatible .yml |

### Advanced

| Tool | Purpose | Returns |
|------|---------|---------|  
| `analyze_impact()` | Assess downstream effects of changes | Affected dashboards/metrics |

## What This Demonstrates

### UX Skills
- **Cognitive Load Reduction** - Designing abstraction layers that simplify complex systems without sacrificing power
- **Trust Design** - Building confidence through transparent quality signals and sophisticated weighted scoring algorithms
- **Progressive Disclosure** - Information architecture that balances discoverability with detail  
- **Conversational UI** - Natural language interfaces for technical configuration

### Technical Skills
- **MCP Development** - Production-grade AI agent with 13 tools and 1,500+ lines of code
- **Database Design** - SQLite persistence with 5-table schema and full audit trails
- **Data Modeling** - Semantic layer design patterns and metric definition frameworks
- **System Architecture** - Governance automation and observability instrumentation
- **Testing** - 35+ tests with pytest, 90%+ coverage on core functionality
- **Integration Patterns** - BI tool exporters for Looker, Tableau, and dbt

### Domain Expertise
- **Metrics Governance** - Establishing ownership models, validation frameworks, and documentation standards
- **Data Lineage** - Dependency graph construction and impact analysis  
- **Data Observability** - Freshness tracking, quality monitoring with time-decay, and usage analytics
- **Semantic Layers** - Modern data stack patterns and metric modeling best practices

## Why This Project Matters

As a **Principal Content Designer at Microsoft** working with data and AI systems, this project showcases:

1. **Deep understanding of data team challenges** - Direct experience with metric proliferation and trust deficits in production environments
2. **UX for technical users** - Designing abstraction layers that preserve system power while reducing cognitive overhead
3. **Design for trust and observability** - Applying enterprise-grade governance patterns through transparent quality instrumentation with weighted scoring
4. **AI-augmented workflows** - Leveraging MCP to enhance (not replace) human decision-making and domain expertise
5. **Production-ready implementation** - 35+ tests, database persistence, and BI integrations ready for real-world deployment

This represents the kind of human-centered design that enterprise data platforms need: governance that's frictionless, trust that's measurable, and complexity that's manageable.

---

## Recent Enhancements

✅ **SQLite Database** - Full persistence with 5-table schema  
✅ **BI Integrations** - Looker and Tableau export tools  
✅ **Enhanced Trust Scoring** - Weighted algorithm with time-decay and trends  
✅ **Mermaid Diagrams** - Modern visualizations for documentation  
✅ **Test Suite** - 35+ tests with pytest and 90%+ coverage

See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for complete technical details.

## About

**Jen Kelleman**  
Staff Product Designer

I design AI and data experiences that reduce cognitive load and build trust through transparent, well-instrumented systems.

### Connect
- [LinkedIn](https://linkedin.com/in/jenniferkelleman)
- [Medium](https://jenkelleman.medium.com)
- [AI Content Design Handbook](https://jkelleman.github.io/ai-content-design-handbook/)

### Other Projects
- **[MCP-Oreilly](https://github.com/jkelleman/MCP-Oreilly)** - Three production MCP agents for content design, meeting analysis, and documentation
- **[AI Content Design Handbook](https://github.com/jkelleman/ai-content-design-handbook)** - Comprehensive guide to UX writing for AI systems

---

**Making data governance human-centered, one metric at a time.**
