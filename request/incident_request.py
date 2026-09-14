from typing import Optional
from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    category_id: int
    title: str = Field(..., max_length=255)
    description: str
    severity: str = Field(..., max_length=10)
    status: str = Field("new", max_length=15)
    location: Optional[str] = Field(None, max_length=255)
    incident_date: Optional[str] = None
    assigned_to: Optional[int] = None
    resolve_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None