from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import HTTPException, FastAPI

class Category(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

