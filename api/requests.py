# api/requests.py
from fastapi import APIRouter, Depends

from repositories.requests import RequestsRepository
from schemas.requests import RequestLogCreate, RequestLog
from .dependecies import get_requests_repo

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=RequestLog)
def create_request_log(
    req_in: RequestLogCreate,
    repo: RequestsRepository = Depends(get_requests_repo),
):
    # пока без валидации user_id, можно добавить в сервис-слое
    return repo.create(
        user_id=req_in.user_id,
        prompt=req_in.prompt,
        model=req_in.model,
        resume_file_id=req_in.resume_file_id,
        vacancy_file_id=req_in.vacancy_file_id,
    )
