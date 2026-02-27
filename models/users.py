from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)

    hashed_password = Column(String(255), nullable=False)

    # новая колонка: роль
    role = Column(String(50), nullable=False, default="user")  # "user" | "admin"

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    requests = relationship("RequestLog", back_populates="user")
