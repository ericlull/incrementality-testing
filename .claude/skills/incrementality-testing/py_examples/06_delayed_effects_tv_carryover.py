#!/usr/bin/env python3
"""
Delayed / Carryover Effects Analysis
======================================
Use for TV campaigns or channels where effects are lagged (not immediate).
Extends Option 4 with lag features and an extended post-period.

Context discovery:
  Q: "When did the TV campaign air?"
  A: "July 1-31, prime time slots"
  Q: "Do you expect immediate or delayed impact?"
  A: "TV usually takes a few days to show up in sales"
"""

import pandas as pd
import matplotlib.pyplot as plt
from causalimpact import CausalImpact

# 1. Prepare data with lagged controls
data['sales_lag_1'] = data['sales'].shift(1)
data['sales_lag_7'] = data['sales'].shift(7)
data = data.dropna()

# 2. Define periods - extend post-period to capture carry-over
pre_period = ['2024-01-01', '2024-06-30']
post_period = ['2024-07-01', '2024-09-30']               # Standard
post_period_extended = ['2024-07-01', '2024-10-31']       # +1 month for carryover

# 3. Run standard analysis
ci = CausalImpact(
    data[['sales', 'organic', 'competitor']],
    pre_period,
    post_period,
    model_args={'nseasons': 7}
)

print("=== Standard Post-Period ===")
print(ci.summary())

# 4. Run extended analysis to capture carryover
ci_extended = CausalImpact(
    data[['sales', 'organic', 'competitor']],
    pre_period,
    post_period_extended,
    model_args={'nseasons': 7}
)

print("\n=== Extended Post-Period (with carryover) ===")
print(ci_extended.summary())

# 5. Analyze temporal pattern - when does the effect peak?
daily_effects = ci_extended.inferences['point_effects']
campaign_start = pd.to_datetime(post_period[0])
peak_day = daily_effects.idxmax()
print(f"\nEffect peaked on: {peak_day} ({(peak_day - campaign_start).days} days after launch)")

# 6. Time-window analysis to see effect evolution
post_windows = [
    ('Week 1-2', ['2024-07-01', '2024-07-14']),
    ('Week 3-4', ['2024-07-15', '2024-07-31']),
    ('Month 2',  ['2024-08-01', '2024-08-31']),
    ('Month 3',  ['2024-09-01', '2024-09-30']),
    ('Carryover', ['2024-10-01', '2024-10-31']),
]

print("\nEffect by Time Window:")
print("-" * 50)
for label, window in post_windows:
    ci_window = CausalImpact(
        data[['sales', 'organic', 'competitor']],
        pre_period,
        window
    )
    effect = ci_window.summary_data['average']['actual'] - ci_window.summary_data['average']['predicted']
    p_val = ci_window.summary_data['p_value']
    sig = '✓' if p_val < 0.05 else '✗'
    print(f"{label}: {effect:+.0f} sales/day (p={p_val:.3f}) {sig}")


# =============================================================================
# USE CASE: Streaming Service Measures TV Campaign with Lagged Impact
# =============================================================================
#
# SCENARIO:
#   A music streaming service ("SoundWave") ran a 4-week national TV campaign
#   in July 2024 to boost premium subscriptions. TV ads aired during prime
#   time across major Spanish channels. Unlike digital campaigns, TV effects
#   don't show up immediately -- viewers see the ad, but may not subscribe
#   until days or weeks later when they remember the brand.
#   The VP of Marketing asks: "What was the real impact of the TV campaign,
#   including the delayed effect after the ads stopped airing?"
#
# DATA AVAILABLE:
#   - Target metric: daily new premium subscriptions (Jan 1 - Oct 31, 2024)
#   - Control 1: organic search volume for "music streaming" (Google Trends)
#   - Control 2: Spotify daily app downloads in Spain (competitor proxy)
#   - TV campaign aired: July 1-31, 2024
#   - TV stopped: August 1 (but carryover expected through September/October)
#   - Total TV spend: €300,000
#   - Premium subscription price: €9.99/month
#
# WHY THIS OPTION:
#   TV campaigns have well-documented delayed and carryover effects. A
#   standard analysis ending at the campaign end date (Jul 31) would miss
#   30-50% of the total impact. This approach:
#   1. Runs a standard post-period (Jul-Sep) for the core effect
#   2. Runs an extended post-period (Jul-Oct) to capture carryover
#   3. Breaks the post-period into time windows to see when the effect
#      peaks and how quickly it decays
#
# WHAT THE ANALYSIS ANSWERS:
#   1. Immediate impact during the campaign (July)
#   2. Sustained effect after ads stopped (August-September)
#   3. Carryover/residual effect (October) -- is the brand lift still there?
#   4. When did the effect peak? (typically 1-2 weeks after first airings)
#   5. Total incremental subscriptions including the full decay tail
#
# EXPECTED OUTPUT INTERPRETATION:
#   - Standard vs. extended comparison shows how much lift you miss by
#     cutting the analysis window too short.
#   - The time-window breakdown reveals the temporal shape of the effect:
#     typically a ramp-up (weeks 1-2), a peak (weeks 3-4), then gradual
#     decay over 4-8 weeks after the campaign ends.
#   - If the carryover window (October) still shows a significant effect,
#     the campaign built lasting brand awareness.
#
# EXAMPLE RESULT:
#   "=== Standard Post-Period (Jul-Sep) ===
#    +85 incremental subscriptions/day (95% CI: [62, 108]), p=0.001
#
#    === Extended Post-Period (Jul-Oct) ===
#    +68 incremental subscriptions/day (95% CI: [49, 87]), p=0.001
#    (lower daily average because October dilutes, but total is higher)
#
#    Effect peaked on: July 22 (21 days after launch)
#
#    Effect by Time Window:
#      Week 1-2:  +45 subs/day (p=0.032) -- ramp-up, ads gaining traction
#      Week 3-4:  +110 subs/day (p=0.001) -- peak effect, heavy airtime
#      Month 2:   +95 subs/day (p=0.001)  -- strong carryover post-campaign
#      Month 3:   +52 subs/day (p=0.008)  -- decaying but still significant
#      Carryover:  +18 subs/day (p=0.142) -- fading, no longer significant
#
#    Total incremental subs (Jul-Oct): ~8,300
#    Incremental revenue (12-month LTV at €9.99/mo): ~€995K
#    Incremental ROAS: 3.3x on the €300K TV spend.
#    Without the extended window, you'd estimate only 7,100 subs (14% undercount)."
# =============================================================================
