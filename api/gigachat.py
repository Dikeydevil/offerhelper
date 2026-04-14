from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import io
import uuid
import os

from api.dependecies import get_db, get_current_user
from models.users import User
from repositories.requests import RequestsRepository
from services.gigachat import generate_resume_from_streams_and_texts
from services.export import build_docx_from_text, build_pdf_from_text

router = APIRouter(prefix="/gigachat", tags=["gigachat"])

EXPORT_DIR = "output_files"
os.makedirs(EXPORT_DIR, exist_ok=True)


@router.post("/generate-resume")
async def generate_resume_endpoint(
    # файлы
    resume: UploadFile | None = File(None),
    vacancy: UploadFile | None = File(None),
    # текст
    resume_text: str | None = Form(None),
    vacancy_text: str | None = Form(None),
    # формат ответа
    output_format: str = Form("text"),  # "text" | "docx" | "pdf"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not any([resume, vacancy, resume_text, vacancy_text]):
        raise HTTPException(
            status_code=400,
            detail="Provide at least one of: resume/vacancy file or text",
        )

    resume_stream = resume_filename = resume_mime = None
    vacancy_stream = vacancy_filename = vacancy_mime = None

    if resume is not None:
        if resume.content_type not in {"application/pdf", "text/plain"}:
            raise HTTPException(status_code=415, detail="Unsupported resume type")
        resume_stream = await resume.read()
        resume_filename = resume.filename
        resume_mime = resume.content_type

    if vacancy is not None:
        if vacancy.content_type not in {"image/jpeg", "image/png"}:
            raise HTTPException(status_code=415, detail="Unsupported vacancy image type")
        vacancy_stream = await vacancy.read()
        vacancy_filename = vacancy.filename
        vacancy_mime = vacancy.content_type

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

    # Вариант 1: отдать просто текст (как сейчас)
    if output_format == "text":
        return {
            "request_id": log.id,
            "resume_text": text,
            "resume_file_id": resume_file_id,
            "vacancy_file_id": vacancy_file_id,
        }

    # Вариант 2: docx
    if output_format == "docx":
        filename = f"resume_{log.id}.docx"
        filepath = os.path.join(EXPORT_DIR, filename)
        build_docx_from_text(text, filepath)
        return FileResponse(
            filepath,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename,
        )

    # Вариант 3: pdf
    if output_format == "pdf":
        filename = f"resume_{log.id}.pdf"
        filepath = os.path.join(EXPORT_DIR, filename)
        build_pdf_from_text(text, filepath)
        return FileResponse(
            filepath,
            media_type="application/pdf",
            filename=filename,
        )

    raise HTTPException(status_code=400, detail="Unsupported output_format")