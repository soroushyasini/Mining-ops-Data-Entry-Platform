import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .database import engine, Base
from .routers import (
    drivers_router,
    trucks_router,
    facilities_router,
    shipments_router,
    bunker_loads_router,
    lab_samples_router,
    payments_router,
    transport_costs_router,
    lookup_router,
    seed_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (if not exist)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="سامانه ورود اطلاعات معدن",
    description="Mining Operations Data Entry Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers with /api prefix
app.include_router(drivers_router, prefix="/api")
app.include_router(trucks_router, prefix="/api")
app.include_router(facilities_router, prefix="/api")
app.include_router(shipments_router, prefix="/api")
app.include_router(bunker_loads_router, prefix="/api")
app.include_router(lab_samples_router, prefix="/api")
app.include_router(payments_router, prefix="/api")
app.include_router(transport_costs_router, prefix="/api")
app.include_router(lookup_router, prefix="/api")
app.include_router(seed_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "سامانه ورود اطلاعات معدن", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
