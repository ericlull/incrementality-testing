---
name: marketing-incrementality-testing
description: Design, execute, and analyze marketing incrementality experiments using causal inference to measure the true impact of paid marketing campaigns on business metrics like sales and revenue. Uses Google's CausalImpact library for Bayesian time series analysis.
---

# Marketing Incrementality Testing

A comprehensive skill for measuring the true causal impact of marketing campaigns using rigorous statistical methods and causal inference.

## Context Files

- **`py_examples/README.md`** — Quick-reference table and detailed use cases for each analysis script. Read to understand which example fits a given scenario.
- **`py_examples/`** — Reference code patterns and implementation examples. When starting a new analysis, check these for reusable patterns before writing from scratch.
- **Past analyses** (e.g., `analysis/ios_DE_meta_2025-12/`, `analysis/ios_US_moloco_meta_2025-12/`, `analysis/ios_CA_moloco_meta_incrementality_test_2025-12/`) — Real completed analyses. Reference these for established conventions: folder structure, output naming, chart types, report format, and deliverable structure. Scan the most recent one to stay consistent with the team's evolving standards.

## Purpose

This skill helps marketing analysts and data scientists determine whether paid marketing campaigns actually generate incremental sales and revenue, or if those outcomes would have occurred anyway. It combines experimental design principles, causal inference methodology, and practical implementation using Google's CausalImpact Python library.

**CRITICAL WORKFLOW**: Before conducting any analysis, this skill ALWAYS engages in a discovery conversation to understand:
1. **Type of intervention**: Single discrete change (on/off) vs progressive/gradual change (ramp-up)
2. **Timeline and pattern**: When did changes occur and how did they evolve
3. **Available data**: What metrics and controls are available
4. **Analysis objectives**: What decisions will this inform

Based on this context, the skill presents appropriate analytical approaches and recommends the best method before proceeding with implementation.

## Discovery & Context Analysis

**MANDATORY FIRST STEP**: Before any analysis, engage the user with these questions:

### 1. Understanding the Intervention

**This is the most important question — it determines the analysis approach.** The same dataset analyzed with different approaches produces materially different iCAC and profitability results (validated on iOS UK Meta 2025-12: iCAC ranged from €29 to €44 depending on approach). Each approach answers a different question, so picking the wrong one gives a correct answer to the wrong question. Also ask whether the pre-period is clean (€0 spend) or contains prior spend — if mixed, Dose-Response benefits from adspend as covariate to improve counterfactual fit.

**Ask about intervention type**:
- "Was this a discrete change (campaign launched on specific date) or gradual/progressive (budget ramped up over time)?"
- "Did the change happen all at once or in phases?"

**Common patterns**:
- **Discrete (On/Off)**: Campaign launched July 1st, turned on for all users
- **Progressive Budget**: Started €200/day, increased to €400/day week 2, €600/day week 3
- **Geographic Rollout**: Launched in Madrid week 1, added Barcelona week 2, Valencia week 3
- **Incremental Testing**: 10% traffic week 1, 25% week 2, 50% week 3, 100% week 4

### 2. Determining Timeline Details

**For discrete interventions**:
- "What exact date did the intervention begin?"
- "How long has it been running?"
- "Has anything else changed during this period?"

**For progressive interventions**:
- "When did the first increase/change occur?"
- "What was the pattern of increases? (daily, weekly, specific schedule)"
- "What were the spend/budget/intensity levels at each phase?"
- "Do you have data on the exact daily spend or can we approximate by week?"

### 3. Assessing Available Data

**Always ask**:
- "Where is your data? (e.g., a CSV file path, a folder in this project, or a Snowflake table)"
- "What time range of data do you have? (from date X to date Y)"
- "What is your target metric? (sales, revenue, conversions, etc.)"
- "What control variables do you have available?"
  - Organic traffic, competitor sales, seasonality indices, other regions, etc.
- "Is your data daily, weekly, or other frequency?"
- "Do you have the actual intervention intensity/spend by day or period?"

### 4. Presenting Analysis Options

**AFTER gathering context above, present the appropriate options**:

#### Option 1: Dose-Response Analysis (RECOMMENDED for progressive changes)
**Best for**: Budget ramp-ups, gradual rollouts, varying intensity
**How it works**: Model relationship between intervention intensity and outcome
**What you need**: Daily/weekly intervention intensity data (€ spend, % rollout, etc.)

```python
# Include intervention intensity as a predictor
data['spend_daily'] = [0]*180 + [200]*14 + [400]*17 + [600]*31 + ...
ci = CausalImpact(
    data[['sales', 'organic_traffic', 'competitor_sales', 'spend_daily']],
    pre_period,
    post_period
)
# Effect scales automatically with dose
```

**Advantages**:
- Captures non-linear relationship (2x spend ≠ 2x effect)
- Single analysis for entire period
- Can project effects at different spend levels

**When to use**:
- You have granular spend/intensity data
- Intervention varied continuously or in many steps
- You want to understand marginal returns

#### Option 2: Covariate Regression (ADVANCED for complex patterns)
**Best for**: Multiple overlapping changes, continuous variables
**How it works**: Model sales as function of controls + intervention intensity
**What you need**: Detailed intervention metrics, stable relationship assumptions

```python
# Intervention as time-varying covariate
# CausalImpact builds counterfactual: what if intervention_var stayed at 0
data['campaign_intensity'] = calculate_intensity(dates, campaign_schedule)
ci = CausalImpact(
    data[['sales', 'organic', 'competitor', 'campaign_intensity']],
    pre_period,
    post_period,
    model_args={'dynamic_regression': True}  # Allow time-varying coefficients
)
```

**Advantages**:
- Most flexible approach
- Handles complex intervention patterns
- Can model interaction effects

**When to use**:
- Multiple campaigns overlapping
- Need to disentangle multiple factors
- Have strong statistical background

#### Option 3: Phase-by-Phase Analysis (SIMPLE for stepped changes)
**Best for**: Clear phases, stepped increases, sequential rollout
**How it works**: Run separate analysis for each escalation step
**What you need**: Clear phase boundaries

```python
# Analyze marginal effect of each increase
phases = [
    {'name': 'Phase 1: €0→€200', 'pre': ['2024-01-01', '2024-06-30'],
     'post': ['2024-07-01', '2024-07-14']},
    {'name': 'Phase 2: €200→€400', 'pre': ['2024-01-01', '2024-07-14'],
     'post': ['2024-07-15', '2024-07-31']},
    {'name': 'Phase 3: €400→€600', 'pre': ['2024-01-01', '2024-07-31'],
     'post': ['2024-08-01', '2024-08-31']}
]

for phase in phases:
    ci = CausalImpact(data, phase['pre'], phase['post'])
    print(f"{phase['name']}: {ci.summary_data['average']['rel_effect']*100:.1f}% lift")
```

**Advantages**:
- Easy to understand and explain
- Shows diminishing returns clearly
- Each phase has its own confidence intervals

**When to use**:
- Clear stepped increases (weekly/monthly)
- Want to see marginal impact of each step
- Simpler explanation needed for stakeholders

#### Option 4: Standard Discrete Analysis (CLASSIC for on/off changes)
**Best for**: Single launch date, binary intervention
**How it works**: Compare pre-period to post-period
**What you need**: Single intervention date

```python
# Traditional CausalImpact for discrete intervention
pre_period = ['2024-01-01', '2024-06-30']
post_period = ['2024-07-01', '2024-09-30']
ci = CausalImpact(data[['sales', 'organic_traffic', 'competitor_sales']],
                  pre_period, post_period)
```

**Advantages**:
- Simplest approach
- Cleanest interpretation
- Standard methodology

**When to use**:
- Campaign launched on specific date
- Binary on/off intervention
- No gradual ramp-up

### 5. Recommendation Logic

**Present recommendation based on context**:

```
IF intervention is gradual/progressive:
    RECOMMEND: Option 1 (Dose-Response)
    EXPLAIN: "Since your spend ramped up progressively, dose-response will capture
              how effect scales with intensity. This gives you a complete picture
              in a single analysis."
    ALTERNATIVE: "Option 3 (Phase-by-Phase) is simpler if you prefer to see the
                  marginal impact of each budget increase separately."

ELSE IF intervention has clear phases (e.g., weekly steps):
    RECOMMEND: Option 3 (Phase-by-Phase)
    EXPLAIN: "Since you have clear weekly phases, analyzing each step separately
              lets you see diminishing returns and makes it easy to explain to
              stakeholders."
    ALTERNATIVE: "Option 1 (Dose-Response) would also work and give you a single
                  overall effect estimate."

ELSE IF intervention is complex (multiple overlapping campaigns):
    RECOMMEND: Option 2 (Covariate Regression)
    EXPLAIN: "With multiple overlapping changes, covariate regression can help
              disentangle the effects. This is more advanced but handles complexity."
    FALLBACK: "If this seems too complex, we can simplify by focusing on the
               largest intervention and using Option 1 or 4."

ELSE IF intervention is simple on/off:
    RECOMMEND: Option 4 (Standard Discrete)
    EXPLAIN: "Since this was a simple launch on a specific date, the standard
              approach is cleanest and easiest to interpret."
```

### 6. Confirming Before Analysis

**Always confirm**:
```
"Based on what you've described, I recommend [OPTION X] because [REASONING].

Here's what the analysis will do:
- [Explanation of approach]
- [What outputs you'll get]
- [How to interpret results]

Does this approach sound good, or would you prefer one of the other options?

Once you confirm, please share your data file and I'll run the analysis."
```

**NEVER proceed with analysis until**:
1. Context is understood
2. Options are presented
3. User confirms approach
4. Data is provided

## Core Capabilities

### 1. Experimental Design

**Pre-Analysis Planning:**
- Define clear intervention periods (pre/post campaign launch or spend change)
- Identify appropriate control metrics that correlate with the outcome but aren't affected by the intervention
- Validate critical assumptions:
  - No anticipation: Control units weren't affected before the intervention
  - Structural stability: Relationship between treated and control units remains stable
  - No interference: Treatment of one unit doesn't affect others
- Design geographic or temporal holdout tests when randomization is possible
- Calculate minimum detectable effect sizes given available data

**Control Selection Strategy:**
- Identify time series that correlate with the target metric (sales, revenue, conversions)
- Use unaffected geographies, segments, or channels as synthetic controls
- Consider seasonality patterns, trends, and external factors
- Validate that control series weren't impacted by the marketing intervention
- Use multiple control series for robust estimation

**Common Experimental Designs:**
- Geographic holdout: Exclude marketing from select regions/cities
- Temporal holdout: Pause campaigns for specific time periods
- Platform tests: Compare channels receiving vs not receiving budget increases
- Audience splits: Target specific segments while holding others constant

### 2. Data Preparation

**Time Series Structure:**
```python
import pandas as pd
from causalimpact import CausalImpact

# Expected format: datetime index, columns for target and controls
# target: metric affected by intervention (e.g., daily_sales)
# controls: correlated metrics NOT affected (e.g., competitor_sales, organic_traffic)

data = pd.DataFrame({
    'date': pd.date_range('2024-01-01', '2024-12-31', freq='D'),
    'daily_sales': [...],           # Target metric
    'organic_traffic': [...],       # Control variable 1
    'competitor_sales': [...],      # Control variable 2
    'seasonality_index': [...]      # Control variable 3
})
data.set_index('date', inplace=True)
```

**Data Quality Validation:**
- Check for missing values and decide on imputation strategy
- Ensure consistent time frequency (daily, weekly, etc.)
- Identify and handle outliers (holidays, promotions, external shocks)
- Verify sufficient pre-period data (recommended: 3x the length of post-period)
- Validate that control variables correlate with target metric in pre-period
- Check for structural breaks or regime changes

**Feature Engineering:**
- Create lagged variables if delayed effects are expected
- Add day-of-week, month, holiday indicators
- Include external factors (weather, competitor actions, macro trends)
- Consider transformations (log, differencing) for non-stationary series
- Build composite control metrics from multiple sources

### 3. CausalImpact Implementation

**Basic Model Setup:**
```python
from causalimpact import CausalImpact

# Define pre and post intervention periods
pre_period = ['2024-01-01', '2024-06-30']   # Before campaign
post_period = ['2024-07-01', '2024-09-30']  # During campaign

# Run causal impact analysis
ci = CausalImpact(
    data=data,
    pre_period=pre_period,
    post_period=post_period,
    model_args={
        'nseasons': 7,              # Weekly seasonality
        'season_duration': 1,        # Daily data
        'prior_level_sd': 0.01,     # Prior uncertainty on level
        'niter': 1000               # MCMC iterations
    }
)

# View results
print(ci.summary())
print(ci.summary(output='report'))
ci.plot()
```

**Advanced Configuration:**
- `nseasons`: Capture seasonality (7 for weekly, 12 for monthly)
- `season_duration`: Time units per season
- `prior_level_sd`: Controls smoothness (lower = smoother trend)
- `dynamic_regression`: Allow time-varying coefficients
- `standardize`: Standardize data before modeling (recommended: True)
- `niter`: MCMC samples (more = better precision but slower)

**Multi-Channel Analysis:**
```python
# Analyze multiple campaigns/channels
results = {}
campaigns = ['google_ads', 'meta_ads', 'tiktok_ads']

for campaign in campaigns:
    # Filter to campaign-specific intervention period
    campaign_data = prepare_campaign_data(data, campaign)

    ci = CausalImpact(
        data=campaign_data,
        pre_period=campaign_pre_period,
        post_period=campaign_post_period
    )

    results[campaign] = {
        'absolute_effect': ci.summary_data['average']['actual'] - ci.summary_data['average']['predicted'],
        'relative_effect': ci.summary_data['average']['rel_effect'],
        'p_value': ci.summary_data['p_value'],
        'ci_lower': ci.summary_data['average']['lower'],
        'ci_upper': ci.summary_data['average']['upper']
    }
```

### 4. Results Interpretation

**Understanding the Output:**

The CausalImpact model produces several key metrics:

- **Predicted (Counterfactual)**: What would have happened without the intervention
- **Actual**: What actually happened during the intervention period
- **Absolute Effect**: Actual - Predicted (incremental units: sales, revenue, conversions)
- **Relative Effect**: (Actual - Predicted) / Predicted (percentage lift)
- **Credible Intervals**: 95% probability range for the effect (Bayesian confidence intervals)
- **P-value**: Probability of seeing this effect by chance

**Statistical Significance:**
- p < 0.05: Strong evidence of causal effect
- 0.05 ≤ p < 0.10: Suggestive evidence, may warrant further testing
- p ≥ 0.10: Insufficient evidence of causal impact

**Effect Size Interpretation:**
```python
# Extract key metrics
summary = ci.summary_data

# Absolute lift
abs_lift = summary['average']['actual'] - summary['average']['predicted']
abs_lift_lower = summary['average']['actual'] - summary['average']['upper']
abs_lift_upper = summary['average']['actual'] - summary['average']['lower']

print(f"Incremental sales: {abs_lift:,.0f}")
print(f"95% CI: [{abs_lift_lower:,.0f}, {abs_lift_upper:,.0f}]")

# Relative lift
rel_lift = summary['average']['rel_effect']
rel_lift_lower = (summary['average']['actual'] - summary['average']['upper']) / summary['average']['predicted']
rel_lift_upper = (summary['average']['actual'] - summary['average']['lower']) / summary['average']['predicted']

print(f"Percentage lift: {rel_lift*100:.1f}%")
print(f"95% CI: [{rel_lift_lower*100:.1f}%, {rel_lift_upper*100:.1f}%]")
```

**Temporal Patterns:**
- Examine the daily/weekly pattern of effects
- Identify when the impact peaks (immediate vs delayed)
- Detect saturation effects (diminishing returns over time)
- Check for carryover effects beyond the campaign period

**Disclaimers and Caveats (MANDATORY):**

When presenting results, when results are weak, mixed, or only a subset of KPIs show movement, include the following cautions:

1. **Correlation ≠ Causation reminder**: Even with causal inference methods, the model relies on assumptions (parallel trends, no unmeasured confounders). External factors when possible need to be taken into account — seasonality, competitor actions, PR events, pricing changes, organic trends, or platform algorithm shifts — may explain part or all of observed effects. State this explicitly.

2. **Partial KPI movement**: If only some KPIs improved while others didn't (e.g., revenue up but conversions flat, or clicks up but sales unchanged), flag this prominently. Partial movement often signals attribution noise, audience mismatch, or lagged effects rather than true incremental impact. Do NOT cherry-pick the favorable metric.

3. **Negative or null results**: When results show no significant effect or negative impact, present this clearly without softening. Recommend further investigation (longer test window, different geo splits, data quality audit) rather than speculative explanations for why the campaign "should have" worked.

4. **Data limitations**: Always disclose known gaps — short pre-periods, missing control markets, data collection issues, small sample sizes, or high variance in the baseline. These directly affect confidence in conclusions.

5. **Recommend next steps over conclusions**: When results are ambiguous, frame output as "findings that warrant further validation" rather than definitive business recommendations. Suggest specific follow-up tests or analyses.

6. **Avoid over-attributing to a single channel**: Marketing effects are often cross-channel. Acknowledge that observed lifts may partially reflect halo effects, media mix interactions, or shifted timing rather than pure incremental contribution of the tested channel.

**Template disclaimer to include in every analysis output:**
> ⚠️ **Important**: These results reflect statistical estimates based on available data and modeling assumptions. They do not account for all possible external factors that may have influenced the observed metrics. Treat these findings as directional evidence, not definitive proof of causation. Further validation is recommended before making significant budget decisions.

### 5. ROI and ROAS Calculation

**Incremental ROI/ROAS:**
```python
# Calculate incremental metrics
campaign_spend = 50000  # Total spend during post-period
incremental_revenue = abs_lift * average_order_value
incremental_margin = incremental_revenue * gross_margin_pct

# Incremental ROAS (Return on Ad Spend)
incremental_roas = incremental_revenue / campaign_spend
print(f"Incremental ROAS: {incremental_roas:.2f}x")

# Incremental ROI
incremental_roi = (incremental_margin - campaign_spend) / campaign_spend
print(f"Incremental ROI: {incremental_roi*100:.1f}%")

# Confidence intervals for ROAS
roas_lower = (abs_lift_lower * average_order_value) / campaign_spend
roas_upper = (abs_lift_upper * average_order_value) / campaign_spend
print(f"ROAS 95% CI: [{roas_lower:.2f}x, {roas_upper:.2f}x]")
```

**Attribution Comparison:**
```python
# Compare to last-touch attribution
last_touch_attributed_revenue = platform_reported_revenue
incremental_attributed_revenue = incremental_revenue

attribution_inflation = last_touch_attributed_revenue / incremental_attributed_revenue
print(f"Attribution inflation factor: {attribution_inflation:.2f}x")
print(f"True incremental revenue: ${incremental_attributed_revenue:,.0f}")
print(f"Platform-reported revenue: ${last_touch_attributed_revenue:,.0f}")
```

### 6. Visualization and Reporting

**Standard Visualizations:**
```python
# CausalImpact built-in plot
ci.plot()
# Shows: original series, pointwise effects, cumulative effects

# Custom visualization for business stakeholders
import matplotlib.pyplot as plt

fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Panel 1: Actual vs Predicted
axes[0].plot(data.index, ci.data['response'], label='Actual', linewidth=2)
axes[0].plot(data.index, ci.inferences['preds'], label='Predicted (no campaign)', linestyle='--')
axes[0].fill_between(data.index,
                       ci.inferences['preds_lower'],
                       ci.inferences['preds_upper'],
                       alpha=0.2, label='95% CI')
axes[0].axvline(pd.to_datetime(post_period[0]), color='red', linestyle=':', label='Campaign start')
axes[0].set_title('Daily Sales: Actual vs Counterfactual')
axes[0].legend()

# Panel 2: Point-wise effect
axes[1].plot(data.index, ci.inferences['point_effects'])
axes[1].fill_between(data.index,
                       ci.inferences['point_effects_lower'],
                       ci.inferences['point_effects_upper'],
                       alpha=0.2)
axes[1].axhline(0, color='black', linestyle='-', linewidth=0.5)
axes[1].axvline(pd.to_datetime(post_period[0]), color='red', linestyle=':')
axes[1].set_title('Daily Incremental Sales')

# Panel 3: Cumulative effect
axes[2].plot(data.index, ci.inferences['cum_effects'])
axes[2].fill_between(data.index,
                       ci.inferences['cum_effects_lower'],
                       ci.inferences['cum_effects_upper'],
                       alpha=0.2)
axes[2].axvline(pd.to_datetime(post_period[0]), color='red', linestyle=':')
axes[2].set_title('Cumulative Incremental Sales')

plt.tight_layout()
plt.savefig('incrementality_analysis.png', dpi=300)
```

**Multi-Channel Comparison:**
```python
# Create comparison chart across channels
import pandas as pd
import matplotlib.pyplot as plt

comparison_df = pd.DataFrame({
    'Channel': campaigns,
    'Incremental ROAS': [results[c]['absolute_effect'] * aov / spend[c] for c in campaigns],
    'P-value': [results[c]['p_value'] for c in campaigns],
    'Lift %': [results[c]['relative_effect'] * 100 for c in campaigns]
})

# Sort by ROAS
comparison_df = comparison_df.sort_values('Incremental ROAS', ascending=False)

# Visualization
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(comparison_df['Channel'], comparison_df['Incremental ROAS'])

# Color by significance
colors = ['green' if p < 0.05 else 'orange' if p < 0.10 else 'red'
          for p in comparison_df['P-value']]
for bar, color in zip(bars, colors):
    bar.set_color(color)

ax.set_xlabel('Incremental ROAS')
ax.set_title('Channel Incrementality Comparison')
ax.axvline(1.0, color='black', linestyle='--', linewidth=1, label='Break-even')
plt.legend()
plt.tight_layout()
plt.savefig('channel_comparison.png', dpi=300)
```

**Executive Summary Template:**
```markdown
# Marketing Incrementality Analysis: {Campaign Name}

## Executive Summary
- **Campaign Period**: {start_date} to {end_date}
- **Total Spend**: ${spend:,.0f}
- **Incremental Revenue**: ${incremental_revenue:,.0f} (95% CI: [${rev_lower:,.0f}, ${rev_upper:,.0f}])
- **Incremental ROAS**: {roas:.2f}x (95% CI: [{roas_lower:.2f}x, {roas_upper:.2f}x])
- **Statistical Significance**: p = {p_value:.3f}
- **Verdict**: {'Significant positive impact' if p_value < 0.05 else 'No significant impact detected'}

## Key Findings
1. The campaign generated an estimated {abs_lift:,.0f} incremental {metric_name} ({rel_lift:.1f}% lift)
2. Effect was {'immediate' if early_effect else 'delayed'}, peaking on day {peak_day}
3. Compared to platform attribution, true incrementality is {attribution_inflation:.1f}x lower
4. {'ROI positive' if roi > 0 else 'ROI negative'}: ${incremental_margin - spend:,.0f} profit

## Recommendations
{recommendations_based_on_results}
```

### 7. Model Validation and Diagnostics

**Assumption Checks:**
```python
# 1. Check control variables weren't affected by intervention
# Plot each control during pre/post periods
for control in control_vars:
    plt.figure(figsize=(10, 4))
    plt.plot(data[control])
    plt.axvline(pd.to_datetime(post_period[0]), color='red', linestyle=':')
    plt.title(f'Control Variable: {control}')
    plt.show()

# 2. Validate structural stability
# Check if pre-period model fits well
pre_data = data.loc[pre_period[0]:pre_period[1]]
# R-squared should be reasonable (>0.5 typically)

# 3. Residual analysis
# Residuals should be random noise, not autocorrelated
from statsmodels.graphics.tsaplots import plot_acf
plot_acf(ci.inferences['point_effects'][:len(pre_data)])
```

**Sensitivity Analysis:**
```python
# Test robustness to different control variables
control_sets = [
    ['organic_traffic', 'competitor_sales'],
    ['organic_traffic', 'seasonality_index'],
    ['competitor_sales', 'seasonality_index'],
    ['organic_traffic', 'competitor_sales', 'seasonality_index']
]

sensitivity_results = []
for controls in control_sets:
    test_data = data[['daily_sales'] + controls]
    ci_test = CausalImpact(test_data, pre_period, post_period)
    sensitivity_results.append({
        'controls': ', '.join(controls),
        'effect': ci_test.summary_data['average']['actual'] - ci_test.summary_data['average']['predicted'],
        'p_value': ci_test.summary_data['p_value']
    })

# Results should be consistent across specifications
sensitivity_df = pd.DataFrame(sensitivity_results)
print(sensitivity_df)
```

**Placebo Tests:**
```python
# Run analysis on pre-period only (should show no effect)
fake_post_start = pre_period[0] + (pd.to_datetime(post_period[0]) - pd.to_datetime(pre_period[0])) / 2
placebo_pre = [pre_period[0], fake_post_start]
placebo_post = [fake_post_start, pre_period[1]]

ci_placebo = CausalImpact(data, placebo_pre, placebo_post)
print(f"Placebo test p-value: {ci_placebo.summary_data['p_value']:.3f}")
# Should be > 0.05 (no false positive)
```

### 8. Common Pitfalls and Best Practices

**Avoid These Mistakes:**

1. **Insufficient pre-period data**: Need at least 3x post-period length
   - ❌ 2 weeks pre, 2 weeks post
   - ✅ 6 weeks pre, 2 weeks post

2. **Contaminated controls**: Control variables affected by intervention
   - ❌ Using total website traffic as control when running display ads
   - ✅ Using competitor website traffic or organic-only traffic

3. **Ignoring seasonality**: Not accounting for day-of-week, monthly patterns
   - ❌ Comparing weekday campaign to weekend baseline
   - ✅ Include nseasons parameter and ensure balanced pre/post periods

4. **Multiple interventions**: Other campaigns or changes during test period
   - ❌ Running multiple new campaigns simultaneously
   - ✅ Isolate each intervention or model them jointly

5. **Misinterpreting correlation as causation**:
   - ❌ "Sales went up when we increased spend, so it worked"
   - ✅ Use CausalImpact to estimate the counterfactual

6. **Cherry-picking time periods**: Selecting periods that show desired results
   - ❌ Testing multiple date ranges until finding significance
   - ✅ Pre-specify analysis periods before seeing results

**Best Practices:**

1. **Pre-register analysis plan**: Document hypotheses, methods, and decision criteria before analysis
2. **Use multiple control series**: Reduces model uncertainty
3. **Check model fit**: Examine in-sample fit during pre-period
4. **Report confidence intervals**: Not just point estimates
5. **Run sensitivity analyses**: Test robustness to modeling choices
6. **Consider external validity**: Results may not generalize to different contexts
7. **Account for carry-over**: Effects may persist after campaign ends
8. **Document assumptions**: Be transparent about limitations

### 9. Advanced Techniques

**Geographic Incrementality:**
```python
# Holdout test with geographic controls
# Exclude marketing from test regions, keep it in control regions

test_regions = ['City_A', 'City_B']  # No marketing
control_regions = ['City_C', 'City_D']  # Marketing as usual

# Use control region sales as synthetic control
data_geo = pd.DataFrame({
    'test_sales': test_region_sales,
    'control_sales': control_region_sales,
    'weather_index': weather_data,
    'local_events': events_data
})

ci_geo = CausalImpact(data_geo, pre_period, post_period)
# Effect should be NEGATIVE (test regions miss out on incremental lift)
```

**Hierarchical Testing:**
```python
# Test at multiple levels: channel → campaign → creative

# Level 1: Overall channel
channel_impact = run_causal_impact(channel_data, pre, post)

# Level 2: Individual campaigns within channel
campaign_impacts = {
    campaign: run_causal_impact(campaign_data[campaign], pre, post)
    for campaign in campaigns
}

# Level 3: Creative variations within campaigns
creative_impacts = {
    creative: run_causal_impact(creative_data[creative], pre, post)
    for creative in creatives
}

# Validate consistency: sum of campaign effects ≈ channel effect
```

**Time-Varying Effects:**
```python
# Allow treatment effect to vary over time
# Split post-period into windows

post_windows = [
    ['2024-07-01', '2024-07-14'],  # Week 1-2
    ['2024-07-15', '2024-07-31'],  # Week 3-4
    ['2024-08-01', '2024-08-31'],  # Month 2
]

window_effects = []
for window in post_windows:
    ci_window = CausalImpact(data, pre_period, window)
    window_effects.append({
        'period': f"{window[0]} to {window[1]}",
        'daily_effect': ci_window.summary_data['average']['actual'] -
                       ci_window.summary_data['average']['predicted'],
        'p_value': ci_window.summary_data['p_value']
    })

# Analyze how effect evolves (diminishing returns? growing impact?)
```

## Output Formats

All analyses should produce:

1. **Code**: Reproducible Python scripts with clear comments
2. **Statistical Summary**: Effect estimates with confidence intervals and p-values
3. **Visualizations**: Time series plots showing actual vs counterfactual
4. **Business Metrics**: Incremental ROAS, ROI, and comparison to attribution
5. **Executive Summary**: Non-technical overview with recommendations
6. **Documentation**: Assumptions, limitations, and caveats

## Use Case Examples

See the `py_examples/` folder for complete, runnable analysis scripts:

| Example | Analysis Option | Use Case |
|---------|----------------|----------|
| `01_standard_discrete_single_launch_fixed_budget.py` | Option 4 | Campaign launched on a specific date with constant budget |
| `02_dose_response_progressive_budget_ramp.py` | Option 1 | Budget ramped up progressively over time |
| `03_phase_by_phase_geo_rollout.py` | Option 3 | Stepped rollout (geographic, budget tiers) |
| `04_covariate_regression_overlapping_campaigns.py` | Option 2 | Multiple overlapping campaigns to disentangle |
| `05_multi_channel_cross_channel_efficiency.py` | Options 1/3/4 | Comparing incrementality across channels |
| `06_delayed_effects_tv_carryover.py` | Option 4+ | TV or campaigns with lagged/carryover effects |

## Expertise and Approach

When helping users with incrementality testing:

1. **Understand the business context**: What decision will this analysis inform?
2. **Assess data quality**: Is there sufficient pre-period data? Are controls valid?
3. **Validate assumptions**: Check that causal inference requirements are met
4. **Explain trade-offs**: Balance statistical rigor with business pragmatism
5. **Interpret results in context**: Translate statistics into business implications
6. **Acknowledge limitations**: Be transparent about what can and cannot be concluded
7. **Provide actionable recommendations**: Don't just report numbers, guide decisions

The skill should demonstrate deep expertise in:
- Causal inference and quasi-experimental design
- Bayesian time series modeling
- Marketing analytics and attribution
- Python data analysis stack (pandas, numpy, matplotlib)
- CausalImpact library implementation
- Statistical interpretation for non-technical stakeholders

All code should be production-ready, well-documented, and reproducible. Results should be presented clearly with appropriate visualizations and business context.

## Confluence Documentation

**AFTER completing an incrementality analysis**, always ask the user if they want to create a Confluence page documenting the results under the team's **DF Analysis > User Acquisition** section.

If yes, follow the full instructions and template in **`.claude/skills/incrementality-confluence/SKILL.md`**.

## Project Environment

### Python Virtual Environment
A shared `.venv` exists at the project root (`incrementality_analytics/.venv`). Always activate it before running scripts:
```bash
source .venv/bin/activate
```
Install any missing packages into this venv — do not create new virtual environments per analysis.

### Past Analyses as Reference
Each subfolder within `incrementality_analytics/` represents a completed or in-progress analysis. Use these as reference for structure, methodology, and output format when running new tests:
- Folder naming convention: `{platform}_{country}_{channel}_{year}-{month}` (e.g., `ios_US_moloco_meta_2025-12`)
- Each top-level analysis folder contains:
  - `data/` — source CSV files
  - One or more named output subfolders (e.g., `discrete-incrementality-test/`, `sep29_oct28_meta_launch_isolated_test/`)
- **Each output subfolder contains both the analysis script AND its outputs** (charts `.png`, text report, optional PDF):
  - `{country}_{descriptive_name}_test.py` — single analysis script, placed inside its output folder
  - Output charts (`.png`), `incrementality_report.txt`, KPI tables
- **Script path convention**: when a script lives inside its output subfolder, set paths as:
  - `CSV = os.path.join(BASE, "..", "data", "{csv_file}.csv")` — one level up to reach `data/`
  - `OUT = BASE` — outputs go to the same folder as the script
- **One script per analysis — all outputs in one run**: do NOT create separate scripts for correlation charts or supplementary visualizations. Instead, include all chart functions (causal impact charts, adspend ↔ KPI correlation scatter + timeseries, KPI tables, report) in the single analysis script and call them all from `main()`. The correlation section should be a numbered section (e.g., `# 7. ADSPEND ↔ KPI CORRELATION`) with:
  - `SPEND_UNIT = 100` constant for the plain-language slope annotation
  - `KPIS_CORR` list with `(col, label, color, is_revenue)` tuples
  - `_plain(slope, is_revenue)` helper returning e.g. "Every +€100 daily spend → +36.4 more users"
  - `plot_adspend_correlation(df_full, out)` generating scatter grid + dual-axis timeseries, with the plain-language annotation displayed as a coloured box in each subplot
- When starting a new analysis, check existing folders for the most recent comparable test and match its output format (charts, report structure, metrics).