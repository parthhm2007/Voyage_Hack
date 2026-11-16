# Phase 2: XGBoost Demand Model - Context

**Gathered:** 2026-11-16
**Status:** Ready for planning
**Source:** Roadmap & Requirements

<domain>
## Phase Boundary
Build offline XGBoost training pipeline predicting P10/P50/P90 quantile demand on historical data (`daily_history.csv`) using a time-based train/validation split, evaluating quantile loss (pinball loss), and saving trained model artifacts to file for backend loading.
</domain>

<decisions>
## Implementation Decisions
### Modeling Architecture (XGBoost Quantile Regression)
- Use XGBoost (`xgboost` Python library) with `reg:quantileerror` objective for alpha levels 0.10, 0.50, and 0.90 to predict P10, P50, and P90 quantile demand.
- Feature engineering from `daily_history.csv` (e.g., rolling averages, lag features, day of week, season) while strictly excluding `true_demand` from feature inputs.
- Time-based train/validation split (e.g., train on first 80% chronological days, validate on last 20%) to prevent data leakage.
- Evaluation metrics: Quantile (pinball) loss across validation set.
- Persistence: Save trained model artifacts (e.g., joblib/pickle or native xgboost model files) to `./backend/models/` so they can be loaded by the FastAPI backend in subsequent phases.
</decisions>

<canonical_refs>
## Canonical References
- `.planning/ROADMAP.md` — Phase 2 definition and success criteria
- `.planning/REQUIREMENTS.md` — ML-01 specification
- `./data/synthetic/daily_history.csv`
- `backend/loader.py` — Existing backend data loader pattern
</canonical_refs>
