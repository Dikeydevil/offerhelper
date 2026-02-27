from datetime import datetime
from pydantic import BaseModel, EmailStr
from models.users import User


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str  # пароль при регистрации


class User(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
