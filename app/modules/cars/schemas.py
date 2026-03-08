from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.modules.drivers.schemas import DriverResponse


class CarBase(BaseModel):
    plate_number: str
    current_driver_id: Optional[int] = None


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    plate_number: Optional[str] = None
    current_driver_id: Optional[int] = None


class CarResponse(CarBase):
    id: int
    created_at: datetime
    updated_at: datetime
    current_driver: Optional[DriverResponse] = None

    model_config = ConfigDict(from_attributes=True)
