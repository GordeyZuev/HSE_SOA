from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional
from datetime import date, datetime

class RegisterRequest(BaseModel):
    username: constr(min_length=3, max_length=50) = Field(..., description="Username (3-50 characters)")
    password: constr(min_length=8, max_length=100) = Field(..., description="Password (8-100 characters)")
    email: EmailStr = Field(..., description="Valid email address")

class LoginRequest(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")

class ProfileUpdateRequest(BaseModel):
    first_name: Optional[constr(max_length=50)] = Field(None, description="First name")
    last_name: Optional[constr(max_length=50)] = Field(None, description="Last name")
    birth_date: Optional[date] = Field(None, description="Birth date")
    phone: Optional[constr(max_length=20)] = Field(None, description="Phone number")

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    message: str