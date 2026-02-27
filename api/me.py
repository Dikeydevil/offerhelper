from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependecies import get_current_user, get_db
from models.users import User
from models.requests import RequestLog

router = APIRouter(tags=["me"])


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at,
    }


@router.get("/me/requests")
def get_my_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(RequestLog)
        .filter(RequestLog.user_id == current_user.id)
        .order_by(RequestLog.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "created_at": r.created_at,
            "prompt": r.prompt,
            "model": r.model,
            "resume_file_id": r.resume_file_id,
            "vacancy_file_id": r.vacancy_file_id,
            "response": r.response,
        }
        for r in rows
    ]
