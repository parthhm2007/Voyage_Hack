# Walking Skeleton — TBO Inventory Optimizer

**Phase:** 1
**Generated:** 2026-11-16

## Capability Proven End-to-End

> A travel inventory analyst can start the FastAPI backend and React Vite frontend, load synthetic CSV data (`inventory_items.csv`, `calendar_events.csv`, `daily_history.csv`) in-memory without modifying source files, query filtered historical records and summary metrics via REST endpoints, and visualize bookings vs searches time-series charts with sold-out day highlights in the Data Explorer UI.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Framework & Language | Python 3.11 + FastAPI (Backend), React 18 + Vite + TypeScript/JS (Frontend) | Extremely fast backend performance, automatic OpenAPI docs, modern component-driven SPA frontend. |
| Data Layer | In-memory Pandas DataFrames singleton loaded at startup | Synthetic dataset (~130k rows) easily fits in RAM (<50MB), offering sub-millisecond filtering without external DB overhead. |
| UI & Visualization | Tailwind CSS + Recharts | Responsive, clean light-themed UI with robust SVG time-series charting and custom reference dots. |
| Data Security | True Demand Isolation middleware/filter | Ensures `true_demand` ground truth target is strictly excluded from API responses and frontend state. |
| Deployment target | Local development monorepo (`/backend`, `/frontend`) | Simple local execution via Uvicorn and Vite dev server. |

## Stack Touched in Phase 1

- [x] Project scaffold (`/backend` FastAPI app, `/frontend` Vite + React app)
- [x] Routing & Endpoints — `/api/items`, `/api/calendar`, `/api/history`, `/api/summary`
- [x] Data layer — In-memory pandas CSV loader for synthetic datasets
- [x] UI — Data Explorer view with filters, summary cards, and Recharts bookings vs searches time-series chart highlighting sold-out days
- [x] Verification — Unit tests (`pytest`) and component tests (`vitest`) establishing end-to-end pipeline

## Out of Scope (Deferred to Later Slices)

- XGBoost demand training and model artifact saving (Phase 2)
- 90-day future demand forecast API and confidence bands (Phase 3)
- Newsvendor profit-maximizing quantity calculation (Phase 4)
- Budget allocation optimizer (Phase 5)
- Recommendations table with risk-appetite slider (Phase 6)
- Monte Carlo risk simulation (Phase 7)
- Naive backtest evaluation (Phase 8)
- Dynamic pricing, buy-timing, and final polish (Phase 9)

## Subsequent Slice Plan

- Phase 2: XGBoost Demand Model (offline training pipeline predicting P10/P50/P90 quantiles)
- Phase 3: Forecast API & Chart (serving 90-day future predictions with confidence bands)
- Phase 4: Newsvendor Calculator (determining optimal buy quantity per item)
- Phase 5: Budget Optimizer (distributing total budget by marginal expected profit per rupee)
- Phase 6: Recommendations Table (interactive budget and risk-appetite controls)
- Phase 7: Monte Carlo Risk View (profit distribution, probability of loss, VaR)
- Phase 8: Backtest Against Naive Strategy (evaluating uplift vs historical baseline)
- Phase 9: Pricing, Buy-Timing & Polish (final dashboard metrics, export, and polish)
