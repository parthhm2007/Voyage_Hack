from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from backend.loader import store

router = APIRouter(prefix="/api", tags=["data"])

@router.get("/items", response_model=List[Dict[str, Any]])
def get_items(
    destination: Optional[str] = Query(default=None, max_length=100),
    item_type: Optional[str] = None
):
    if store.items is None:
        store.load()
        
    if destination is not None and destination != "All":
        known_destinations = set(store.items["destination"].dropna().unique())
        if destination not in known_destinations:
            raise HTTPException(status_code=404, detail="Destination not found")
    
    df = store.items.copy()
    if destination and destination != "All":
        df = df[df["destination"] == destination]
    if item_type and item_type != "All":
        df = df[df["item_type"] == item_type]
        
    return df.to_dict(orient="records")

@router.get("/calendar", response_model=List[Dict[str, Any]])
def get_calendar(
    season: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    if store.calendar is None:
        store.load()
        
    df = store.calendar.copy()
    if season and season != "All":
        df = df[df["season"] == season]
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]
        
    return df.to_dict(orient="records")

@router.get("/history", response_model=List[Dict[str, Any]])
def get_history(
    item_id: Optional[str] = Query(default=None, max_length=50, pattern=r"^[A-Za-z0-9_-]+$"),
    destination: Optional[str] = Query(default=None, max_length=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(default=1000, ge=1, le=10000)
):
    if store.history is None or store.items is None:
        store.load()
        
    if item_id is not None:
        known_items = set(store.items["item_id"].dropna().unique())
        if item_id not in known_items:
            raise HTTPException(status_code=404, detail="Item not found")

    if destination is not None and destination != "All":
        known_destinations = set(store.items["destination"].dropna().unique())
        if destination not in known_destinations:
            raise HTTPException(status_code=404, detail="Destination not found")
        
    df = store.history.copy()
    
    # CRITICAL: Enforce True Demand Isolation - explicitly drop true_demand column
    if "true_demand" in df.columns:
        df = df.drop(columns=["true_demand"], errors="ignore")
        
    if item_id:
        df = df[df["item_id"] == item_id]
        
    if destination and destination != "All":
        # Merge with items to filter by destination, then drop destination to maintain consistent schema
        merged = df.merge(store.items[["item_id", "destination"]], on="item_id", how="inner")
        df = merged[merged["destination"] == destination].drop(columns=["destination"])
        
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]
        
    df = df.sort_values("date")
    if limit and len(df) > limit:
        df = df.head(limit)
        
    return df.to_dict(orient="records")

@router.get("/summary", response_model=Dict[str, Any])
def get_summary():
    if store.items is None or store.history is None:
        store.load()
        
    total_items = int(len(store.items))
    destinations = store.items["destination"].unique().tolist() if "destination" in store.items.columns else []
    
    total_bookings = int(store.history["bookings"].sum()) if "bookings" in store.history.columns else 0
    total_searches = int(store.history["searches"].sum()) if "searches" in store.history.columns else 0
    total_sold_out_days = int(store.history["sold_out_flag"].sum()) if "sold_out_flag" in store.history.columns else 0
    
    return {
        "total_items": total_items,
        "destinations": destinations,
        "total_bookings": total_bookings,
        "total_searches": total_searches,
        "total_sold_out_days": total_sold_out_days
    }
