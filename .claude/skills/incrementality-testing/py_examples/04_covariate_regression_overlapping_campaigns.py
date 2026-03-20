#!/usr/bin/env python3
"""
Option 2: Covariate Regression (ADVANCED)
==========================================
Use when multiple overlapping campaigns need disentangling.

Context discovery:
  Q: "Tell me about all the changes that happened"
  A: "Google Ads ramped up, Meta stayed constant, we also ran TV spots
      weeks 2-4, and increased email frequency throughout"
"""

import pandas as pd
from causalimpact import CausalImpact

# 1. Create detailed intervention variables
data = pd.DataFrame({
    'date': date_range,
    'sales': sales,
    'organic': organic,
    'competitor': competitor,
    'google_spend': google_daily_spend,   # Ramped up
    'meta_spend': meta_daily_spend,       # Constant
    'tv_grps': tv_grps_by_day,           # Weeks 2-4 only
    'email_sends': email_volume_daily     # Increased over time
})
data.set_index('date', inplace=True)

pre_period = ['2024-01-01', '2024-06-30']
post_period = ['2024-07-01', '2024-09-30']

# 2. Run with all intervention variables as predictors
ci = CausalImpact(
    data[['sales', 'organic', 'competitor',
          'google_spend', 'meta_spend', 'tv_grps', 'email_sends']],
    pre_period,
    post_period,
    model_args={
        'dynamic_regression': True,
        'nseasons': 7
    }
)

# 3. Interpret overall effect
# Counterfactual = what if all intervention variables stayed at pre-period levels
total_incremental = ci.summary_data['average']['actual'] - ci.summary_data['average']['predicted']

print(ci.summary())
print(ci.summary(output='report'))
ci.plot()

# 4. Decompose effects (advanced)
# Run separate analyses zeroing out each intervention
intervention_vars = ['google_spend', 'meta_spend', 'tv_grps', 'email_sends']
decomposition = {}

for intervention_var in intervention_vars:
    data_partial = data.copy()
    other_interventions = [v for v in intervention_vars if v != intervention_var]

    # Set others to pre-period average
    for other in other_interventions:
        pre_avg = data.loc[:pre_period[1], other].mean()
        data_partial.loc[post_period[0]:, other] = pre_avg

    ci_partial = CausalImpact(data_partial, pre_period, post_period)
    decomposition[intervention_var] = (
        ci_partial.summary_data['average']['actual'] -
        ci_partial.summary_data['average']['predicted']
    )

print("\nEffect Decomposition:")
print("-" * 50)
for intervention, effect in decomposition.items():
    contribution_pct = (effect / total_incremental) * 100
    print(f"{intervention}: {effect:.0f} sales/day ({contribution_pct:.1f}% of total)")


# =============================================================================
# USE CASE: Fitness App's New Year Marketing Blitz
# =============================================================================
#
# SCENARIO:
#   A fitness app ("FitPulse") runs a multi-channel push in January to
#   capture New Year's resolution traffic. Multiple things changed at once:
#     - Google Ads: ramped from €500/day to €2,000/day over 4 weeks
#     - Meta Ads: constant €1,000/day (retargeting existing users)
#     - TV spots: aired weeks 2-4 only (national prime time)
#     - Email: increased send frequency from 2x/week to daily
#   The CMO asks: "Which channel actually drove the subscription lift,
#   and which ones are just taking credit?"
#
# DATA AVAILABLE:
#   - Target metric: daily new paid subscriptions (Jul 2023 - Mar 2024)
#   - Control 1: organic search volume for "fitness app" (Google Trends)
#   - Control 2: competitor ("MyFitnessPal") daily active users (proxy)
#   - Intervention variables: daily spend per channel, TV GRPs, email volume
#   - Pre-period: Jul 2023 - Dec 2023 (6 months, no campaigns)
#   - Post-period: Jan 1 - Mar 31, 2024 (campaign blitz)
#
# WHY THIS OPTION:
#   Multiple campaigns overlap in time. A standard analysis would lump all
#   effects together. Covariate regression lets CausalImpact model each
#   intervention as a separate predictor, then decompose the total lift
#   into channel-level contributions.
#
# WHAT THE ANALYSIS ANSWERS:
#   1. Total incremental subscriptions from all campaigns combined
#   2. Contribution of each channel to the total lift (decomposition)
#   3. Which channel has the highest marginal impact per € spent?
#   4. Is TV adding real value or just correlating with the digital push?
#
# EXPECTED OUTPUT INTERPRETATION:
#   - The counterfactual assumes ALL intervention variables stayed at
#     pre-period levels (no campaigns).
#   - Decomposition isolates each channel by running "what if only this
#     channel was active?" scenarios.
#   - Contributions may not sum to exactly 100% due to interaction effects.
#   - dynamic_regression=True allows the coefficient for each channel to
#     shift over time (useful if TV effect fades while Google strengthens).
#
# EXAMPLE RESULT:
#   "Total incremental lift: +340 subscriptions/day (p=0.001)
#
#    Effect Decomposition:
#      google_spend:  +155 subs/day (45.6% of total) -- strongest driver
#      meta_spend:     +72 subs/day (21.2% of total) -- solid retargeting
#      tv_grps:        +88 subs/day (25.9% of total) -- real but expensive
#      email_sends:    +25 subs/day  (7.4% of total) -- low cost, decent lift
#
#    TV contributed meaningfully, but at €150K total spend its incremental
#    ROAS (0.7x) is below break-even. Reallocate TV budget to Google Ads
#    where incremental ROAS is 2.3x."
# =============================================================================
