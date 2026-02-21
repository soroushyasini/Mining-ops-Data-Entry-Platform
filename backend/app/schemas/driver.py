from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class DriverBase(BaseModel):
    canonical_name: str
    aliases: Optional[List[str]] = []
    status: Optional[str] = "active"
    bank_account: Optional[str] = None
    phone: Optional[str] = None


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    canonical_name: Optional[str] = None
    aliases: Optional[List[str]] = None
    status: Optional[str] = None
    bank_account: Optional[str] = None
    phone: Optional[str] = None


class DriverRead(DriverBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
