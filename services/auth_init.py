# services/auth_init.py
from sqlalchemy.orm import Session

from config import settings
from database import SessionLocal
from models.users import User
from services.auth import AuthService

auth_service = AuthService()


def ensure_default_admin():
    db: Session = SessionLocal()
    try:
        # есть ли вообще пользователи
        count = db.query(User).count()
        if count > 0:
            return

        # создаём первого пользователя-админа
        admin = User(
            email=settings.DEFAULT_ADMIN_EMAIL,
            hashed_password=auth_service.hash_password(settings.DEFAULT_ADMIN_PASSWORD),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(
            f"[init] created default admin: {admin.email} / {settings.DEFAULT_ADMIN_PASSWORD}"
        )
    finally:
        db.close()