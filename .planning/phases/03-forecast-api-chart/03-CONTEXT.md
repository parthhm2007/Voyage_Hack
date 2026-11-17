# Phase 3: Forecast API & Chart - Context

**Gathered:** 2026-11-17
**Status:** Ready for planning
**Source:** Roadmap & Requirements (API-01)

<domain>
## Phase Boundary
Implement backend API endpoint serving 90-day future predictions (`future_window.csv` combined with `ModelStore` P10/P50/P90 demand predictions) per item, and build frontend React forecast chart with confidence bands (P10-P90 shaded area, P50 line).
</domain>

<decisions>
## Implementation Decisions
### Backend Forecast API (`/api/forecast`)
- Create a new router `backend/routers/forecast.py` providing GET `/api/forecast` supporting query parameter `item_id`.
- Endpoint loads `future_window.csv` (containing future dates, pricing, supplier cost, lead days, lag features, etc. for the 90-day window per item).
- Uses `model_store` from `backend/model_loader.py` to run predictions (`p10`, `p50`, `p90`) on the 90-day future feature set for the specified item.
- Returns list of daily predictions for the 90-day window: `date`, `item_id`, `p10`, `p50`, `p90`, along with item metadata (`sell_price`, `supplier_cost`, etc.).
- Enforce True Demand Isolation: never expose `true_demand`.

### Frontend Forecast Chart Component
- Build `ForecastChart.jsx` component using Recharts (`AreaChart`, `Line`, `Area`, `XAxis`, `YAxis`, `Tooltip`, `ResponsiveContainer`).
- Display P50 as solid line, and confidence band (P10 to P90) as shaded area.
- Item selector dropdown or integration with Data Explorer / item selection state.
- Clean styling matching existing dashboard components (`index.css`).
</decisions>

<canonical_refs>
## Canonical References
- `.planning/ROADMAP.md` — Phase 3 definition & success criteria
- `.planning/REQUIREMENTS.md` — API-01
- `backend/model_loader.py` — ModelStore implementation
- `backend/routers/data.py` — Existing FastAPI router patterns
- `data/synthetic/future_window.csv` — Future 90-day window data
- `frontend/src/components/BookingsChart.jsx` — Existing Recharts pattern
</canonical_refs>
