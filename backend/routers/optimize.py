from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any, Optional, Annotated
import math
import logging
import pandas as pd
import numpy as np
from backend.config import DEFAULT_SALVAGE_RATES, MAX_BUDGET, get_risk_weights
from backend.loader import store
from backend.model_loader import model_store, clamp_and_sort_quantiles

router = APIRouter(prefix="/api", tags=["optimize"])

@router.get("/optimize", response_model=Dict[str, Any])
def get_budget_optimization(
    total_budget: Annotated[float, Query(ge=0.0, le=MAX_BUDGET, description="Total available budget for inventory pre-buy")] = 500000.0,
    risk_appetite: Annotated[float, Query(ge=0.0, le=1.0, description="Risk appetite factor (0.0 = conservative P10, 0.5 = balanced P50, 1.0 = aggressive P90)")] = 0.5,
    start_date: Annotated[Optional[str], Query(pattern=r"^\d{4}-\d{2}-\d{2}$")] = None,
    end_date: Annotated[Optional[str], Query(pattern=r"^\d{4}-\d{2}-\d{2}$")] = None
):
    # Validate total_budget
    if math.isnan(total_budget) or math.isinf(total_budget):
        raise HTTPException(status_code=422, detail="total_budget must be a finite number")
    if total_budget < 0.0 or total_budget > MAX_BUDGET:
        raise HTTPException(status_code=422, detail=f"total_budget must be between 0 and {MAX_BUDGET}")

    # Validate risk_appetite
    if math.isnan(risk_appetite) or math.isinf(risk_appetite) or risk_appetite < 0.0 or risk_appetite > 1.0:
        raise HTTPException(status_code=422, detail="risk_appetite must be between 0.0 and 1.0")

    if store.future_window is None or store.items is None:
        store.load()
        
    items_df = store.items.copy()
    if items_df.empty:
        raise HTTPException(status_code=404, detail="No inventory items found")

    # Date range validation matching newsvendor.py
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must be on or before end_date")
        
    window_min = str(store.future_window["date"].min())[:10]
    window_max = str(store.future_window["date"].max())[:10]
    if start_date and (start_date < window_min or start_date > window_max):
        raise HTTPException(
            status_code=422,
            detail=f"start_date {start_date} is outside the available forecast window ({window_min} to {window_max})"
        )
    if end_date and (end_date < window_min or end_date > window_max):
        raise HTTPException(
            status_code=422,
            detail=f"end_date {end_date} is outside the available forecast window ({window_min} to {window_max})"
        )

    effective_start = start_date if start_date is not None else window_min
    effective_end = end_date if end_date is not None else window_max

    # Filter future window by dates
    df = store.future_window.copy()
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]

    if df.empty:
        raise HTTPException(status_code=404, detail="No forecast records found in specified date range")

    dates_in_window = sorted(df["date"].unique())
    num_days = len(dates_in_window)

    # Compute scenario weights centrally
    w_p10, w_p50, w_p90 = get_risk_weights(risk_appetite)

    # Batch prediction across the whole future window (Finding 15)
    try:
        preds = model_store.predict(df)
    except Exception as e:
        logging.exception("Batch prediction failure in optimizer")
        raise HTTPException(status_code=500, detail=f"Model prediction error: {str(e)}")

    # Strict NaN check (Finding 4)
    raw_p10 = preds["p10"].values
    raw_p50 = preds["p50"].values
    raw_p90 = preds["p90"].values
    nan_mask = np.isnan(raw_p10) | np.isnan(raw_p50) | np.isnan(raw_p90)
    if np.any(nan_mask):
        bad_idx = int(np.where(nan_mask)[0][0])
        bad_item = df.iloc[bad_idx]["item_id"]
        bad_date = str(df.iloc[bad_idx]["date"])[:10]
        raise HTTPException(
            status_code=500,
            detail=f"Forecast prediction contains NaN for item {bad_item} on date {bad_date}"
        )

    # Vectorized clamp and sort quantiles (Finding 8)
    p10_clamped = np.maximum(0.0, raw_p10)
    p50_clamped = np.maximum(0.0, raw_p50)
    p90_clamped = np.maximum(0.0, raw_p90)
    stacked = np.sort(np.stack([p10_clamped, p50_clamped, p90_clamped], axis=1), axis=1)

    df["p10"] = stacked[:, 0]
    df["p50"] = stacked[:, 1]
    df["p90"] = stacked[:, 2]

    # Map capacity per day from items metadata
    items_meta = {}
    for _, row in items_df.iterrows():
        iid = str(row["item_id"])
        items_meta[iid] = {
            "item_id": iid,
            "name": str(row.get("name", iid)),
            "item_type": str(row.get("item_type", "hotel")).lower(),
            "destination": str(row.get("destination", "Global")),
            "capacity_per_day": float(row.get("capacity_per_day", 100.0)),
            "base_supplier_cost": float(row.get("base_supplier_cost", 100.0)),
            "base_sell_price": float(row.get("base_sell_price", 150.0)),
        }

    # Vectorized daily demand capping by physical capacity (Finding 1)
    caps_series = df["item_id"].map(lambda x: items_meta[x]["capacity_per_day"] if x in items_meta else 100.0).values
    df["d10"] = np.minimum(caps_series, df["p10"].values)
    df["d50"] = np.minimum(caps_series, df["p50"].values)
    df["d90"] = np.minimum(caps_series, df["p90"].values)

    # Sum scenario demands per item over the window
    agg_demands = df.groupby("item_id")[["d10", "d50", "d90"]].sum()

    tranches = []
    excluded_items = []
    item_summaries = {}
    cheapest_cost = float("inf")

    for iid, meta in items_meta.items():
        c = meta["base_supplier_cost"]
        p = meta["base_sell_price"]
        cheapest_cost = min(cheapest_cost, c)
        cap_daily = meta["capacity_per_day"]
        item_max_cap = int(cap_daily * num_days)

        salvage_rate = DEFAULT_SALVAGE_RATES.get(meta["item_type"], 0.40 if "hotel" in meta["item_type"] else 0.15)
        s = round(salvage_rate * c, 2)

        if iid not in agg_demands.index:
            excluded_items.append({"item_id": iid, "reason": "no forecast records in window"})
            continue

        row_demands = agg_demands.loc[iid]
        D10 = int(np.round(min(item_max_cap, max(0.0, row_demands["d10"]))))
        D50 = int(np.round(min(item_max_cap, max(float(D10), row_demands["d50"]))))
        D90 = int(np.round(min(item_max_cap, max(float(D50), row_demands["d90"]))))

        # Expected profit helper for Q integer units
        def make_profit_fn(d10_val, d50_val, d90_val, cost_val, price_val, salvage_val):
            def calc_profit(q_int: int) -> float:
                tot_p = 0.0
                for d_val, weight in [(d10_val, w_p10), (d50_val, w_p50), (d90_val, w_p90)]:
                    sales = min(q_int, d_val)
                    unsold = max(0, q_int - d_val)
                    tot_p += weight * (price_val * sales + salvage_val * unsold - cost_val * q_int)
                return tot_p
            return calc_profit

        profit_fn = make_profit_fn(D10, D50, D90, c, p, s)

        # Tranches of marginal value
        # Tranche 1: [0, D10]
        n1 = D10
        m1 = p - c
        v1 = (m1 / c) if c > 0 else 0.0

        # Tranche 2: (D10, D50]
        n2 = max(0, D50 - D10)
        m2 = (w_p50 + w_p90) * p + w_p10 * s - c
        v2 = (m2 / c) if c > 0 else 0.0

        # Tranche 3: (D50, D90]
        n3 = max(0, D90 - D50)
        m3 = w_p90 * p + (w_p10 + w_p50) * s - c
        v3 = (m3 / c) if c > 0 else 0.0

        # If even first unit has non-positive profit, exclude item (Finding 2)
        if m1 <= 0:
            excluded_items.append({"item_id": iid, "reason": "non-positive expected profit"})
            item_summaries[iid] = {
                "profit_fn": profit_fn,
                "unconstrained_units": 0,
                "unconstrained_profit": 0.0,
                "unconstrained_cost": 0.0,
                "max_marginal_roi": 0.0,
                "capacity_capped": False,
                "unit_cost": c,
                "salvage_rate": salvage_rate
            }
            continue

        q_unconstrained = 0
        if n1 > 0 and m1 > 0:
            q_unconstrained += n1
            tranches.append({
                "item_id": iid,
                "units": n1,
                "unit_cost": c,
                "marginal_roi": v1,
                "tranche_idx": 1
            })
        if n2 > 0 and m2 > 0:
            q_unconstrained += n2
            tranches.append({
                "item_id": iid,
                "units": n2,
                "unit_cost": c,
                "marginal_roi": v2,
                "tranche_idx": 2
            })
        if n3 > 0 and m3 > 0:
            q_unconstrained += n3
            tranches.append({
                "item_id": iid,
                "units": n3,
                "unit_cost": c,
                "marginal_roi": v3,
                "tranche_idx": 3
            })

        unconstrained_profit = profit_fn(q_unconstrained)
        if unconstrained_profit <= 0:
            excluded_items.append({"item_id": iid, "reason": "non-positive expected profit"})
            # Remove any tranches added for this item
            tranches = [t for t in tranches if t["item_id"] != iid]
            item_summaries[iid] = {
                "profit_fn": profit_fn,
                "unconstrained_units": 0,
                "unconstrained_profit": 0.0,
                "unconstrained_cost": 0.0,
                "max_marginal_roi": 0.0,
                "capacity_capped": False,
                "unit_cost": c,
                "salvage_rate": salvage_rate
            }
            continue

        item_summaries[iid] = {
            "profit_fn": profit_fn,
            "unconstrained_units": q_unconstrained,
            "unconstrained_profit": unconstrained_profit,
            "unconstrained_cost": q_unconstrained * c,
            "max_marginal_roi": v1,
            "capacity_capped": (q_unconstrained >= item_max_cap),
            "unit_cost": c,
            "salvage_rate": salvage_rate
        }

    # Deterministic knapsack allocation (Findings 11, 12)
    # Sort tranches by (marginal_roi desc, unconstrained_profit desc, item_id asc, tranche_idx asc)
    tranches.sort(
        key=lambda x: (
            -x["marginal_roi"],
            -item_summaries[x["item_id"]]["unconstrained_profit"],
            x["item_id"],
            x["tranche_idx"]
        )
    )

    remaining_budget = total_budget
    allocated_units_per_item = {iid: 0 for iid in items_meta}

    if total_budget > 0:
        for tr in tranches:
            c = tr["unit_cost"]
            if remaining_budget < c:
                continue
            avail = tr["units"]
            max_affordable = int(np.floor(remaining_budget / c))
            take = min(avail, max_affordable)
            if take > 0:
                allocated_units_per_item[tr["item_id"]] += take
                remaining_budget -= take * c

    # Build allocations list
    # Sort items deterministically: (max_marginal_roi desc, unconstrained_profit desc, item_id asc)
    sorted_item_ids = sorted(
        items_meta.keys(),
        key=lambda iid: (
            -item_summaries.get(iid, {}).get("max_marginal_roi", 0.0),
            -item_summaries.get(iid, {}).get("unconstrained_profit", 0.0),
            iid
        )
    )

    allocations = []
    total_spent = 0.0
    total_profit = 0.0

    for iid in sorted_item_ids:
        meta = items_meta[iid]
        summary = item_summaries.get(iid, {})
        profit_fn = summary.get("profit_fn")
        c = meta["base_supplier_cost"]
        cap_daily = meta["capacity_per_day"]
        item_max_cap = int(cap_daily * num_days)

        units = allocated_units_per_item[iid]
        alloc_cost = round(units * c, 2)
        profit = round(profit_fn(units) if profit_fn else 0.0, 2)
        roi = round(profit / alloc_cost, 4) if alloc_cost > 0 else 0.0
        is_capped = (units >= item_max_cap and item_max_cap > 0)

        total_spent += alloc_cost
        total_profit += profit

        allocations.append({
            "item_id": iid,
            "item_name": meta["name"],
            "item_type": meta["item_type"],
            "destination": meta["destination"],
            "allocated_budget": alloc_cost,
            "units_purchased": units,
            "expected_profit": profit,
            "roi": roi,
            "capacity_per_day": cap_daily,
            "capacity_capped": is_capped,
            "unit_cost": round(c, 2)
        })

    total_spent = round(total_spent, 2)
    total_profit = round(total_profit, 2)
    portfolio_roi = round(total_profit / total_spent, 4) if total_spent > 0 else 0.0

    # Explanatory notes for edge cases (Finding 12)
    note = None
    if total_budget == 0.0:
        note = "Total budget is 0. No inventory can be purchased."
    elif total_spent == 0.0 and total_budget < cheapest_cost:
        note = f"Budget not fully used: total budget (₹{total_budget:,.0f}) is less than the cheapest available unit (₹{cheapest_cost:,.0f}). No inventory can be purchased."
    elif remaining_budget > 0.0 and all(
        allocated_units_per_item[t["item_id"]] >= item_summaries[t["item_id"]]["unconstrained_units"]
        for t in tranches
    ):
        note = "Budget not fully used: all profitable inventory capped at capacity has been purchased."

    response = {
        "total_budget": round(total_budget, 2),
        "risk_appetite": round(risk_appetite, 2),
        "allocated_budget": total_spent,
        "total_expected_profit": total_profit,
        "portfolio_roi": portfolio_roi,
        "allocations": allocations,
        "excluded": excluded_items,
        "assumptions": {
            "salvage_rates": DEFAULT_SALVAGE_RATES,
            "risk_weights": {
                "p10": round(w_p10, 4),
                "p50": round(w_p50, 4),
                "p90": round(w_p90, 4)
            },
            "start_date": effective_start,
            "end_date": effective_end,
            "days": num_days
        }
    }
    if note:
        response["note"] = note

    return response
