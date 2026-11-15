# TBO Inventory Optimizer — Developer Guide

## Project Overview
- **Platform:** TBO Inventory Optimizer (Travel inventory pre-buy optimization platform)
- **Backend:** Python 3.11 + FastAPI + pandas + uvicorn (`/backend`)
- **Frontend:** React + Vite + Recharts (`/frontend`)
- **Data Source:** `./data/synthetic/` (`inventory_items.csv`, `calendar_events.csv`, `daily_history.csv`, `future_window.csv`)

## Core Rules
1. **Never modify raw data:** `./data/synthetic/` is read-only.
2. **True Demand Isolation:** `true_demand` is ground truth evaluation target only — NEVER use as a model feature and NEVER expose in any API response.
3. **Architecture:** Monolithic separation (`/backend` and `/frontend`). No database, no auth, no dark mode.
4. **Workflow:** Execute phases sequentially using GSD planning and execution workflows (`/gsd:plan-phase N`).

## Quick Commands
- Start backend: `uvicorn backend.main:app --reload`
- Start frontend: `npm run dev` (in `/frontend`)
- Run tests: pytest (backend), npm test (frontend)
