# src/co2_emissions/features.py
from __future__ import annotations
import numpy as np
import pandas as pd

def log_safe(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    return np.log(s.where(s > 0))

def add_deforestation_intensity(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    denom = df["Annual_CO₂_emissions_including_land-use_change"].replace(0, np.nan)
    df["deforestation_intensity"] = df["Deforestation"] / denom
    return df

def country_panel(df: pd.DataFrame, country: str) -> pd.DataFrame:
    out = df[df["country"] == country].sort_values("year").reset_index(drop=True).copy()
    return out
