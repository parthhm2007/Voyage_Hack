# Phase 4: Newsvendor Calculator - Context

**Gathered:** 2026-11-17
**Status:** Ready for planning
**Source:** Roadmap & Requirements (OPT-01), User Discussion

<domain>
## Phase Boundary
Implement newsvendor optimization logic (critical fractile model balancing overage vs. underage costs using demand quantiles P10/P50/P90) and build an interactive calculator component allowing users to adjust unit economics (cost, price, salvage value) and view optimal buy quantity and expected profit per item.
</domain>

<decisions>
## Implementation Decisions
### Backend Newsvendor Optimization (`/api/newsvendor`)
- Create a new router `backend/routers/newsvendor.py` providing an endpoint (e.g. GET/POST `/api/newsvendor`) taking `item_id`, date range or specific date, unit cost ($c$), sell price ($p$), and salvage value ($s$).
- **Quantile Mapping & Distribution:** Fit a parametric distribution (e.g. Lognormal or Normal) matching the P10, P50, and P90 quantile forecasts from `ModelStore` to evaluate the cumulative distribution function (CDF) and inverse CDF (quantile function) accurately for any Critical Fractile $CR = \frac{p - c}{p - s}$.
- **Aggregation Window:** Support calculation per specific date or across a selected date range within the 90-day forecast window.
- **Default Unit Economics & Salvage Value:**
  - Base cost $c$ (`base_supplier_cost`) and sell price $p$ (`base_sell_price`) populated from `inventory_items.csv`.
  - Salvage value defaults to **40% of supplier cost for hotels** and **15% for flights**, defined as constants in a configuration file (`backend/config.py` or similar).
  - Users can override salvage value, cost, and price interactively in the UI calculator.
- **Metrics Returned:** Optimal buy quantity $Q^*$, expected profit, overage cost, underage cost, and critical fractile.

### Frontend Newsvendor Calculator Component (`NewsvendorCalculator.jsx`)
- Build `NewsvendorCalculator.jsx` component allowing analysts to interactively adjust unit cost, sell price, and salvage value (with pre-populated defaults per item type).
- Display forecasted demand distribution quantiles (P10, P50, P90) and date selector (single date or range).
- Show optimal buy quantity ($Q^*$), expected profit, and visual breakdown of expected profit vs. buy quantity.
- Integrate smoothly with existing dashboard layout and data services.
</decisions>

<canonical_refs>
## Canonical References
- `.planning/ROADMAP.md` — Phase 4 definition & success criteria
- `.planning/REQUIREMENTS.md` — OPT-01
- `backend/model_loader.py` — ModelStore quantile predictions
- `backend/routers/forecast.py` — Forecast API integration pattern
- `frontend/src/components/ForecastChart.jsx` — Recharts pattern for UI
- `data/synthetic/inventory_items.csv` — Item metadata (base costs, prices, types)
</canonical_refs>
