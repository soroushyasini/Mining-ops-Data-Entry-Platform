from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TruckBase(BaseModel):
    number: str
    status: Optional[str] = "active"


class TruckCreate(TruckBase):
    pass


class TruckUpdate(BaseModel):
    number: Optional[str] = None
    status: Optional[str] = None


class TruckRead(TruckBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
