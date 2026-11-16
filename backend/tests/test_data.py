import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.loader import store

client = TestClient(app)

def test_loader():
    store.load()
    assert store.items is not None
    assert store.calendar is not None
    assert store.history is not None
    assert len(store.items) > 0
    assert len(store.calendar) > 0
    assert len(store.history) > 0

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["items_loaded"] > 0

def test_get_items():
    response = client.get("/api/items")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) > 0
    assert "item_id" in items[0]
    assert "destination" in items[0]

def test_get_items_with_filter():
    # First get items to find a destination
    res = client.get("/api/items")
    items = res.json()
    dest = items[0]["destination"]

    filtered_res = client.get(f"/api/items?destination={dest}")
    assert filtered_res.status_code == 200
    filtered_items = filtered_res.json()
    assert len(filtered_items) > 0
    for item in filtered_items:
        assert item["destination"] == dest

def test_get_calendar():
    response = client.get("/api/calendar")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)
    assert len(events) > 0
    assert "date" in events[0]

def test_get_history_and_true_demand_isolation():
    response = client.get("/api/history?limit=50")
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    assert len(history) > 0
    
    # Verify True Demand Isolation: true_demand must NOT be present in API output
    for record in history:
        assert "true_demand" not in record, "CRITICAL: true_demand leaked in API history response!"
        assert "item_id" in record
        assert "bookings" in record
        assert "searches" in record
        assert "sold_out_flag" in record

def test_get_history_filters():
    # Test item_id filter
    items_res = client.get("/api/items")
    item_id = items_res.json()[0]["item_id"]

    res = client.get(f"/api/history?item_id={item_id}&limit=10")
    assert res.status_code == 200
    records = res.json()
    assert len(records) > 0
    for r in records:
        assert r["item_id"] == item_id
        assert "true_demand" not in r

def test_get_summary():
    response = client.get("/api/summary")
    assert response.status_code == 200
    summary = response.json()
    assert "total_items" in summary
    assert "destinations" in summary
    assert "total_bookings" in summary
    assert "total_searches" in summary
    assert "total_sold_out_days" in summary
    assert summary["total_items"] > 0
