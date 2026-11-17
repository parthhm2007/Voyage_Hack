# Roadmap — TBO Inventory Optimizer

## Overview

- **Phases:** 9 phases
- **Scope:** End-to-end travel inventory pre-buy optimization platform
- **Mode:** Fine granularity, sequential execution

---

## Phases

### Phase 1: Data Explorer

**Goal:** Scaffold backend and frontend, load synthetic data (`inventory_items.csv`, `calendar_events.csv`, `daily_history.csv`), and build the Data Explorer UI with filters, summary cards, and bookings vs searches charts highlighting sold-out days.
**Mode:** mvp
**Requirements:** DATA-01, DATA-02
**Plans:** 2/2 plans complete
Plans:

- [x] 01-01-PLAN.md — FastAPI Backend & Synthetic Data Loader
- [x] 01-02-PLAN.md — React Frontend & Data Explorer UI

**Success Criteria:**

1. FastAPI backend successfully loads all 4 synthetic CSV datasets without modifying source files.
2. React frontend displays Data Explorer with item and destination filters.
3. Bookings vs searches time-series charts correctly highlight sold-out days.

### Phase 2: XGBoost Demand Model

**Goal:** Build offline XGBoost training pipeline predicting P10/P50/P90 quantile demand on historical data with a time-based train/validation split, saving trained models.
**Mode:** mvp
**Requirements:** ML-01
**Plans:** 2/2 plans complete
Plans:

- [x] 02-01-PLAN.md — XGBoost Feature Engineering & Training Pipeline
- [x] 02-02-PLAN.md — Model Loader & Verification Tests

**Success Criteria:**

1. Training script successfully trains XGBoost P10, P50, and P90 quantile models using `daily_history.csv` features (excluding `true_demand`).
2. Time-based train/validation split evaluates quantile loss correctly.
3. Trained model artifacts are saved to file and loadable by the backend.

### Phase 3: Forecast API & Chart

**Goal:** Implement forecast endpoint and UI chart serving 90-day future predictions (`future_window.csv`) with P10/P50/P90 confidence bands per item.
**Mode:** mvp
**Requirements:** API-01
**Plans:** 2/2 plans complete
Plans:

- [x] 03-01-PLAN.md — Backend Forecast API Endpoint
- [x] 03-02-PLAN.md — Frontend Forecast Chart Component

### Phase 4: Newsvendor Calculator

**Goal:** Implement newsvendor optimization logic and calculator component to determine optimal buy quantity per item from cost, price, salvage value, and forecast distribution.
**Mode:** mvp
**Requirements:** OPT-01
**Success Criteria:**

1. Newsvendor calculation correctly balances overage and underage costs using demand quantiles.
2. Interactive calculator allows adjusting unit economics and viewing optimal quantity and expected profit.

### Phase 5: Budget Optimizer

**Goal:** Implement budget allocation engine and UI to distribute a total budget across items by marginal expected profit per rupee.
**Mode:** mvp
**Requirements:** OPT-02
**Success Criteria:**

1. Optimizer allocates budget across items iteratively based on marginal ROI per rupee.
2. Backend optimization endpoint executes efficiently and returns optimal allocation arrays.

### Phase 6: Recommendations Table

**Goal:** Build recommendations table UI with interactive budget input and risk-appetite slider connecting forecast and budget optimizer.
**Mode:** mvp
**Requirements:** UI-01
**Success Criteria:**

1. Recommendations table displays item-level buy recommendations, expected revenue, and cost.
2. User can adjust total budget and risk-appetite slider, instantly updating recommendations.

### Phase 7: Monte Carlo Risk View

**Goal:** Implement Monte Carlo simulation view showing profit distribution, probability of loss, and worst-5% outcome across the portfolio.
**Mode:** mvp
**Requirements:** RISK-01
**Success Criteria:**

1. Monte Carlo simulation samples from forecast distributions to project portfolio profit outcomes.
2. Risk view displays profit distribution histogram, probability of loss, and VaR (worst 5% outcome).

### Phase 8: Backtest Against Naive Strategy

**Goal:** Build backtest module comparing optimizer performance against a naive "buy last year's volume" historical baseline.
**Mode:** mvp
**Requirements:** EVAL-01
**Success Criteria:**

1. Backtest runner simulates historical performance of optimizer vs naive strategy over test windows.
2. Comparison dashboard shows profit uplift, fill rate, and stockout reduction metrics.

### Phase 9: Pricing, Buy-Timing & Polish

**Goal:** Add pricing and buy-timing recommendations, summary dashboard metrics, CSV export, and overall interface polish.
**Mode:** mvp
**Requirements:** POLISH-01
**Success Criteria:**

1. Recommendations include optimal buy timing and dynamic pricing suggestions based on lead days.
2. Interface polished with clean layout, export capabilities, and robust error handling.

---
*Last updated: 2026-03-31 after Phase 3 completion*
