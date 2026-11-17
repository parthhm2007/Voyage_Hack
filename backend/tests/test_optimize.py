import math
import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from backend.main import app
from backend.loader import store
from backend.config import get_risk_weights, MAX_BUDGET
from backend.routers.optimize import get_budget_optimization
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture(autouse=True)
def ensure_store_loaded():
    if store.future_window is None or store.items is None:
        store.load()

def test_get_optimization_valid_budget():
    res = client.get("/api/optimize?total_budget=1000000")
    assert res.status_code == 200
    data = res.json()

    assert data["total_budget"] == 1000000.0
    assert data["risk_appetite"] == 0.5
    assert "allocated_budget" in data
    assert "total_expected_profit" in data
    assert "portfolio_roi" in data
    assert "allocations" in data
    assert "assumptions" in data
    assert "excluded" in data

    # 1. Budget never exceeded
    assert data["allocated_budget"] <= data["total_budget"]

    # 2. Total spent equals sum of line allocated_budget values exactly
    line_spend_sum = round(sum(a["allocated_budget"] for a in data["allocations"]), 2)
    assert data["allocated_budget"] == line_spend_sum

    # 3. Total profit equals sum of line expected_profit values exactly
    line_profit_sum = round(sum(a["expected_profit"] for a in data["allocations"]), 2)
    assert data["total_expected_profit"] == line_profit_sum

    # 4. Strict true_demand exclusion
    assert "true_demand" not in str(data), "CRITICAL: true_demand leaked in response!"

    # 5. Line item integrity
    num_days = data["assumptions"]["days"]
    for alloc in data["allocations"]:
        # Units purchased is an integer >= 0 and <= capacity_per_day * number_of_days
        units = alloc["units_purchased"]
        assert isinstance(units, int) or (isinstance(units, float) and units.is_integer()), f"Units {units} must be integer"
        assert units >= 0
        cap_max = alloc["capacity_per_day"] * num_days
        assert units <= cap_max, f"Item {alloc['item_id']} units {units} exceeds max window cap {cap_max}"

        # allocated_budget == units_purchased * unit_cost
        expected_cost = round(units * alloc["unit_cost"], 2)
        assert alloc["allocated_budget"] == expected_cost, f"Item {alloc['item_id']} spend mismatch"

        # No non-positive profit units
        if units > 0:
            assert alloc["expected_profit"] > 0, f"Item {alloc['item_id']} bought with non-positive profit"

def test_get_optimization_edge_budgets():
    # A) Budget 0: returns explained empty allocation
    res_zero = client.get("/api/optimize?total_budget=0")
    assert res_zero.status_code == 200
    data_zero = res_zero.json()
    assert data_zero["allocated_budget"] == 0.0
    assert data_zero["total_expected_profit"] == 0.0
    assert all(a["units_purchased"] == 0 for a in data_zero["allocations"])
    assert "note" in data_zero
    assert "0" in data_zero["note"]

    # B) Tiny budget below cheapest unit (cheapest unit is ₹1347)
    res_tiny = client.get("/api/optimize?total_budget=500")
    assert res_tiny.status_code == 200
    data_tiny = res_tiny.json()
    assert data_tiny["allocated_budget"] == 0.0
    assert all(a["units_purchased"] == 0 for a in data_tiny["allocations"])
    assert "note" in data_tiny
    assert "less than the cheapest" in data_tiny["note"]

    # C) Huge budget (₹500,000,000): all items within physical capacity limits
    res_huge = client.get("/api/optimize?total_budget=500000000")
    assert res_huge.status_code == 200
    data_huge = res_huge.json()
    assert data_huge["allocated_budget"] <= 500000000.0
    num_days = data_huge["assumptions"]["days"]
    for alloc in data_huge["allocations"]:
        assert alloc["units_purchased"] <= alloc["capacity_per_day"] * num_days
    # Specifically check H014 (capacity_per_day = 10, max window cap = 900)
    h014 = [a for a in data_huge["allocations"] if a["item_id"] == "H014"][0]
    assert h014["units_purchased"] <= 900

def test_get_optimization_risk_appetite_monotonicity():
    # 1. Weights sum to 1 and are monotonic
    for r in [0.0, 0.25, 0.5, 0.75, 1.0]:
        w10, w50, w90 = get_risk_weights(r)
        assert math.isclose(w10 + w50 + w90, 1.0, rel_tol=1e-5)
        assert w10 >= 0 and w50 >= 0 and w90 >= 0

    w10_0, _, w90_0 = get_risk_weights(0.0)
    w10_5, _, w90_5 = get_risk_weights(0.5)
    w10_1, _, w90_1 = get_risk_weights(1.0)

    # Monotonicity checks: higher appetite never lowers P90 weight and never raises P10 weight
    assert w10_0 >= w10_5 >= w10_1
    assert w90_0 <= w90_5 <= w90_1

    # Endpoints exact checks
    assert math.isclose(w10_0, 0.60) and math.isclose(w90_0, 0.00)
    assert math.isclose(w10_5, 0.25) and math.isclose(w90_5, 0.25)
    assert math.isclose(w10_1, 0.00) and math.isclose(w90_1, 0.70)

    # API responses across risk appetite
    res_cons = client.get("/api/optimize?total_budget=500000&risk_appetite=0.0")
    res_bal = client.get("/api/optimize?total_budget=500000&risk_appetite=0.5")
    res_aggr = client.get("/api/optimize?total_budget=500000&risk_appetite=1.0")

    assert res_cons.status_code == 200
    assert res_bal.status_code == 200
    assert res_aggr.status_code == 200

    data_cons = res_cons.json()
    data_bal = res_bal.json()
    data_aggr = res_aggr.json()

    assert data_cons["risk_appetite"] == 0.0
    assert data_bal["risk_appetite"] == 0.5
    assert data_aggr["risk_appetite"] == 1.0

def test_get_optimization_validation_errors():
    # Negative budget -> 422
    assert client.get("/api/optimize?total_budget=-50000").status_code == 422

    # Over MAX_BUDGET -> 422
    assert client.get(f"/api/optimize?total_budget={MAX_BUDGET + 1}").status_code == 422

    # Infinity and NaN budget -> 422
    assert client.get("/api/optimize?total_budget=inf").status_code == 422
    assert client.get("/api/optimize?total_budget=nan").status_code == 422

    # Risk appetite out of range -> 422
    assert client.get("/api/optimize?total_budget=500000&risk_appetite=-0.1").status_code == 422
    assert client.get("/api/optimize?total_budget=500000&risk_appetite=1.5").status_code == 422

    # Inverted dates -> 422
    res_inv = client.get("/api/optimize?total_budget=500000&start_date=2026-12-01&end_date=2026-01-01")
    assert res_inv.status_code == 422
    assert "on or before" in res_inv.json()["detail"]

    # Malformed dates -> 422
    assert client.get("/api/optimize?total_budget=500000&start_date=invalid-date").status_code == 422
    assert client.get("/api/optimize?total_budget=500000&end_date=2026/12/01").status_code == 422

def test_get_optimization_determinism_and_ties():
    res1 = client.get("/api/optimize?total_budget=500000&risk_appetite=0.5")
    res2 = client.get("/api/optimize?total_budget=500000&risk_appetite=0.5")
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res1.json() == res2.json()

def test_get_optimization_nan_prediction_raises_500():
    from backend.model_loader import model_store
    
    real_predict = model_store.predict
    def mock_predict_with_nan(df):
        res = real_predict(df)
        res.loc[0, "p50"] = np.nan
        return res

    with patch.object(model_store, "predict", side_effect=mock_predict_with_nan):
        res = client.get("/api/optimize?total_budget=500000")
        assert res.status_code == 500
        detail = res.json()["detail"]
        assert "NaN" in detail
        assert "date" in detail

def test_direct_python_invocation():
    # Finding 18: Function can be invoked directly in Python with defaults
    res = get_budget_optimization()
    assert res["total_budget"] == 500000.0
    assert res["risk_appetite"] == 0.5
    assert res["allocated_budget"] <= 500000.0
    assert isinstance(res["allocations"], list)
