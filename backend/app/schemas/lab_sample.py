from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LabSampleBase(BaseModel):
    sample_code: str
    sheet_name: str
    au_ppm: Optional[float] = None
    au_detected: Optional[bool] = True
    below_detection_limit: Optional[bool] = False
    sample_type: Optional[str] = None
    date: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    sample_number: Optional[int] = None
    is_special: Optional[bool] = False
    facility_id: Optional[int] = None


class LabSampleCreate(LabSampleBase):
    pass


class LabSampleUpdate(BaseModel):
    sample_code: Optional[str] = None
    sheet_name: Optional[str] = None
    au_ppm: Optional[float] = None
    au_detected: Optional[bool] = None
    below_detection_limit: Optional[bool] = None
    sample_type: Optional[str] = None
    date: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    sample_number: Optional[int] = None
    is_special: Optional[bool] = None
    facility_id: Optional[int] = None


class LabSampleRead(LabSampleBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
