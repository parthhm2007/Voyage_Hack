# TBO Inventory Optimizer

A data-driven decision-support platform for travel inventory planning. **TBO Inventory Optimizer** helps analysts estimate future demand for hotel and flight inventory, evaluate purchase quantities, and plan how to distribute a fixed pre-buy budget across inventory items.

The application combines a Python/FastAPI analytics backend with a React dashboard. It uses quantile demand forecasts (P10, P50 and P90) to make uncertainty visible rather than relying on a single point estimate.

> **Data note:** The repository includes synthetic datasets for development and demonstration. Results produced from these datasets should not be interpreted as live TBO.com forecasts or operational purchasing advice.

## Key capabilities

- **Inventory explorer** — browse inventory items and filter by destination or item type.
- **Historical demand view** — inspect bookings and searches over time, including sold-out indicators.
- **90-day demand forecast** — view P10, P50 and P90 demand estimates for a selected item.
- **Newsvendor calculator** — evaluate an item's purchase quantity using unit cost, selling price, salvage value and forecast demand.
- **Portfolio budget optimization** — allocate a total budget across eligible inventory using expected marginal profit and a configurable risk appetite.
- **Risk-aware scenarios** — adjust the weighting of conservative, median and optimistic demand scenarios.

The dashboard also presents summary metrics and historical records to help users understand the data behind the recommendations.

## Tech stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, Vite, Recharts, Axios, Lucide React |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| Data processing | pandas, NumPy |
| Machine learning | XGBoost, scikit-learn, joblib |
| Testing | pytest, httpx, Vitest, React Testing Library |
| Data storage | CSV files and in-memory data processing |

## Repository structure

```text
Voyage_Hack-main/
├── backend/
│   ├── main.py                 # FastAPI application and router registration
│   ├── config.py               # Optimizer settings and risk weights
│   ├── loader.py               # Loads and prepares CSV datasets
│   ├── model_loader.py         # Loads trained quantile models for inference
│   ├── train_models.py        # Offline XGBoost training pipeline
│   ├── models/                 # Saved P10, P50 and P90 model artifacts
│   ├── routers/
│   │   ├── data.py             # Inventory, calendar, history and summary APIs
│   │   ├── forecast.py         # Demand forecast API
│   │   ├── newsvendor.py       # Item-level newsvendor calculations
│   │   └── optimize.py         # Portfolio budget optimization API
│   └── tests/                  # Backend API and model tests
├── data/
│   └── synthetic/              # Demonstration CSV datasets
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── components/          # Dashboard, charts and optimization UI
│       ├── services/api.js      # Frontend API client
│       └── __tests__/           # Frontend component tests
├── requirements.txt
└── README.md
```

## Getting started

### Prerequisites

Install the following before running the project:

- Python **3.11** (recommended)
- Node.js and npm
- Git (optional, for cloning the repository)

### 1. Clone the repository

```bash
git clone https://github.com/parthhm2007/Voyage_Hack.git
cd Voyage_Hack
```

If you have downloaded the source as a ZIP, extract it and open the extracted project folder in your terminal or VS Code.

### 2. Set up the backend

Create and activate a virtual environment from the project root.

**Windows PowerShell**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Start the API from the project root:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The backend loads the CSV files during application startup. Keep the `data/synthetic/` directory in its expected location relative to the project root.

- API base URL: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

### 3. Set up the frontend

Open a **second terminal**, move into the frontend directory, install dependencies and start Vite:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (the project config uses port `3000` by default):

```text
http://localhost:3000
```

The Vite development server proxies `/api` requests to the backend at `http://localhost:8000`, so keep both servers running while using the dashboard.

## API overview

All application endpoints are registered under `/api`.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend health and loaded-record counts |
| GET | `/api/summary` | Dashboard summary metrics |
| GET | `/api/items` | Inventory items; supports destination and item-type filters |
| GET | `/api/calendar` | Calendar events; supports season and date filters |
| GET | `/api/history` | Historical records; supports item, destination, date and limit filters |
| GET | `/api/forecast?item_id={id}` | Forecast demand for an inventory item |
| GET | `/api/newsvendor?item_id={id}` | Item-level purchase quantity and newsvendor analysis |
| GET | `/api/optimize` | Portfolio-level budget allocation and recommendations |

Use the interactive Swagger documentation at `/docs` for parameter details, request examples and response schemas.

## Demand forecasting approach

The training pipeline in `backend/train_models.py` builds time-based features, including:

- Day of week, month, day of month and weekend indicator
- Selling price, supplier cost, lead time and gross margin
- Seven-day booking and search lags
- Seven-day rolling booking and search averages

It trains three XGBoost quantile-regression models for the **10th, 50th and 90th percentiles**. The chronological validation split helps preserve time order. The trained models and feature-column list are saved under `backend/models/` and loaded by the API for prediction.

To retrain the models manually, run this command from the project root after installing dependencies:

```bash
python -m backend.train_models
```

This writes model artifacts to `backend/models/`. Keep the training data format and feature definitions consistent with the inference pipeline.

## Data handling and important constraints

- The application uses the CSV files in `data/synthetic/`; it does not require a database server.
- The data loader reads the source datasets and prepares in-memory data for the API.
- The `true_demand` field is deliberately excluded from model features and API responses. It must remain isolated to avoid target leakage and to preserve the intended evaluation setup.
- The project is designed as a single-tenant decision-support application. Authentication and user accounts are not part of the current scope.
- The supplied datasets are synthetic. A production deployment would require approved operational data, monitoring, validation and domain review before recommendations could be used for purchasing decisions.

## Running tests

Run backend tests from the project root with the virtual environment activated:

```bash
pytest backend/tests -v
```

Run frontend tests from the `frontend/` directory:

```bash
npm test -- --run
```

Create a production frontend build:

```bash
npm run build
```

## Current scope and future work

The repository contains the data explorer, forecast endpoint and user-interface flow, as well as newsvendor and portfolio optimization modules. The project planning documents also identify further work around expanded evaluation/backtesting, risk reporting, pricing and timing recommendations, and final product polish. Check the current implementation and test results before treating any planned capability as complete.

Potential future extensions include live data ingestion, scheduled model retraining, persistent storage, authentication and role-based access control. These are not prerequisites for running the current local demonstration.

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-change`.
3. Make focused changes and add or update tests.
4. Run the backend and frontend test suites.
5. Open a pull request with a clear description of the change.

## License

No license file was present in the supplied repository snapshot. Unless a license is added by the project owner, the source should be treated as **all rights reserved**; contact the repository owner before reusing or redistributing it.

---

<p align="center">Built as a data-driven travel inventory planning and optimization project.</p>
