#!/usr/bin/env python3
"""
Option 3: Phase-by-Phase Analysis
==================================
Use when there are clear stepped increases (geographic rollout, weekly budget tiers).

Context discovery:
  Q: "Did you launch everywhere at once?"
  A: "No, Madrid week 1, Barcelona week 2, Valencia week 3"
  Q: "Do you have city-level data?"
  A: "Yes, I have daily sales by city"
"""

import pandas as pd
import matplotlib.pyplot as plt
from causalimpact import CausalImpact

# 1. Define phases clearly
phases = [
    {
        'name': 'Phase 1: Madrid Launch',
        'pre': ['2024-01-01', '2024-06-30'],
        'post': ['2024-07-01', '2024-07-07'],
        'description': 'First week, Madrid only'
    },
    {
        'name': 'Phase 2: Add Barcelona',
        'pre': ['2024-01-01', '2024-07-07'],
        'post': ['2024-07-08', '2024-07-14'],
        'description': 'Marginal effect of adding Barcelona'
    },
    {
        'name': 'Phase 3: Add Valencia',
        'pre': ['2024-01-01', '2024-07-14'],
        'post': ['2024-07-15', '2024-07-21'],
        'description': 'Marginal effect of adding Valencia'
    },
    {
        'name': 'Phase 4: Full Rollout',
        'pre': ['2024-01-01', '2024-07-21'],
        'post': ['2024-07-22', '2024-09-30'],
        'description': 'Sustained effect with all cities'
    }
]

# 2. Run analysis for each phase
results = []
for phase in phases:
    ci = CausalImpact(
        data[['sales', 'organic_traffic', 'competitor_sales']],
        phase['pre'],
        phase['post']
    )

    results.append({
        'phase': phase['name'],
        'incremental_sales': ci.summary_data['average']['actual'] -
                            ci.summary_data['average']['predicted'],
        'relative_lift': ci.summary_data['average']['rel_effect'] * 100,
        'p_value': ci.summary_data['p_value'],
        'days': len(pd.date_range(phase['post'][0], phase['post'][1]))
    })

# 3. Display marginal impacts
print("Marginal Impact by Phase:")
print("-" * 60)
for r in results:
    sig = '✓' if r['p_value'] < 0.05 else '✗'
    print(f"{r['phase']}")
    print(f"  Incremental sales/day: {r['incremental_sales']:.0f}")
    print(f"  Relative lift: {r['relative_lift']:.1f}%")
    print(f"  Statistical significance: {sig} (p={r['p_value']:.3f})")
    print()

# 4. Visualize diminishing returns
phases_names = [r['phase'] for r in results]
lifts = [r['relative_lift'] for r in results]
plt.bar(phases_names, lifts)
plt.ylabel('Relative Lift (%)')
plt.title('Diminishing Returns Across Rollout Phases')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# =============================================================================
# USE CASE: Food Delivery App Rolls Out to New Cities
# =============================================================================
#
# SCENARIO:
#   A food delivery startup ("QuickBite") is expanding its paid acquisition
#   into new Spanish cities. Instead of launching everywhere at once, they
#   roll out city by city to measure the marginal impact of each new market:
#     Week 1 (Jul 1-7):   Madrid only, €1,500/day
#     Week 2 (Jul 8-14):  + Barcelona, total €2,800/day
#     Week 3 (Jul 15-21): + Valencia, total €3,500/day
#     Week 4+ (Jul 22+):  All 3 cities sustained at €3,500/day
#   They want to know: which city contributed the most incremental orders?
#
# DATA AVAILABLE:
#   - Target metric: total daily orders across all cities (Jan 1 - Sep 30, 2024)
#   - Control 1: organic app installs from App Store/Play Store
#   - Control 2: Uber Eats order volume in Spain (industry proxy from SimilarWeb)
#   - Each phase has a clear start/end date
#
# WHY THIS OPTION:
#   Clear stepped rollout with distinct phases. Phase-by-phase analysis shows
#   the marginal lift from each new city, making it easy to compare ROI across
#   markets and explain to stakeholders: "Madrid added X, Barcelona added Y."
#
# WHAT THE ANALYSIS ANSWERS:
#   1. Marginal incremental orders from each city launch
#   2. Relative lift (%) at each phase -- are returns diminishing?
#   3. Which city is most efficient for marketing spend?
#   4. Is the sustained full-rollout period holding its lift or decaying?
#
# EXPECTED OUTPUT INTERPRETATION:
#   - Each phase has its own CausalImpact run with independent confidence
#     intervals and p-values.
#   - Phase 1 uses the clean 6-month pre-period. Later phases include
#     prior phases in the baseline, so they measure MARGINAL (not total) lift.
#   - The bar chart visually shows if lift per city is decreasing (diminishing
#     returns) or if certain cities outperform others.
#
# EXAMPLE RESULT:
#   "Phase 1 - Madrid:     +120 orders/day (8.2% lift, p=0.002)
#    Phase 2 - Barcelona:  +85 orders/day  (5.1% lift, p=0.011)
#    Phase 3 - Valencia:   +35 orders/day  (1.9% lift, p=0.087) -- not significant
#    Phase 4 - Sustained:  +230 orders/day (12.5% lift, p=0.001)
#
#    Madrid drives the strongest marginal impact. Valencia's contribution is
#    not statistically significant -- consider reallocating that budget to
#    Madrid or Barcelona where ROI is proven."
# =============================================================================
