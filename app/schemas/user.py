from uuid import UUID
from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic import ConfigDict
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    email: EmailStr
    created_at: Optional[datetime]

