import pandas as pd
import os

class DataStore:
    def __init__(self, data_dir: str = "data/synthetic"):
        self.data_dir = data_dir
        self.items: pd.DataFrame | None = None
        self.calendar: pd.DataFrame | None = None
        self.history: pd.DataFrame | None = None

    def load(self):
        items_path = os.path.join(self.data_dir, "inventory_items.csv")
        calendar_path = os.path.join(self.data_dir, "calendar_events.csv")
        history_path = os.path.join(self.data_dir, "daily_history.csv")

        self.items = pd.read_csv(items_path)
        self.calendar = pd.read_csv(calendar_path)
        self.history = pd.read_csv(history_path)

store = DataStore()
