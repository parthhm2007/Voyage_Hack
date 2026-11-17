import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.loader import store

client = TestClient(app)

def test_future_window_loaded():
    store.load()
    assert store.future_window is not None
    assert len(store.future_window) > 0
    assert "item_id" in store.future_window.columns
    assert "date" in store.future_window.columns

def test_get_forecast_valid_item():
    # Get a valid item_id from /api/items
    items_res = client.get("/api/items")
    assert items_res.status_code == 200
    items = items_res.json()
    assert len(items) > 0
    item_id = items[0]["item_id"]

    res = client.get(f"/api/forecast?item_id={item_id}")
    assert res.status_code == 200
    forecasts = res.json()
    assert isinstance(forecasts, list)
    assert len(forecasts) > 0

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

    # Verify quantile ordering across records
    for r in forecasts:
        assert r["p10"] <= r["p90"]
        assert 0 <= r["p10"]
        assert 0 <= r["p50"]
        assert 0 <= r["p90"]

def test_get_forecast_unknown_item():
    res = client.get("/api/forecast?item_id=UNKNOWN-999")
    assert res.status_code == 404
    assert res.json() == {"detail": "Item not found"}

def test_get_forecast_invalid_item_id():
    res = client.get("/api/forecast?item_id=bad@item!id")
    assert res.status_code == 422
