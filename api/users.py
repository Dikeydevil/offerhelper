# api/users.py
from fastapi import APIRouter, Depends, HTTPException

from repositories.users import UsersRepository
from schemas.users import UserCreate, User
from .dependecies import get_users_repo

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=User)
def create_user(
    user_in: UserCreate,
    users_repo: UsersRepository = Depends(get_users_repo),
):
    existing = users_repo.get_by_email(user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    return users_repo.create(email=user_in.email)
