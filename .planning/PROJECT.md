# TBO Inventory Optimizer

## What This Is

TBO Inventory Optimizer is a web decision-support platform that recommends which travel inventory (hotels, flights) TBO.com should pre-buy within a fixed budget to maximize risk-adjusted profit. It handles demand censoring, trains XGBoost quantile demand models, computes optimal newsvendor quantities, allocates budgets across items, and provides Monte Carlo risk views and backtests.

## Core Value

Accurately forecast uncensored travel demand and optimize pre-buy allocation within budget to maximize risk-adjusted profit without exceeding budget constraints.

## Requirements

### Validated

- ✓ Read-only synthetic data source (`./data/synthetic/`: `inventory_items.csv`, `calendar_events.csv`, `daily_history.csv`, `future_window.csv`) — existing

### Active

- [ ] **DATA-01**: Backend API and data loader serving inventory items, calendar events, and historical records without modifying raw data.
- [ ] **DATA-02**: Data Explorer UI with item/destination filters and bookings vs searches charts highlighting sold-out days.
- [ ] **ML-01**: XGBoost offline training pipeline predicting P10/P50/P90 quantile demand using time-based train/validation split.
- [ ] **API-01**: Forecast API serving 90-day future predictions with confidence bands per item.
- [ ] **OPT-01**: Newsvendor calculator for optimal buy quantity from cost, price, salvage value, and forecast distribution.
- [ ] **OPT-02**: Budget optimizer allocating total budget across items by marginal expected profit per rupee.
- [ ] **UI-01**: Recommendations table with budget input and risk-appetite slider.
- [ ] **RISK-01**: Monte Carlo risk view showing profit distribution, probability of loss, and worst-5% outcome.
- [ ] **EVAL-01**: Backtest module comparing optimizer against a naive "buy last year's volume" strategy.
- [ ] **POLISH-01**: Pricing and buy-timing recommendations, export features, and interface polish.

### Out of Scope

- **Authentication / User Accounts**: Single-tenant internal tool for TBO.com optimization team.
- **Dark Mode**: Light theme only as specified by styling constraints.
- **Database Storage**: Pure CSV/file-based persistence and in-memory analytics using pandas and Python backend.
- **Modifying Raw Data**: `./data/synthetic/` is strictly read-only.

## Context

- Tech Stack: Python 3.11 + FastAPI + pandas + uvicorn in `/backend`; React + Vite + Recharts in `/frontend`.
- Data constraint: `true_demand` must never be a model feature and must never be exposed by any API endpoint.
- Fixed 9-phase roadmap where each phase is executed one at a time.

## Constraints

- **Tech Stack**: Python 3.11, FastAPI, pandas, uvicorn, React, Vite, Recharts. No auth, no dark mode, no databases.
- **Data Integrity**: Never modify `/data/synthetic/`. `true_demand` hidden from features and APIs.
- **Scope**: Phase 1 in scope first; do not proceed to subsequent phases until approved.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FastAPI + React monolithic separation (`/backend` and `/frontend`) | Clean separation of Python analytics/ML backend and React SPA frontend | — Pending |
| XGBoost quantile regression for demand forecasting | Captures P10/P50/P90 uncertainty distribution needed for newsvendor optimization | — Pending |

---
*Last updated: 2026-11-16 after initialization*

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state
