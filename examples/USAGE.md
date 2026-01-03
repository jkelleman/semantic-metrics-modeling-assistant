# Usage Examples

This guide shows real-world scenarios for using the Semantic Metrics Modeling Assistant.

## Scenario 1: Data Team Member Creates a New Metric

**Goal:** Define a trusted "Active Users" metric for the product team.

```
Step 1: Define the metric with complete context
> define_metric(
    name="Active Users",
    description="Daily unique user logins, counting users who authenticate at least once per 24-hour period",
    calculation="SELECT COUNT(DISTINCT user_id) FROM analytics.user_events WHERE event_type = 'login' AND event_date = CURRENT_DATE",
    owner="@engagement-team",
    tags="engagement,daily,key-metric",
    data_source="analytics.user_events"
)

Result:
✅ Metric Created: Active Users

📊 Definition:
Daily unique user logins, counting users who authenticate at least once per 24-hour period

🛡️ Initial Trust Score: 50/100
⚠️ Trust score is low. Consider:
  • Adding tests with validate_metric()

Step 2: Add validation tests
> validate_metric("Active Users", "Verified counts match production dashboard within 1%")

Result:
✅ All validation checks passed!
🧪 Test Added: Verified counts match production dashboard within 1%
🛡️ Trust Score: 50/100 → 65/100 (+15) 📈

Step 3: Check trust score details
> check_trust_score("Active Users")

Result:
Overall Trust Score: 65/100
🟡 Good - Minor Improvements Recommended

💡 Recommendations:
  • Add more tests for comprehensive coverage
  • Promote metric to increase adoption
```

**Outcome:** Metric is defined, validated, and ready for team adoption with a clear trust indicator.

---

## Scenario 2: Analytics Engineer Debugs Metric Discrepancies

**Goal:** Figure out why "Revenue per Customer" differs from "Monthly Recurring Revenue".

```
Step 1: Search for revenue metrics
> search_metrics(query="revenue")

Result:
🟢 Monthly Recurring Revenue (Trust: 85/100)
   Sum of all recurring subscription revenue normalized to a monthly amount
   Owner: @revenue-team
   Usage: 24 times

🟡 Average Revenue Per User (Trust: 72/100)
   Total revenue divided by total active users
   Owner: @revenue-team
   Usage: 15 times

Step 2: Compare the two metrics
> compare_metrics("Monthly Recurring Revenue", "Average Revenue Per User")

Result:
Metric Comparison
═══════════════════════════════

Calculation:
  1️⃣ SUM(CASE WHEN billing_frequency = 'monthly' THEN amount...)
  2️⃣ SUM(revenue.total_amount) / COUNT(DISTINCT users.user_id)...

Trust Score:
  1️⃣ 85/100 🟢
  2️⃣ 72/100 🟡

💡 Recommendation: 'Monthly Recurring Revenue' has higher trust - prefer using it

Step 3: Visualize dependencies
> visualize_lineage("Average Revenue Per User")

Result:
⬆️ Upstream Dependencies:
   └── analytics.revenue_events
   └── analytics.user_events

⬇️ Downstream Dependents:
   └── Customer Lifetime Value

🎯 Impact Analysis:
   Direct dependencies: 2
   Direct dependents: 1

⚠️ Caution: Changes to this metric will affect 1 downstream metric(s)
```

**Outcome:** Engineer understands the different calculation methods, data sources, and impact of changes.

---

## Scenario 3: Data Leader Assesses Governance Coverage

**Goal:** Audit all metrics for trust and identify improvement areas.

```
Step 1: Search all metrics
> search_metrics()

Result:
Search Results (7 metrics found)
═══════════════════════════════

🟢 Monthly Recurring Revenue (Trust: 85/100)
   Owner: @revenue-team
   Usage: 24 times

🟢 Active Users (Trust: 80/100)
   Owner: @engagement-team
   Usage: 18 times

🟡 Churn Rate (Trust: 72/100)
   Owner: @customer-success-team
   Usage: 12 times

🟡 Average Revenue Per User (Trust: 65/100)
   Owner: @revenue-team
   Usage: 15 times

🔴 Feature Adoption Rate (Trust: 45/100)
   Owner: Unassigned
   Usage: 3 times

🔴 Conversion Rate (Trust: 40/100)
   Owner: Unassigned
   Usage: 1 time

🔴 Trial Signups (Trust: 35/100)
   Owner: Unassigned
   Usage: 0 times

Step 2: Check details on low-trust metric
> check_trust_score("Feature Adoption Rate")

Result:
Overall Trust Score: 45/100
🔴 Needs Improvement

📅 Freshness: 5/20
⚠️ Updated: 3 months ago

🧪 Test Coverage: 0/25
❌ Tests: 0 passing

👤 Ownership: 0/15
❌ Owner: Unassigned

💡 Recommendations:
  • Assign an owner
  • Add validation tests
  • Specify the data source
  • Add relevant tags for discoverability

⚠️ Low trust score. Prioritize improvements before widespread use.
```

**Outcome:** Leader identifies 3 metrics needing immediate governance attention and can assign remediation work.

---

## Scenario 4: Exporting to dbt Semantic Layer

**Goal:** Generate dbt-compatible YAML for production deployment.

```
Step 1: Export metric definition
> export_to_dbt("Monthly Recurring Revenue")

Result:
✅ dbt Export for: Monthly Recurring Revenue
═══════════════════════════════

```yaml
version: 2

metrics:
  - name: monthly_recurring_revenue
    label: Monthly Recurring Revenue
    description: Sum of all recurring subscription revenue normalized to a monthly amount
    
    calculation_method: derived
    expression: SUM(CASE WHEN billing_frequency = 'monthly'...)
    
    meta:
      owner: @revenue-team
      tags: ['revenue', 'subscription', 'monthly', 'key-metric']
      trust_score: 85
```

💡 Next steps:
1. Copy the YAML above to your dbt project
2. Place in: models/metrics/monthly_recurring_revenue.yml
3. Run: dbt compile
4. Run: dbt run --select monthly_recurring_revenue
```

**Outcome:** Seamless integration with existing data infrastructure and deployment workflows.

---

## Scenario 5: Conversational Metric Discovery

**Goal:** Find metrics related to user engagement without knowing exact names.

```
Step 1: Search by topic
> search_metrics(query="users")

Result:
🟢 Active Users (Trust: 80/100)
   Daily unique user logins
   
🟡 Average Revenue Per User (Trust: 65/100)
   Total revenue divided by total active users

Step 2: Search by tags
> search_metrics(tags="engagement")

Result:
🟢 Active Users (Trust: 80/100)
🟢 Weekly Active Users (Trust: 82/100)
🟡 Feature Adoption Rate (Trust: 45/100)

Step 3: Get definition guidance
> (Use the metric_definition_guide prompt)

Result:
# Guide to Defining High-Quality Metrics

## Best Practices
✅ Clear naming
✅ Descriptive explanations
✅ Explicit calculations
...
```

**Outcome:** Easy discovery and self-service for non-technical stakeholders.

---

## Key Benefits Demonstrated

### 🗣️ Conversational First
No YAML editing required - define metrics in natural language

### 👁️ Show, Don't Tell
Visual lineage and dependency graphs make complex relationships clear

### 🛡️ Trust Through Transparency
Upfront quality indicators help teams choose reliable metrics

### 📈 Progressive Disclosure
Basic info first (name, trust score), details on demand (calculation, lineage)

### ✅ Governance by Default
Built-in prompts for ownership, documentation, and validation make it easy to do the right thing

---

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/jkelleman/semantics-metrics-modeling-assistant.git
cd semantics-metrics-modeling-assistant

# Install with uv (recommended)
uv pip install -e .

# Configure in Claude Desktop (config.json)
{
  "mcpServers": {
    "semantic-metrics": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/semantics-metrics-modeling-assistant",
        "run",
        "semantic_metrics/server.py"
      ]
    }
  }
}

# Restart Claude Desktop
```

---

## Next Steps

- Try defining your own metrics with `define_metric()`
- Validate existing metrics with `validate_metric()`
- Audit governance coverage with `search_metrics()` and `check_trust_score()`
- Export to dbt with `export_to_dbt()`

For questions or feedback: jenkelleman@microsoft.com
