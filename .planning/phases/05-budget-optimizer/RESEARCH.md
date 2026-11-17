# Phase 5: Budget Optimizer — Research

**Analyzed:** 2026-11-17
**Status:** Complete

## Technical Architecture & Design Patterns

### 1. Greedy Marginal Allocation Algorithm (Knapsack-style / Marginal ROI)
- **Problem Statement:** Given a fixed total budget $B$ and a set of items $i = 1, \dots, N$ (hotels and flights), each with daily demand distributions (P10, P50, P90) and unit economics ($c_i, p_i, s_i$), find the optimal purchase quantities $Q_{i, t}$ across items and dates to maximize total expected portfolio profit subject to $\sum_i c_i Q_{i, t} \le B$ (or aggregate budget across the 90-day window).
- **Greedy Heuristic:**
  1. Compute the baseline unconstrained optimal newsvendor quantity $Q^*_{i, t}$ and expected profit for each item-date pair (reusing logic from Phase 4).
  2. Compute the unit cost $c_i$ and marginal profit of the first unit vs subsequent units, or evaluate marginal expected return per rupee for each batch increment.
  3. Alternatively, sort all item-date opportunities by their marginal profit-to-cost ratio (ROI) or expected marginal value, and greedily allocate budget units until the total budget $B$ is reached.
  4. For simplicity and robustness in portfolio allocation across the 90-day horizon, we can aggregate expected demand and profit per item across the 90-day window, compute item-level cost per unit, and allocate budget across items based on maximum expected profit per rupee (marginal ROI).

### 2. Backend Endpoint Design (`/api/optimize`)
- **Method:** `GET /api/optimize`
- **Parameters:**
  - `total_budget`: float (required, e.g., 500,000)
  - `start_date`: Optional[str]
  - `end_date`: Optional[str]
- **Response:**
  - `total_budget`: float
  - `allocated_budget`: float
  - `total_expected_profit`: float
  - `portfolio_roi`: float
  - `allocations`: List of dicts per item (`item_id`, `item_name`, `item_type`, `destination`, `allocated_budget`, `units_purchased`, `expected_revenue`, `expected_profit`, `roi`)

### 3. Frontend Component (`BudgetOptimizer.jsx`)
- Interactive inputs for total budget (slider + number input).
- Summary cards: Total Budget, Allocated Budget, Expected Profit, Portfolio ROI %.
- Item allocation table with progress bars or visual allocation share.
- Integrated into `App.jsx`.
