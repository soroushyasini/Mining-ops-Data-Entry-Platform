from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.modules.attachments.schemas import AttachmentResponse
from app.shared.enums import RecordStatus
from app.shared.jalali import jalali_to_gregorian


# ---------------------------------------------------------------------------
# LabIssueBatch schemas
# ---------------------------------------------------------------------------

class LabBatchCreate(BaseModel):
    issue_date_jalali: str
    notes: Optional[str] = None

    @field_validator("issue_date_jalali")
    @classmethod
    def validate_jalali_date(cls, v: str) -> str:
        jalali_to_gregorian(v)
        return v


class LabBatchUpdate(BaseModel):
    analysis_count: Optional[int] = None
    total_cost_rials: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[RecordStatus] = None


class LabBatchResponse(BaseModel):
    id: int
    issue_date_jalali: str
    issue_date_gregorian: date
    analysis_count: Optional[int] = None
    total_cost_rials: Optional[int] = None
    status: RecordStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    results: List["LabResultResponse"] = []
    results_count: int = 0
    attachments: List[AttachmentResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# LabResult schemas
# ---------------------------------------------------------------------------

class LabResultCreate(BaseModel):
    sample_code: str
    gold_ppm: Decimal


class LabResultBulkCreate(BaseModel):
    batch_id: int
    results: List[LabResultCreate]


class LabResultUpdate(BaseModel):
    sample_code: Optional[str] = None
    gold_ppm: Optional[Decimal] = None


class LabResultResponse(BaseModel):
    id: int
    batch_id: int
    sample_code: str
    source_facility: Optional[str] = None
    sample_date_jalali: Optional[str] = None
    sample_date_gregorian: Optional[date] = None
    sample_type: Optional[str] = None
    sequence_number: Optional[int] = None
    gold_ppm: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Required for forward reference in LabBatchResponse
LabBatchResponse.model_rebuild()
