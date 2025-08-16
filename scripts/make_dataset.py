#!/usr/bin/env python
# scripts/make_dataset.py
# --- allow running this script directly from repo root ---
import os, sys
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(REPO_ROOT, "src")
for p in (REPO_ROOT, SRC_PATH):
    if p not in sys.path:
        sys.path.insert(0, p)

from pathlib import Path
import argparse
from co2_emissions import data as D

def main(args):
    raw = Path(args.source)
    processed = Path(args.out)

    # --- read raw files ---
    co2_emission_data    = D.read_csv(raw / "owid-co2-data.csv")
    deforestation_data   = D.read_csv(raw / "annual-deforestation.csv")
    temperature_data     = D.read_csv(raw / "annual-temperature-anomalies.csv")
    precip_data          = D.read_csv(raw / "average-precipitation-per-year.csv")
    co2_fossil_land_data = D.read_csv(raw / "co2-fossil-plus-land-use.csv")
    drought_data         = D.read_csv(raw / "Drought affected annual number.csv")
    gdp_data             = D.read_csv(raw / "GDP By Country.csv")
    land_usage_data      = D.read_csv(raw / "land-use-over-the-long-term.csv")
    co2_sector_data      = D.read_csv(raw / "per-capita-co2-sector.csv")
    exclude_countries    = D.read_csv(raw / "refined_countries.csv")

    cohort = D.build_master_cohort(co2_emission_data, exclude_countries)
    master = D.assemble_master(cohort, deforestation_data, co2_emission_data, temperature_data,
                               precip_data, co2_fossil_land_data, drought_data, gdp_data,
                               land_usage_data, co2_sector_data)
    filtered = D.filter_years_and_columns(master, 1990, 2015)
    cleaned = D.clean_interpolate(filtered)

    D.save_csv(cleaned, processed / "Master_filtered_df_cleaned.csv")
    cleaned.sample(min(500, len(cleaned))).to_csv(processed / "sample.csv", index=False)

    print(f"✅ Saved: {processed/'Master_filtered_df_cleaned.csv'}  (rows={len(cleaned):,})")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", default="data/raw")
    p.add_argument("--out", default="data/processed")
    main(p.parse_args())
