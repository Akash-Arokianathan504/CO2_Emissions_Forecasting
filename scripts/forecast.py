#!/usr/bin/env python
# scripts/forecast.py
import os, sys
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(REPO_ROOT, "src")
for p in (REPO_ROOT, SRC_PATH):
    if p not in sys.path:
        sys.path.insert(0, p)

import argparse
import numpy as np
import pandas as pd
import arviz as az
import matplotlib.pyplot as plt
from pathlib import Path
from co2_emissions.features import country_panel, log_safe

def plot_forecast(years, hist_log_values, all_years, mean_pred, pi_sigma=None,
                  title="Forecast", save_path=None, show=True):
    plt.figure(figsize=(12, 6))
    plt.plot(years, np.exp(hist_log_values), label="Historical", marker="o")
    plt.plot(all_years, np.exp(mean_pred), label="Forecast", linestyle="--")
    if pi_sigma is not None:
        future_mask = all_years > years.max()
        future_years = all_years[future_mask]
        mean_future = mean_pred[-len(future_years):]
        plt.fill_between(future_years,
                         np.exp(mean_future - pi_sigma),
                         np.exp(mean_future + pi_sigma),
                         alpha=0.2, label="Prediction Interval")
    plt.axvline(x=years.max(), color="gray", linestyle="--")
    plt.title(title); plt.xlabel("Year"); plt.ylabel("Value"); plt.legend(); plt.grid()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"✅ Saved figure → {save_path}")
    if show:
        plt.show()
    else:
        plt.close()

def main(args):
    df = pd.read_csv(args.data)
    cp = country_panel(df, args.country)
    trace = az.from_netcdf(args.trace)
    years = cp["year"].values

    if "slope" in trace.posterior:  # pop-trend
        hist_log = log_safe(cp["population"]).values
        all_years = np.arange(years.min(), years.max() + args.horizon + 1)
        years_c = all_years - years.mean()
        intercept = trace.posterior["intercept"].mean(dim=["chain","draw"]).values
        slope = trace.posterior["slope"].mean(dim=["chain","draw"]).values
        mean_pred = intercept + slope * years_c
        sigma = trace.posterior["sigma"].mean().values
        model_tag = "pop_trend"
        title = f"Population Forecast: {args.country}"
    else:  # co2-gdp
        hist_log = log_safe(cp["Annual_CO₂_emissions"]).values
        log_gdp = log_safe(cp["GDP"]).values
        future_years = np.arange(years[-1] + 1, years[-1] + 1 + args.horizon)
        gdp_trend = np.linspace(log_gdp[-1], log_gdp[-1] * 1.05, len(future_years))
        all_years = np.concatenate([years, future_years])
        years_c = all_years - years.mean()
        all_gdp = np.concatenate([log_gdp, gdp_trend])
        gdp_c = all_gdp - np.nanmean(log_gdp)
        intercept = trace.posterior["intercept"].mean(dim=["chain","draw"]).values
        slope_year = trace.posterior["slope_year"].mean(dim=["chain","draw"]).values
        slope_gdp = trace.posterior["slope_gdp"].mean(dim=["chain","draw"]).values
        mean_pred = intercept + slope_year * years_c + slope_gdp * gdp_c
        sigma = trace.posterior["sigma"].mean().values
        model_tag = "co2_gdp"
        title = f"CO₂ Forecast w/ GDP: {args.country}"

    # save path (if provided)
    save_path = None
    if args.save_dir:
        save_path = os.path.join(args.save_dir, f"forecast_{args.country}_{model_tag}.png")

    plot_forecast(years, hist_log, all_years, mean_pred, pi_sigma=sigma,
                  title=title, save_path=save_path, show=not args.no_show)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/processed/Master_filtered_df_cleaned.csv")
    p.add_argument("--trace", required=True)
    p.add_argument("--country", default="China")
    p.add_argument("--horizon", type=int, default=10)
    p.add_argument("--save_dir", default="reports/results")
    p.add_argument("--no_show", action="store_true", help="Save figure without popping a window")
    args = p.parse_args()
    main(args)
