from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.modules.attachments.schemas import AttachmentResponse
from app.shared.enums import GrindingFacility, RecordStatus
from app.shared.jalali import jalali_to_gregorian


class TruckLoadBase(BaseModel):
    date_jalali: str
    truck_plate_number: str
    receipt_number: int
    tonnage_kg: int
    destination: GrindingFacility
    driver_name: str
    cost_per_ton_rials: Optional[int] = None
    total_cost_rials: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("date_jalali")
    @classmethod
    def validate_jalali_date(cls, v: str) -> str:
        jalali_to_gregorian(v)  # raises ValueError if invalid
        return v


class TruckLoadCreate(TruckLoadBase):
    status: Optional[RecordStatus] = None


class TruckLoadUpdate(BaseModel):
    date_jalali: Optional[str] = None
    truck_plate_number: Optional[str] = None
    receipt_number: Optional[int] = None
    tonnage_kg: Optional[int] = None
    destination: Optional[GrindingFacility] = None
    driver_name: Optional[str] = None
    cost_per_ton_rials: Optional[int] = None
    total_cost_rials: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("date_jalali")
    @classmethod
    def validate_jalali_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            jalali_to_gregorian(v)
        return v


class TruckStatusPatch(BaseModel):
    status: RecordStatus


class TruckLoadResponse(TruckLoadBase):
    id: int
    date_gregorian: date
    status: RecordStatus
    created_at: datetime
    updated_at: datetime
    attachments: List[AttachmentResponse] = []

    model_config = ConfigDict(from_attributes=True)
