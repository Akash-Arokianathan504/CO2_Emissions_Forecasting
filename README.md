[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## CO₂ Emissions: Bayesian Regression & Forecasting

This project analyzes and forecasts CO₂ emissions using Bayesian regression models with a Student’s t-distribution for robustness against outliers.  
The workflow covers **data ingestion, cleaning, exploratory data analysis (EDA), modeling, and forecasting**, focusing on predictors strongly correlated with emissions such as GDP and deforestation.

---

#### 📂 Repository Structure

```text
co2-emissions-forecasting/
├─ README.md
├─ .gitignore
├─ requirements.txt / pyproject.toml
├─ data/
│  ├─ raw/         # Original datasets (CSV, unmodified)
│  └─ processed/   # Cleaned, ready-to-model data
├─ notebooks/
│  └─ co2_forecasting_end_to_end.ipynb   # Full pipeline on notebook -sequential run
├─ reports/
│  ├─ figures/     # Plots for reports
│  └─ results/     # Metrics, tables, model cards(if implemented)
├─ src/co2_emissions/
│  ├─ __init__.py
│  ├─ data.py      # Data loading, cleaning, merging
│  ├─ features.py  # Feature engineering utilities
│  ├─ modeling.py  # Statistical & Bayesian models
│  └─ viz.py       # Plotting functions
├─ scripts/
│  ├─ make_dataset.py  # CLI: Build processed dataset
│  ├─ train.py         # CLI: Train models
│  ├─ forecast.py      # CLI: Forecast & plot results
│  └─ run.sh           # End-to-end runner script
├─ models/             # Saved model traces
└─ tests/              # Unit tests (if implemented)
```

### 🚀 Quickstart
### Clone the repository:

    git clone https://github.com/Akash-Arokianathan504/CO2_Emissions_Forecasting.git
    cd co2-emissions-forecasting

### Install dependencies:

pip install -r requirements.txt

### Run the entire pipeline (end-to-end):

    ./scripts/run.sh --pop-country Latvia --co2-country China --horizon 10


📊 Workflow (Inside run.sh)

    Step 1: Build cleaned dataset from data/raw/

    Step 2: Train models (pop-trend for population, co2-gdp for emissions vs GDP)

    Step 3: Forecast CO₂ emissions for a given country and horizon

You can override defaults with flags:

    ./scripts/run.sh --raw data/raw --processed data/processed \
                    --pop-country India --co2-country UnitedStates \
                    --horizon 15


                           
### 📈 Example Outputs

EDA: Correlation heatmaps, distribution plots (log & raw)
Model Fits: Posterior parameter estimates from Bayesian regression
Forecasts: 10-year predictions with credible intervals
Insights: Top emitters, deforestation intensity trends

### 📓 Interactive Walkthrough  
For a step-by-step end-to-end demonstration of this project, see the [Full Pipeline Notebook](notebook/co2_forecasting_end_to_end.ipynb).  


### 🛠 CLI Commands Overview

Command								Description
python scripts/make_dataset.py	    Build cleaned dataset from raw CSVs
python scripts/train.py	            Train Bayesian model (pop-trend or co2-gdp)
python scripts/forecast.py	        Forecast and plot results from a trained model

### 📜 Methods

EDA: Data completeness checks, null interpolation, correlation analysis, log transformations.
Modeling: Bayesian regression with PyMC using Student’s t-distribution for heavy-tailed data; GDP and year as predictors.
Evaluation: R², MSE, and visual inspection of prediction intervals.

### 📚 Dependencies

Python 3.10+
pandas, numpy, matplotlib, seaborn
PyMC, ArviZ, scipy, scikit-learn

### 📜 License
MIT License — see LICENSE for details.

### 🙌 Acknowledgements
Data sourced from Our World in Data and other open sources.