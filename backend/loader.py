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

    def load(self):
        items_path = self.data_dir / "inventory_items.csv"
        calendar_path = self.data_dir / "calendar_events.csv"
        history_path = self.data_dir / "daily_history.csv"

        self.items = pd.read_csv(items_path)
        self.calendar = pd.read_csv(calendar_path)
        raw_history = pd.read_csv(history_path)
        self.history = raw_history.drop(columns=["true_demand"], errors="ignore")

store = DataStore()
