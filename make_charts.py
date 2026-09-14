import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

mix = pd.read_csv("data/mart_generation_mix_monthly.csv")
yoy = pd.read_csv("data/mart_yoy_generation_by_source.csv")
pl = pd.read_csv("data/mart_price_load_renewables.csv")

GREEN = "#2f855a"
BLUE = "#2b6cb0"
ORANGE = "#dd6b20"
GRAY = "#718096"

# Chart 1: renewable share, 2024 vs 2025 by calendar month
mix["cal_month"] = mix["month"].str[5:7].astype(int)
p24 = mix[mix["year"]==2024].sort_values("cal_month")
p25 = mix[mix["year"]==2025].sort_values("cal_month")
month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

fig, ax = plt.subplots(figsize=(7.5,4.5), dpi=150)
ax.plot(p24["cal_month"], p24["renewable_share_pct"], marker='o', color=GRAY, label="2024", linewidth=2)
ax.plot(p25["cal_month"], p25["renewable_share_pct"], marker='o', color=GREEN, label="2025", linewidth=2)
ax.set_xticks(range(1,13)); ax.set_xticklabels(month_names)
ax.set_ylabel("Renewable share of tracked generation (%)")
ax.set_title("Germany: Renewable Generation Share, 2024 vs 2025", fontsize=12, fontweight='bold')
ax.legend(frameon=False)
ax.spines[['top','right']].set_visible(False)
ax.yaxis.grid(True, color='#e5e5e5', linewidth=0.8)
ax.set_axisbelow(True)
plt.tight_layout()
plt.savefig("renewable_share_2024_2025.png", dpi=150)
plt.close()

# Chart 2: YoY change by source, diverging
yoy_sorted = yoy.sort_values("yoy_change_pct")
colors = [GREEN if v>=0 else ORANGE for v in yoy_sorted["yoy_change_pct"]]
fig, ax = plt.subplots(figsize=(7.2,4.2), dpi=150)
bars = ax.barh(yoy_sorted["label"], yoy_sorted["yoy_change_pct"], color=colors)
for bar,val in zip(bars, yoy_sorted["yoy_change_pct"]):
    ha = 'left' if val>=0 else 'right'
    off = 0.3 if val>=0 else -0.3
    ax.text(val+off, bar.get_y()+bar.get_height()/2, f"{val:+.1f}%", va='center', ha=ha, fontsize=9)
ax.axvline(0, color='#999999', linewidth=0.8)
xmin, xmax = yoy_sorted["yoy_change_pct"].min(), yoy_sorted["yoy_change_pct"].max()
ax.set_xlim(xmin-4.5, xmax+4.5)
ax.set_xlabel("YoY change in annual generation, 2024 -> 2025 (%)")
ax.set_title("Which sources grew or shrank in 2025?", fontsize=12, fontweight='bold')
ax.spines[['top','right']].set_visible(False)
plt.tight_layout()
plt.savefig("yoy_generation_change.png", dpi=150)
plt.close()

# Chart 3: price vs renewable share (dual axis)
pl2 = pl.copy()
pl2["idx"] = range(len(pl2))
fig, ax1 = plt.subplots(figsize=(8,4.5), dpi=150)
ax2 = ax1.twinx()
ax1.bar(pl2["idx"], pl2["renewable_share_pct"], color="#c6f6d5", label="Renewable share (%)", width=0.7)
ax2.plot(pl2["idx"], pl2["avg_price_eur_mwh"], color=BLUE, marker='o', linewidth=2, label="Avg day-ahead price (EUR/MWh)")
ax1.set_ylabel("Renewable share (%)", color=GREEN)
ax2.set_ylabel("Avg day-ahead price (EUR/MWh)", color=BLUE)
ax1.set_xticks(pl2["idx"][::2])
ax1.set_xticklabels(pl2["month"][::2], rotation=45, ha='right', fontsize=8)
ax1.set_title("Low Renewable Share Months Line Up With Price Spikes\n(the 'Dunkelflaute' effect)", fontsize=12, fontweight='bold')
ax1.spines[['top']].set_visible(False)
ax2.spines[['top']].set_visible(False)
fig.legend(loc='upper center', bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=False)
plt.tight_layout()
plt.savefig("price_vs_renewable_share.png", dpi=150)
plt.close()

print("charts done")
