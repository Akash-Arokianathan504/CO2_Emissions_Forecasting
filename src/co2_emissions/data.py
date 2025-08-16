# src/co2_emissions/data.py
from __future__ import annotations
from pathlib import Path
import pandas as pd

# ---------------- IO ----------------
def read_csv(path: Path | str) -> pd.DataFrame:
    return pd.read_csv(path)

def save_csv(df: pd.DataFrame, path: Path | str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

# ------------- Helpers --------------
def _drop_code_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Drop generic 'Code' columns that collide during merges (retain iso_code)."""
    drop_these = [c for c in df.columns
                  if c.lower() in {"code", "code_x", "code_y", "country code", "indicator code"}]
    return df.drop(columns=drop_these, errors="ignore")

def melt_wide_year(df: pd.DataFrame, id_col: str, value_name: str = "Value") -> pd.DataFrame:
    out = df.melt(id_vars=[id_col], var_name="Year", value_name=value_name)
    out["Year"] = pd.to_numeric(out["Year"], errors="coerce").astype("Int64")
    return out

# ---------- Build Master -----------
def build_master_cohort(co2_emission_data: pd.DataFrame,
                        exclude_countries: pd.DataFrame,
                        year_min: int = 1980, year_max: int = 2018) -> pd.DataFrame:
    cohort = co2_emission_data[["country", "year", "iso_code"]].copy()
    cohort["year"] = pd.to_numeric(cohort["year"], errors="coerce")
    cohort = (cohort
              .query(f"{year_min} <= year <= {year_max}")
              .sort_values(["country", "year"])
              .drop_duplicates())
    allow = set(exclude_countries["Country"].astype(str).tolist())
    cohort = cohort[cohort["country"].astype(str).isin(allow)].reset_index(drop=True)
    return cohort

def assemble_master(
    cohort: pd.DataFrame,
    deforestation: pd.DataFrame,
    co2_emissions: pd.DataFrame,
    temperature: pd.DataFrame,
    precipitation: pd.DataFrame,
    co2_fossil_land: pd.DataFrame,
    drought_wide: pd.DataFrame,
    gdp_wide: pd.DataFrame,
    land_usage: pd.DataFrame,
    co2_sector: pd.DataFrame
) -> pd.DataFrame:
    # Wide → long
    drought_p = melt_wide_year(drought_wide, id_col="Drought affected") \
        .rename(columns={"Drought affected": "country", "Year": "year"})
    gdp_p = gdp_wide.melt(
        id_vars=["Country Name", "Country Code", "Indicator Name", "Indicator Code"],
        var_name="Year", value_name="GDP"
    )
    gdp_p["Year"] = pd.to_numeric(gdp_p["Year"], errors="coerce").astype("Int64")
    gdp_p = gdp_p.rename(columns={"Country Name": "country", "Year": "year"})

    # Normalize RHS frames & drop generic 'Code' columns
    defo   = _drop_code_cols(deforestation.rename(columns={"Entity": "country", "Year": "year"}))
    temp   = _drop_code_cols(temperature.rename(columns={"Entity": "country", "Year": "year"}))
    precip = _drop_code_cols(precipitation.rename(columns={"Entity": "country", "Year": "year"}))
    fossil = _drop_code_cols(co2_fossil_land.rename(columns={"Entity": "country", "Year": "year"}))
    land   = _drop_code_cols(land_usage.rename(columns={"Entity": "country", "Year": "year"}))
    sector = _drop_code_cols(co2_sector.rename(columns={"Entity": "country", "Year": "year"}))
    co2    = _drop_code_cols(co2_emissions)
    left   = _drop_code_cols(cohort)

    # Merge
    master = (
        left
        .merge(defo,   on=["country", "year"], how="left")
        .merge(co2,    on=["country", "year", "iso_code"], how="left")
        .merge(temp,   on=["country", "year"], how="left")
        .merge(precip, on=["country", "year"], how="left")
        .merge(fossil, on=["country", "year"], how="left")
        .merge(drought_p, on=["country", "year"], how="left")
        .merge(gdp_p,  on=["country", "year"], how="left")
        .merge(land,   on=["country", "year"], how="left")
        .merge(sector, on=["country", "year"], how="left")
    )

    # Belt-and-suspenders cleanup
    dup_suffix_cols = [c for c in master.columns if c.endswith(("_x", "_y"))]
    master = master.drop(columns=dup_suffix_cols, errors="ignore")
    return master

# ------ Filter & Clean -------
COLUMNS_TO_KEEP = [
    "country", "year", "Deforestation", "Temperature_anomaly",
    "Annual_precipitation", "co2",
    "Annual_CO₂_emissions_including_land-use_change",
    "Annual_CO₂_emissions_from_land-use_change", "Annual_CO₂_emissions", "population",
    "GDP", "Per_capita_carbon_dioxide_emissions_from_buildings",
    "Per_capita_carbon_dioxide_emissions_from_electricity_and_heat",
    "Per_capita_carbon_dioxide_emissions_from_industry",
    "Per_capita_carbon_dioxide_emissions_from_bunker_fuels",
    "Per_capita_carbon_dioxide_emissions_from_land_use_change_and_forestry",
    "Per_capita_carbon_dioxide_emissions_from_transport",
    "Per_capita_carbon_dioxide_emissions_from_manufacturing_and_construction",
    "Per_capita_carbon_dioxide_emissions_from_other_fuel_combustion",
]

def filter_years_and_columns(master: pd.DataFrame,
                             year_min: int = 1990, year_max: int = 2015,
                             keep_cols: list[str] | None = None) -> pd.DataFrame:
    keep_cols = keep_cols or COLUMNS_TO_KEEP
    df = master.copy()
    df.columns = df.columns.str.replace(" ", "_")
    available = [c for c in keep_cols if c in df.columns]
    return df.query(f"{year_min} <= year <= {year_max}")[available]

def clean_interpolate(df: pd.DataFrame, round_decimals: int = 2) -> pd.DataFrame:
    df = df.copy()
    cols_to_check = df.columns.difference(["Deforestation"])
    df = df.dropna(subset=cols_to_check).round(round_decimals)
    return df.interpolate(method="linear", limit_direction="both", axis=0)
