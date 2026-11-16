# Phase 1: Data Explorer - Context

**Gathered:** 2026-11-16
**Status:** Ready for planning
**Source:** Roadmap & Requirements

<domain>
## Phase Boundary
Scaffold project backend (FastAPI) and frontend (React + Vite + Tailwind CSS), load synthetic datasets (`inventory_items.csv`, `calendar_events.csv`, `daily_history.csv`) in-memory without modifying source files, and build the Data Explorer UI with item/destination filters, summary cards, and bookings vs searches time-series charts highlighting sold-out days.
</domain>

<decisions>
## Implementation Decisions
### Backend Architecture (FastAPI)
- FastAPI backend running on port 8000 (or standard dev port).
- Startup lifespan event loader that loads CSVs from `./data/synthetic/` into pandas DataFrames in memory.
- Endpoints to query inventory items, calendar events, and historical records with filtering support.
- Strict isolation: `true_demand` must never be exposed by API or model features.

### Frontend Architecture (React + Vite + Tailwind)
- React SPA with Vite and Tailwind CSS.
- Data Explorer view featuring:
  - Item and destination filters.
  - Summary cards (total items, total bookings, average search volume, sold-out days count).
  - Bookings vs searches time-series charts using Recharts, highlighting sold-out days (`sold_out_flag === 1`).
</decisions>

<canonical_refs>
## Canonical References
- `.planning/ROADMAP.md` — Phase 1 definition and success criteria
- `.planning/REQUIREMENTS.md` — DATA-01, DATA-02 specifications
- `./data/synthetic/inventory_items.csv`
- `./data/synthetic/calendar_events.csv`
- `./data/synthetic/daily_history.csv`
</canonical_refs>
