# Semantics Metrics Modeling Assistant

**An MCP agent that helps data teams define, validate, and visualize semantic metrics models with trust and observability built-in.**

## Overview

The Semantics Metrics Modeling Assistant is a Model Context Protocol (MCP) agent designed to reduce cognitive load for data teams working with semantic layers. It provides a conversational interface for defining metrics, visual feedback on lineage and dependencies, and trust indicators that help teams build confidence in their data.

## Key Features

### Conversational Metric Definition
Define metrics naturally through conversation:
```
"Define 'Active Users' as daily unique logins"
"Create a metric for revenue per customer"
"What's the definition of our churn rate metric?"
```

### Visual Lineage & Dependencies
- Understand metric relationships and data flow
- Map upstream dependencies and source tables
- Analyze downstream impact before making changes
- Detect circular dependencies and potential conflicts

### Trust Indicators
Build confidence in your metrics through transparent quality signals:
- **Freshness** - Last update timestamp and data staleness
- **Test Coverage** - Number of passing validation tests
- **Usage Statistics** - Adoption metrics across teams
- **Documentation Completeness** - Description, tags, and source attribution
- **Ownership Attribution** - Clear accountability and maintenance responsibility

### Integration Support
Seamless integration with modern semantic layer tools:
- **dbt** - Metrics definitions and models
- **LookML** - Looker semantic models
- **YAML specs** - Standard metric definitions

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
git clone https://github.com/jkelleman/semantics-metrics-modeling-assistant.git
cd semantics-metrics-modeling-assistant

# Install dependencies
uv add "mcp[cli]"
uv pip install -e .

# Run the agent
uv run python -m semantic_metrics.server
```

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

**Check trust score:**
```python
check_trust_score("Active Users")

# Returns:
# Trust Score: 85/100
# Freshness: Updated 2 hours ago (18/20 points)
# Test Coverage: 4 tests passing (20/25 points)
# Usage: Low adoption - 3 users (5/20 points)
# Documentation: Complete (20/20 points)
# Ownership: Assigned to @data-team (15/15 points)
```

**Visualize lineage:**
```python
visualize_lineage("Revenue per Customer")

# Returns:
# Revenue per Customer
#   ├── Total Revenue
#   │   ├── Order Amount (raw.orders)
#   │   └── Refunds (raw.refunds)
#   └── Customer Count
#       └── Unique Customers (raw.users)
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
- **SQLAlchemy** - Database interactions
- **YAML/JSON** - Metric definitions
- **NetworkX** - Lineage graphs
- **Rich** - Terminal visualizations

## MCP Tools

### Core Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `define_metric()` | Create new metric | Define "Active Users" |
| `validate_metric()` | Check metric validity | Validate SQL and logic |
| `search_metrics()` | Find existing metrics | Search for "revenue" |
| `visualize_lineage()` | Show dependencies | See metric relationships |
| `check_trust_score()` | Assess metric quality | Check trust indicators |
| `suggest_improvements()` | Recommend fixes | Improve metric quality |
| `compare_metrics()` | Compare definitions | Why do these differ? |
| `export_to_dbt()` | Generate dbt YAML | Create dbt metric file |

## What This Demonstrates

### UX Skills
- **Cognitive Load Reduction** - Designing abstraction layers that simplify complex systems without sacrificing power
- **Trust Design** - Building confidence through transparent quality signals and multi-dimensional scoring
- **Progressive Disclosure** - Information architecture that balances discoverability with detail
- **Conversational UI** - Natural language interfaces for technical configuration

### Technical Skills
- **MCP Development** - Production-grade AI agent development using Model Context Protocol
- **Data Modeling** - Semantic layer design patterns and metric definition frameworks
- **System Design** - Governance architecture and observability instrumentation
- **Integration Patterns** - Interoperability with dbt, LookML, and modern data stack tooling

### Domain Expertise
- **Metrics Governance** - Establishing ownership models, validation frameworks, and documentation standards
- **Data Lineage** - Dependency graph construction and impact analysis
- **Data Observability** - Freshness tracking, quality monitoring, and usage analytics
- **Semantic Layers** - Modern data stack patterns and metric modeling best practices

## Why This Project Matters

As a **Principal Content Designer at Microsoft** working with data and AI systems, this project showcases:

1. **Deep understanding of data team challenges** - Direct experience with metric proliferation and trust deficits in production environments
2. **UX for technical users** - Designing abstraction layers that preserve system power while reducing cognitive overhead
3. **Design for trust and observability** - Applying enterprise-grade governance patterns through transparent quality instrumentation
4. **AI-augmented workflows** - Leveraging MCP to enhance (not replace) human decision-making and domain expertise

This represents the kind of human-centered design that enterprise data platforms need: governance that's frictionless, trust that's measurable, and complexity that's manageable.

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
