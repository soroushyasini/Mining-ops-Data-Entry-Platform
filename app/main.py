from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import AsyncSessionLocal
from app.modules.drivers.router import router as drivers_router
from app.modules.cars.router import router as cars_router
from app.modules.trucks.router import router as trucks_router
from app.modules.attachments.router import router as attachments_router

app = FastAPI(
    title="Mining Supply Chain API",
    description="Gold Mining Supply Chain CRUD API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drivers_router, prefix="/api/v1/drivers", tags=["drivers"])
app.include_router(cars_router, prefix="/api/v1/cars", tags=["cars"])
app.include_router(trucks_router, prefix="/api/v1/trucks", tags=["trucks"])
app.include_router(attachments_router, prefix="/api/v1/attachments", tags=["attachments"])


@app.get("/health", tags=["health"])
async def health_check():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "healthy", "database": db_status}
