---
phase: 04-newsvendor-calculator
plan: 01
status: completed
subsystem: backend
tags: [newsvendor, optimization, fastapi, api, backend]
---

# Plan 04-01 Summary: Backend Newsvendor Optimization API

Implemented the `/api/newsvendor` FastAPI endpoint computing optimal pre-buy quantity ($Q^*$), critical fractile, expected profit, and expected demand using P10/P50/P90 quantile demand forecasts, item economics, and default salvage values (40% for hotels, 15% for flights) with support for parameter overrides and date filtering.

## Accomplishments
- **Newsvendor Router (`backend/routers/newsvendor.py`)**:
  - GET `/api/newsvendor` supporting `item_id`, `start_date`, `end_date`, `unit_cost`, `sell_price`, and `salvage_value` parameters.
  - Automatic item-type specific salvage value defaults (40% for hotels, 15% for flights).
  - Robust critical fractile computation and quantile interpolation mapping to find optimal pre-buy quantity $Q^*$.
  - Expected profit evaluation across P10, P50, and P90 demand scenarios.
- **FastAPI Registration (`backend/main.py`)**:
  - Registered `newsvendor.router` under `/api`.
- **Comprehensive Unit Tests (`backend/tests/test_newsvendor.py`)**:
  - Verified hotel and flight salvage defaults, custom parameter overrides, and unknown item error handling. All 4 new tests plus all 23 existing backend tests pass cleanly.

## Key Files Created/Modified
- `backend/routers/newsvendor.py` (Created)
- `backend/main.py` (Modified)
- `backend/tests/test_newsvendor.py` (Created)

## Verification Results
- `python -m pytest backend/tests/test_newsvendor.py` → 4 passed (100%)
- `python -m pytest` → 27 passed (100%)
