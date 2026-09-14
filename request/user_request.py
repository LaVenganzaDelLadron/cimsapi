from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class UserRequest(BaseModel):
    email: EmailStr
    firstname: str = Field(min_length=1, max_length=255)
    lastname: str = Field(min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=255)
    role: Literal["admin", "analyst", "user"] = "user"
    status: Literal["active", "inactive", "pending"] = "active"
