from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.loader import store
from backend.routers import data

@asynccontextmanager
async def lifespan(app: FastAPI):
    store.load()
    yield

app = FastAPI(
    title="TBO Inventory Optimizer API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "items_loaded": len(store.items) if store.items is not None else 0,
        "history_loaded": len(store.history) if store.history is not None else 0
    }
