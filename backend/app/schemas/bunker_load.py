from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BunkerLoadBase(BaseModel):
    date: str                                    # Jalali YYYY/MM/DD
    time: Optional[str] = None                   # HH:MM
    truck_number_raw: Optional[str] = None       # شماره ماشین
    receipt_number: Optional[str] = None         # شماره قبض
    tonnage_kg: float                            # تناژ
    origin: Optional[str] = None                 # مبدا
    cost_per_ton_rial: Optional[float] = None    # هزینه حمل هر تن
    total_cost_rial: Optional[float] = None      # مبلغ (ریال)
    notes: Optional[str] = None                  # توضیحات
    facility_id: Optional[int] = None
    driver_id: Optional[int] = None


class BunkerLoadCreate(BunkerLoadBase):
    pass


class BunkerLoadUpdate(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    truck_number_raw: Optional[str] = None
    receipt_number: Optional[str] = None
    tonnage_kg: Optional[float] = None
    origin: Optional[str] = None
    cost_per_ton_rial: Optional[float] = None
    total_cost_rial: Optional[float] = None
    notes: Optional[str] = None
    facility_id: Optional[int] = None
    driver_id: Optional[int] = None


class BunkerLoadRead(BunkerLoadBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
