from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BunkerLoadBase(BaseModel):
    date: str  # Jalali YYYY/MM/DD
    tonnage_kg: float
    cumulative_tonnage_kg: Optional[float] = None
    transport_cost_rial: Optional[float] = None
    sheet_name: Optional[str] = None
    facility_id: Optional[int] = None
    driver_id: Optional[int] = None


class BunkerLoadCreate(BunkerLoadBase):
    pass


class BunkerLoadUpdate(BaseModel):
    date: Optional[str] = None
    tonnage_kg: Optional[float] = None
    cumulative_tonnage_kg: Optional[float] = None
    transport_cost_rial: Optional[float] = None
    sheet_name: Optional[str] = None
    facility_id: Optional[int] = None
    driver_id: Optional[int] = None


class BunkerLoadRead(BunkerLoadBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
