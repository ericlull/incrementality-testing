import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
weeks = np.arange(20)
campaign_start = 12

pre = 40 + np.random.normal(0, 1.5, campaign_start)

post_cf  = 40 + np.linspace(0, 4, 8) + np.random.normal(0, 1, 8)
post_act = 40 + np.linspace(22, 58, 8) + np.random.normal(0, 2, 8)

actual        = np.concatenate([pre, post_act])
counterfactual = np.concatenate([pre, post_cf])

fig, ax = plt.subplots(figsize=(11, 5))

ax.plot(weeks, actual,        color="#2563EB", linewidth=2.5, label="Actual results")
ax.plot(weeks, counterfactual, color="#94A3B8", linewidth=2, linestyle="--", label="Counterfactual (without campaign)")
ax.fill_between(weeks[campaign_start:], post_cf, post_act, alpha=0.15, color="#2563EB", label="Incremental impact")

ax.axvline(campaign_start, color="#DC2626", linewidth=1.5, linestyle="--")
ax.text(campaign_start + 0.2, 8, "Campaign Launch", color="#DC2626", fontsize=10)

mid = 4
ax.annotate("", xy=(campaign_start + mid, post_act[mid]),
                xytext=(campaign_start + mid, post_cf[mid]),
                arrowprops=dict(arrowstyle="<->", color="#16A34A", lw=2))
ax.text(campaign_start + mid + 0.3, (post_act[mid] + post_cf[mid]) / 2,
        "Incremental impact\n(true causal effect)", color="#16A34A", fontsize=10, va="center")

ax.set(xlabel="Week", ylabel="Revenue (€k)", title="Incrementality: Actual vs Counterfactual",
       ylim=(0, 115))
ax.legend(loc="upper left", fontsize=10)
ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
plt.savefig("incrementality_chart.png", dpi=150, bbox_inches="tight")
print("Chart saved to incrementality_chart.png")
