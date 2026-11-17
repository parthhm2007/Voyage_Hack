import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.loader import store
from backend.model_loader import model_store

client = TestClient(app)

def test_future_window_loaded():
    store.load()
    assert store.future_window is not None
    assert len(store.future_window) > 0
    assert "item_id" in store.future_window.columns
    assert "date" in store.future_window.columns

def test_get_forecast_valid_item():
    items_res = client.get("/api/items")
    assert items_res.status_code == 200
    items = items_res.json()
    assert len(items) > 0
    item_id = items[0]["item_id"]

    res = client.get(f"/api/forecast?item_id={item_id}")
    assert res.status_code == 200
    forecasts = res.json()
    assert isinstance(forecasts, list)
    assert len(forecasts) == 90

    # Verify prediction keys and values
    rec = forecasts[0]
    assert rec["item_id"] == item_id
    assert "date" in rec
    assert "p10" in rec
    assert "p50" in rec
    assert "p90" in rec
    assert "sell_price" in rec
    assert "supplier_cost" in rec
    assert "true_demand" not in rec

    # Real nulls are preserved as None/null
    assert rec["bookings"] is None
    assert rec["searches"] is None
    assert rec["sold_out_flag"] is None

    # Verify quantile ordering across all 90 records
    for r in forecasts:
        assert 0 <= r["p10"] <= r["p50"] <= r["p90"]

def test_future_feature_matrix_no_nan_for_items():
    store.load()
    model_store.load_models()
    test_items = ["H001", "H002", "F001"]
    for item_id in test_items:
        item_df = store.future_window[store.future_window["item_id"] == item_id]
        assert len(item_df) == 90
        feature_data = item_df[model_store.feature_cols]
        nan_counts = feature_data.isna().sum().sum()
        assert nan_counts == 0, f"Item {item_id} has {nan_counts} NaNs in future feature matrix"

def test_get_forecast_unknown_item():
    res = client.get("/api/forecast?item_id=UNKNOWN-999")
    assert res.status_code == 404
    assert res.json() == {"detail": "Item not found"}

def test_get_forecast_invalid_item_id():
    res = client.get("/api/forecast?item_id=bad@item!id")
    assert res.status_code == 422
