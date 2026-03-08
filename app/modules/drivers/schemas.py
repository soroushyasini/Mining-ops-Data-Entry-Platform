from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DriverBase(BaseModel):
    full_name: str
    iban: Optional[str] = None
    phone: Optional[str] = None


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    full_name: Optional[str] = None
    iban: Optional[str] = None
    phone: Optional[str] = None


class DriverResponse(DriverBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
