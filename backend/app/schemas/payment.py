from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaymentBase(BaseModel):
    date: str  # Jalali YYYY/MM/DD
    amount_rial: float
    payment_type: str  # "owed" | "paid"
    notes: Optional[str] = None
    driver_id: Optional[int] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    date: Optional[str] = None
    amount_rial: Optional[float] = None
    payment_type: Optional[str] = None
    notes: Optional[str] = None
    driver_id: Optional[int] = None


class PaymentRead(PaymentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
