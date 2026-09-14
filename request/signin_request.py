from pydantic import BaseModel, EmailStr, Field

class SigninRequest(BaseModel):
    email: EmailStr
    password: str
