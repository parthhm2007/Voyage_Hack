# Phase 4: Newsvendor Calculator - Discussion Log

**Date:** 2026-11-17

## Discussion Summary
- **Domain:** Newsvendor optimization logic & calculator component (OPT-01).
- **Mathematical Approach:** Critical fractile $CR = \frac{p - c}{p - s}$ evaluated against P10/P50/P90 quantile forecasts.
- **Backend:** New endpoint `/api/newsvendor` computing optimal buy quantity and expected profit.
- **Frontend:** Interactive calculator component with adjustable unit economics and visual demand/profit feedback.
