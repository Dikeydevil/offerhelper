from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import SessionLocal
from models.users import User
from repositories.users import UsersRepository
from repositories.requests import RequestsRepository
from services.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
auth_service = AuthService()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_users_repo(db: Session = Depends(get_db)) -> UsersRepository:
    return UsersRepository(db=db)


def get_requests_repo(db: Session = Depends(get_db)) -> RequestsRepository:
    return RequestsRepository(db=db)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = auth_service.decode_token(token)
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
