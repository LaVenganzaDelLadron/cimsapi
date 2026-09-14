from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    id: Optional[int] = None
    user_id: int
    userinput: str = Field(..., max_length=1000)
    response: str = Field(..., max_length=1000)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None