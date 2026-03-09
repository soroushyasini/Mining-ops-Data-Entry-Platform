from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.modules.attachments.schemas import AttachmentResponse
from app.shared.enums import GrindingFacility, RecordStatus
from app.shared.jalali import jalali_to_gregorian


class GrindingCreate(BaseModel):
    date_jalali: str
    facility: GrindingFacility
    input_tonnage_kg: int
    output_tonnage_kg: Optional[int] = None
    waste_tonnage_kg: Optional[int] = None
    grinding_cost_rials: Optional[int] = None
    transport_cost_rials: Optional[int] = None
    total_cost_rials: Optional[int] = None
    receipt_number: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("date_jalali")
    @classmethod
    def validate_jalali_date(cls, v: str) -> str:
        jalali_to_gregorian(v)
        return v


class GrindingUpdate(BaseModel):
    date_jalali: Optional[str] = None
    facility: Optional[GrindingFacility] = None
    input_tonnage_kg: Optional[int] = None
    output_tonnage_kg: Optional[int] = None
    waste_tonnage_kg: Optional[int] = None
    grinding_cost_rials: Optional[int] = None
    transport_cost_rials: Optional[int] = None
    total_cost_rials: Optional[int] = None
    receipt_number: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("date_jalali")
    @classmethod
    def validate_jalali_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            jalali_to_gregorian(v)
        return v


class GrindingResponse(BaseModel):
    id: int
    date_jalali: str
    date_gregorian: date
    facility: GrindingFacility
    input_tonnage_kg: int
    output_tonnage_kg: Optional[int] = None
    waste_tonnage_kg: Optional[int] = None
    grinding_cost_rials: Optional[int] = None
    transport_cost_rials: Optional[int] = None
    total_cost_rials: Optional[int] = None
    receipt_number: Optional[int] = None
    notes: Optional[str] = None
    status: RecordStatus
    created_at: datetime
    updated_at: datetime
    attachments: List[AttachmentResponse] = []

    model_config = ConfigDict(from_attributes=True)
