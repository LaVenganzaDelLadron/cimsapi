from pydantic import BaseModel, Field, EmailStr

class SignupRequest(BaseModel):
    email: EmailStr
    firstname: str = Field(min_length=1, max_length=255)
    lastname: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=255)
