from pathlib import Path
import sys
import pandas as pd
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data" / "synthetic"
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

class DataStore:
    def __init__(self, data_dir: Path | str = DEFAULT_DATA_DIR):
        self.data_dir = Path(data_dir)
        self.items: pd.DataFrame | None = None
        self.calendar: pd.DataFrame | None = None
        self.history: pd.DataFrame | None = None
        self.future_window: pd.DataFrame | None = None

    def load(self):
        items_path = self.data_dir / "inventory_items.csv"
        calendar_path = self.data_dir / "calendar_events.csv"
        history_path = self.data_dir / "daily_history.csv"
        future_path = self.data_dir / "future_window.csv"

        self.items = pd.read_csv(items_path)
        self.calendar = pd.read_csv(calendar_path)
        raw_history = pd.read_csv(history_path)
        self.history = raw_history.drop(columns=["true_demand"], errors="ignore")
        
        raw_future = pd.read_csv(future_path)
        raw_future['date'] = pd.to_datetime(raw_future['date'])
        
        if self.history is not None:
            hist = self.history.copy()
            hist['date'] = pd.to_datetime(hist['date'])
            cols = ['date', 'item_id', 'bookings', 'searches', 'sell_price', 'supplier_cost', 'lead_days']
            hist_sub = hist[[c for c in cols if c in hist.columns]].copy()
            fut_sub = raw_future[[c for c in cols if c in raw_future.columns]].copy()
            
            # Lag and rolling feature calculation for future window:
            # Future dates lack recorded bookings and searches. To avoid NaNs from day 8 onward,
            # we fill bookings and searches in fut_sub using the per-item day-of-week average
            # of the most recent 8 weeks of history. The lag-7 and rolling-mean-7 features are
            # then computed from this filled series. We never touch or read true_demand.
            # Real nulls in raw_future remain intact for response output.
            cutoff_date = hist['date'].max() - pd.Timedelta(weeks=8)
            recent_hist = hist[hist['date'] >= cutoff_date].copy()
            recent_hist['day_of_week'] = recent_hist['date'].dt.day_of_week
            dow_profile = (
                recent_hist.groupby(['item_id', 'day_of_week'])[['bookings', 'searches']]
                .mean()
                .reset_index()
            )
            dow_profile = dow_profile.rename(
                columns={'bookings': 'fill_bookings', 'searches': 'fill_searches'}
            )
            
            fut_sub['day_of_week'] = fut_sub['date'].dt.day_of_week
            fut_sub = fut_sub.merge(dow_profile, on=['item_id', 'day_of_week'], how='left')
            fut_sub['bookings'] = fut_sub['bookings'].fillna(fut_sub['fill_bookings'])
            fut_sub['searches'] = fut_sub['searches'].fillna(fut_sub['fill_searches'])
            fut_sub = fut_sub.drop(columns=['day_of_week', 'fill_bookings', 'fill_searches'], errors='ignore')
            
            combined = pd.concat([hist_sub, fut_sub], ignore_index=True)
            combined = combined.sort_values(['item_id', 'date']).reset_index(drop=True)
            
            combined['day_of_week'] = combined['date'].dt.day_of_week
            combined['month'] = combined['date'].dt.month
            combined['day_of_month'] = combined['date'].dt.day
            combined['is_weekend'] = combined['day_of_week'].isin([5, 6]).astype(int)
            combined['margin'] = combined['sell_price'] - combined['supplier_cost']
            
            for col in ['bookings', 'searches']:
                if col in combined.columns:
                    combined[f'{col}_lag_7'] = combined.groupby('item_id')[col].shift(7)
                    combined[f'{col}_roll_mean_7'] = combined.groupby('item_id')[col].transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean())
            
            min_fut_date = raw_future['date'].min()
            future_feat = combined[combined['date'] >= min_fut_date].copy()
            future_feat['date'] = future_feat['date'].dt.strftime('%Y-%m-%d')
            raw_future['date'] = raw_future['date'].dt.strftime('%Y-%m-%d')
            
            lag_roll_cols = ['day_of_week', 'month', 'day_of_month', 'is_weekend', 'margin', 'bookings_lag_7', 'searches_lag_7', 'bookings_roll_mean_7', 'searches_roll_mean_7']
            
            self.future_window = raw_future.merge(
                future_feat[['date', 'item_id'] + [c for c in lag_roll_cols if c in future_feat.columns]],
                on=['date', 'item_id'],
                how='left'
            )
        else:
            raw_future['date'] = raw_future['date'].dt.strftime('%Y-%m-%d')
            self.future_window = raw_future

store = DataStore()
