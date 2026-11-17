from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from backend.config import DEFAULT_SALVAGE_RATES
from backend.loader import store
from backend.model_loader import model_store, clamp_and_sort_quantiles

router = APIRouter(prefix="/api", tags=["newsvendor"])

@router.get("/newsvendor", response_model=Dict[str, Any])
def get_newsvendor(
    item_id: str = Query(..., max_length=50, pattern=r"^[A-Za-z0-9_-]+$"),
    start_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    start: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    unit_cost: Optional[float] = Query(None, gt=0),
    sell_price: Optional[float] = Query(None, gt=0),
    salvage_value: Optional[float] = Query(None, ge=0)
):
    if store.future_window is None or store.items is None:
        store.load()
        
    known_items = set(store.items["item_id"].dropna().unique())
    if item_id not in known_items:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # Get item metadata
    item_row = store.items[store.items["item_id"] == item_id].iloc[0]
    item_type = str(item_row.get("item_type", "hotel")).lower()
    item_name = str(item_row.get("name", item_id))
    capacity_per_day = float(item_row.get("capacity_per_day", 100.0))
    base_cost = float(item_row.get("base_supplier_cost", 100.0))
    base_price = float(item_row.get("base_sell_price", 150.0))
    
    # Resolve date parameters (accepting both start_date/end_date and start/end)
    effective_start = start_date if start_date is not None else start
    effective_end = end_date if end_date is not None else end
    
    if effective_start and effective_end and effective_start > effective_end:
        raise HTTPException(status_code=422, detail="start_date must be on or before end_date")
        
    window_min = str(store.future_window["date"].min())[:10]
    window_max = str(store.future_window["date"].max())[:10]
    if effective_start and (effective_start < window_min or effective_start > window_max):
        raise HTTPException(
            status_code=422,
            detail=f"start_date {effective_start} is outside the available forecast window ({window_min} to {window_max})"
        )
    if effective_end and (effective_end < window_min or effective_end > window_max):
        raise HTTPException(
            status_code=422,
            detail=f"end_date {effective_end} is outside the available forecast window ({window_min} to {window_max})"
        )
        
    # Determine unit economics
    c = unit_cost if unit_cost is not None else base_cost
    p = sell_price if sell_price is not None else base_price
    
    # Central salvage configuration lookup
    salvage_rate = DEFAULT_SALVAGE_RATES.get(item_type, 0.40 if "hotel" in item_type else 0.15)
    
    if salvage_value is not None:
        s = salvage_value
        effective_salvage_rate = round(s / c, 4) if c > 0 else 0.0
    else:
        # Default salvage from effective unit cost
        s = round(salvage_rate * c, 2)
        effective_salvage_rate = salvage_rate
        
    # Validate unit economics
    if s > c:
        raise HTTPException(
            status_code=422,
            detail=f"salvage_value ({s}) cannot exceed unit_cost ({c})"
        )
    if p < c:
        raise HTTPException(
            status_code=422,
            detail=f"sell_price ({p}) cannot be less than unit_cost ({c}): negative profit margin is invalid for inventory optimization"
        )
        
    if p <= c:
        critical_fractile = 0.0
    elif p <= s:
        critical_fractile = 1.0
    else:
        critical_fractile = (p - c) / (p - s)
    critical_fractile = max(0.0, min(1.0, critical_fractile))
    
    # Filter future window
    df = store.future_window.copy()
    item_df = df[df["item_id"] == item_id].sort_values("date").reset_index(drop=True)
    
    if item_df.empty:
        raise HTTPException(status_code=404, detail="Forecast not found for item")
        
    if effective_start:
        item_df = item_df[item_df["date"] >= effective_start]
    if effective_end:
        item_df = item_df[item_df["date"] <= effective_end]
        
    if item_df.empty:
        raise HTTPException(status_code=404, detail="No forecast records found in specified date range")
        
    try:
        preds = model_store.predict(item_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
        
    daily_results = []
    total_opt_qty = 0.0
    total_expected_profit = 0.0
    total_expected_demand = 0.0
    total_expected_unsold = 0.0
    capacity_capped = False
    
    for idx, row in item_df.iterrows():
        raw_p10 = preds.loc[idx, "p10"]
        raw_p50 = preds.loc[idx, "p50"]
        raw_p90 = preds.loc[idx, "p90"]
        
        date_str = str(row["date"])[:10]
        # Silent NaN check: never convert NaN to 0; raise clear 500 error naming date and item
        if np.isnan(raw_p10) or np.isnan(raw_p50) or np.isnan(raw_p90):
            raise HTTPException(
                status_code=500,
                detail=f"Forecast prediction contains NaN for item {item_id} on date {date_str}"
            )
            
        p10, p50, p90 = clamp_and_sort_quantiles(raw_p10, raw_p50, raw_p90)
        
        # Quantile interpolation for Q* based on critical fractile CR
        if critical_fractile <= 0.0:
            uncapped_q = 0.0
        elif critical_fractile <= 0.10:
            uncapped_q = p10 * (critical_fractile / 0.10)
        elif critical_fractile <= 0.50:
            frac = (critical_fractile - 0.10) / (0.50 - 0.10)
            uncapped_q = p10 + frac * (p50 - p10)
        elif critical_fractile <= 0.90:
            frac = (critical_fractile - 0.50) / (0.90 - 0.50)
            uncapped_q = p50 + frac * (p90 - p50)
        else:
            frac = (critical_fractile - 0.90) / 0.10
            uncapped_q = p90 + frac * max(0.0, p90 - p50)
            
        uncapped_q = max(0.0, uncapped_q)
        q_star = min(capacity_per_day, uncapped_q)
        if q_star < uncapped_q:
            capacity_capped = True
            
        # Expected demand capped at physical capacity
        uncapped_exp_demand = 0.25 * p10 + 0.50 * p50 + 0.25 * p90
        exp_demand = min(capacity_per_day, uncapped_exp_demand)
        
        # Evaluate expected profit across P10, P50, P90 scenarios using capped q_star
        scenarios = [
            (min(capacity_per_day, p10), 0.25),
            (min(capacity_per_day, p50), 0.50),
            (min(capacity_per_day, p90), 0.25)
        ]
        day_profit = 0.0
        day_unsold = 0.0
        for d_val, weight in scenarios:
            sales = min(q_star, d_val)
            unsold = max(0.0, q_star - d_val)
            revenue = p * sales + s * unsold
            cost = c * q_star
            day_profit += weight * (revenue - cost)
            day_unsold += weight * unsold
            
        daily_results.append({
            "date": date_str,
            "p10": round(p10, 2),
            "p50": round(p50, 2),
            "p90": round(p90, 2),
            "expected_demand": round(exp_demand, 2),
            "optimal_quantity": round(q_star, 2),
            "expected_profit": round(day_profit, 2),
            "expected_unsold_units": round(day_unsold, 2)
        })
        
        total_opt_qty += q_star
        total_expected_profit += day_profit
        total_expected_demand += exp_demand
        total_expected_unsold += day_unsold
        
    num_days = len(daily_results)
    max_window_capacity = capacity_per_day * num_days
    if total_opt_qty > max_window_capacity:
        total_opt_qty = max_window_capacity
        capacity_capped = True
        
    avg_opt_qty = total_opt_qty / num_days if num_days > 0 else 0.0
    avg_expected_demand = total_expected_demand / num_days if num_days > 0 else 0.0
    
    return {
        "item_id": item_id,
        "item_name": item_name,
        "item_type": item_type,
        "capacity_per_day": capacity_per_day,
        "capacity_capped": capacity_capped,
        "unit_cost": round(c, 2),
        "sell_price": round(p, 2),
        "salvage_value": round(s, 2),
        "critical_fractile": round(critical_fractile, 4),
        "optimal_quantity_avg": round(avg_opt_qty, 2),
        "total_optimal_quantity": round(total_opt_qty, 2),
        "total_expected_profit": round(total_expected_profit, 2),
        "expected_demand_avg": round(avg_expected_demand, 2),
        "total_expected_unsold": round(total_expected_unsold, 2),
        "assumptions": {
            "salvage_rate": effective_salvage_rate,
            "salvage_value": round(s, 2),
            "default_salvage_rate": salvage_rate,
            "capacity_per_day": capacity_per_day
        },
        "daily_breakdown": daily_results
    }
