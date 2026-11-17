---
phase: 06-recommendations-table
plan: 01
status: completed
subsystem: backend
tags: [optimize, risk_appetite, backend, fastapi, roi]
---

# Plan 06-01 Summary: Backend Optimization Risk Appetite Weighting

Enhanced the `/api/optimize` FastAPI endpoint to support a `risk_appetite` query parameter (`0.0` to `1.0`), dynamically weighting demand quantiles (`p10`, `p50`, `p90`) to allow revenue managers to switch between conservative, balanced, and aggressive pre-buy allocation strategies.

## Accomplishments
- **Optimization Endpoint Update (`backend/routers/optimize.py`)**:
  - Added `risk_appetite` query parameter with FastAPI validation bounds (`ge=0.0, le=1.0`).
  - Implemented scenario weight blending between conservative P10 (`risk_appetite=0.0`), balanced P50 (`risk_appetite=0.5`), and aggressive P90 (`risk_appetite=1.0`).
  - Returned `risk_appetite` in response metadata.
- **Unit Tests (`backend/tests/test_optimize.py`)**:
  - Added test cases covering conservative vs aggressive risk appetite outputs and boundary validation. All 5 tests passed successfully.

## Key Files Created/Modified
- `backend/routers/optimize.py` (Modified)
- `backend/tests/test_optimize.py` (Modified)

## Verification Results
- `python -m pytest backend/tests/test_optimize.py` → 5 passed (100%)
- `python -m pytest` → 37 passed (100%)
