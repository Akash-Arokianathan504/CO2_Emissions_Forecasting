#!/usr/bin/env bash
set -euo pipefail

# -------------------------------
# CO2 Emissions: end-to-end runner
# -------------------------------
# Usage:
#   ./run.sh
#   ./run.sh --raw data/raw --processed data/processed \
#            --pop-country Latvia --co2-country China \
#            --horizon 10
#
# Notes:
# - Assumes your scripts live in ./scripts and models save to ./models
# - Adjust defaults below if your paths differ

# -------- Defaults ----------
RAW_DIR="data/raw"
PROCESSED_DIR="data/processed"
DATASET="${PROCESSED_DIR}/Master_filtered_df_cleaned.csv"
MODELS_DIR="models"

POP_COUNTRY="Latvia"   # for the population trend model
CO2_COUNTRY="China"    # for the CO2 ~ GDP + Year model
HORIZON=10

# ------ Parse flags --------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --raw) RAW_DIR="$2"; shift 2 ;;
    --processed) PROCESSED_DIR="$2"; DATASET="${PROCESSED_DIR}/Master_filtered_df_cleaned.csv"; shift 2 ;;
    --pop-country) POP_COUNTRY="$2"; shift 2 ;;
    --co2-country) CO2_COUNTRY="$2"; shift 2 ;;
    --horizon) HORIZON="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,60p' "$0"; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# ------ Prep dirs ----------
mkdir -p "${PROCESSED_DIR}" "${MODELS_DIR}"

echo "== Step 2: Build cleaned dataset =="
python scripts/make_dataset.py \
  --source "${RAW_DIR}" \
  --out "${PROCESSED_DIR}"

echo "== Step 3a: Train population trend model (${POP_COUNTRY}) =="
python scripts/train.py \
  --data "${DATASET}" \
  --models "${MODELS_DIR}" \
  --country "${POP_COUNTRY}" \
  --model pop-trend

echo "== Step 3b: Train CO2 ~ GDP + Year model (${CO2_COUNTRY}) =="
python scripts/train.py \
  --data "${DATASET}" \
  --models "${MODELS_DIR}" \
  --country "${CO2_COUNTRY}" \
  --model co2-gdp

TRACE_PATH="${MODELS_DIR}/${CO2_COUNTRY}_co2_gdp.nc"
if [[ ! -f "${TRACE_PATH}" ]]; then
  echo "ERROR: Expected trace not found at ${TRACE_PATH}" >&2
  echo "       Check your train.py saving convention or adjust TRACE_PATH logic." >&2
  exit 2
fi

echo "== Step 4: Forecast (${CO2_COUNTRY}, horizon=${HORIZON}) =="
python scripts/forecast.py \
  --data "${DATASET}" \
  --trace "${TRACE_PATH}" \
  --country "${CO2_COUNTRY}" \
  --horizon "${HORIZON}"

echo "✅ Done."
echo "   Processed data: ${DATASET}"
echo "   Trace:          ${TRACE_PATH}"
