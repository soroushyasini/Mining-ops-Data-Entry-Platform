from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.shared.enums import EntityType


class AttachmentResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    file_name: str
    file_path: str
    file_type: str
    file_size_bytes: Optional[int] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
