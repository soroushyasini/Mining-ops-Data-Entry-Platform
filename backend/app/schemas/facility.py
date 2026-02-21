from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FacilityBase(BaseModel):
    code: str
    name_fa: str
    name_en: Optional[str] = None
    bunker_sheet_name: Optional[str] = None
    truck_destination: Optional[str] = None


class FacilityCreate(FacilityBase):
    pass


class FacilityUpdate(BaseModel):
    code: Optional[str] = None
    name_fa: Optional[str] = None
    name_en: Optional[str] = None
    bunker_sheet_name: Optional[str] = None
    truck_destination: Optional[str] = None


class FacilityRead(FacilityBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
