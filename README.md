CO₂ Emissions: Bayesian Regression & Forecasting
This project analyzes and forecasts CO₂ emissions using Bayesian regression models with a Student’s t-distribution for robustness against outliers.
The workflow covers data ingestion, cleaning, exploratory data analysis (EDA), modeling, and forecasting, focusing on predictors strongly correlated with emissions such as GDP and deforestation.

📂 Repository Structure
graphql
Copy
Edit
co2-emissions-forecasting/
├─ README.md
├─ .gitignore
├─ requirements.txt / pyproject.toml
├─ data/
│  ├─ raw/         # Original datasets (CSV, unmodified)
│  ├─ processed/   # Cleaned, ready-to-model data
├─ notebooks/
│  ├─ 10-eda.ipynb
│  ├─ 20-modeling-bayes-trend.ipynb
│  └─ 30-co2-gdp-forecast.ipynb
├─ reports/
│  ├─ figures/     # Plots for README & reports
│  └─ results/     # Metrics, tables, model cards
├─ src/co2_emissions/
│  ├─ __init__.py
│  ├─ data.py      # Data loading, cleaning, merging
│  ├─ features.py  # Feature engineering utilities
│  ├─ modeling.py  # Statistical & Bayesian models
│  ├─ viz.py       # Plotting functions
├─ scripts/
│  ├─ make_dataset.py  # CLI: Build processed dataset
│  ├─ train.py         # CLI: Train models
│  ├─ forecast.py      # CLI: Forecast & plot results
├─ models/             # Saved model traces
└─ tests/              # Unit tests (if implemented)

🚀 Quickstart

1. Clone the repository:

git clone https://github.com/YOUR_USERNAME/co2-emissions-forecasting.git
cd co2-emissions-forecasting

2. Install dependencies:

pip install -r requirements.txt

📊 Workflow

Step 1 — Place raw datasets in data/raw/

Required CSV files include:

owid-co2-data.csv
annual-deforestation.csv
annual-temperature-anomalies.csv
average-precipitation-per-year.csv
co2-fossil-plus-land-use.csv
Drought affected annual number.csv
GDP By Country.csv
land-use-over-the-long-term.csv
per-capita-co2-sector.csv
refined_countries.csv

Step 2 — Build cleaned dataset:

python scripts/make_dataset.py --source data/raw --out data/processed

Step 3 — Train models:

Population trend model:
python scripts/train.py --data data/processed/Master_filtered_df_cleaned.csv \
                        --models models \
                        --country Latvia \
                        --model pop-trend
CO₂ vs GDP + Year model:
python scripts/train.py --data data/processed/Master_filtered_df_cleaned.csv \
                        --models models \
                        --country China \
                        --model co2-gdp

Step 4 — Forecast:

python scripts/forecast.py --data data/processed/Master_filtered_df_cleaned.csv \
                           --trace models/China_co2_gdp.nc \
                           --country China \
                           --horizon 10
                           
📈 Example Outputs

EDA: Correlation heatmaps, distribution plots (log & raw)
Model Fits: Posterior parameter estimates from Bayesian regression
Forecasts: 10-year predictions with credible intervals
Insights: Top emitters, deforestation intensity trends

🛠 CLI Commands Overview

Command								Description
python scripts/make_dataset.py	Build cleaned dataset from raw CSVs
python scripts/train.py	Train Bayesian model (pop-trend or co2-gdp)
python scripts/forecast.py	Forecast and plot results from a trained model

📜 Methods

EDA: Data completeness checks, null interpolation, correlation analysis, log transformations.
Modeling: Bayesian regression with PyMC using Student’s t-distribution for heavy-tailed data; GDP and year as predictors.
Evaluation: R², MSE, and visual inspection of prediction intervals.

📚 Dependencies

Python 3.10+
pandas, numpy, matplotlib, seaborn
PyMC, ArviZ, scipy, scikit-learn

📜 License
MIT License — see LICENSE for details.

🙌 Acknowledgements
Data sourced from Our World in Data and other open sources.