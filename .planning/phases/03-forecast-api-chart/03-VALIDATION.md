# Phase 3: Forecast API & Chart - Validation Strategy

**Phase:** 3 (Forecast API & Chart)
**Created:** 2026-11-17

## Test Coverage & Verification

### Backend Tests (`backend/tests/test_forecast.py`)
1. Test GET `/api/forecast?item_id=...` returns 200 and list of 90-day predictions with `p10`, `p50`, `p90`.
2. Test error handling for invalid or missing `item_id`.
3. Verify no `true_demand` leakage in response.

### Frontend Tests (`frontend/src/__tests__/ForecastChart.test.jsx`)
1. Test rendering of forecast chart with mock data.
2. Verify confidence intervals and P50 line are rendered correctly.
