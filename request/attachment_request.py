from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AttachmentRequest(BaseModel):
    id: Optional[int] = None
    incident_id: int
    filename: str = Field(..., max_length=255)
    filepath: str = Field(..., max_length=255)
    filetype: str = Field(..., max_length=255)
    uploaded_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
