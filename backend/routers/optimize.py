from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from backend.loader import store
from backend.model_loader import model_store

router = APIRouter(prefix="/api", tags=["optimize"])

@router.get("/optimize", response_model=Dict[str, Any])
def get_budget_optimization(
    total_budget: float = Query(..., gt=0, description="Total available budget for inventory pre-buy"),
    risk_appetite: float = Query(0.5, ge=0.0, le=1.0, description="Risk appetite factor (0.0 = conservative P10, 0.5 = balanced P50, 1.0 = aggressive P90)"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    if store.future_window is None or store.items is None:
        store.load()
        
    df = store.future_window.copy()
    items_df = store.items.copy()
    
    if items_df.empty:
        raise HTTPException(status_code=404, detail="No inventory items found")
        
    # Compute scenario weights based on risk_appetite
    # risk_appetite ranges from 0.0 (conservative) to 1.0 (aggressive)
    if risk_appetite <= 0.5:
        t = risk_appetite / 0.5
        w_p10 = 0.60 * (1 - t) + 0.25 * t
        w_p50 = 0.40 * (1 - t) + 0.50 * t
        w_p90 = 0.00 * (1 - t) + 0.25 * t
    else:
        t = (risk_appetite - 0.5) / 0.5
        w_p10 = 0.25 * (1 - t) + 0.00 * t
        w_p50 = 0.50 * (1 - t) + 0.30 * t
        w_p90 = 0.25 * (1 - t) + 0.70 * t
        
    item_opportunities = []
    
    for _, item_row in items_df.iterrows():
        item_id = str(item_row["item_id"])
        item_type = str(item_row.get("item_type", "hotel")).lower()
        item_name = str(item_row.get("name", item_id))
        destination = str(item_row.get("destination", "Global"))
        base_cost = float(item_row.get("base_supplier_cost", 100.0))
        base_price = float(item_row.get("base_sell_price", 150.0))
        
        # Default salvage value: 40% for hotels, 15% for flights
        s = 0.40 * base_cost if "hotel" in item_type else 0.15 * base_cost
        c = base_cost
        p = base_price
        
        # Critical fractile adjusted by risk appetite
        # Effective critical fractile shifts slightly with risk appetite
        if p <= c:
            cr = 0.0
        elif p <= s:
            cr = 1.0
        else:
            cr = (p - c) / (p - s)
        # Risk appetite adjustment on critical fractile
        cr = cr * (1.0 + (risk_appetite - 0.5) * 0.2)
        cr = max(0.0, min(1.0, cr))
        
        item_df = df[df["item_id"] == item_id].sort_values("date").reset_index(drop=True)
        if start_date:
            item_df = item_df[item_df["date"] >= start_date]
        if end_date:
            item_df = item_df[item_df["date"] <= end_date]
            
        if item_df.empty:
            continue
            
        try:
            preds = model_store.predict(item_df)
        except Exception:
            continue
            
        item_total_cost = 0.0
        item_total_profit = 0.0
        item_total_units = 0.0
        
        for idx, row in item_df.iterrows():
            p10 = max(0.0, float(preds.loc[idx, "p10"]))
            p50 = max(0.0, float(preds.loc[idx, "p50"]))
            p90 = max(0.0, float(preds.loc[idx, "p90"]))
            p10, p50, p90 = sorted([p10, p50, p90])
            
            # Quantile interpolation for Q*
            if cr <= 0.0:
                q_star = 0.0
            elif cr <= 0.10:
                q_star = p10 * (cr / 0.10)
            elif cr <= 0.50:
                frac = (cr - 0.10) / (0.50 - 0.10)
                q_star = p10 + frac * (p50 - p10)
            elif cr <= 0.90:
                frac = (cr - 0.50) / (0.90 - 0.50)
                q_star = p50 + frac * (p90 - p50)
            else:
                frac = (cr - 0.90) / 0.10
                q_star = p90 + frac * max(0.0, p90 - p50)
                
            q_star = max(0.0, q_star)
            
            # Expected profit scenarios with risk-appetite weighted probabilities
            scenarios = [(p10, w_p10), (p50, w_p50), (p90, w_p90)]
            day_profit = 0.0
            for d_val, weight in scenarios:
                sales = min(q_star, d_val)
                unsold = max(0.0, q_star - d_val)
                revenue = p * sales + s * unsold
                cost = c * q_star
                day_profit += weight * (revenue - cost)
                
            item_total_cost += c * q_star
            item_total_profit += day_profit
            item_total_units += q_star
            
        if item_total_cost > 0:
            marginal_roi = item_total_profit / item_total_cost
        else:
            marginal_roi = 0.0
            
        item_opportunities.append({
            "item_id": item_id,
            "item_name": item_name,
            "item_type": item_type,
            "destination": destination,
            "unit_cost": c,
            "unconstrained_cost": item_total_cost,
            "unconstrained_profit": item_total_profit,
            "units_unconstrained": item_total_units,
            "marginal_roi": marginal_roi
        })
        
    # Sort items by descending marginal ROI (greedy knapsack allocation)
    item_opportunities.sort(key=lambda x: x["marginal_roi"], reverse=True)
    
    remaining_budget = total_budget
    allocated_budget = 0.0
    total_expected_profit = 0.0
    allocations = []
    
    for opp in item_opportunities:
        if remaining_budget <= 0:
            # Zero allocation for remaining items
            allocations.append({
                "item_id": opp["item_id"],
                "item_name": opp["item_name"],
                "item_type": opp["item_type"],
                "destination": opp["destination"],
                "allocated_budget": 0.0,
                "units_purchased": 0.0,
                "expected_profit": 0.0,
                "roi": 0.0
            })
            continue
            
        req_cost = opp["unconstrained_cost"]
        if req_cost <= remaining_budget:
            # Full allocation
            alloc_cost = req_cost
            units = opp["units_unconstrained"]
            profit = opp["unconstrained_profit"]
        else:
            # Partial allocation
            alloc_cost = remaining_budget
            fraction = remaining_budget / req_cost if req_cost > 0 else 0
            units = opp["units_unconstrained"] * fraction
            profit = opp["unconstrained_profit"] * fraction
            
        remaining_budget -= alloc_cost
        allocated_budget += alloc_cost
        total_expected_profit += profit
        roi = (profit / alloc_cost) if alloc_cost > 0 else 0.0
        
        allocations.append({
            "item_id": opp["item_id"],
            "item_name": opp["item_name"],
            "item_type": opp["item_type"],
            "destination": opp["destination"],
            "allocated_budget": round(alloc_cost, 2),
            "units_purchased": round(units, 2),
            "expected_profit": round(profit, 2),
            "roi": round(roi, 4)
        })
        
    portfolio_roi = (total_expected_profit / allocated_budget) if allocated_budget > 0 else 0.0
    
    return {
        "total_budget": round(total_budget, 2),
        "risk_appetite": round(risk_appetite, 2),
        "allocated_budget": round(allocated_budget, 2),
        "total_expected_profit": round(total_expected_profit, 2),
        "portfolio_roi": round(portfolio_roi, 4),
        "allocations": allocations
    }
