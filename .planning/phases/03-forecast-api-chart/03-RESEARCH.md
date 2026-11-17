# Phase 3: Forecast API & Chart - Research

**Researched:** 2026-11-17
**Status:** Complete

## Technical Approach & Architecture

### 1. Data Loader & Future Window (`future_window.csv`)
- `future_window.csv` contains columns: `date`, `item_id`, `day_of_week`, `month`, `day_of_month`, `is_weekend`, `sell_price`, `supplier_cost`, `lead_days`, `margin`, `bookings_lag_7`, `searches_lag_7`, `bookings_roll_mean_7`, `searches_roll_mean_7`.
- We can add a loader method in `backend/loader.py` or directly in `backend/routers/forecast.py` to load `data/synthetic/future_window.csv`.

### 2. FastAPI Endpoint (`/api/forecast`)
- Query parameters: `item_id` (required or optional; if optional, returns list of items or requires item_id).
- Returns JSON array of 90-day predictions for the item:
  ```json
  [
    {
      "date": "2026-01-01",
      "item_id": "HOTEL_001",
      "p10": 12.5,
      "p50": 18.0,
      "p90": 24.2,
      "sell_price": 150.0,
      "supplier_cost": 100.0
    }
  ]
  ```

### 3. Frontend Recharts Forecast Chart
- Use Recharts `ComposedChart` or `AreaChart` with `XAxis`, `YAxis`, `Tooltip`, `Legend`, `CartesianGrid`.
- P10 to P90 confidence interval can be rendered using stacked `Area` components (translucent fill for p10-p90 spread).
- P50 rendered as a distinct line (`type="monotone" dataKey="p50" stroke="#3b82f6"`).
