from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ShipmentBase(BaseModel):
    date: str  # Jalali YYYY/MM/DD
    receipt_number: Optional[str] = None
    tonnage_kg: float
    destination: Optional[str] = None
    cost_per_ton_rial: Optional[float] = None
    total_cost_rial: Optional[float] = None
    notes: Optional[str] = None
    facility_id: Optional[int] = None
    driver_id: Optional[int] = None
    truck_id: Optional[int] = None


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentUpdate(BaseModel):
    date: Optional[str] = None
    receipt_number: Optional[str] = None
    tonnage_kg: Optional[float] = None
    destination: Optional[str] = None
    cost_per_ton_rial: Optional[float] = None
    total_cost_rial: Optional[float] = None
    notes: Optional[str] = None
    facility_id: Optional[int] = None
    driver_id: Optional[int] = None
    truck_id: Optional[int] = None


class ShipmentRead(ShipmentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
