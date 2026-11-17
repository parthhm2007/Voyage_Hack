import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.loader import store

client = TestClient(app)

def test_get_optimization_valid_budget():
    store.load()
    res = client.get("/api/optimize?total_budget=1000000")
    assert res.status_code == 200
    data = res.json()

    assert data["total_budget"] == 1000000.0
    assert data["risk_appetite"] == 0.5
    assert "allocated_budget" in data
    assert "total_expected_profit" in data
    assert "portfolio_roi" in data
    assert "allocations" in data
    assert isinstance(data["allocations"], list)
    assert len(data["allocations"]) > 0

    # Verify allocation structure
    alloc = data["allocations"][0]
    assert "item_id" in alloc
    assert "allocated_budget" in alloc
    assert "units_purchased" in alloc
    assert "expected_profit" in alloc
    assert "roi" in alloc

def test_get_optimization_zero_budget():
    res = client.get("/api/optimize?total_budget=0")
    assert res.status_code == 422 # Pydantic validation error (gt=0)

def test_get_optimization_negative_budget():
    res = client.get("/api/optimize?total_budget=-50000")
    assert res.status_code == 422 # Pydantic validation error (gt=0)

def test_get_optimization_risk_appetite():
    store.load()
    res_cons = client.get("/api/optimize?total_budget=500000&risk_appetite=0.0")
    assert res_cons.status_code == 200
    data_cons = res_cons.json()
    assert data_cons["risk_appetite"] == 0.0

    res_aggr = client.get("/api/optimize?total_budget=500000&risk_appetite=1.0")
    assert res_aggr.status_code == 200
    data_aggr = res_aggr.json()
    assert data_aggr["risk_appetite"] == 1.0

    # Conservative vs aggressive should yield different expected profits or allocations
    assert data_cons["total_expected_profit"] != data_aggr["total_expected_profit"]

def test_get_optimization_invalid_risk_appetite():
    res_high = client.get("/api/optimize?total_budget=500000&risk_appetite=1.5")
    assert res_high.status_code == 422

    res_low = client.get("/api/optimize?total_budget=500000&risk_appetite=-0.1")
    assert res_low.status_code == 422
