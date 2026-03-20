# Incrementality Analysis — Confluence Page Creation

Instructions for creating a Confluence page to document an incrementality analysis under the team's **DF Analysis > User Acquisition** section.

## Audience & Tone

> **IMPORTANT**: This Confluence page is written for **Business Stakeholders** — not data scientists or engineers.
>
> - **No jargon.** Strip out: p-values, confidence intervals, posterior distributions, Bayesian inference, counterfactual, R², sin/cos encoding, MCMC, bootstrap iterations, control variables, model diagnostics. If a term needs explaining, it doesn't belong.
> - **Plain language only.** "We're confident" not "statistically significant". "What would have happened without ads" not "counterfactual". "We estimated" not "the model predicted".
> - **Short paragraphs.** Max 2 sentences per paragraph. If it's longer, split it or cut it.
> - **Lead with the business outcome.** Every section should answer: what happened, how much, does it matter for the budget?
> - **Numbers tell the story.** Favour bullet points and tables over prose wherever possible.

## When to Use

After completing an incrementality analysis, ask the user:

> "Would you like me to create a Confluence page documenting this analysis under **DF Analysis > User Acquisition**?
> I'll follow the standard incrementality report format and publish it to the team's documentation."

## Confluence Details

Read the following values from the `.env` file at the project root before creating the page:

- **Parent page ID**: `CONFLUENCE_PARENT_PAGE_ID` (User Acquisition folder under DF Analysis)
- **Space**: `CONFLUENCE_SPACE`
- **Cloud ID**: `ATLASSIAN_BASE`
- **Title convention**: `{Country} Incrementality analysis [{Channel} {Platform} {MMM YY}]`
  - Example: `DE Incrementality analysis [FET iOS DEC 25]`

Use `mcp__atlassian__createConfluencePage` with `contentFormat: "markdown"`.

## Page Template

Populate all `{placeholders}` with real data from the analysis. Remove sections that don't apply.

```markdown
---

## TL;DR

`Changes in {period_description}:`

- **{Change 1 description}** {date}
- **{Change 2 description}** {date}

`Above led to:`

**{One-line verdict on overall outcome}**

> {1-2 sentence executive summary: what changed, how many incremental users/purchasers, and the bottom line on profitability.}

- Blended **1Y pROAS** at `{X}x` — {interpretation}
- **Incremental First Purchasers CAC**: `€{X}` per each additional First Purchaser
- **Incremental ROAS (1Y)**: `{X}x` — {interpretation}

> ⚠️ **How to read these numbers**: The *incremental* CAC and ROAS measure only the cost of the *extra* customers observed during the test period — this is intentionally a stricter, more conservative view. The *blended* figures (which include all customers in the cohort) are typically much healthier. **A tight incremental margin does not mean the business is unprofitable** — it means the change we introduced is adding customers on top of a strong organic base. Note: other factors we may not be aware of could have also contributed to the uplift during the test period.

**Limitations / Known Issues**
{List any known data quality issues, platform bugs, or confounders that affect interpretation}

**Actions**

- **{Action 1}** — {rationale}
- **{Action 2}** — {rationale}

---

## What we tested

- **{Research question framed as a question}**

{Brief context on what the acquisition data model measures and any caveats}

- Dates: {intervention_start} until {intervention_end}

## KPIs

- **Signups** Confirmed
- **First Purchasers** (after X days since signup)
- **Revenues** (incremental revenues after X days since signup)
- **CAC €** (cost per customer, new purchasers)
- **1y pLTV €**:
    - Gross Revenues with App Store Fees deducted.
    - Projection at 1y of the Net Revenues for each First Purchaser.
        - `sum(Gross Revenue - Chargeback + Chargeback Lift - Refund - Store commission (only apps) - VAT (only apps)) / sum(First Purchasers)`

## Period findings

| **Period** | **Date** | **Adspend** | **ROAS** | **LTV / CAC** |
| --- | --- | --- | --- | --- |
| **P1: Baseline** | `{dates}` {N} days | ~€{X} | {interpretation} | 1Y pARPPU €{X} |
| **P2: {Intervention name}** | `{dates}` {N} days | ~€{X}/d | `{X}x ROAS` — {interpretation} | 1Y pARPPU €{X} vs CAC €{X} |

**The scalability story (LTV vs CAC):**

- **P1 (baseline)**: {summary}
- **P2 ({intervention})**: {summary with incremental CAC detail}

> 📎 *[Placeholder — `adspend_budget_ramp.png` should be uploaded here]*

## Uplift

| **KPI** | **Uplift (% relative)** | **Abs. Uplift/Day** | **Statistical Significance** |
| --- | --- | --- | --- |
| Signup Users | **+{X}%** `[{CI_lower}%, {CI_upper}%]` | **+{X}**/day | {Stat. Significance or Not Significant} |
| First Purchasers | **+{X}%** `[{CI_lower}%, {CI_upper}%]` | **+{X}**/day | {Stat. Significance or Not Significant} |
| D7 Net Revenues € | **+{X}%** `[{CI_lower}%, {CI_upper}%]` | **+{X}€**/day | {Stat. Significance or Not Significant} |
| D30 Net Revenue € | **+{X}%** `[{CI_lower}%, {CI_upper}%]` | **+{X}€**/day | {Stat. Significance or Not Significant} |

> 📎 *[Placeholder — `cumulative_uplift.png` should be uploaded here]*

## Incremental Metrics in Test period

| **KPI** | **P1 (baseline)** | **P2 ({intervention})** | **Incremental (in P2)** |
| --- | --- | --- | --- |
| Adspend € | {X}€ | {X}€/day | **+{X}€/day** |
| Signup Users | {X}/day | {X}/day | **+{X}**/day |
| First Purchasers | {X}/day | {X}/day | **+{X}**/day |
| Cost per Signup € | {X}€ | {X}€ | **{X}€** `[Cost of each additional Signup]` |
| CAC € | {X}€ | {X}€ | **{X}€** `[Cost of each additional First Purchaser]` |
| 1y pLTV | {X}€ | {X}€ | **{X}€** `[Net revenues € projection for each First Purchaser at 1 year since their signup]` |

### Blended & Incremental iCAC€ & iROAS %

{Summary of efficiency metrics and incremental CAC & ROAS during the test period}

> 📎 *[Placeholder — `cac_roas_incrementality.png` should be uploaded here]*

### Incremental First Purchasers

{Narrative on how incremental budgets drove incremental First Purchasers, referencing the time series}

> 📎 *[Placeholder — `first_purchasers_incrementality.png` should be uploaded here]*

### Other KPIs incrementality

{Commentary on how other KPIs (Signups, Revenues) responded to the budget change, noting any confounders like price changes}

> 📎 *[Placeholder — `signups_incrementality.png` should be uploaded here]*

> 📎 *[Placeholder — `d7_revenue_incrementality.png` should be uploaded here]*

> 📎 *[Placeholder — `d30_revenue_incrementality.png` should be uploaded here]*

### Does more spend actually mean more results?

{1 sentence: e.g. "Higher spend days consistently produced more signups and purchases — confirming the uplift is spend-driven, not coincidence."}

- **Every +€{X} daily spend → +{X} more signups**
- **Every +€{X} daily spend → +{X} more first purchasers**
- **Every +€{X} daily spend → +€{X} in D7 revenue**
- **Every +€{X} daily spend → +€{X} in D30 revenue**

> 📎 *[Placeholder — `{country}_adspend_kpi_scatter.png` should be uploaded here]*

> 📎 *[Placeholder — `{country}_adspend_kpi_timeseries.png` should be uploaded here]*

## Lessons learned

- **{Lesson 1}**: {detail}
- **{Lesson 2}**: {detail}

## Annex

**Methodology**

We used {N} days of historical data to estimate what our KPIs would have looked like without the campaign. Incrementality is the gap between that estimate and what actually happened.

- Pre-period: {start} – {end} ({N} days, {spend})
- Post-period: {start} – {end} ({N} days, ~€{X}/day)
- Confidence intervals: 95% (range shown in brackets throughout)

## Tickets related

{Link to related Jira tickets if available}
```

## Usage Notes

- Populate **all numeric fields** from the actual analysis output
- **No technical jargon** — if a sentence contains p-values, R², control variables, MCMC, or model names, rewrite or cut it
- **Paragraphs max 2 sentences** — if longer, split or convert to bullet points
- Charts can't be added via the API — the template includes `📎 [Placeholder — {image name} should be uploaded here]` markers at each chart insertion point. After publishing, remind the user to attach the PNGs from the analysis output folder and replace each placeholder inline in the Confluence editor
- Adapt the Annex Methodology description if a different approach was used (e.g. dose-response vs discrete)
- Ask the user to **confirm the title and review the content** before publishing

## Image Upload Utility

Use **`upload_confluence_images.py`** (in this folder) to automate PNG uploads after publishing. It authenticates via classic API token, uploads PNGs, and replaces the `📎 [Placeholder — ...]` markers in the page.
