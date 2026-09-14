from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import HTTPException, FastAPI

class Chats(BaseModel):
    id: Optional[int] = None
    user_id: int
    userinput: str = Field(..., max_length=1000)
    message: str = Field(..., max_length=1000)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None