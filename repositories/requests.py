# repositories/requests.py
from .base import BaseRepository
from models.requests import RequestLog


class RequestsRepository(BaseRepository):
    def create(
        self,
        user_id: int,
        prompt: str,
        model: str | None = None,
        resume_file_id: str | None = None,
        vacancy_file_id: str | None = None,
        response: str | None = None,
    ) -> RequestLog:
        obj = RequestLog(
            user_id=user_id,
            prompt=prompt,
            model=model,
            resume_file_id=resume_file_id,
            vacancy_file_id=vacancy_file_id,
            response=response,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
