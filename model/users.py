from datetime import datetime
from typing import Optional
from fastapi import HTTPException, FastAPI
from pydantic import BaseModel, Field


class User(BaseModel):
    id: Optional[int] = None
    email: str = Field(..., max_length=255)
    firstname: str = Field(..., max_length=255)
    lastname: str = Field(..., max_length=255)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
