#!/usr/bin/env python3
"""
Option 1: Dose-Response Analysis (RECOMMENDED for progressive changes)
======================================================================
Use when budget ramped up progressively over time.

Context discovery:
  Q: "Was budget constant or did it change over time?"
  A: "Started €200/day, increased €100/day each week"
  Q: "Do you have the exact daily spend?"
  A: "Yes, I have daily spend data"
"""

import pandas as pd
from causalimpact import CausalImpact

# 1. Prepare data with spend intensity
data = pd.DataFrame({
    'date': pd.date_range('2024-01-01', '2024-09-30', freq='D'),
    'sales': daily_sales,
    'organic_traffic': organic_data,
    'competitor_sales': competitor_data,
    'daily_spend': daily_spend_data  # [0, 0, ..., 200, 200, ..., 300, 300, ..., etc]
})
data.set_index('date', inplace=True)

# 2. Define periods (pre = before any spend, post = during ramp-up)
pre_period = ['2024-01-01', '2024-06-30']
post_period = ['2024-07-01', '2024-09-30']

# 3. Run dose-response analysis
# CausalImpact will model: sales ~ f(organic, competitor, daily_spend)
ci = CausalImpact(
    data[['sales', 'organic_traffic', 'competitor_sales', 'daily_spend']],
    pre_period,
    post_period,
    model_args={'nseasons': 7}
)

# 4. Interpret results
# Effect automatically scales with spend level
# Counterfactual assumes daily_spend stayed at 0
incremental_effect = ci.summary_data['average']['actual'] - ci.summary_data['average']['predicted']
total_spend = data.loc[post_period[0]:post_period[1], 'daily_spend'].sum()
incremental_revenue = incremental_effect * len(data.loc[post_period[0]:post_period[1]]) * aov
roas = incremental_revenue / total_spend

print(ci.summary())
print(ci.summary(output='report'))
ci.plot()

print(f"Total spend over ramp-up: €{total_spend:,.0f}")
print(f"Incremental sales per day: {incremental_effect:.0f}")
print(f"Incremental ROAS: {roas:.2f}x")

# 5. Analyze marginal returns
# Group by spend level to see diminishing returns
spend_levels = data.loc[post_period[0]:post_period[1]].groupby('daily_spend')
for spend, group in spend_levels:
    avg_sales = group['sales'].mean()
    print(f"At €{spend}/day: {avg_sales:.0f} avg sales")


# =============================================================================
# USE CASE: SaaS Company Gradually Increases Meta Ads Budget
# =============================================================================
#
# SCENARIO:
#   A B2B SaaS tool ("DataPipe") starts running Meta Lead Ads in July.
#   The growth team is cautious and ramps up spend weekly:
#     Week 1-2:  €200/day  (testing creatives)
#     Week 3-4:  €400/day  (scaling winning ads)
#     Week 5-8:  €600/day  (full scale)
#     Week 9-12: €800/day  (aggressive push)
#   They want to know: at which spend level do returns start diminishing?
#
# DATA AVAILABLE:
#   - Target metric: daily trial signups (Jan 1 - Sep 30, 2024)
#   - Control 1: organic Google search traffic to the website
#   - Control 2: competitor ("Fivetran") job postings count (proxy for market demand)
#   - Daily spend column: exact €/day from Meta Ads Manager export
#   - Average trial-to-paid conversion: 18%, average contract value: €299/month
#
# WHY THIS OPTION:
#   Budget changed continuously over time. A standard on/off analysis would
#   average across all spend levels and miss the diminishing returns curve.
#   Dose-response lets CausalImpact model the relationship between spend
#   intensity and outcome, capturing non-linear effects.
#
# WHAT THE ANALYSIS ANSWERS:
#   1. Overall incremental effect across the entire ramp-up period
#   2. How the effect scales with daily spend (diminishing returns?)
#   3. What's the optimal daily budget before returns flatten out?
#   4. Incremental ROAS at each spend tier
#
# EXPECTED OUTPUT INTERPRETATION:
#   - The counterfactual assumes daily_spend stayed at €0 (pre-period level).
#   - Marginal returns table shows: at €200/day you get X signups, at €400/day
#     you get Y signups, etc. If Y < 2*X, there are diminishing returns.
#   - The "sweet spot" is the spend level where incremental ROAS is still > 1.0x.
#
# EXAMPLE RESULT:
#   "DataPipe's Meta Ads drove +14 incremental trial signups/day on average
#    (95% CI: [9, 19]). Marginal returns by spend level:
#      €200/day: +8 signups/day  (ROAS: 2.1x)
#      €400/day: +13 signups/day (ROAS: 1.5x)
#      €600/day: +16 signups/day (ROAS: 1.2x)
#      €800/day: +17 signups/day (ROAS: 0.9x)  <-- below break-even
#    Recommendation: cap daily budget at €600/day for optimal efficiency."
# =============================================================================
