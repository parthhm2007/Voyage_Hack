from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
import pandas as pd
from backend.loader import store
from backend.model_loader import model_store

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
    result_df["p10"] = preds["p10"].values
    result_df["p50"] = preds["p50"].values
    result_df["p90"] = preds["p90"].values
    
    if "true_demand" in result_df.columns:
        result_df = result_df.drop(columns=["true_demand"])
        
    return result_df.to_dict(orient="records")
