from datetime import datetime
from pydantic import BaseModel, EmailStr


class AdminUser(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
