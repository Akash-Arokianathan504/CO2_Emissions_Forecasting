# src/co2_emissions/viz.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def visualize_nulls(df: pd.DataFrame):
    null_counts = df.isnull().sum()
    null_counts = null_counts[null_counts > 0]
    if null_counts.empty:
        print("No missing values in the dataset!")
        return
    plt.figure(figsize=(12, 6))
    null_counts.plot(kind="bar")
    plt.title("Null Value Count by Column")
    plt.xlabel("Columns"); plt.ylabel("Number of Null Values"); plt.tight_layout(); plt.show()

def correlation_heatmap(df: pd.DataFrame, fig_size=(12, 10)):
    numeric = df.select_dtypes(include=["float64", "int64"])
    plt.figure(figsize=fig_size)
    sns.heatmap(numeric.corr(), annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
    plt.title("Correlation Matrix Heatmap"); plt.tight_layout(); plt.show()

def plot_distributions_grid(df: pd.DataFrame, n_cols=3):
    numeric = df.select_dtypes(include=["float64", "int64"]).columns
    n_rows = -(-len(numeric) // n_cols)
    plt.figure(figsize=(n_cols * 5, n_rows * 5))
    for i, col in enumerate(numeric, 1):
        plt.subplot(n_rows, n_cols, i)
        sns.histplot(df[col].dropna(), kde=True, bins=30)
        plt.title(col); plt.xlabel(""); plt.ylabel("Frequency")
    plt.tight_layout(); plt.show()

def plot_log_distributions_grid(df: pd.DataFrame, n_cols=3):
    import numpy as np
    numeric = df.select_dtypes(include=["float64", "int64"]).columns
    n_rows = -(-len(numeric) // n_cols)
    plt.figure(figsize=(n_cols * 5, n_rows * 5))
    for i, col in enumerate(numeric, 1):
        plt.subplot(n_rows, n_cols, i)
        data = df[col].dropna()
        data = data[data > 0].apply(np.log)
        sns.histplot(data, kde=True, bins=30)
        plt.title(f"Log({col})"); plt.xlabel(""); plt.ylabel("Frequency")
    plt.tight_layout(); plt.show()

def plot_global_trend(df: pd.DataFrame, col="Annual_CO₂_emissions"):
    ax = df.groupby("year")[col].sum().plot(kind="line", marker="o", title=f"Global {col} Over Time", figsize=(10, 6))
    ax.set_ylabel(col); ax.set_xlabel("Year"); plt.grid(True); plt.show()

def plot_top_emitters(df: pd.DataFrame, n=10, col="Annual_CO₂_emissions"):
    top = df.groupby("country")[col].sum().nlargest(n)
    top.plot(kind="bar", figsize=(10, 6), title=f"Top {n} CO₂ Emitting Countries")
    plt.ylabel(col); plt.xlabel("Country"); plt.show()

def plot_forecast(years, hist_log_values, all_years, mean_pred, pi_sigma=None, title="Forecast"):
    import numpy as np
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
    plt.title(title); plt.xlabel("Year"); plt.ylabel("Value"); plt.legend(); plt.grid(); plt.show()
