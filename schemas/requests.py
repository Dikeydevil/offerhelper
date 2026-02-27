# schemas/requests.py
from datetime import datetime
from pydantic import BaseModel


class RequestLogBase(BaseModel):
    prompt: str
    model: str | None = None
    resume_file_id: str | None = None
    vacancy_file_id: str | None = None


class RequestLogCreate(RequestLogBase):
    user_id: int


class RequestLog(RequestLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
