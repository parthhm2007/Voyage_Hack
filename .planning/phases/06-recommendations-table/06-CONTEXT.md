# Phase 6: Recommendations Table - Context

**Gathered:** 2026-11-18
**Status:** Ready for planning
**Source:** Roadmap & Requirements (UI-01), User Discussion

<domain>
## Phase Boundary
Build the Recommendations Table UI (`RecommendationsTable.jsx`) and supporting API or frontend orchestration connecting 90-day demand forecasts, unit economics, budget constraints, and risk-appetite adjustments. Allows revenue managers to view actionable inventory pre-buy recommendations across all items, adjust total budget and risk appetite (quantile weighting across P10/P50/P90), and view expected revenue, cost, and profit impact in real time.
</domain>

<decisions>
## Implementation Decisions
### Recommendations Table & Portfolio Integration (`RecommendationsTable.jsx`)
- **Interactive Controls:**
  - Total Capital Budget input (with preset buttons matching Phase 5 BudgetOptimizer).
  - Risk-Appetite Slider or selector (controlling quantile weighting between conservative P10, median P50, and aggressive P90 demand expectations).
- **Table Columns & Metrics:**
  - Item ID, Name, Type (Hotel/Flight), Destination.
  - Recommended Buy Quantity ($Q^*$).
  - Recommended Allocation Budget ($C$).
  - Expected Revenue & Expected Profit.
  - Marginal ROI / Expected Return %.
  - Stockout Risk / Unsold Inventory Risk indicators.
- **Backend / Frontend Synthesis:**
  - Leverage existing backend optimization (`/api/optimize`) and forecast endpoints, combining budget allocation with risk appetite weighting.
- **Dashboard Integration:**
  - Integrate `RecommendationsTable.jsx` into `App.jsx` as the primary operational pre-buy decision dashboard.
</decisions>

<canonical_refs>
## Canonical References
- `.planning/ROADMAP.md` — Phase 6 definition & success criteria
- `.planning/REQUIREMENTS.md` — UI-01
- `backend/routers/optimize.py` — Budget allocation optimization logic
- `frontend/src/components/BudgetOptimizer.jsx` — Existing budget optimization component
- `frontend/src/components/NewsvendorCalculator.jsx` — Item-level calculator component
- `frontend/src/services/api.js` — API client integration
</canonical_refs>
