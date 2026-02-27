# models/requests.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    model = Column(String(100), nullable=True)

    resume_file_id = Column(String(100), nullable=True)
    vacancy_file_id = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="requests")
