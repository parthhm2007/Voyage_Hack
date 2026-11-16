# Phase 2: XGBoost Demand Model — Research

**Status:** Research Complete  
**Date:** 2026-11-16  
**Requirement:** ML-01  

## 1. Executive Summary
Phase 2 builds an offline machine learning training script that reads historical daily records (`daily_history.csv`), engineers robust temporal and behavioral features (while strictly excluding `true_demand`), trains XGBoost quantile regression models for P10, P50, and P90 demand quantiles using `reg:quantileerror`, evaluates performance on a chronological train/validation split, and saves model artifacts (e.g., via `joblib` or native XGBoost JSON/binary format) into `./backend/models/` for downstream inference API usage in Phase 3.

---

## 2. Dataset & Feature Engineering (`daily_history.csv`)
- **Dataset schema:** `date`, `item_id`, `searches`, `true_demand`, `bookings`, `sold_out_flag`, `cancellations`, `sell_price`, `supplier_cost`, `lead_days`.
- **Target Variable:** `bookings` (or censored demand proxy). Note: `true_demand` is strictly forbidden as a feature or target during training/inference per data privacy and realism constraints.
- **Feature Engineering Plan:**
  - *Temporal features:* `day_of_week`, `month`, `day_of_month`, `is_weekend`.
  - *Lag features:* 7-day and 14-day lagged `bookings` and `searches` per `item_id`.
  - *Rolling statistics:* 7-day rolling mean and standard deviation of `bookings` and `searches` per `item_id`.
  - *Commercial features:* `sell_price`, `supplier_cost`, `lead_days`, gross margin (`sell_price - supplier_cost`).
  - *Categorical encoding:* One-hot or target encoding for `item_id` (or using XGBoost native categorical support / item embedding).

---

## 3. Modeling Architecture (XGBoost Quantile Regression)
- **Library:** `xgboost` (Python package).
- **Objective:** `reg:quantileerror` for alpha levels:
  - `alpha = 0.10` (P10 - pessimistic demand)
  - `alpha = 0.50` (P50 - median/expected demand)
  - `alpha = 0.90` (P90 - optimistic demand)
- **Train/Validation Split Strategy:**
  - Time-based split: Sort historical data chronologically by `date`.
  - Use the first 80% of dates for training and the last 20% for validation to prevent data leakage and simulate real-world forecasting.
- **Evaluation Metric:** Pinball loss (quantile loss) evaluated across the validation set for each quantile.

---

## 4. Pipeline Script & Persistence
- **Training Script Location:** `backend/train_models.py` (or similar script executable via python).
- **Artifact Output Directory:** `backend/models/`
- **Saved Artifacts:**
  - Quantile models (`model_p10.json`, `model_p50.json`, `model_p90.json` or joblib bundle).
  - Feature scaler/metadata if necessary.

---

## 5. Success Criteria & Validation
1. Training script successfully executes without errors, processing `daily_history.csv`.
2. Time-based train/validation split correctly computes pinball loss for P10, P50, and P90.
3. `true_demand` is successfully excluded from features and targets.
4. Model artifacts are successfully saved to `./backend/models/` and can be loaded successfully by backend helper functions.

## RESEARCH COMPLETE
