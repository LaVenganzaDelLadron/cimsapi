from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import HTTPException, FastAPI

class Attachments(BaseModel):
    id: Optional[int] = None
    incident_id: int
    filename: str = Field(..., max_length=255)
    filepath: str = Field(..., max_length=500)
    filetype: str = Field(..., max_length=50)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None