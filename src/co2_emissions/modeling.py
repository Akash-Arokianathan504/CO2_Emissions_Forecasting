# src/co2_emissions/modeling.py
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import t as student_t, ks_2samp
import pymc as pm
import arviz as az

# ----- Distribution utilities -----
def fit_student_t_params(series: pd.Series):
    data = series.dropna().astype(float)
    df, loc, scale = student_t.fit(data)
    return {"df": df, "loc": loc, "scale": scale}

def synthetic_from_t(params: dict, size: int = 1000):
    return student_t.rvs(params["df"], params["loc"], params["scale"], size=size)

def ks_test_ref(series: pd.Series, synthetic: np.ndarray):
    s = series.dropna().astype(float)
    return ks_2samp(s, synthetic)

# ----- Bayesian models -----
def bayes_trend_student_t(years: np.ndarray, y_log: np.ndarray,
                          random_seed: int = 42, draws: int = 2000, tune: int = 1000):
    years_c = years - years.mean()
    with pm.Model() as model:
        intercept = pm.Normal("intercept", mu=np.nanmean(y_log), sigma=5)
        slope = pm.Normal("slope", mu=0, sigma=1)
        sigma = pm.HalfNormal("sigma", sigma=1)
        nu = pm.Exponential("nu", lam=1)
        mean = intercept + slope * years_c
        pm.StudentT("likelihood", mu=mean, sigma=sigma, nu=nu, observed=y_log)
        trace = pm.sample(draws, tune=tune, return_inferencedata=True,
                          target_accept=0.9, random_seed=random_seed)
    return model, trace

def bayes_co2_gdp(years: np.ndarray, log_co2: np.ndarray, log_gdp: np.ndarray,
                  random_seed: int = 42, draws: int = 2000, tune: int = 1000):
    years_c = years - years.mean()
    gdp_c = log_gdp - np.nanmean(log_gdp)
    with pm.Model() as model:
        intercept = pm.Normal("intercept", mu=np.nanmean(log_co2), sigma=5)
        slope_gdp = pm.Normal("slope_gdp", mu=0, sigma=1)
        slope_year = pm.Normal("slope_year", mu=0, sigma=1)
        sigma = pm.HalfNormal("sigma", sigma=1)
        nu = pm.Exponential("nu", lam=1)
        mean = intercept + slope_gdp * gdp_c + slope_year * years_c
        pm.StudentT("likelihood", mu=mean, sigma=sigma, nu=nu, observed=log_co2)
        trace = pm.sample(draws, tune=tune, return_inferencedata=True,
                          target_accept=0.9, random_seed=random_seed)
    return model, trace
