# Phase 5: Budget Optimizer - Context

**Gathered:** 2026-11-17
**Status:** Ready for planning
**Source:** Roadmap & Requirements (OPT-02)

<domain>
## Phase Boundary
Implement budget allocation engine and backend optimization endpoint (`/api/optimize` or `/api/budget`) to distribute a fixed total budget across travel inventory items (hotels and flights) iteratively based on marginal expected profit per rupee (ROI), alongside frontend UI for interactive budget adjustment and allocation visualization.
</domain>

<decisions>
## Implementation Decisions
### Backend Budget Optimization Engine (`/api/optimize`)
- Create `backend/routers/optimize.py` providing `GET /api/optimize` or `POST /api/optimize` taking `total_budget` (float, required), and optional parameters (e.g. date range, risk tolerance).
- **Greedy Marginal ROI Allocation Algorithm:**
  - For each item, calculate the marginal expected profit per rupee for pre-buying incremental units based on the newsvendor demand distribution (P10/P50/P90 quantiles and unit economics).
  - Iteratively allocate budget chunks to the item offering the highest marginal expected return per rupee until `total_budget` is fully utilized or marginal returns are non-positive.
- **Metrics Returned:** Item-level allocated budget, optimal units to buy, expected revenue, expected profit, and ROI (profit / cost) per item, plus portfolio totals.

### Frontend Budget Allocator UI (`BudgetOptimizer.jsx` / Dashboard integration)
- Build interactive budget slider and input box allowing analysts to dynamically adjust the total budget.
- Display portfolio summary cards (Total Budget, Total Expected Profit, Expected ROI %, Allocated Items Count).
- Render allocation breakdown table showing item ID, name, destination, allocated budget, units purchased, expected profit, and ROI.
</decisions>

<canonical_refs>
## Canonical References
- `.planning/ROADMAP.md` — Phase 5 definition & success criteria
- `.planning/REQUIREMENTS.md` — OPT-02
- `backend/routers/newsvendor.py` — Newsvendor optimization logic and pricing/cost economics
- `backend/model_loader.py` — Demand quantiles (P10, P50, P90)
- `frontend/src/components/NewsvendorCalculator.jsx` — Component design pattern
</canonical_refs>
