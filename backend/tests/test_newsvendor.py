import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.loader import store
from backend.config import DEFAULT_SALVAGE_RATES

client = TestClient(app)

def test_get_newsvendor_valid_hotel():
    store.load()
    hotel_row = store.items[store.items["item_type"] == "hotel"].iloc[0]
    item_id = hotel_row["item_id"]
    base_cost = float(hotel_row["base_supplier_cost"])

    res = client.get(f"/api/newsvendor?item_id={item_id}")
    assert res.status_code == 200
    data = res.json()

    assert data["item_id"] == item_id
    assert data["item_type"] == "hotel"
    assert "critical_fractile" in data
    assert "optimal_quantity_avg" in data
    assert "total_expected_profit" in data
    assert "daily_breakdown" in data
    assert len(data["daily_breakdown"]) > 0
    assert "capacity_per_day" in data
    assert "capacity_capped" in data
    assert "assumptions" in data
    assert data["assumptions"]["salvage_rate"] == DEFAULT_SALVAGE_RATES["hotel"]

    expected_salvage = round(DEFAULT_SALVAGE_RATES["hotel"] * base_cost, 2)
    assert abs(data["salvage_value"] - expected_salvage) < 1e-2

def test_get_newsvendor_valid_flight():
    store.load()
    flight_rows = store.items[store.items["item_type"] == "flight"]
    if flight_rows.empty:
        pytest.skip("No flight items in dataset")
    flight_row = flight_rows.iloc[0]
    item_id = flight_row["item_id"]
    base_cost = float(flight_row["base_supplier_cost"])

    res = client.get(f"/api/newsvendor?item_id={item_id}")
    assert res.status_code == 200
    data = res.json()

    assert data["item_id"] == item_id
    assert data["item_type"] == "flight"
    assert data["assumptions"]["salvage_rate"] == DEFAULT_SALVAGE_RATES["flight"]
    expected_salvage = round(DEFAULT_SALVAGE_RATES["flight"] * base_cost, 2)
    assert abs(data["salvage_value"] - expected_salvage) < 1e-2

def test_get_newsvendor_with_overrides():
    store.load()
    item_id = store.items.iloc[0]["item_id"]

    res = client.get(f"/api/newsvendor?item_id={item_id}&unit_cost=100&sell_price=200&salvage_value=20")
    assert res.status_code == 200
    data = res.json()

    assert data["unit_cost"] == 100.0
    assert data["sell_price"] == 200.0
    assert data["salvage_value"] == 20.0
    assert abs(data["critical_fractile"] - (100.0 / 180.0)) < 1e-3

def test_get_newsvendor_cost_override_default_salvage():
    store.load()
    hotel_row = store.items[store.items["item_type"] == "hotel"].iloc[0]
    item_id = hotel_row["item_id"]

    res = client.get(f"/api/newsvendor?item_id={item_id}&unit_cost=500&sell_price=1000")
    assert res.status_code == 200
    data = res.json()

    expected_salvage = round(DEFAULT_SALVAGE_RATES["hotel"] * 500, 2)
    assert abs(data["salvage_value"] - expected_salvage) < 1e-2
    assert data["assumptions"]["salvage_rate"] == DEFAULT_SALVAGE_RATES["hotel"]

def test_get_newsvendor_capacity_cap_h001():
    store.load()
    res = client.get("/api/newsvendor?item_id=H001")
    assert res.status_code == 200
    data = res.json()

    cap_per_day = data["capacity_per_day"]
    days = len(data["daily_breakdown"])
    assert days == 90
    assert data["total_optimal_quantity"] <= cap_per_day * 90
    for day in data["daily_breakdown"]:
        assert day["optimal_quantity"] <= cap_per_day
    assert isinstance(data["capacity_capped"], bool)

def test_get_newsvendor_date_validation():
    store.load()
    # start > end returns 422
    res = client.get("/api/newsvendor?item_id=H001&start_date=2026-12-10&end_date=2026-12-01")
    assert res.status_code == 422
    assert "start_date must be on or before end_date" in res.json()["detail"]

    # alias start and end
    res_alias = client.get("/api/newsvendor?item_id=H001&start=2026-12-10&end=2026-12-01")
    assert res_alias.status_code == 422
    assert "start_date must be on or before end_date" in res_alias.json()["detail"]

    # Date outside available window returns 422
    res_past = client.get("/api/newsvendor?item_id=H001&start_date=2020-01-01")
    assert res_past.status_code == 422
    assert "outside the available forecast window" in res_past.json()["detail"]

def test_get_newsvendor_economics_validation():
    store.load()
    # salvage_value > unit_cost returns 422
    res_salvage = client.get("/api/newsvendor?item_id=H001&unit_cost=100&sell_price=200&salvage_value=150")
    assert res_salvage.status_code == 422
    assert "salvage_value" in res_salvage.json()["detail"]

    # sell_price < unit_cost returns 422
    res_loss = client.get("/api/newsvendor?item_id=H001&unit_cost=200&sell_price=100")
    assert res_loss.status_code == 422
    assert "sell_price" in res_loss.json()["detail"]

    # negative unit_cost returns 422
    res_neg_cost = client.get("/api/newsvendor?item_id=H001&unit_cost=-50")
    assert res_neg_cost.status_code == 422

def test_get_newsvendor_unknown_item():
    res = client.get("/api/newsvendor?item_id=UNKNOWN_999")
    assert res.status_code == 404
    assert res.json() == {"detail": "Item not found"}
