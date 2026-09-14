from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import HTTPException, FastAPI

class Incidents(BaseModel):
    id: Optional[int] = None
    user_id: int
    category_id: int
    title: str = Field(..., max_length=255)
    description: str
    severity: str = Field(..., max_length=10)
    status: str = Field(..., max_length=15)
    location: Optional[str] = Field(None, max_length=255)
    incident_date: Optional[datetime] = None
    assigned_to: int
    resolve_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
