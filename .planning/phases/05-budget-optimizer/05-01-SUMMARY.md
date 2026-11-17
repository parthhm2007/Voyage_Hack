---
phase: 05-budget-optimizer
plan: 01
status: completed
subsystem: backend
tags: [optimize, budget, greedy, allocation, fastapi, api, backend]
---

# Plan 05-01 Summary: Backend Budget Optimization API

Implemented the `/api/optimize` FastAPI endpoint distributing a given total budget across travel inventory items iteratively based on marginal expected profit per rupee (ROI) derived from newsvendor demand distributions and unit economics.

## Accomplishments
- **Optimization Router (`backend/routers/optimize.py`)**:
  - GET `/api/optimize` accepting `total_budget`, `start_date`, and `end_date`.
  - Greedy marginal ROI knapsack allocation algorithm sorting item opportunities by expected profit per rupee.
  - Returns portfolio summary (`total_budget`, `allocated_budget`, `total_expected_profit`, `portfolio_roi`) and item-level allocation arrays (`allocated_budget`, `units_purchased`, `expected_profit`, `roi`).
- **FastAPI Registration (`backend/main.py`)**:
  - Registered `optimize.router` under `/api`.
- **Comprehensive Unit Tests (`backend/tests/test_optimize.py`)**:
  - Verified valid budget allocations and zero/negative budget validation. All 3 new tests plus all 32 existing backend tests pass cleanly.

## Key Files Created/Modified
- `backend/routers/optimize.py` (Created)
- `backend/main.py` (Modified)
- `backend/tests/test_optimize.py` (Created)

## Verification Results
- `python -m pytest backend/tests/test_optimize.py` → 3 passed (100%)
- `python -m pytest` → 35 passed (100%)
