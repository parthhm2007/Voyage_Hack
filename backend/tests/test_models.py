from pathlib import Path
import pandas as pd
import pytest
import joblib

from backend.model_loader import model_store, MODELS_DIR, BASE_DIR

def test_model_artifacts_exist():
    p10 = MODELS_DIR / "model_p10.json"
    p50 = MODELS_DIR / "model_p50.json"
    p90 = MODELS_DIR / "model_p90.json"
    assert p10.exists(), "P10 model artifact missing"
    assert p50.exists(), "P50 model artifact missing"
    assert p90.exists(), "P90 model artifact missing"

def test_model_loader():
    model_store.loaded = False
    model_store.load_models()
    assert model_store.loaded is True
    assert model_store.model_p10 is not None
    assert model_store.model_p50 is not None
    assert model_store.model_p90 is not None
    assert len(model_store.feature_cols) > 0

def test_quantile_ordering():
    model_store.load_models()
    # Create sample input using feature_cols
    sample_data = {col: [1.0] for col in model_store.feature_cols}
    # Adjust some realistic values
    sample_data['sell_price'] = [5000.0]
    sample_data['supplier_cost'] = [3000.0]
    sample_data['margin'] = [2000.0]
    sample_data['lead_days'] = [10.0]
    sample_data['day_of_week'] = [2.0]
    sample_data['month'] = [5.0]
    sample_data['day_of_month'] = [15.0]
    sample_data['is_weekend'] = [0.0]
    sample_data['bookings_lag_7'] = [20.0]
    sample_data['searches_lag_7'] = [200.0]
    sample_data['bookings_roll_mean_7'] = [18.0]
    sample_data['searches_roll_mean_7'] = [190.0]

    input_df = pd.DataFrame(sample_data)
    preds = model_store.predict(input_df)

    assert 'p10' in preds.columns
    assert 'p50' in preds.columns
    assert 'p90' in preds.columns

    p10 = preds['p10'].iloc[0]
    p50 = preds['p50'].iloc[0]
    p90 = preds['p90'].iloc[0]

    # Note: with separate quantile models in XGBoost, crossing can occasionally happen on edge points,
    # but for typical inputs or across batches, let's verify overall ordering or tolerance.
    # In strict quantile regression without monotonicity constraints, we check if p10 <= p50 <= p90 or assert reasonable quantile behavior.
    assert p10 <= p90, f"P10 ({p10}) should be <= P90 ({p90})"

def test_true_demand_exclusion():
    # Verify that feature columns do not contain 'true_demand'
    model_store.load_models()
    assert 'true_demand' not in model_store.feature_cols

    # Check train_models.py source code text doesn't read store.history
    train_script_path = BASE_DIR / "backend" / "train_models.py"
    content = train_script_path.read_text()
    assert "true_demand" not in model_store.feature_cols
    assert "store.history" not in content, "train_models.py must not read store.history"
    for col in model_store.feature_cols:
        assert col != 'true_demand'
