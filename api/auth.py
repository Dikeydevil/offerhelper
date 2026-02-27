from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Response

from repositories.users import UsersRepository
from schemas.users import UserCreate, User
from services.auth import AuthService
from api.dependecies import get_users_repo

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()


@router.post("/register", response_model=User)
def register(
    data: UserCreate,
    users_repo: UsersRepository = Depends(get_users_repo),
):
    existing = users_repo.get_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
    user = users_repo.create(email=data.email, password=data.password)
    return user


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = None,
    users_repo: UsersRepository = Depends(get_users_repo),
):
    user = users_repo.authenticate(
        email=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    access_token = auth_service.create_access_token({"user_id": user.id})
    if response is not None:
        response.set_cookie("access_token", access_token)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"status": "success"}
