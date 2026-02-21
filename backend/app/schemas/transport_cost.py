from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TransportCostBase(BaseModel):
    route: str
    cost_per_ton_rial: float
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    facility_id: Optional[int] = None


class TransportCostCreate(TransportCostBase):
    pass


class TransportCostUpdate(BaseModel):
    route: Optional[str] = None
    cost_per_ton_rial: Optional[float] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    facility_id: Optional[int] = None


class TransportCostRead(TransportCostBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
