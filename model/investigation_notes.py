from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import HTTPException, FastAPI

class InvestigationNotes(BaseModel):
    id: Optional[int] = None
    incident_id: int
    note: str = Field(..., max_length=1000)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None