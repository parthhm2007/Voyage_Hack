# Requirements — TBO Inventory Optimizer

## v1 Requirements

### Data & Architecture

- [x] **DATA-01**: Backend API and data loader serving inventory items (`inventory_items.csv`), calendar events (`calendar_events.csv`), and historical records (`daily_history.csv`) without modifying raw data.
- [x] **DATA-02**: Data Explorer UI with item/destination filters and bookings vs searches charts highlighting sold-out days and summary cards.

### Machine Learning & Forecasting

- [ ] **ML-01**: XGBoost offline training pipeline predicting P10/P50/P90 quantile demand using time-based train/validation split, saving models to file.
- [x] **API-01**: Forecast API serving 90-day future predictions (`future_window.csv`) with P10/P50/P90 confidence bands per item.

### Optimization & Decision Support

- [ ] **OPT-01**: Newsvendor calculator computing optimal buy quantity per item from supplier cost, sell price, salvage value, and forecast distribution.
- [ ] **OPT-02**: Budget optimizer allocating one total budget across items by marginal expected profit per rupee.
- [ ] **UI-01**: Recommendations table with interactive budget input and risk-appetite slider.

### Risk & Evaluation

- [ ] **RISK-01**: Monte Carlo risk view displaying profit distribution, probability of loss, and worst-5% outcome.
- [ ] **EVAL-01**: Backtest module evaluating optimizer performance against a naive "buy last year's volume" strategy.

### Polish & Recommendations

- [ ] **POLISH-01**: Pricing and buy-timing recommendations, summary dashboard, and final polish.

## v2 Requirements (Deferred)

- [ ] Multi-user authentication and role-based access control.
- [ ] Automated daily retraining pipeline with live data ingestion.
- [ ] Database migration (PostgreSQL) for large-scale transaction history.

## Out of Scope

- **Authentication**: Single-tenant internal tool for TBO.com analysts.
- **Dark Mode**: Light theme only.
- **Modifying Raw Data**: Read-only access to `./data/synthetic/`.
