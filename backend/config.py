"""Central configuration for backend constants and assumptions."""

MAX_BUDGET = 1_000_000_000

DEFAULT_SALVAGE_RATES = {
    "hotel": 0.40,
    "flight": 0.15
}

def get_risk_weights(risk_appetite: float) -> tuple[float, float, float]:
    """
    Return (w_p10, w_p50, w_p90) scenario weights for risk_appetite in [0.0, 1.0].
    Weights are non-negative, sum to exactly 1.0, and monotonic:
    - w_p10 is non-increasing as risk_appetite increases.
    - w_p90 is non-decreasing as risk_appetite increases.
    Endpoints:
    - 0.0: (0.60, 0.40, 0.00) (conservative, P10 heavy)
    - 0.5: (0.25, 0.50, 0.25) (balanced)
    - 1.0: (0.00, 0.30, 0.70) (aggressive, P90 upside)
    """
    ra = max(0.0, min(1.0, float(risk_appetite)))
    if ra <= 0.5:
        t = ra / 0.5
        w_p10 = 0.60 * (1.0 - t) + 0.25 * t
        w_p50 = 0.40 * (1.0 - t) + 0.50 * t
        w_p90 = 0.00 * (1.0 - t) + 0.25 * t
    else:
        t = (ra - 0.5) / 0.5
        w_p10 = 0.25 * (1.0 - t) + 0.00 * t
        w_p50 = 0.50 * (1.0 - t) + 0.30 * t
        w_p90 = 0.25 * (1.0 - t) + 0.70 * t
        
    s = w_p10 + w_p50 + w_p90
    return (w_p10 / s, w_p50 / s, w_p90 / s)
