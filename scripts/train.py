#!/usr/bin/env python
# scripts/train.py
import os, sys
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(REPO_ROOT, "src")
for p in (REPO_ROOT, SRC_PATH):
    if p not in sys.path:
        sys.path.insert(0, p)

import argparse
import pandas as pd
import arviz as az
from pathlib import Path
from co2_emissions.features import country_panel, log_safe
from co2_emissions.modeling import bayes_trend_student_t, bayes_co2_gdp

def main(args):
    df = pd.read_csv(args.data)
    out_models = Path(args.models); out_models.mkdir(parents=True, exist_ok=True)

    if args.model == "pop-trend":
        cp = country_panel(df, args.country)
        years = cp["year"].values
        ylog = log_safe(cp["population"]).values
        model, trace = bayes_trend_student_t(years, ylog)
        az_path = out_models / f"{args.country}_pop_trend.nc"

    elif args.model == "co2-gdp":
        cp = country_panel(df, args.country)
        years = cp["year"].values
        log_co2 = log_safe(cp["Annual_CO₂_emissions"]).values
        log_gdp = log_safe(cp["GDP"]).values
        model, trace = bayes_co2_gdp(years, log_co2, log_gdp)
        az_path = out_models / f"{args.country}_co2_gdp.nc"

    else:
        raise ValueError("model must be one of: pop-trend, co2-gdp")

    az.to_netcdf(trace, az_path)
    print(f"✅ Saved trace → {az_path}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/processed/Master_filtered_df_cleaned.csv")
    p.add_argument("--models", default="models")
    p.add_argument("--country", default="China")
    p.add_argument("--model", choices=["pop-trend", "co2-gdp"], default="co2-gdp")
    main(p.parse_args())
