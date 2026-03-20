# Incrementality Analysis Examples

Complete, runnable analysis scripts for each CausalImpact analysis approach.

## Examples

| File | Option | When to Use |
|------|--------|-------------|
| `01_standard_discrete_single_launch_fixed_budget.py` | Option 4 - Standard Discrete | Campaign launched on a specific date, constant budget, binary on/off |
| `02_dose_response_progressive_budget_ramp.py` | Option 1 - Dose-Response | Budget ramped up progressively, varying daily spend intensity |
| `03_phase_by_phase_geo_rollout.py` | Option 3 - Phase-by-Phase | Stepped rollout, on/off testing, or budget tiers in distinct phases |
| `04_covariate_regression_overlapping_campaigns.py` | Option 2 - Covariate Regression | Multiple overlapping campaigns that need disentangling |
| `05_multi_channel_cross_channel_efficiency.py` | Options 1/3/4 combined | Comparing incrementality across channels with different ramp patterns |
| `06_delayed_effects_tv_carryover.py` | Option 4 with extensions | TV or campaigns with lagged/carryover effects |

**Quick guide:** Ask yourself two questions:
1. **How did the campaign start?** One date (01), gradual ramp (02), stepped rollout (03), or multiple things at once (04)?
2. **What do you want to know?** Single campaign impact (01-04), channel comparison (05), or long-tail effect (06)?

## Detailed Use Cases

### 01 - Standard Discrete (Single Launch, Fixed Budget)

**File:** `01_standard_discrete_single_launch_fixed_budget.py`
**Option:** 4 - Standard Discrete

You flipped a switch. Campaign was **off**, then **on** at a specific date, with the **same budget every day**.

**When to use:**
- "We launched Google Ads on July 1st at €2K/day and never changed it."
- Any binary on/off intervention with a single launch date and constant spend.

---

### 02 - Dose-Response (Progressive Budget Ramp)

**File:** `02_dose_response_progressive_budget_ramp.py`
**Option:** 1 - Dose-Response

You **gradually turned up the dial**. Budget started small and increased over time.

**When to use:**
- "We started at €200/day and added €100/day each week to see what happens."
- You have daily spend data and want to understand diminishing returns at each spend level.

---

### 03 - Phase-by-Phase (Geo Rollout, On/Off Testing, Budget Tiers)

**File:** `03_phase_by_phase_geo_rollout.py`
**Option:** 3 - Phase-by-Phase

You **expanded in steps**, or switched campaigns on and off in distinct phases. Each step is analyzed separately so you see which one moved the needle most.

**When to use:**
- **Geographic rollout**: "Week 1 Madrid, week 2 Barcelona, week 3 Valencia."
- **On then off in one region**: "We ran ads in Madrid for 4 weeks, then turned them off. Did the lift disappear?"
- **On/off/on testing**: "We ran ads for 2 weeks, paused for 2 weeks, then turned back on — did the effect come back?"
- **Budget tiers in one market**: "Same city, but €500/day week 1, €1,000/day week 2, back to €500/day week 3."

**Why the "off" phase matters:** If the lift disappears when you stop spending, that's strong proof the campaign was truly causal, not just a coincidence.

---

### 04 - Covariate Regression (Overlapping Campaigns)

**File:** `04_covariate_regression_overlapping_campaigns.py`
**Option:** 2 - Covariate Regression (Advanced)

You had **multiple things happening at once** and need to untangle which one actually drove the results.

**When to use:**
- "We ramped Google Ads, kept Meta flat, ran TV spots for 3 weeks, AND increased email frequency — which one actually drove sales?"
- Multiple campaigns overlap in time and you need to decompose the total lift into channel-level contributions.

---

### 05 - Multi-Channel (Cross-Channel Efficiency)

**File:** `05_multi_channel_cross_channel_efficiency.py`
**Option:** 1/3/4 combined

You want to **compare channels side by side** to decide where to put next quarter's budget. Each channel may have launched differently, so the script picks the right analysis method per channel.

**When to use:**
- "Google, Meta, and TikTok all ran differently — which one gives us the most bang per €1,000?"
- Budget planning: you need a single efficiency metric to rank all channels fairly.

---

### 06 - Delayed Effects (TV Carryover)

**File:** `06_delayed_effects_tv_carryover.py`
**Option:** 4 with extensions

Your campaign's impact **doesn't show up right away**. The script extends the analysis window and breaks down the effect over time to capture the full tail.

**When to use:**
- "The TV ads aired in July but people keep subscribing in August and September because they remember the ad."
- Any channel with lagged effects: TV, podcasts, billboards, brand campaigns, influencer partnerships.

---

## How to Use

1. Copy the relevant example script
2. Replace placeholder data with your actual dataset
3. Adjust pre/post periods to match your intervention timeline
4. Run and interpret results using the methodology in `../.claude/commands/incrementality-testing.md`
