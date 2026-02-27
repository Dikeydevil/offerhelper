from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependecies import get_db, get_current_admin
from models.users import User
from repositories.users import UsersRepository
from schemas.admin import AdminUser

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[AdminUser])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    skip = (page - 1) * page_size
    repo = UsersRepository(db=db)
    users = repo.list_users(skip=skip, limit=page_size)
    return users


@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    repo = UsersRepository(db=db)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_plain = repo.set_random_password(user)
    # Вариант 1: вернуть новый пароль (для dev)
    return {"user_id": user.id, "new_password": new_plain}
    # В реале обычно отправляют пароль по почте и НЕ возвращают в API.
