#!/usr/bin/env python3
"""
Option 4: Standard Discrete Analysis
=====================================
Use when a campaign launched on a specific date with constant budget.

Context discovery:
  Q: "Was this launched all at once or ramped up gradually?"
  A: "Launched July 1st, full budget from day 1"
  Q: "What's your daily budget?"
  A: "€2,000/day constant"
"""

import pandas as pd
from causalimpact import CausalImpact

# 1. Load data
sales_data = load_daily_sales()          # Target metric
organic_traffic = load_organic_visits()  # Control 1
competitor_sales = load_competitor_data() # Control 2

# 2. Prepare dataset
data = pd.DataFrame({
    'sales': sales_data,
    'organic': organic_traffic,
    'competitor': competitor_sales
}).dropna()

# 3. Define periods
pre_period = ['2024-01-01', '2024-06-30']   # 6 months before
post_period = ['2024-07-01', '2024-09-30']  # 3 months during campaign

# 4. Run analysis
ci = CausalImpact(data, pre_period, post_period, model_args={'nseasons': 7})

# 5. Extract results
incremental_sales = ci.summary_data['average']['actual'] - ci.summary_data['average']['predicted']
total_spend = 92 * 2000  # 92 days * €2000/day
roas = (incremental_sales * avg_order_value) / total_spend

# 6. Report
print(ci.summary())
print(ci.summary(output='report'))
ci.plot()

print(f"Incremental daily sales: {incremental_sales:.0f}")
print(f"Total incremental revenue: ${incremental_sales * 92 * avg_order_value:,.0f}")
print(f"Incremental ROAS: {roas:.2f}x")
print(f"P-value: {ci.summary_data['p_value']:.3f}")


# =============================================================================
# USE CASE: Subscription App Launches Google Ads Campaign
# =============================================================================
#
# SCENARIO:
#   A meditation app ("CalmMind") has been growing organically for 6 months.
#   On July 1st, the marketing team launches a Google Ads campaign targeting
#   "meditation app" and "mindfulness" keywords at a fixed €2,000/day budget.
#   They want to know: did the campaign actually drive incremental subscriptions,
#   or would those users have subscribed anyway through organic discovery?
#
# DATA AVAILABLE:
#   - Target metric: daily new subscriptions (Jan 1 - Sep 30, 2024)
#   - Control 1: organic App Store search impressions (not influenced by paid ads)
#   - Control 2: competitor app ("HeadSpace") daily downloads from SensorTower
#   - Campaign launched: July 1, 2024
#   - Daily budget: €2,000 (constant, no ramp-up)
#   - Average subscription price: €9.99/month
#
# WHY THIS OPTION:
#   Binary on/off intervention. No budget changes. Single launch date.
#   Standard CausalImpact is the cleanest and simplest approach.
#
# WHAT THE ANALYSIS ANSWERS:
#   1. How many daily subscriptions are truly incremental (caused by the ads)?
#   2. What is the incremental ROAS vs. what Google Ads reports in its dashboard?
#   3. Is the campaign worth continuing at this budget level?
#
# EXPECTED OUTPUT INTERPRETATION:
#   - CausalImpact builds a counterfactual: "what would subscriptions look like
#     if the campaign never launched?" using organic impressions and competitor
#     downloads as predictors.
#   - If p < 0.05 and the lift is positive, the campaign has a statistically
#     significant causal effect on subscriptions.
#   - Compare incremental ROAS to Google's reported ROAS to see how much
#     the platform over-attributes (typically 2-4x inflation).
#
# EXAMPLE RESULT:
#   "CalmMind's Google Ads campaign generated +23 incremental subscriptions/day
#    (95% CI: [15, 31]), a 12.4% lift over the counterfactual baseline.
#    Incremental ROAS: 1.06x vs. Google-reported ROAS of 3.2x.
#    The campaign is marginally profitable -- consider testing a lower budget
#    to find the efficiency sweet spot."
# =============================================================================
