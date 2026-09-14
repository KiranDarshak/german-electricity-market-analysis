# German Electricity Market Analysis (2024–2025)

A Bronze → Silver → Gold analytics pipeline built on real, public generation, consumption and day-ahead price data from **Bundesnetzagentur / SMARD** (Germany's federal electricity market data platform), tracking the country's energy transition month by month across 2024 and 2025.

## Tools

Python · Pandas · SMARD REST API (`smard.de/app/chart_data`) · matplotlib — pipeline structured to map directly onto a GCP BigQuery + dbt Medallion setup (Bronze/Silver/Gold), same architecture as my [German Motorcycle Market Analysis](https://github.com/KiranDarshak/germany-motorcycle-market-analysis) project.

## Data source

[SMARD.de](https://www.smard.de) — Bundesnetzagentur's official electricity market data platform, published under CC BY 4.0. Monthly generation (MWh) for six sources, total system load, and the average DE/LU day-ahead auction price, January 2024 through December 2025 (24 months).

## Pipeline

- **Bronze** (`data/bronze_raw_series.csv`) — raw [timestamp, value] pairs as returned by the SMARD API, one row per series per month.
- **Silver** (`data/silver_standardized.csv`) — cleaned, timezone-corrected (Europe/Berlin), unit-converted to GWh, human-readable labels.
- **Gold** — three dimensional marts:
  - `mart_generation_mix_monthly.csv` — monthly generation mix and renewable share %
  - `mart_yoy_generation_by_source.csv` — 2024 vs 2025 annual totals and YoY % change per source
  - `mart_price_load_renewables.csv` — monthly avg day-ahead price, total load, and renewable share together

## Key findings

- **Solar had the strongest year of any source**: +16.8% generation growth in 2025 vs 2024, far ahead of natural gas (+6.4%) and hard coal (+3.0%).
- **Lignite (-5.4%) and onshore wind (-5.2%) both declined** — coal continuing its structural phase-down, while onshore wind simply had a weaker wind year.
- **Renewable share swung from 39.7% to 74.4% month to month** — June 2025 was the greenest month on record in this dataset (74.4%), while February 2025 was the least green (39.7%), a wider spread than the same months in 2024.
- **The "Dunkelflaute" effect shows up clearly in price data**: February 2025's renewable dip (39.7%) coincided with the highest average day-ahead price in the two-year window (€128.52/MWh) — low wind-and-solar months are consistently the most expensive months, in both 2024 and 2025.

## Repo structure

```
data/
  bronze_raw_series.csv
  silver_standardized.csv
  mart_generation_mix_monthly.csv
  mart_yoy_generation_by_source.csv
  mart_price_load_renewables.csv
  raw_series.py              # raw SMARD API pull, source of truth for bronze layer
build_pipeline.py            # Bronze -> Silver -> Gold transform
make_charts.py                # chart generation
renewable_share_2024_2025.png
yoy_generation_change.png
price_vs_renewable_share.png
README.md
```

## Notes on data

Generation totals cover the six SMARD filters with the most complete 2024-2025 history (lignite, hard coal, natural gas, onshore wind, offshore wind, solar); smaller categories (biomass, hydro, pumped storage, "other") are not included, so renewable/fossil shares are relative to this tracked subset, not all of German generation. All figures pulled directly from the SMARD API on 2026-09-14 and not modified beyond unit conversion (MWh → GWh) and timezone localization.
