#!/usr/bin/env python3
"""
Multi-Channel Budget Optimization
===================================
Compare incrementality across channels with different ramp patterns.
Combines Options 1/3/4 depending on each channel's intervention type.

Context discovery:
  Q: "Did all channels launch the same way?"
  A: "Google ramped up gradually, Meta was constant, TikTok had weekly steps"
"""

import pandas as pd
import matplotlib.pyplot as plt
from causalimpact import CausalImpact

pre_period = ['2024-01-01', '2024-06-30']
post_period = ['2024-07-01', '2024-09-30']

channels = {
    'google': {
        'type': 'progressive',
        'data': google_data_with_daily_spend,
        'spend_total': 75000
    },
    'meta': {
        'type': 'discrete',
        'data': meta_data,
        'spend_total': 50000
    },
    'tiktok': {
        'type': 'phased',
        'data': tiktok_data,
        'spend_total': 25000,
        'phases': [...]
    }
}

results = {}
for channel, config in channels.items():
    if config['type'] == 'progressive':
        # Option 1: Dose-response
        ci = CausalImpact(
            config['data'][['sales', 'organic', 'competitor', 'daily_spend']],
            pre_period,
            post_period
        )
    elif config['type'] == 'discrete':
        # Option 4: Standard
        ci = CausalImpact(
            config['data'][['sales', 'organic', 'competitor']],
            pre_period,
            post_period
        )
    elif config['type'] == 'phased':
        # Option 3: Aggregate phase results
        phase_results = []
        for phase in config['phases']:
            ci_phase = CausalImpact(config['data'], phase['pre'], phase['post'])
            phase_results.append(ci_phase)
        ci = aggregate_phase_results(phase_results)

    inc_revenue = (ci.summary_data['average']['actual'] -
                   ci.summary_data['average']['predicted']) * days * aov
    inc_roas = inc_revenue / config['spend_total']

    results[channel] = {
        'incremental_revenue': inc_revenue,
        'incremental_roas': inc_roas,
        'efficiency_score': inc_roas / config['spend_total'] * 1000
    }

# Print results
print("Channel Incrementality Comparison:")
print("-" * 60)
for channel, metrics in results.items():
    print(f"{channel}:")
    print(f"  Incremental revenue: €{metrics['incremental_revenue']:,.0f}")
    print(f"  Incremental ROAS: {metrics['incremental_roas']:.2f}x")
    print(f"  Efficiency (per €1k): €{metrics['efficiency_score']:.2f}")
    print()

# Recommend budget reallocation
best_channel = max(results.items(), key=lambda x: x[1]['efficiency_score'])[0]
print(f"Reallocate budget toward: {best_channel}")
print(f"Efficiency: €{results[best_channel]['efficiency_score']:.2f} incremental revenue per €1k spent")

# Visualize
fig, ax = plt.subplots(figsize=(10, 6))
channel_names = list(results.keys())
roas_values = [results[c]['incremental_roas'] for c in channel_names]
ax.barh(channel_names, roas_values)
ax.set_xlabel('Incremental ROAS')
ax.set_title('Channel Incrementality Comparison')
ax.axvline(1.0, color='black', linestyle='--', linewidth=1, label='Break-even')
plt.legend()
plt.tight_layout()
plt.show()


# =============================================================================
# USE CASE: E-Commerce Company Compares Channel Efficiency for Q4 Planning
# =============================================================================
#
# SCENARIO:
#   An online fashion retailer ("StyleBox") ran paid campaigns across 3
#   channels during summer 2024. Each channel had a different ramp pattern:
#     - Google Shopping: progressive ramp from €500 to €2,000/day (8 weeks)
#     - Meta (Instagram): flat €1,200/day from day 1 (constant)
#     - TikTok Ads: stepped weekly from €200 to €800/day (4 tiers)
#   Q4 budget planning is coming up. The Head of Growth needs to know:
#   "Per €1,000 spent, which channel drives the most incremental revenue?"
#
# DATA AVAILABLE:
#   - Target metric: daily online revenue in EUR (Jan 1 - Sep 30, 2024)
#   - Control 1: direct traffic sessions (brand strength proxy)
#   - Control 2: ASOS.com daily traffic estimate (competitor/market proxy)
#   - Per-channel daily spend from ad platform exports
#   - TikTok phase dates: €200 (Jul 1-7), €400 (Jul 8-14), €600 (Jul 15-21), €800 (Jul 22+)
#   - Average order value: €67
#
# WHY THIS OPTION:
#   Each channel has a different intervention pattern, so no single analysis
#   type fits all three. This script picks the right CausalImpact approach
#   per channel (dose-response for Google, standard for Meta, phase-by-phase
#   for TikTok) and then compares all three on the same efficiency metric.
#
# WHAT THE ANALYSIS ANSWERS:
#   1. Incremental revenue attributed to each channel
#   2. Incremental ROAS per channel (is each one profitable?)
#   3. Efficiency score: incremental € revenue per €1,000 spent
#   4. Where should the Q4 budget be concentrated?
#
# EXPECTED OUTPUT INTERPRETATION:
#   - Each channel gets its own CausalImpact analysis with the appropriate
#     method, so the results are comparable on a per-€ basis.
#   - The bar chart ranks channels by ROAS. Channels above the 1.0x line
#     are profitable; below it, they're burning money.
#   - Efficiency score normalizes for different total spends so you can
#     compare a €75K Google budget fairly against a €25K TikTok budget.
#
# EXAMPLE RESULT:
#   "Channel Incrementality Comparison:
#      Google Shopping: €142,000 incremental revenue, ROAS 1.89x, efficiency €25.2/€1k
#      Meta Instagram:  €71,000 incremental revenue, ROAS 1.42x, efficiency €28.4/€1k
#      TikTok Ads:      €18,000 incremental revenue, ROAS 0.72x, efficiency €14.4/€1k
#
#    Recommendation: Reallocate TikTok's €25K to Google Shopping and Meta.
#    Meta has the highest efficiency per €1k, but Google can absorb more
#    budget before hitting diminishing returns. Proposed Q4 split:
#      Google: 55% (+10%)  |  Meta: 45% (+5%)  |  TikTok: 0% (-15%)"
# =============================================================================
