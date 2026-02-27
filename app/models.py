# app/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    requests = relationship("RequestLog", back_populates="user")


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    prompt = Column(Text, nullable=False)          # то, что шлёшь в GigaChat
    response = Column(Text, nullable=True)         # ответ модели (опционально)
    model = Column(String(100), nullable=True)     # GigaChat-2-Max и т.п.
    resume_file_id = Column(String(100), nullable=True)
    vacancy_file_id = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="requests")
