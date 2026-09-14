from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class InvestigationRequest(BaseModel):
    id: Optional[int] = None
    incident_id: int
    analyst_id: Optional[int] = None
    note: str = Field(..., max_length=1000)
    recommendation: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None