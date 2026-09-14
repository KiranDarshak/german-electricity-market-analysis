import sys
sys.path.insert(0, 'data')
from raw_series import raw
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------- BRONZE: raw ingestion ----------------
rows = []
for series_name, points in raw.items():
    for ts, val in points:
        rows.append({"series": series_name, "timestamp_ms": int(ts), "value": val})
bronze = pd.DataFrame(rows)
bronze.to_csv("data/bronze_raw_series.csv", index=False)

# ---------------- SILVER: cleaned / standardized ----------------
silver = bronze.copy()
silver["month"] = pd.to_datetime(silver["timestamp_ms"], unit="ms", utc=True).dt.tz_convert("Europe/Berlin").dt.to_period("M").astype(str)
silver["year"] = silver["month"].str[:4].astype(int)

label_map = {
    "braunkohle_lignite": "Lignite (Braunkohle)",
    "steinkohle_hardcoal": "Hard coal (Steinkohle)",
    "erdgas_naturalgas": "Natural gas (Erdgas)",
    "wind_onshore": "Wind onshore",
    "wind_offshore": "Wind offshore",
    "photovoltaik_solar": "Solar (Photovoltaik)",
    "stromverbrauch_total_load": "Total load (consumption)",
    "marktpreis_de_lu_eur_mwh": "Day-ahead price DE/LU",
}
silver["label"] = silver["series"].map(label_map)

# Unit conversion: generation/consumption filters are in MWh -> convert to GWh for readability
gen_series = [s for s in raw if s not in ("marktpreis_de_lu_eur_mwh",)]
silver.loc[silver["series"].isin(gen_series), "value_gwh"] = silver.loc[silver["series"].isin(gen_series), "value"] / 1000.0
silver.loc[silver["series"] == "marktpreis_de_lu_eur_mwh", "price_eur_mwh"] = silver.loc[silver["series"] == "marktpreis_de_lu_eur_mwh", "value"]
silver.to_csv("data/silver_standardized.csv", index=False)

# ---------------- GOLD: dimensional marts ----------------
GENERATION_SOURCES = ["braunkohle_lignite","steinkohle_hardcoal","erdgas_naturalgas","wind_onshore","wind_offshore","photovoltaik_solar"]
RENEWABLE = {"wind_onshore","wind_offshore","photovoltaik_solar"}
FOSSIL = {"braunkohle_lignite","steinkohle_hardcoal","erdgas_naturalgas"}

gen = silver[silver["series"].isin(GENERATION_SOURCES)].copy()

# mart 1: generation mix by month (GWh) + renewable share
mix = gen.pivot_table(index="month", columns="label", values="value_gwh", aggfunc="sum").fillna(0)
mix["total_tracked_gwh"] = mix.sum(axis=1)
renew_cols = [label_map[s] for s in RENEWABLE]
fossil_cols = [label_map[s] for s in FOSSIL]
mix["renewable_gwh"] = mix[renew_cols].sum(axis=1)
mix["fossil_gwh"] = mix[fossil_cols].sum(axis=1)
mix["renewable_share_pct"] = (mix["renewable_gwh"] / mix["total_tracked_gwh"] * 100).round(2)
mix = mix.reset_index()
mix["year"] = mix["month"].str[:4].astype(int)
mix.to_csv("data/mart_generation_mix_monthly.csv", index=False)

# mart 2: YoY comparison per source (2024 total vs 2025 total, GWh)
yoy = gen.groupby(["label","year"])["value_gwh"].sum().unstack("year")
yoy.columns = [f"gwh_{c}" for c in yoy.columns]
yoy["yoy_change_pct"] = ((yoy["gwh_2025"] - yoy["gwh_2024"]) / yoy["gwh_2024"] * 100).round(2)
yoy = yoy.reset_index()
yoy.to_csv("data/mart_yoy_generation_by_source.csv", index=False)

# mart 3: price mart - monthly avg day-ahead price + total load, with simple price/load correlation input
price = silver[silver["series"]=="marktpreis_de_lu_eur_mwh"][["month","price_eur_mwh"]].rename(columns={"price_eur_mwh":"avg_price_eur_mwh"})
load = silver[silver["series"]=="stromverbrauch_total_load"][["month","value_gwh"]].rename(columns={"value_gwh":"total_load_gwh"})
renew_share = mix[["month","renewable_share_pct"]]
price_mart = price.merge(load, on="month").merge(renew_share, on="month").sort_values("month")
price_mart.to_csv("data/mart_price_load_renewables.csv", index=False)

print("Bronze rows:", len(bronze))
print("Silver rows:", len(silver))
print(mix[["month","renewable_share_pct"]].to_string(index=False))
print(yoy.to_string(index=False))
print(price_mart.to_string(index=False))
