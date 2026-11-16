import os
from pathlib import Path
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "synthetic"
MODELS_DIR = BASE_DIR / "backend" / "models"

def pinball_loss(y_true, y_pred, alpha):
    diff = y_true - y_pred
    return np.mean(np.maximum(alpha * diff, (alpha - 1) * diff))

def train():
    print("Loading daily history...")
    history_path = DATA_DIR / "daily_history.csv"
    df = pd.read_csv(history_path)
    
    # Ensure date is datetime and sort
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['item_id', 'date']).reset_index(drop=True)
    
    print("Engineering features...")
    # Temporal features
    df['day_of_week'] = df['date'].dt.day_of_week
    df['month'] = df['date'].dt.month
    df['day_of_month'] = df['date'].dt.day
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Gross margin
    df['margin'] = df['sell_price'] - df['supplier_cost']
    
    # Lag and rolling features per item_id
    feature_cols = []
    lag_cols = ['bookings', 'searches']
    rolling_cols = ['bookings', 'searches']
    
    for col in lag_cols:
        df[f'{col}_lag_7'] = df.groupby('item_id')[col].shift(7)
        feature_cols.append(f'{col}_lag_7')
        
    for col in rolling_cols:
        df[f'{col}_roll_mean_7'] = df.groupby('item_id')[col].transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean())
        feature_cols.append(f'{col}_roll_mean_7')
        
    base_features = ['day_of_week', 'month', 'day_of_month', 'is_weekend', 'sell_price', 'supplier_cost', 'lead_days', 'margin']
    all_features = base_features + feature_cols
    
    # Drop rows with NaN from lagging
    df = df.dropna(subset=all_features + ['bookings']).reset_index(drop=True)
    
    # Chronological 80/20 train/validation split
    dates = np.sort(df['date'].unique())
    split_idx = int(len(dates) * 0.8)
    split_date = dates[split_idx]
    
    train_df = df[df['date'] < split_date]
    val_df = df[df['date'] >= split_date]
    
    X_train = train_df[all_features]
    y_train = train_df['bookings']
    X_val = val_df[all_features]
    y_val = val_df['bookings']
    
    print(f"Train samples: {len(X_train)}, Validation samples: {len(X_val)}")
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    quantiles = [0.10, 0.50, 0.90]
    models = {}
    
    for q in quantiles:
        print(f"Training XGBoost quantile model for alpha={q}...")
        model = xgb.XGBRegressor(
            objective='reg:quantileerror',
            quantile_alpha=q,
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        
        preds = model.predict(X_val)
        loss = pinball_loss(y_val.values, preds, q)
        print(f"Validation Pinball Loss (alpha={q}): {loss:.4f}")
        
        model_filename = MODELS_DIR / f"model_p{int(q*100)}.json"
        model.save_model(model_filename)
        print(f"Saved model to {model_filename}")
        models[q] = model
        
    # Also save feature columns list for loader/inference consistency
    joblib.dump(all_features, MODELS_DIR / "feature_cols.pkl")
    print("Feature columns saved successfully.")

if __name__ == '__main__':
    train()
