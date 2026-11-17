from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from backend.loader import store
from backend.model_loader import model_store, clamp_and_sort_quantiles

router = APIRouter(prefix="/api", tags=["forecast"])

@router.get("/forecast", response_model=List[Dict[str, Any]])
def get_forecast(
    item_id: str = Query(..., max_length=50, pattern=r"^[A-Za-z0-9_-]+$")
):
    if store.future_window is None or store.items is None:
        store.load()
        
    known_items = set(store.items["item_id"].dropna().unique())
    if item_id not in known_items:
        raise HTTPException(status_code=404, detail="Item not found")
        
    df = store.future_window.copy()
    item_df = df[df["item_id"] == item_id].sort_values("date").reset_index(drop=True)
    
    if item_df.empty:
        raise HTTPException(status_code=404, detail="Forecast not found for item")
        
    try:
        preds = model_store.predict(item_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
        
    result_df = item_df.copy()
    
    clamped_p10 = []
    clamped_p50 = []
    clamped_p90 = []
    for idx in range(len(preds)):
        r10 = float(preds.loc[idx, "p10"])
        r50 = float(preds.loc[idx, "p50"])
        r90 = float(preds.loc[idx, "p90"])
        c10, c50, c90 = clamp_and_sort_quantiles(r10, r50, r90)
        clamped_p10.append(c10)
        clamped_p50.append(c50)
        clamped_p90.append(c90)

    result_df["p10"] = clamped_p10
    result_df["p50"] = clamped_p50
    result_df["p90"] = clamped_p90
    
    if "true_demand" in result_df.columns:
        result_df = result_df.drop(columns=["true_demand"])
        
    records = result_df.to_dict(orient="records")
    clean_records = []
    for r in records:
        clean_r = {}
        for k, v in r.items():
            if pd.isna(v):
                clean_r[k] = None
            else:
                clean_r[k] = v
        clean_records.append(clean_r)

    return clean_records
