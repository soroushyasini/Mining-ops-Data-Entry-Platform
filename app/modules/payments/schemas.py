from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.modules.attachments.schemas import AttachmentResponse
from app.shared.enums import EntityType
from app.shared.jalali import jalali_to_gregorian


class PaymentItemCreate(BaseModel):
    entity_type: EntityType
    entity_id: int
    amount_rials: int


class PaymentGroupCreate(BaseModel):
    payment_date_jalali: str
    payment_time: Optional[str] = None
    payer_name: str
    bank_name: str
    bank_account_number: Optional[str] = None
    total_amount_rials: int
    note: Optional[str] = None
    payments: List[PaymentItemCreate]

    @field_validator("payment_date_jalali")
    @classmethod
    def validate_jalali_date(cls, v: str) -> str:
        jalali_to_gregorian(v)
        return v

    @field_validator("payments")
    @classmethod
    def validate_payments_not_empty(cls, v: List[PaymentItemCreate]) -> List[PaymentItemCreate]:
        if not v:
            raise ValueError("payments must contain at least one item")
        return v


class PaymentGroupUpdate(BaseModel):
    payment_date_jalali: Optional[str] = None
    payment_time: Optional[str] = None
    payer_name: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    total_amount_rials: Optional[int] = None
    note: Optional[str] = None

    @field_validator("payment_date_jalali")
    @classmethod
    def validate_jalali_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            jalali_to_gregorian(v)
        return v


class PaymentItemResponse(BaseModel):
    id: int
    group_id: int
    entity_type: str
    entity_id: int
    amount_rials: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentGroupResponse(BaseModel):
    id: int
    payment_date_jalali: str
    payment_date_gregorian: date
    payment_time: Optional[str] = None
    payer_name: str
    bank_name: str
    bank_account_number: Optional[str] = None
    total_amount_rials: int
    note: Optional[str] = None
    created_at: datetime
    payments: List[PaymentItemResponse] = []
    payments_count: int = 0
    attachments: List[AttachmentResponse] = []

    model_config = ConfigDict(from_attributes=True)
