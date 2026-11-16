---
phase: 02-xgboost-demand-model
plan: 01
subsystem: backend
tags: [xgboost, scikit-learn, joblib, ml-pipeline, feature-engineering]
dependency_graph:
  requires: [phase-1-data-loader]
  provides: [xgboost-training-pipeline, quantile-models, model-artifacts, true-demand-isolation]
  affects: [phase-2-model-loader, phase-3-forecasting]
tech-stack:
  added: [xgboost, scikit-learn, joblib]
  patterns: [chronological-split, quantile-regression, feature-engineering-pipeline]
key-files:
  created:
    - backend/train_models.py
    - backend/models/model_p10.json
    - backend/models/model_p50.json
    - backend/models/model_p90.json
    - backend/models/feature_cols.pkl
  modified:
    - requirements.txt
decisions:
  - "Engineered robust temporal, lag (7-day), rolling mean (7-day), and commercial (margin, lead time) features per item_id."
  - "Strictly excluded `true_demand` from feature matrix and target."
  - "Trained XGBoost quantile regressors (`reg:quantileerror`) for alpha values 0.10, 0.50, and 0.90 predicting `bookings`."
metrics:
  duration: "30 minutes"
  completed_date: "2026-11-17"
---

# Phase 2 Plan 1: XGBoost Feature Engineering & Training Pipeline Summary

Built the offline XGBoost training pipeline (`backend/train_models.py`) with feature engineering, chronological train/validation split, quantile regression training, and saved model artifacts.

## Performance Metrics

- **Duration:** ~30 minutes
- **Completed Tasks:** 2 / 2
- **Training Results:** Successfully trained P10, P50, and P90 quantile models with evaluated validation pinball losses.

## Accomplishments

- Updated `requirements.txt` with `xgboost`, `scikit-learn`, and `joblib`.
- Implemented `backend/train_models.py` featuring:
  - Temporal feature extraction (`day_of_week`, `month`, `day_of_month`, `is_weekend`).
  - Lag and rolling features (7-day lag and rolling mean for bookings and searches per item_id).
  - Commercial features (`sell_price`, `supplier_cost`, `lead_days`, gross margin).
  - Strict exclusion of `true_demand`.
  - Chronological 80/20 train/validation split.
  - Training of XGBoost `reg:quantileerror` models for P10, P50, and P90.
- Generated and saved model artifacts in `backend/models/`.

## Deviations from Plan

None - plan executed exactly as written.

## Verification Evidence

- Successfully executed `python backend/train_models.py`:
  - Train samples: 104,400, Validation samples: 26,160
  - P10 Loss: 1.6940
  - P50 Loss: 3.8796
  - P90 Loss: 1.9293
  - Artifacts successfully created at `backend/models/`.

## Self-Check: PASSED

- Created files exist on disk:
  - `backend/train_models.py`
  - `backend/models/model_p10.json`
  - `backend/models/model_p50.json`
  - `backend/models/model_p90.json`
  - `backend/models/feature_cols.pkl`
