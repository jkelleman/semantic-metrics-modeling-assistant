# Semantics Metrics Modeling Assistant

**An MCP agent that helps data teams define, validate, and visualize semantic metrics models with trust and observability built-in.**

## 🎯 Overview

The Semantics Metrics Modeling Assistant is a Model Context Protocol (MCP) agent designed to reduce cognitive load for data teams working with semantic layers. It provides a conversational interface for defining metrics, visual feedback on lineage and dependencies, and trust indicators that help teams build confidence in their data.

## ✨ Key Features

### 🗣️ Conversational Metric Definition
Define metrics naturally through conversation:
```
"Define 'Active Users' as daily unique logins"
"Create a metric for revenue per customer"
"What's the definition of our churn rate metric?"
```

### 📊 Visual Lineage & Dependencies
- See how metrics relate to each other
- Understand upstream dependencies
- Track downstream impact of changes
- Identify circular dependencies

### 🛡️ Trust Indicators
Build confidence in your metrics with:
- **Freshness** - When was data last updated?
- **Test Coverage** - Are metrics validated?
- **Usage Stats** - How widely adopted is this metric?
- **Documentation Quality** - Is it well-documented?
- **Ownership** - Who maintains this metric?

### 🔌 Integration Support
Works with popular semantic layer tools:
- **dbt** - Metrics definitions and models
- **LookML** - Looker semantic models
- **YAML specs** - Standard metric definitions

## 🌟 Why This Matters

### The Problem
Data teams struggle with:
- **Metric sprawl** - 50 different "revenue" metrics
- **Trust issues** - "Which metric should I use?"
- **Cognitive overload** - Complex dependencies and lineage
- **Governance gaps** - No clear ownership or validation

### The Solution
This assistant provides:
- ✅ **Reduced cognitive load** - Conversational interface over complex YAML
- ✅ **Built-in trust** - Transparency into metric quality
- ✅ **Governance guardrails** - Validation and ownership tracking
- ✅ **Observability** - See how metrics are used and maintained

## 🏗️ Architecture

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

## 🚀 Quick Start

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
# ✅ Freshness: Updated 2 hours ago
# ✅ Test Coverage: 4 tests passing
# ⚠️ Usage: Low adoption (3 users)
# ✅ Documentation: Complete
# ✅ Owner: Assigned (@data-team)
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

## 🎨 Design Principles

### 1. Conversational First
Complex YAML configurations become natural language conversations. Users shouldn't need to remember syntax.

### 2. Show, Don't Tell
Visual lineage graphs > text descriptions. Make dependencies and relationships immediately clear.

### 3. Trust Through Transparency
Display quality indicators upfront. Users should know what they can rely on.

### 4. Progressive Disclosure
Show basic info first, details on demand. Don't overwhelm with complexity.

### 5. Governance by Default
Make it easy to do the right thing (add owners, tests, docs). Make it hard to create orphaned metrics.

## 📋 Use Cases

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

## 🔧 Technical Stack

- **Python 3.10+** - Core language
- **FastMCP** - MCP protocol implementation
- **SQLAlchemy** - Database interactions
- **YAML/JSON** - Metric definitions
- **NetworkX** - Lineage graphs
- **Rich** - Terminal visualizations

## 🛠️ MCP Tools

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

## 📚 What This Demonstrates

### UX Skills
- **Cognitive Load Reduction** - Complex systems made simple
- **Trust Design** - Building confidence through transparency
- **Progressive Disclosure** - Information architecture for complexity
- **Conversational UI** - Natural language over configuration files

### Technical Skills
- **MCP Development** - Building production AI agents
- **Data Modeling** - Understanding semantic layers
- **System Design** - Governance and observability
- **Integration** - Working with dbt, LookML, and data tools

### Domain Expertise
- **Metrics Governance** - Ownership, validation, documentation
- **Data Lineage** - Dependency tracking and impact analysis
- **Data Observability** - Freshness, quality, usage metrics
- **Semantic Layers** - Modern data stack patterns

## 🎓 Why This Project Matters

As a **Principal Content Designer at Microsoft** working with data and AI systems, this project showcases:

1. **Deep understanding of data team challenges** - Metrics sprawl and trust issues are real problems
2. **UX for technical users** - Making complex systems accessible without oversimplifying
3. **Design for trust and observability** - Critical for enterprise data systems
4. **AI-augmented workflows** - Using MCP to enhance (not replace) human expertise

This is the kind of UX design that enterprise data teams need - making governance easy, trust visible, and complexity manageable.

## 👤 About

**Jen Kelleman**  
Principal Content Designer @ Microsoft

Passionate about designing AI and data experiences that reduce cognitive load and build trust.

### Connect
- 💼 [LinkedIn](https://linkedin.com/in/jenniferkelleman)
- ✍️ [Medium](https://jenkelleman.medium.com)
- 🌐 [AI Content Design Handbook](https://jkelleman.github.io/ai-content-design-handbook/)
- 📧 jenkelleman@microsoft.com

### Other Projects
- **[MCP-Oreilly](https://github.com/jkelleman/MCP-Oreilly)** - Three production MCP agents for real-world workflows
- **[AI Content Design Handbook](https://github.com/jkelleman/ai-content-design-handbook)** - Comprehensive UX writing guide for AI

---

**Making data governance human-centered, one metric at a time.**
