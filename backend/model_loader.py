from pathlib import Path
import joblib
import pandas as pd
import xgboost as xgb

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "backend" / "models"

class ModelStore:
    def __init__(self, models_dir: Path | str = MODELS_DIR):
        self.models_dir = Path(models_dir)
        self.model_p10 = None
        self.model_p50 = None
        self.model_p90 = None
        self.feature_cols = None
        self.loaded = False

    def load_models(self):
        if self.loaded:
            return
        
        p10_path = self.models_dir / "model_p10.json"
        p50_path = self.models_dir / "model_p50.json"
        p90_path = self.models_dir / "model_p90.json"
        feats_path = self.models_dir / "feature_cols.pkl"

        if not (p10_path.exists() and p50_path.exists() and p90_path.exists()):
            raise FileNotFoundError("Model artifact files not found in models directory.")

        self.model_p10 = xgb.XGBRegressor()
        self.model_p10.load_model(p10_path)

        self.model_p50 = xgb.XGBRegressor()
        self.model_p50.load_model(p50_path)

        self.model_p90 = xgb.XGBRegressor()
        self.model_p90.load_model(p90_path)

        if feats_path.exists():
            self.feature_cols = joblib.load(feats_path)
        else:
            self.feature_cols = [
                'day_of_week', 'month', 'day_of_month', 'is_weekend',
                'sell_price', 'supplier_cost', 'lead_days', 'margin',
                'bookings_lag_7', 'searches_lag_7', 'bookings_roll_mean_7', 'searches_roll_mean_7'
            ]

        self.loaded = True

    def predict(self, input_df: pd.DataFrame) -> pd.DataFrame:
        self.load_models()
        missing = [c for c in self.feature_cols if c not in input_df.columns]
        if missing:
            raise ValueError(f"Missing required feature columns: {missing}")

        X = input_df[self.feature_cols]
        p10 = self.model_p10.predict(X)
        p50 = self.model_p50.predict(X)
        p90 = self.model_p90.predict(X)

        res = pd.DataFrame({
            'p10': p10,
            'p50': p50,
            'p90': p90
        })
        return res

def clamp_and_sort_quantiles(p10: float, p50: float, p90: float) -> tuple[float, float, float]:
    """
    Ensure quantile predictions are non-negative and properly ordered:
    1. Clamps each quantile at >= 0.0.
    2. Sorts so that p10 <= p50 <= p90.
    """
    c10 = max(0.0, float(p10))
    c50 = max(0.0, float(p50))
    c90 = max(0.0, float(p90))
    s10, s50, s90 = sorted([c10, c50, c90])
    return s10, s50, s90

model_store = ModelStore()
