import pytest
import os
from fastapi.testclient import TestClient
from backend.main import app
from backend.loader import store, DataStore, BASE_DIR

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

# --- New tests verifying findings F2, F5, F6, F7, F8, F9 ---

def test_unknown_item_id_returns_404():
    res = client.get("/api/history?item_id=UNKNOWN-999")
    assert res.status_code == 404
    assert res.json() == {"detail": "Item not found"}

def test_unknown_destination_returns_404():
    res = client.get("/api/history?destination=Atlantis")
    assert res.status_code == 404
    assert res.json() == {"detail": "Destination not found"}

    res_items = client.get("/api/items?destination=Atlantis")
    assert res_items.status_code == 404
    assert res_items.json() == {"detail": "Destination not found"}

def test_limit_bounds_validation():
    res_zero = client.get("/api/history?limit=0")
    assert res_zero.status_code == 422

    res_neg = client.get("/api/history?limit=-1")
    assert res_neg.status_code == 422

    res_over = client.get("/api/history?limit=10001")
    assert res_over.status_code == 422

def test_overlong_and_invalid_item_id_returns_422():
    overlong_id = "A" * 51
    res_over = client.get(f"/api/history?item_id={overlong_id}")
    assert res_over.status_code == 422

    res_invalid = client.get("/api/history?item_id=bad@item!id")
    assert res_invalid.status_code == 422

def test_consistent_history_schema_without_destination_column():
    items_res = client.get("/api/items")
    dest = items_res.json()[0]["destination"]

    res_unfiltered = client.get("/api/history?limit=10")
    assert res_unfiltered.status_code == 200
    rec_unfiltered = res_unfiltered.json()[0]
    assert "destination" not in rec_unfiltered
    assert "true_demand" not in rec_unfiltered

    res_filtered = client.get(f"/api/history?destination={dest}&limit=10")
    assert res_filtered.status_code == 200
    rec_filtered = res_filtered.json()[0]
    assert "destination" not in rec_filtered
    assert "true_demand" not in rec_filtered

    assert set(rec_unfiltered.keys()) == set(rec_filtered.keys())

def test_cors_headers_disallow_unauthorized_origins():
    # Disallowed origin
    res = client.options(
        "/api/items",
        headers={
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert res.headers.get("access-control-allow-origin") != "*"
    assert res.headers.get("access-control-allow-origin") != "http://evil.com"

    # Allowed origin
    res_auth = client.options(
        "/api/items",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert res_auth.headers.get("access-control-allow-origin") == "http://localhost:3000"

def test_loader_path_anchoring_from_different_cwd():
    old_cwd = os.getcwd()
    try:
        os.chdir(str(BASE_DIR / "backend"))
        new_store = DataStore()
        new_store.load()
        assert new_store.items is not None
        assert len(new_store.items) > 0
        assert "true_demand" not in new_store.history.columns
    finally:
        os.chdir(old_cwd)
