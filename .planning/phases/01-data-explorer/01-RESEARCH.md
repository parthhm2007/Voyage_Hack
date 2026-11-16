# Phase 1: Data Explorer - Research

**Researched:** 2026-11-16
**Domain:** Full-stack scaffolding (FastAPI backend + React/Vite frontend), CSV data ingestion, time-series data visualization with Recharts.
**Confidence:** HIGH

## Summary

Phase 1 establishes the foundational architecture and user interface for the TBO Inventory Optimizer platform. It encompasses setting up a Python FastAPI backend that ingests and serves read-only synthetic datasets (`inventory_items.csv`, `calendar_events.csv`, `daily_history.csv`) stored in `./data/synthetic/`, adhering strictly to the **True Demand Isolation** rule (never exposing `true_demand` via API). On the frontend, it scaffolds a modern React + Vite application using Tailwind CSS, Lucide icons, and Recharts to build the Data Explorer interface featuring multi-dimensional filters (destination, item type, item ID, date range), executive summary metrics cards, and dual-axis bookings vs. searches time-series charts that explicitly highlight sold-out days.

**Primary recommendation:** Implement a clean, modular monolith structure with `/backend` (FastAPI + pandas data loader singleton caching CSVs in memory) and `/frontend` (React + Vite + Recharts). Use robust Pydantic v2 data validation and REST endpoints with query parameter filtering.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DATA-01 | Backend API and data loader serving inventory items (`inventory_items.csv`), calendar events (`calendar_events.csv`), and historical records (`daily_history.csv`) without modifying raw data. | FastAPI lifespan startup loader reading CSVs into memory pandas DataFrames with strict exclusion of `true_demand` field. |
| DATA-02 | Data Explorer UI with item/destination filters and bookings vs searches charts highlighting sold-out days and summary cards. | React frontend with Recharts `ComposedChart` / `LineChart`, custom reference areas / dots for `sold_out_flag === 1`, and interactive filter state management. |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| CSV Data Ingestion & Caching | API / Backend | — | Python pandas efficiently loads and parses tabular CSV data on startup. |
| Data Filtering & Querying | API / Backend | — | Backend pandas filtering ensures consistent query logic and reduces frontend payload size. |
| Summary Metrics Calculation | API / Backend | Frontend | Backend aggregates totals (items, bookings, searches, sold-out counts) for fast initial rendering. |
| Interactive Data Explorer UI | Browser / Client | — | React client handles filter state, user interaction, and responsive layout. |
| Bookings vs. Searches Charting | Browser / Client | — | Recharts renders high-performance SVG time-series charts with custom sold-out highlights in the browser. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python / FastAPI | 3.11+ / 0.110+ | Backend API framework | Extremely fast, automatic OpenAPI docs, robust Pydantic validation. |
| Pandas | 2.2+ | Data loading & manipulation | Industry standard for tabular data loading and fast in-memory filtering. |
| React / Vite | 18+ / 5+ | Frontend UI framework & bundler | Fast HMR, component-driven UI architecture, lightweight ecosystem. |
| Recharts | 2.12+ | Data visualization | React-native charting library built on D3 with excellent time-series and custom reference support. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Uvicorn | 0.28+ | ASGI server | Running FastAPI backend locally and in production. |
| Pydantic | 2.6+ | Data validation & serialization | Defining strict API response and request models. |
| Lucide React | 0.300+ | UI icons | Clean, modern iconography for summary cards and navigation. |
| Tailwind CSS | 3.4+ / 4.0 | Styling | Rapid utility-first UI styling complying with light theme requirement. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pandas in-memory | SQLite / DuckDB | Overkill for ~130k historical rows which fit entirely in RAM (<50MB). Pandas is simpler and directly processes the CSV source files. |
| Recharts | Chart.js / Nivo | Recharts integrates most naturally with React component lifecycle and declarative props. |

**Installation:**
```bash
# Backend
pip install fastapi uvicorn pandas pydantic

# Frontend
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install recharts lucide-react axios
```

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| fastapi | PyPI | 6+ yrs | 10M+/wk | github.com/tiangolo/fastapi | [OK] | Approved |
| uvicorn | PyPI | 7+ yrs | 25M+/wk | github.com/encode/uvicorn | [OK] | Approved |
| pandas | PyPI | 15+ yrs | 40M+/wk | github.com/pandas-dev/pandas | [OK] | Approved |
| pydantic | PyPI | 7+ yrs | 30M+/wk | github.com/pydantic/pydantic | [OK] | Approved |
| react | npm | 11+ yrs | 20M+/wk | github.com/facebook/react | [OK] | Approved |
| vite | npm | 4+ yrs | 15M+/wk | github.com/vitejs/vite | [OK] | Approved |
| recharts | npm | 8+ yrs | 3M+/wk | github.com/recharts/recharts | [OK] | Approved |
| lucide-react | npm | 3+ yrs | 5M+/wk | github.com/lucide-icons/lucide | [OK] | Approved |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
[ ./data/synthetic/*.csv ]
         │
         ▼ (Startup / FastAPI Lifespan)
┌────────────────────────────────────────┐
│             FastAPI Backend            │
│  - In-memory Pandas DataFrames Cache   │
│  - Strict True Demand Isolation        │
│  - REST Endpoints (/api/items, etc.)   │
└────────────────────────────────────────┘
         │
         ▼ (JSON REST API via HTTP)
┌────────────────────────────────────────┐
│             React Frontend             │
│  - Filter State (Destination, Item)    │
│  - Summary Metrics Cards               │
│  - Recharts Bookings vs Searches       │
└────────────────────────────────────────┘
```

### Recommended Project Structure
```
inventory-optimizer/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── loader.py
│   └── routers/
│       ├── __init__.py
│       └── data.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SummaryCards.jsx
│   │   │   ├── FilterBar.jsx
│   │   │   └── BookingsChart.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── data/
    └── synthetic/
        ├── inventory_items.csv
        ├── calendar_events.csv
        ├── daily_history.csv
        └── future_window.csv
```

### Pattern 1: Singleton Data Loader with FastAPI Lifespan
**What:** Load CSV files once during application startup into module-level pandas DataFrames (or a singleton state object) managed by FastAPI's modern lifespan context manager.
**When to use:** For static or read-only synthetic datasets where fast in-memory filtering (`df[df['destination'] == dest]`) avoids repeated disk I/O.
**Example:**
```python
# Source: FastAPI Lifespan documentation & standard data science pattern
from contextlib import asynccontextmanager
import pandas as pd
from fastapi import FastAPI

class DataStore:
    def __init__(self):
        self.items = None
        self.calendar = None
        self.history = None

    def load(self):
        self.items = pd.read_csv("data/synthetic/inventory_items.csv")
        self.calendar = pd.read_csv("data/synthetic/calendar_events.csv")
        self.history = pd.read_csv("data/synthetic/daily_history.csv")
        # Ensure true_demand is stripped from history if present, or never exposed in API output
        if 'true_demand' in self.history.columns:
            # We keep true_demand in memory internally ONLY if needed for later offline ML training (Phase 2),
            # but API responses must explicitly omit it.

store = DataStore()

@asynccontextmanager
async def lifespan(app: FastAPI):
    store.load()
    yield

app = FastAPI(lifespan=lifespan)
```

### Anti-Patterns to Avoid
- **Exposing `true_demand` in API responses:** Violates the Core Rule. `true_demand` must never be sent to the frontend or serialized in any API response.
- **Reloading CSV files on every request:** Causes severe latency and disk thrashing. Load once on startup into memory.
- **Modifying raw CSV files:** The `./data/synthetic/` directory is strictly read-only.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSV Parsing & Filtering | Custom file readers | Pandas | Handles missing values, type inference, and vectorized filtering effortlessly. |
| Charting & Tooltips | Custom SVG / Canvas | Recharts | Built-in responsive containers, legends, tooltips, and reference lines for sold-out days. |
| API Validation | Manual dictionary checks | Pydantic v2 | Automatic type coercion, validation errors, and OpenAPI schema generation. |

## Runtime State Inventory

*Phase 1 is a greenfield scaffolding and Data Explorer phase. No rename or migration state exists.*

## Common Pitfalls

### Pitfall 1: Leaking `true_demand`
**What goes wrong:** `true_demand` column from `daily_history.csv` is accidentally serialized in API responses or frontend state.
**Why it happens:** Passing raw DataFrame `.to_dict(orient='records')` without explicitly dropping `true_demand`.
**How to avoid:** Explicitly drop or omit `true_demand` in Pydantic response models or when converting pandas records: `df.drop(columns=['true_demand'], errors='ignore')`.
**Warning signs:** `true_demand` appearing in browser network inspector JSON responses.

### Pitfall 2: Date Sorting & Formatting Mismatches in Charts
**What goes wrong:** Time-series charts render dates out of order or as strings instead of chronological points.
**Why it happens:** Dates loaded as string objects rather than sorted datetime strings or ISO dates.
**How to avoid:** Sort historical records by `date` ascending before sending to the frontend; ensure Recharts `XAxis` uses dataKey="date".

## Code Examples

### FastAPI Data Endpoint (Excluding `true_demand`)
```python
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from backend.main import store

router = APIRouter(prefix="/api", tags=["data"])

@router.get("/history")
def get_history(
    item_id: Optional[str] = None,
    destination: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    df = store.history.copy()
    
    # Drop true_demand to enforce core isolation rule
    if "true_demand" in df.columns:
        df = df.drop(columns=["true_demand"])
        
    if item_id:
        df = df[df["item_id"] == item_id]
        
    if destination and "item_id" in df.columns:
        # Merge with items to filter by destination
        merged = df.merge(store.items[["item_id", "destination"]], on="item_id", how="inner")
        if destination != "All":
            merged = merged[merged["destination"] == destination]
        df = merged

    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]
        
    df = df.sort_values("date")
    return df.to_dict(orient="records")
```

### Recharts Bookings vs Searches Chart with Sold-Out Highlights
```jsx
// Source: Recharts documentation & custom reference dot/area pattern
import React from 'react';
import { ResponsiveContainer, ComposedChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ReferenceDot } from 'recharts';

export default function BookingsChart({ data }) {
  // Filter sold out days for highlighting
  const soldOutPoints = data.filter(d => d.sold_out_flag === 1);

  return (
    <div className="bg-white p-4 rounded-lg shadow border">
      <h3 className="text-lg font-semibold mb-2">Bookings vs. Searches (Sold-Out Days Highlighted)</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
            <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
            <Tooltip />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="searches" stroke="#8884d8" name="Searches" dot={false} />
            <Line yAxisId="right" type="monotone" dataKey="bookings" stroke="#82ca9d" name="Bookings" dot={false} />
            {soldOutPoints.map((d, index) => (
              <ReferenceDot
                key={index}
                yAxisId="right"
                x={d.date}
                y={d.bookings}
                r={5}
                fill="red"
                stroke="none"
                title={`Sold Out on ${d.date}`}
              />
            ))}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual CSV file reading per request | FastAPI lifespan singleton DataFrame cache | FastAPI 0.100+ | Zero disk overhead after startup; sub-millisecond query responses. |
| Custom D3 chart boilerplates | Recharts declarative React components | Recharts 2.x | Rapid development of responsive, interactive time-series charts with custom overlays. |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Synthetic CSV files in `./data/synthetic/` have consistent schema matching inspection | Summary Stack | Loader might fail if columns differ; mitigated by robust pandas parsing and error handling. |

## Open Questions

1. **Date Range Defaults:** Should the Data Explorer default to loading the full date range (~2023-2024 history) or a recent 90-day window?
   - *Recommendation:* Load full historical dataset on client filter change, but provide quick date range presets (Last 30 days, Last 90 days, All time) for optimal browser rendering performance.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Backend API | ✓ | 3.13.7 | — |
| FastAPI | Backend API | ✓ (to install) | 0.110+ | — |
| Pandas | Data Loader | ✓ (to install) | 2.2+ | — |
| Node.js / npm | Frontend UI | ✓ | v24.19.0 / 10.x | — |
| Recharts | Frontend Charts | ✓ (to install) | 2.12+ | — |

**Missing dependencies with no fallback:** None. All required runtimes and packages are fully available for installation.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (Backend) + Vitest / React Testing Library (Frontend) |
| Config file | `pytest.ini` / `vite.config.js` |
| Quick run command | `pytest` |
| Full suite command | `pytest && npm test` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DATA-01 | FastAPI loads CSVs and serves items/history endpoints without exposing `true_demand` | unit | `pytest backend/tests/test_data.py` | ❌ Wave 0 |
| DATA-02 | Data Explorer UI renders summary cards, filters, and bookings chart | component | `npm test -- --run` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest`
- **Per wave merge:** `pytest && npm test`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `backend/tests/test_data.py` — tests data loader and API endpoints (ensuring `true_demand` is excluded)
- [ ] `frontend/src/__tests__/DataExplorer.test.jsx` — tests component rendering and filtering

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Single-tenant internal tool for TBO.com analysts (Auth out of scope per PROJECT.md). |
| V3 Session Management | No | Single-tenant internal tool. |
| V4 Access Control | No | Internal tool. |
| V5 Input Validation | Yes | Pydantic v2 query parameter validation on FastAPI endpoints. |
| V6 Cryptography | No | No sensitive user data or auth credentials stored. |

### Known Threat Patterns for {stack}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via file parameters | Tampering | Restrict data loading strictly to predefined paths in `./data/synthetic/`. |
| Data leakage (`true_demand`) | Information Disclosure | Explicitly drop `true_demand` from Pandas DataFrames before JSON serialization. |

## Sources

### Primary (HIGH confidence)
- FastAPI Official Documentation - Lifespan events & dependency injection (`fastapi.tiangolo.com`)
- Pandas Official Documentation - CSV reading and DataFrame filtering (`pandas.pydata.org`)
- Recharts Official Documentation - ComposedChart & ReferenceDot (`recharts.org`)

### Secondary (MEDIUM confidence)
- Project guidelines (`CLAUDE.md`, `ROADMAP.md`, `REQUIREMENTS.md`)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified via PyPI/npm registries and slopcheck.
- Architecture: HIGH - Established FastAPI + React patterns.
- Pitfalls: HIGH - Ground truth isolation and data loading patterns well understood.

**Research date:** 2026-11-16
**Valid until:** 30 days
