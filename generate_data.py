#!/usr/bin/env python3
"""
generate_data.py
================
Synthetic travel-inventory data for the TBO.com pre-buy optimization project.

Creates four CSVs in ./data/synthetic/ :
  1. inventory_items.csv  - 120 items (80 hotels + 40 flight routes, 12 destinations,
                            budget / mid / luxury tiers, capacity 10-150)
  2. calendar_events.csv  - daily calendar: 3 years history (1095 days) + next 90 days
  3. daily_history.csv    - one row per item per history day (~131,400 rows), incl. true_demand
  4. future_window.csv    - one row per item per future day (10,800 rows). Same feature
                            columns; outcome columns are EMPTY; true_demand is not present.

Only pandas + numpy are used. Fixed seed (42) => fully reproducible. Runs in a few seconds.

KEY DESIGN IDEA - DEMAND CENSORING
----------------------------------
true_demand is what customers WOULD have booked with unlimited supply.
bookings = min(true_demand, capacity_per_day), so on sold-out days observed bookings
understate demand. A model trained on raw bookings under-forecasts peaks; correcting that
bias is the point of the project. true_demand exists ONLY in daily_history.csv as ground
truth for evaluation - it must NEVER be used as a model feature.
"""

import os
import time

import numpy as np
import pandas as pd

T_START = time.time()

# --------------------------------------------------------------------------
# 0. Global configuration
# --------------------------------------------------------------------------
SEED = 42
rng = np.random.default_rng(SEED)  # single main RNG => reproducible everywhere

OUT_DIR = os.path.join(".", "data", "synthetic")
os.makedirs(OUT_DIR, exist_ok=True)

TODAY = pd.Timestamp("2026-11-15")                    # "now" of the project
HIST_DAYS = 1095                                      # 3 years of history
FUT_DAYS = 90                                         # next 90 days to forecast
HIST_START = TODAY - pd.Timedelta(days=HIST_DAYS)     # 2023-11-16
HIST_END = TODAY - pd.Timedelta(days=1)               # 2026-11-14
FUT_START = TODAY                                     # 2026-11-15
FUT_END = TODAY + pd.Timedelta(days=FUT_DAYS - 1)     # 2027-02-12

DESTINATIONS = ["Goa", "Dubai", "Bali", "Manali", "Singapore", "Jaipur",
                "Kerala", "Bangkok", "Maldives", "Udaipur", "Kashmir", "Phuket"]
DEST_IDX = {d: i for i, d in enumerate(DESTINATIONS)}

# Calibration target: share of history rows with sold_out_flag = 1.
TARGET_SOLD_OUT = 0.20          # script auto-tunes demand level to land near this (15%-25% required)

# --------------------------------------------------------------------------
# 1. Behavioural parameters (the "rules" of the simulated world)
# --------------------------------------------------------------------------
# Destination-specific yearly seasonality, Jan..Dec (1.0 = average month). Deliberately sharp
# so the seasonal peak is clearly visible and learnable:
#   Goa Nov-Feb | Dubai Nov-Mar | Manali Apr-Jun + Dec | Kerala Sep(end of monsoon)-Feb
DEST_MONTH_PROFILE = np.array([
    # Jan   Feb   Mar   Apr   May   Jun   Jul   Aug   Sep   Oct   Nov   Dec
    [1.50, 1.35, 0.95, 0.75, 0.65, 0.45, 0.40, 0.45, 0.60, 0.90, 1.40, 1.70],  # Goa
    [1.50, 1.45, 1.30, 0.90, 0.70, 0.55, 0.50, 0.55, 0.70, 1.00, 1.45, 1.60],  # Dubai
    [0.90, 0.80, 0.85, 1.00, 1.10, 1.25, 1.50, 1.55, 1.30, 1.10, 0.90, 1.30],  # Bali (Jul-Aug dry season)
    [1.00, 0.80, 0.80, 1.40, 1.80, 1.60, 0.55, 0.50, 0.65, 0.90, 0.75, 1.60],  # Manali
    [1.00, 0.95, 0.95, 1.00, 1.10, 1.30, 1.25, 1.10, 0.90, 0.95, 1.05, 1.45],  # Singapore
    [1.40, 1.40, 1.15, 0.70, 0.50, 0.45, 0.55, 0.65, 0.80, 1.30, 1.60, 1.60],  # Jaipur (Oct-Mar)
    [1.45, 1.30, 0.95, 0.80, 0.70, 0.60, 0.65, 0.80, 1.05, 1.30, 1.40, 1.60],  # Kerala
    [1.40, 1.30, 1.00, 0.95, 0.75, 0.75, 0.85, 0.85, 0.75, 0.95, 1.30, 1.50],  # Bangkok
    [1.50, 1.50, 1.40, 1.20, 0.70, 0.55, 0.60, 0.70, 0.60, 0.85, 1.35, 1.70],  # Maldives (Nov-Apr dry)
    [1.30, 1.40, 1.20, 0.75, 0.50, 0.45, 0.55, 0.65, 0.80, 1.30, 1.60, 1.60],  # Udaipur (wedding season)
    [1.20, 0.90, 0.90, 1.40, 1.80, 1.60, 1.20, 1.00, 0.80, 0.90, 0.60, 1.00],  # Kashmir (summer + snow)
    [1.50, 1.45, 1.30, 1.00, 0.60, 0.50, 0.55, 0.55, 0.50, 0.75, 1.30, 1.70],  # Phuket (Nov-Apr dry)
])

# Yearly growth trend per destination, within the required 5%-10% band.
# trend = (1 + g) ** years_since_history_start  (compound growth).
DEST_ANNUAL_GROWTH = np.array([0.06, 0.08, 0.10, 0.05, 0.07, 0.06,
                               0.08, 0.05, 0.10, 0.09, 0.10, 0.07])

# Day-of-week demand curve (Mon..Sun). This is the "weekend multiplier": hotels peak Fri/Sat,
# flights peak Fri/Sun (return trips), midweek is weakest.
DOW_MULT = {
    "hotel":  np.array([0.88, 0.85, 0.88, 0.95, 1.15, 1.30, 1.12]),
    "flight": np.array([1.05, 0.92, 0.90, 0.98, 1.15, 1.00, 1.12]),
}

# Calendar-driven multipliers.
SEASON_MULT = {"peak": 1.15, "shoulder": 1.00, "off": 0.85}   # global calendar season
SCHOOL_VACATION_MULT = 1.08                                   # family travel uplift
EVENT_BOOST = {                                               # holiday / long-weekend uplift
    "Diwali": 1.30, "Christmas/New Year": 1.40, "Holi": 1.15, "Dussehra": 1.12,
    "Eid": 1.10, "Good Friday": 1.10, "Republic Day": 1.12, "Independence Day": 1.12,
    "Long Weekend": 1.18,
}

# Demand shocks: (label, destination, start, end, kind, magnitude). NOT visible in any feature,
# so the model sees them as outliers / regime changes.
#   "decay": multiplier = 1 + mag * exp(-days_since_start / 10)   (viral spike that fades)
#   "flat" : multiplier = mag for the whole window
SHOCKS = [
    ("Bali viral-trend spike",       "Bali",     "2025-03-10", "2025-04-09", "decay", 1.20),
    ("Manali road-closure dip (3w)", "Manali",   "2025-07-05", "2025-07-25", "flat",  0.30),
    ("Dubai flight-disruption dip",  "Dubai",    "2025-12-01", "2025-12-10", "flat",  0.45),
    ("Maldives influencer spike",    "Maldives", "2026-01-10", "2026-01-23", "flat",  1.60),
]

# Supplier-cost rules.
SEASON_COST_IDX = {"peak": 1.18, "shoulder": 1.00, "off": 0.88}   # peak => pricier
ANNUAL_COST_INFLATION = 0.04      # ~4%/yr general inflation
LEAD_DRIFT_MAX = 0.18             # cost up to +18% right before travel ...
LEAD_DRIFT_TAU = 45.0             # ... decaying with an e-fold of 45 days (pre-buy incentive)

# Demand noise: Negative Binomial built as a Gamma-Poisson mixture.
# NB_K=25 => gamma multiplier has ~20% std; Poisson on top. Moderate, not dominant.
NB_K = 25.0

# Cancellation rule: cancel_prob = base + 0.14 * (1 - exp(-lead_days / 50)); rises with lead time.
CANCEL_LEAD_COEF = 0.14
CANCEL_LEAD_TAU = 50.0

# --------------------------------------------------------------------------
# 2. calendar_events.csv
# --------------------------------------------------------------------------
# Approximate dates of movable festivals: (name, centre date, +/- window days).
# Window 0 => single-day holiday (used to derive long weekends).
HOLIDAYS = [
    ("Diwali", "2023-11-12", 2), ("Diwali", "2024-11-01", 2),
    ("Diwali", "2025-10-20", 2), ("Diwali", "2026-11-08", 2),
    ("Dussehra", "2024-10-12", 0), ("Dussehra", "2025-10-02", 0), ("Dussehra", "2026-10-20", 0),
    ("Holi", "2024-03-25", 0), ("Holi", "2025-03-14", 0), ("Holi", "2026-03-04", 0),
    ("Eid", "2024-04-11", 0), ("Eid", "2025-03-31", 0), ("Eid", "2026-03-20", 0),
    ("Good Friday", "2024-03-29", 0), ("Good Friday", "2025-04-18", 0), ("Good Friday", "2026-04-03", 0),
    ("Republic Day", "2024-01-26", 0), ("Republic Day", "2025-01-26", 0),
    ("Republic Day", "2026-01-26", 0), ("Republic Day", "2027-01-26", 0),
    ("Independence Day", "2024-08-15", 0), ("Independence Day", "2025-08-15", 0),
    ("Independence Day", "2026-08-15", 0),
]


def build_calendar() -> pd.DataFrame:
    """One row per day from HIST_START to FUT_END."""
    dates = pd.date_range(HIST_START, FUT_END, freq="D")
    cal = pd.DataFrame({"date": dates})
    n = len(cal)
    md = (cal["date"].dt.month * 100 + cal["date"].dt.day).values   # e.g. Dec 25 -> 1225

    cal["is_weekend"] = (cal["date"].dt.dayofweek >= 5).astype(int)  # Sat/Sun

    # Event names: broad periods first; specific holidays and long weekends override them.
    event = np.full(n, "", dtype=object)
    event[(md >= 616) & (md <= 915)] = "Monsoon Off-Season"   # Jun 16 - Sep 15
    event[(md >= 420) & (md <= 610)] = "Summer Vacation"      # Apr 20 - Jun 10
    is_holiday = np.zeros(n, dtype=int)

    # School vacation: summer break, Christmas break, and the days around Diwali.
    school = ((md >= 420) & (md <= 610)) | (md >= 1220) | (md <= 105)
    near_diwali = np.zeros(n, dtype=bool)    # +/-10 days around Diwali => peak season

    for name, centre, half_window in HOLIDAYS:
        signed = (cal["date"] - pd.Timestamp(centre)).dt.days.values
        in_window = np.abs(signed) <= half_window
        event[in_window] = name
        is_holiday[in_window] = 1
        if name == "Diwali":
            near_diwali |= np.abs(signed) <= 10
            school |= (signed >= -3) & (signed <= 5)      # Diwali school break

    # Christmas / New Year: Dec 24 - Jan 2.
    xmas = (md >= 1224) | (md <= 102)
    event[xmas] = "Christmas/New Year"
    is_holiday[xmas] = 1

    # Long weekends: single-day holiday on Fri/Mon => adjacent Sat+Sun; on Tue/Thu => bridge day
    # plus the weekend. These days are not holidays themselves but get their own uplift.
    long_weekend = np.zeros(n, dtype=bool)
    bridge_offsets = {4: [1, 2], 0: [-2, -1], 1: [-3, -2, -1], 3: [1, 2, 3]}
    for name, centre, half_window in HOLIDAYS:
        if half_window != 0:
            continue
        c = pd.Timestamp(centre)
        for off in bridge_offsets.get(c.dayofweek, []):
            long_weekend |= (cal["date"] == c + pd.Timedelta(days=off)).values
    long_weekend &= (is_holiday == 0)
    event[long_weekend] = "Long Weekend"

    # Season: peak / shoulder / off.
    season = np.full(n, "shoulder", dtype=object)
    season[(md >= 616) & (md <= 915)] = "off"                                           # monsoon
    peak = ((md >= 415) & (md <= 615)) | (md >= 1215) | (md <= 110) | near_diwali
    season[peak] = "peak"                                                               # summer, Xmas/NY, Diwali

    cal["is_holiday"] = is_holiday
    cal["event_name"] = event
    cal["season"] = season
    cal["school_vacation_flag"] = school.astype(int)
    return cal[["date", "is_weekend", "is_holiday", "event_name",
                "season", "school_vacation_flag"]]


# --------------------------------------------------------------------------
# 3. inventory_items.csv (+ hidden simulation parameters)
# --------------------------------------------------------------------------
# 80 hotels: 8 destinations x 7 + 4 destinations x 6.
HOTEL_COUNTS = {"Goa": 7, "Dubai": 7, "Bali": 7, "Manali": 6, "Singapore": 7, "Jaipur": 7,
                "Kerala": 7, "Bangkok": 7, "Maldives": 6, "Udaipur": 6, "Kashmir": 6, "Phuket": 7}
HOTEL_TIER_PLAN = {6: ["budget", "budget", "mid", "mid", "luxury", "luxury"],
                   7: ["budget", "budget", "mid", "mid", "mid", "luxury", "luxury"]}
HOTEL_BASE_COST = {  # supplier cost per room-night (INR) for a MID-tier hotel
    "Goa": 3500, "Dubai": 9000, "Bali": 5500, "Manali": 3000, "Singapore": 11000, "Jaipur": 3200,
    "Kerala": 3800, "Bangkok": 4500, "Maldives": 15000, "Udaipur": 4200, "Kashmir": 3800,
    "Phuket": 5200,
}
HOTEL_PREFIX = {  # fictional name stems
    "Goa": "Azure Coast", "Dubai": "Marina Gold", "Bali": "Ubud Jade", "Manali": "Pine Ridge",
    "Singapore": "Lion Bay", "Jaipur": "Pink City", "Kerala": "Backwater Palm",
    "Bangkok": "Siam Orchid", "Maldives": "Coral Atoll", "Udaipur": "Lakeview Mewar",
    "Kashmir": "Chinar Valley", "Phuket": "Andaman Pearl",
}
HOTEL_SUFFIX = {
    "budget": ["Budget Inn", "Backpacker Lodge", "Value Stay"],
    "mid": ["Comfort Suites", "Heritage Boutique", "City Retreat"],
    "luxury": ["Grand Resort", "Royal Residences", "Signature Villas"],
}
HOTEL_TIER_COST_MULT = {"budget": 0.45, "mid": 1.00, "luxury": 2.40}
HOTEL_TIER_CAP = {"budget": (60, 150), "mid": (30, 90), "luxury": (10, 35)}   # rooms/day

# 40 flight routes: destination -> list of (origin city, origin code).
DEST_AIRPORT = {"Goa": "GOI", "Dubai": "DXB", "Bali": "DPS", "Manali": "KUU", "Singapore": "SIN",
                "Jaipur": "JAI", "Kerala": "COK", "Bangkok": "BKK", "Maldives": "MLE",
                "Udaipur": "UDR", "Kashmir": "SXR", "Phuket": "HKT"}
MUM, DEL, BLR = ("Mumbai", "BOM"), ("Delhi", "DEL"), ("Bengaluru", "BLR")
HYD, MAA, CCU = ("Hyderabad", "HYD"), ("Chennai", "MAA"), ("Kolkata", "CCU")
IXC, AMD = ("Chandigarh", "IXC"), ("Ahmedabad", "AMD")
FLIGHT_ROUTES = {
    "Goa": [MUM, DEL, BLR, HYD], "Dubai": [MUM, DEL, BLR, HYD], "Bali": [DEL, MUM, BLR],
    "Manali": [DEL, IXC], "Singapore": [MUM, DEL, MAA, BLR], "Jaipur": [MUM, BLR, CCU],
    "Kerala": [MUM, DEL, BLR, MAA], "Bangkok": [DEL, MUM, CCU, BLR], "Maldives": [MUM, DEL, BLR],
    "Udaipur": [MUM, DEL, AMD], "Kashmir": [DEL, MUM, BLR], "Phuket": [DEL, MUM, BLR],
}
FLIGHT_BASE_COST = {  # supplier cost per seat (INR), mid tier
    "Goa": 4500, "Dubai": 14000, "Bali": 22000, "Manali": 7500, "Singapore": 20000, "Jaipur": 4800,
    "Kerala": 5200, "Bangkok": 12000, "Maldives": 18000, "Udaipur": 5500, "Kashmir": 7500,
    "Phuket": 13000,
}
FLIGHT_CAP_RANGE = {  # seats/day the platform can hold, by destination (small planes => small caps)
    "Manali": (10, 30), "Maldives": (20, 60), "Kashmir": (40, 120), "Udaipur": (40, 100),
    "Goa": (60, 150), "Jaipur": (60, 150), "Kerala": (60, 150),
    "Dubai": (40, 120), "Bali": (40, 120), "Singapore": (40, 120), "Bangkok": (40, 120),
    "Phuket": (40, 120),
}
FLIGHT_TIER_PLAN = ["mid", "budget", "luxury", "mid"]          # by route index within destination
FLIGHT_TIER_COST_MULT = {"budget": 0.75, "mid": 1.00, "luxury": 1.90}

# Price sensitivity by tier: budget shoppers are the most price-elastic, luxury the least.
TIER_ELASTICITY = {"budget": (1.3, 2.0), "mid": (0.9, 1.5), "luxury": (0.5, 1.0)}


def build_items() -> pd.DataFrame:
    """
    Returns a frame with the 7 public columns PLUS hidden simulation parameters
    (tier, markup, conv_rate, elasticity, base_util, cancel_base). Hidden columns are NOT
    written to inventory_items.csv.
    """
    rows = []

    # ---- 80 hotels ----
    h = 1
    for dest in DESTINATIONS:
        tiers = HOTEL_TIER_PLAN[HOTEL_COUNTS[dest]]
        used = {"budget": 0, "mid": 0, "luxury": 0}
        for tier in tiers:
            suffix = HOTEL_SUFFIX[tier][used[tier]]; used[tier] += 1
            cost = round(HOTEL_BASE_COST[dest] * HOTEL_TIER_COST_MULT[tier] * rng.uniform(0.92, 1.08))
            markup = rng.uniform(0.22, 0.40)                       # hotels: richer margin
            lo, hi = HOTEL_TIER_CAP[tier]
            rows.append(dict(
                item_id=f"H{h:03d}", item_type="hotel", destination=dest,
                name=f"{HOTEL_PREFIX[dest]} {suffix}",
                capacity_per_day=int(rng.integers(lo, hi + 1)),
                base_supplier_cost=float(cost),
                base_sell_price=round(cost * (1 + markup), 2),
                tier=tier, markup=markup,
                conv_rate=rng.uniform(0.03, 0.12),                 # look-to-book 3%-12%
                elasticity=rng.uniform(*TIER_ELASTICITY[tier]),
                base_util=rng.uniform(0.45, 0.75),                 # avg demand / capacity (pre-calibration)
                cancel_base=0.06,
            ))
            h += 1

    # ---- 40 flight routes ----
    f = 1
    for dest in DESTINATIONS:
        for k, (city, code) in enumerate(FLIGHT_ROUTES[dest]):
            tier = FLIGHT_TIER_PLAN[k % len(FLIGHT_TIER_PLAN)]
            cost = round(FLIGHT_BASE_COST[dest] * FLIGHT_TIER_COST_MULT[tier] * rng.uniform(0.90, 1.15))
            markup = rng.uniform(0.15, 0.28)                       # flights: thinner margin
            lo, hi = FLIGHT_CAP_RANGE[dest]
            cap = int(rng.integers(lo, hi + 1))
            if tier == "luxury":                                   # premium cabins: far fewer seats
                cap = max(10, cap // 2)
            rows.append(dict(
                item_id=f"F{f:03d}", item_type="flight", destination=dest,
                name=f"{city} to {dest} ({code}-{DEST_AIRPORT[dest]})",
                capacity_per_day=cap,
                base_supplier_cost=float(cost),
                base_sell_price=round(cost * (1 + markup), 2),
                tier=tier, markup=markup,
                conv_rate=rng.uniform(0.03, 0.12),
                elasticity=rng.uniform(*TIER_ELASTICITY[tier]),
                base_util=rng.uniform(0.48, 0.78),
                cancel_base=0.03,
            ))
            f += 1

    items = pd.DataFrame(rows)
    assert len(items) == 120 and (items.item_type == "hotel").sum() == 80
    assert items["capacity_per_day"].between(10, 150).all()
    return items


# --------------------------------------------------------------------------
# 4. Panel builders
# --------------------------------------------------------------------------
def make_panel(cal_slice: pd.DataFrame, items_all: pd.DataFrame) -> pd.DataFrame:
    """Cross-join calendar days x items, then attach calendar + item attributes."""
    n_d, n_i = len(cal_slice), len(items_all)
    panel = pd.DataFrame({
        "date": np.tile(cal_slice["date"].values, n_i),
        "item_id": np.repeat(items_all["item_id"].values, n_d),
    })
    panel = panel.merge(cal_slice, on="date", how="left")
    panel = panel.merge(items_all, on="item_id", how="left")
    return panel


def add_prices(p: pd.DataFrame, lead_days: np.ndarray):
    """
    Price rules (used for both history and future):
      supplier_cost = base_cost * inflation * season/holiday/weekend index
                      * (1 + LEAD_DRIFT_MAX * exp(-lead/TAU))   <- drifts UP as the travel
                        date approaches (small lead_days => higher cost)
                      * small lognormal noise
      sell_price    = supplier_cost * (1 + markup), markup clipped to [15%, 40%]
    Also returns the 'reference' price customers expect (no lead drift / noise), used for the
    price-elasticity effect on demand.
    """
    n = len(p)
    years = ((p["date"] - HIST_START).dt.days / 365.25).values
    season = p["season"].values

    cost_idx = (p["season"].map(SEASON_COST_IDX).values
                * (1 + 0.12 * p["is_holiday"].values)    # holidays cost more
                * (1 + 0.05 * p["is_weekend"].values))   # weekends cost more
    inflation = (1 + ANNUAL_COST_INFLATION) ** years
    lead_drift = LEAD_DRIFT_MAX * np.exp(-lead_days / LEAD_DRIFT_TAU)

    supplier_cost = (p["base_supplier_cost"].values * inflation * cost_idx
                     * (1 + lead_drift) * rng.lognormal(0.0, 0.02, n))

    # Dynamic markup: item's base markup, +3pts in peak, -2pts in off-season, plus noise.
    markup = (p["markup"].values
              + np.where(season == "peak", 0.03, 0.0)
              - np.where(season == "off", 0.02, 0.0)
              + rng.normal(0.0, 0.015, n))
    markup = np.clip(markup, 0.15, 0.40)                 # enforce the 15%-40% rule
    sell_price = supplier_cost * (1 + markup)

    ref_price = p["base_sell_price"].values * inflation * cost_idx
    return supplier_cost, sell_price, ref_price, years


def calibrate_scale(mean_unscaled: np.ndarray, cap: np.ndarray, target: float) -> float:
    """
    Find a global demand multiplier so that ~`target` of rows end up sold out.
    Bisection on a *separate* RNG (common random numbers each iteration), so the main
    RNG stream - and thus reproducibility of everything else - is unaffected.
    """
    lo, hi = 0.2, 4.0
    for _ in range(14):
        mid = (lo + hi) / 2
        r = np.random.default_rng(SEED + 1)
        lam = mean_unscaled * mid * r.gamma(NB_K, 1.0 / NB_K, len(cap))
        rate = (r.poisson(lam) > cap).mean()
        lo, hi = (mid, hi) if rate < target else (lo, mid)
    return (lo + hi) / 2


# --------------------------------------------------------------------------
# 5. daily_history.csv
# --------------------------------------------------------------------------
def build_history(cal: pd.DataFrame, items_all: pd.DataFrame):
    hist_cal = cal[(cal["date"] >= HIST_START) & (cal["date"] <= HIST_END)]
    p = make_panel(hist_cal, items_all)
    n = len(p)
    is_hotel = (p["item_type"] == "hotel").values
    season = p["season"].values

    # --- lead_days: typical booking lead time for that travel date ---
    # Gamma-distributed; mean 25d (hotels) / 18d (flights); longer in peak (people book
    # early), shorter in off-season (last minute).
    mean_lead = (np.where(is_hotel, 25.0, 18.0)
                 * np.where(season == "peak", 1.4, np.where(season == "off", 0.85, 1.0)))
    lead_days = np.clip(np.rint(rng.gamma(3.0, mean_lead / 3.0)), 1, 120).astype(int)

    supplier_cost, sell_price, ref_price, years = add_prices(p, lead_days)

    # --- true_demand = base x dest-seasonality x dow(weekend) x holiday x season x school
    #                   x trend x price effect x shocks x negative-binomial noise ---
    cap = p["capacity_per_day"].values
    base = cap * p["base_util"].values                         # item's baseline daily demand
    dest_idx = p["destination"].map(DEST_IDX).values
    month = p["date"].dt.month.values
    dow = p["date"].dt.dayofweek.values

    seasonal = DEST_MONTH_PROFILE[dest_idx, month - 1]          # destination x month curve
    weekend = np.where(is_hotel, DOW_MULT["hotel"][dow], DOW_MULT["flight"][dow])
    holiday = p["event_name"].map(EVENT_BOOST).fillna(1.0).values   # Diwali, Xmas/NY, long weekends...
    season_m = p["season"].map(SEASON_MULT).values                  # peak / shoulder / off
    school_m = np.where(p["school_vacation_flag"].values == 1, SCHOOL_VACATION_MULT, 1.0)
    trend = (1 + DEST_ANNUAL_GROWTH[dest_idx]) ** years             # 5-10% yearly growth
    # Price elasticity: demand falls when price is above what customers expect.
    price_effect = np.clip((sell_price / ref_price) ** (-p["elasticity"].values), 0.5, 1.3)

    # Demand shocks (outliers not explained by any feature).
    shock = np.ones(n)
    for label, dest, start, end, kind, mag in SHOCKS:
        m = ((p["destination"].values == dest)
             & (p["date"] >= pd.Timestamp(start)).values
             & (p["date"] <= pd.Timestamp(end)).values)
        if kind == "decay":
            days_in = (p.loc[m, "date"] - pd.Timestamp(start)).dt.days.values
            shock[m] = 1.0 + mag * np.exp(-days_in / 10.0)
        else:
            shock[m] = mag

    mean_unscaled = base * seasonal * weekend * holiday * season_m * school_m * trend * price_effect * shock
    # Auto-calibrate the global demand level so ~TARGET_SOLD_OUT of rows are sold out.
    scale = calibrate_scale(mean_unscaled, cap, TARGET_SOLD_OUT)
    mean_demand = mean_unscaled * scale

    # Negative-binomial noise = Poisson(lambda * Gamma(k, 1/k)); over-dispersed counts.
    lam = mean_demand * rng.gamma(NB_K, 1.0 / NB_K, n)
    true_demand = rng.poisson(lam)

    # --- CENSORING: we only observe sales up to capacity ---
    bookings = np.minimum(true_demand, cap)
    sold_out = (true_demand > cap).astype(int)

    # --- searches ~ true_demand / conversion_rate (look-to-book 3%-12%) ---
    # Searches measure uncensored interest, so they are NOT capped by capacity.
    searches = rng.poisson(true_demand / p["conv_rate"].values * rng.lognormal(0.0, 0.10, n))
    searches = np.maximum(searches, bookings)

    # --- cancellations ~ Binomial(bookings, p); p rises with lead_days ---
    cancel_prob = np.clip(p["cancel_base"].values
                          + CANCEL_LEAD_COEF * (1 - np.exp(-lead_days / CANCEL_LEAD_TAU)),
                          0.0, 0.45)
    cancellations = rng.binomial(bookings, cancel_prob)

    out = pd.DataFrame({
        "date": p["date"].dt.strftime("%Y-%m-%d"),
        "item_id": p["item_id"].values,
        "searches": searches.astype(int),
        "true_demand": true_demand.astype(int),    # GROUND TRUTH ONLY - never a feature
        "bookings": bookings.astype(int),
        "sold_out_flag": sold_out,
        "cancellations": cancellations.astype(int),
        "sell_price": np.round(sell_price, 2),
        "supplier_cost": np.round(supplier_cost, 2),
        "lead_days": lead_days,
    })
    return out.sort_values(["date", "item_id"]).reset_index(drop=True), scale


# --------------------------------------------------------------------------
# 6. future_window.csv
# --------------------------------------------------------------------------
def build_future(cal: pd.DataFrame, items_all: pd.DataFrame) -> pd.DataFrame:
    fut_cal = cal[(cal["date"] >= FUT_START) & (cal["date"] <= FUT_END)]
    p = make_panel(fut_cal, items_all)

    # In the future window lead_days is the KNOWN horizon: days from today to the travel date
    # (1..90). Prices are today's quotes for that date, so supplier_cost is naturally cheaper
    # for far-out dates (the pre-buy lever).
    lead_days = ((p["date"] - FUT_START).dt.days.values + 1).astype(int)
    supplier_cost, sell_price, _, _ = add_prices(p, lead_days)

    out = pd.DataFrame({
        "date": p["date"].dt.strftime("%Y-%m-%d"),
        "item_id": p["item_id"].values,
        # Unobserved outcomes - left EMPTY. (true_demand is deliberately absent: it lives
        # only in daily_history.csv.)
        "searches": np.nan,
        "bookings": np.nan,
        "sold_out_flag": np.nan,
        "cancellations": np.nan,
        # Known / plannable features:
        "sell_price": np.round(sell_price, 2),
        "supplier_cost": np.round(supplier_cost, 2),
        "lead_days": lead_days,
    })
    return out.sort_values(["date", "item_id"]).reset_index(drop=True)


# --------------------------------------------------------------------------
# 7. Sanity baseline model
# --------------------------------------------------------------------------
def wape(y, yhat):
    """Weighted absolute percentage error = sum|y - yhat| / sum(y)."""
    return np.abs(y - yhat).sum() / y.sum()


def sanity_baseline(history, calendar, inventory):
    """
    Simple linear baseline on normalised demand, trained on the first 2.5 years and tested on
    the last 6 months. Features: destination x month, day of week, holiday, school flag, long
    weekend, season, linear trend, log price vs. item norm. NO true_demand feature.

    Target "searches-based demand" = searches x item conversion rate, where conversion is
    estimated from NON-sold-out training days only (bookings / searches). Because searches are
    not capped by capacity, this proxy recovers demand on sold-out days too.
    true_demand is used here ONLY to score the forecasts.
    """
    h = history.copy()
    h["date"] = pd.to_datetime(h["date"])
    h = h.merge(inventory[["item_id", "destination"]], on="item_id")
    h = h.merge(calendar, on="date", how="left")
    h["dest_idx"] = h["destination"].map(DEST_IDX)
    h["month"] = h["date"].dt.month
    h["dow"] = h["date"].dt.dayofweek
    h["years"] = (h["date"] - HIST_START).dt.days / 365.25

    cutoff = HIST_END - pd.Timedelta(days=182)           # last 183 days (~6 months) = test
    train, test = h[h["date"] < cutoff].copy(), h[h["date"] >= cutoff].copy()

    # Item conversion estimated on uncensored (not sold-out) training days.
    ok = train[train["sold_out_flag"] == 0].groupby("item_id")[["bookings", "searches"]].sum()
    conv = (ok["bookings"] / ok["searches"]).rename("conv_hat")
    for d in (train, test):
        d["demand_proxy"] = d["searches"] * d["item_id"].map(conv)

    price_med = train.groupby("item_id")["sell_price"].median()
    mean_proxy = train.groupby("item_id")["demand_proxy"].mean().clip(lower=0.5)
    mean_book = train.groupby("item_id")["bookings"].mean().clip(lower=0.5)

    def design(df):
        n = len(df)
        x_dm = np.zeros((n, 144)); x_dm[np.arange(n), df["dest_idx"].values * 12 + df["month"].values - 1] = 1
        x_dow = np.zeros((n, 6))
        d = df["dow"].values; m = d > 0
        x_dow[np.arange(n)[m], d[m] - 1] = 1
        extra = np.column_stack([
            df["is_holiday"], df["school_vacation_flag"], df["event_name"] == "Long Weekend",
            df["season"] == "peak", df["season"] == "off", df["years"],
            np.log(df["sell_price"] / df["item_id"].map(price_med)),
        ]).astype(float)
        return np.hstack([x_dm, x_dow, extra])

    Xtr, Xte = design(train), design(test)
    Ytr = np.column_stack([train["demand_proxy"] / train["item_id"].map(mean_proxy),
                           train["bookings"] / train["item_id"].map(mean_book)])
    beta, *_ = np.linalg.lstsq(Xtr, Ytr, rcond=None)
    pred = np.clip(Xte @ beta, 0, None)
    pred_proxy = pred[:, 0] * test["item_id"].map(mean_proxy).values       # trained on searches-based demand
    pred_book = pred[:, 1] * test["item_id"].map(mean_book).values         # trained on raw (censored) bookings
    naive = test["item_id"].map(mean_proxy).values                         # item average only

    y_proxy, y_true = test["demand_proxy"].values, test["true_demand"].values
    print("\nSanity baseline (train: first ~2.5 years, test: last 6 months)")
    print(f"  train rows {len(train):,} | test rows {len(test):,} | "
          f"test sold-out share {test['sold_out_flag'].mean() * 100:.1f}%")
    print(f"  {'model':<40}{'target':<18}{'WAPE':>7}{'MAE':>8}{'bias':>8}")
    rows = [
        ("Naive item-average", "searches-demand", naive, y_proxy),
        ("Linear baseline (searches-demand)", "searches-demand", pred_proxy, y_proxy),
        ("Linear baseline (searches-demand)", "true_demand", pred_proxy, y_true),
        ("Linear baseline (raw bookings)", "true_demand", pred_book, y_true),
    ]
    for name, tgt, yh, y in rows:
        print(f"  {name:<40}{tgt:<18}{wape(y, yh) * 100:>6.1f}%{np.abs(y - yh).mean():>8.2f}"
              f"{(yh.sum() - y.sum()) / y.sum() * 100:>+7.1f}%")
    print("  (bias < 0 => under-forecast; the raw-bookings model is hurt by censoring.)")


# --------------------------------------------------------------------------
# 8. Main
# --------------------------------------------------------------------------
def main():
    calendar = build_calendar()
    items_all = build_items()
    history, scale = build_history(calendar, items_all)
    future = build_future(calendar, items_all)

    public_item_cols = ["item_id", "item_type", "destination", "name",
                        "capacity_per_day", "base_supplier_cost", "base_sell_price"]
    inventory = items_all[public_item_cols]

    cal_out = calendar.copy()
    cal_out["date"] = cal_out["date"].dt.strftime("%Y-%m-%d")

    # ---- sanity checks on the rules ----
    cap_row = history["item_id"].map(items_all.set_index("item_id")["capacity_per_day"])
    assert len(history) == 120 * 1095 and len(future) == 120 * 90
    assert (history["bookings"] == np.minimum(history["true_demand"], cap_row)).all()   # censoring holds
    assert (history["sold_out_flag"] == (history["true_demand"] > cap_row).astype(int)).all()
    assert (history["cancellations"] <= history["bookings"]).all()
    assert "true_demand" not in future.columns                                          # no leakage
    markup_check = history["sell_price"] / history["supplier_cost"] - 1
    assert markup_check.between(0.14, 0.41).all()                                       # 15%-40% (rounding slack)
    sold_out_pct = history["sold_out_flag"].mean() * 100
    assert 15.0 <= sold_out_pct <= 25.0, f"sold-out {sold_out_pct:.1f}% outside 15-25% target"

    inventory.to_csv(os.path.join(OUT_DIR, "inventory_items.csv"), index=False)
    cal_out.to_csv(os.path.join(OUT_DIR, "calendar_events.csv"), index=False)
    history.to_csv(os.path.join(OUT_DIR, "daily_history.csv"), index=False)
    future.to_csv(os.path.join(OUT_DIR, "future_window.csv"), index=False)

    # ---- summary ----
    print(f"Output directory: {os.path.abspath(OUT_DIR)}")
    print(f"Calibrated demand scale: {scale:.3f} (target sold-out {TARGET_SOLD_OUT * 100:.0f}%)\n")
    print(f"{'file':<22}{'rows':>10}")
    print("-" * 32)
    for name, df in [("inventory_items", inventory), ("calendar_events", cal_out),
                     ("daily_history", history), ("future_window", future)]:
        print(f"{name:<22}{len(df):>10,}")

    h = history.merge(inventory[["item_id", "destination"]], on="item_id")
    h["month"] = pd.to_datetime(h["date"]).dt.month

    print(f"\nSold-out % overall: {sold_out_pct:.2f}%")
    print("Sold-out % per destination:")
    print(h.groupby("destination")["sold_out_flag"].mean().mul(100).round(1)
          .reindex(DESTINATIONS).to_string())

    print("\nAverage bookings per item-day by month (all years pooled):")
    by_month = h.groupby("month")["bookings"].mean()
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for m, v in by_month.items():
        print(f"  {names[m - 1]}  {v:6.2f}  {'#' * int(round(v / by_month.max() * 40))}")

    zero_items = int((history.groupby("item_id")["bookings"].sum() == 0).sum())
    print(f"\nItems with zero total bookings: {zero_items} / {len(inventory)}")
    print(f"Item-days with zero bookings: {(history['bookings'] == 0).mean() * 100:.2f}%")

    print("\nDemand shocks injected (history only, not visible in any feature):")
    for label, dest, start, end, kind, mag in SHOCKS:
        print(f"  {start} -> {end}  {dest:<9} {label}")

    sanity_baseline(history, calendar, inventory)
    print(f"\nRuntime: {time.time() - T_START:.1f}s")


if __name__ == "__main__":
    main()
