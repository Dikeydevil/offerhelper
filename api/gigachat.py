# api/gigachat.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from api.dependecies import get_db, get_current_user
from models.users import User
from repositories.requests import RequestsRepository
from services.gigachat import generate_resume_from_streams_and_texts
from services.gigachat import generate_resume


router = APIRouter(prefix="/gigachat", tags=["gigachat"])


@router.post("/generate-resume")
async def generate_resume_endpoint(
    # опциональные файлы
    resume: UploadFile | None = File(None),
    vacancy: UploadFile | None = File(None),
    # опциональный текст
    resume_text: str | None = Form(None),
    vacancy_text: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Проверяем, что хоть что‑то пришло
    if not any([resume, vacancy, resume_text, vacancy_text]):
        raise HTTPException(
            status_code=400,
            detail="Provide at least one of: resume file/text and vacancy file/text",
        )

    # Подготовим бинарные потоки и MIME’ы для файлов (если есть)
    resume_stream = None
    resume_filename = None
    resume_mime = None

    if resume is not None:
        if resume.content_type not in {"application/pdf", "text/plain"}:
            raise HTTPException(status_code=415, detail="Unsupported resume type")
        resume_stream = await resume.read()
        resume_filename = resume.filename
        resume_mime = resume.content_type

    vacancy_stream = None
    vacancy_filename = None
    vacancy_mime = None

    if vacancy is not None:
        if vacancy.content_type not in {"image/jpeg", "image/png"}:
            raise HTTPException(status_code=415, detail="Unsupported vacancy image type")
        vacancy_stream = await vacancy.read()
        vacancy_filename = vacancy.filename
        vacancy_mime = vacancy.content_type

    # Вызов сервиса GigaChat (новая функция, см. ниже)
    text, resume_file_id, vacancy_file_id = generate_resume_from_streams_and_texts(
        resume_stream=resume_stream,
        resume_filename=resume_filename,
        resume_mime=resume_mime,
        resume_text=resume_text,
        vacancy_stream=vacancy_stream,
        vacancy_filename=vacancy_filename,
        vacancy_mime=vacancy_mime,
        vacancy_text=vacancy_text,
    )

    repo = RequestsRepository(db=db)
    log = repo.create(
        user_id=current_user.id,
        prompt="generate-resume",
        model="GigaChat-2-Max",
        resume_file_id=resume_file_id,
        vacancy_file_id=vacancy_file_id,
        response=text,
    )

    return {
        "request_id": log.id,
        "resume_text": text,
        "resume_file_id": resume_file_id,
        "vacancy_file_id": vacancy_file_id,
    }
