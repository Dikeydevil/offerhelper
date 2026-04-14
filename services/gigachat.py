# services/gigachat.py
import io
import uuid
from typing import BinaryIO

import requests

from config import settings


NGW_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
BASE_URL = "https://gigachat.devices.sberbank.ru/api/v1"
CA_BUNDLE = "certs/ca.pem"


def get_access_token() -> str:
    payload = "scope=GIGACHAT_API_PERS"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {settings.GIGACHAT_AUTH_KEY}",
    }
    resp = requests.post(NGW_URL, headers=headers, data=payload, verify=CA_BUNDLE)
    resp.raise_for_status()
    return resp.json()["access_token"]


def upload_file(
    f: BinaryIO,
    filename: str,
    mime: str,
    access_token: str,
) -> str:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    files = {"file": (filename, f, mime)}
    data = {"purpose": "general"}
    resp = requests.post(
        f"{BASE_URL}/files",
        headers=headers,
        files=files,
        data=data,
        verify=CA_BUNDLE,
    )
    print("GIGACHAT FILE UPLOAD:", resp.status_code, resp.text)  # <---
    resp.raise_for_status()
    return resp.json()["id"]


def generate_resume(
    # резюме: файл и/или текст
    resume_stream: bytes | None = None,
    resume_filename: str | None = None,
    resume_mime: str | None = None,
    resume_text: str | None = None,
    # вакансия: файл и/или текст
    vacancy_stream: bytes | None = None,
    vacancy_filename: str | None = None,
    vacancy_mime: str | None = None,
    vacancy_text: str | None = None,
) -> tuple[str, str | None, str | None]:
    """
    Возвращает: (text_response, resume_file_id | None, vacancy_file_id | None).

    Можно передавать любые комбинации:
    - файл+файл
    - файл+текст
    - текст+файл
    - текст+текст
    Главное — чтобы в сумме было хоть что‑то для резюме и/или вакансии.
    """
    access_token = get_access_token()

    resume_file_id: str | None = None
    vacancy_file_id: str | None = None

    # --- РЕЗЮМЕ ---
    if resume_stream is not None:
        resume_file_id = upload_file(
            io.BytesIO(resume_stream),
            resume_filename or "resume.bin",
            resume_mime or "application/octet-stream",
            access_token,
        )
    elif resume_text is not None:
        resume_bytes = resume_text.encode("utf-8")
        resume_file_id = upload_file(
            io.BytesIO(resume_bytes),
            "resume.txt",
            "text/plain",
            access_token,
        )

    # --- ВАКАНСИЯ ---
    if vacancy_stream is not None:
        vacancy_file_id = upload_file(
            io.BytesIO(vacancy_stream),
            vacancy_filename or "vacancy.bin",
            vacancy_mime or "application/octet-stream",
            access_token,
        )
    elif vacancy_text is not None:
        vacancy_bytes = vacancy_text.encode("utf-8")
        vacancy_file_id = upload_file(
            io.BytesIO(vacancy_bytes),
            "vacancy.txt",
            "text/plain",
            access_token,
        )

    attachments: list[str] = []
    if resume_file_id:
        attachments.append(resume_file_id)
    if vacancy_file_id:
        attachments.append(vacancy_file_id)

    if not attachments:
        raise ValueError("No resume or vacancy data provided to send to GigaChat")

    headers_chat = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "GigaChat-2-Max",
        "function_call": "auto",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты мастер написания резюме и карьерный консультант. "
                    "Глубоко анализируешь прикрепленные резюме и вакансии, "
                    "пишешь новое резюме с нуля под вакансию, из старого берешь только контакты кандидата. "
                    "Всегда выдаешь результат двумя блоками: «РЕЗЮМЕ ДЛЯ HH.RU» и «СОПРОВОДИТЕЛЬНОЕ ПИСЬМО», "
                    "пишешь по-русски, деловым, но живым языком, без канцелярита и воды."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Сейчас ты выступаешь как эксперт по рынку труда и карьерный консультант. "
                    "Твоя задача — подготовить для меня:\n\n"
                    "1) полностью готовое резюме для размещения на hh.ru;\n"
                    "2) индивидуальное сопроводительное письмо под конкретную вакансию.\n\n"
                    "Вот мое резюме (в прикрепленном файле: текст или pdf) и вакансия (на картинке или в виде текста). "
                    "Возьми из моего резюме только контакты, остальное придумай с нуля так, "
                    "чтобы идеально подходило под эту вакансию. В конце кратко опиши, про что была вакансия.\n\n"
                    "Сделай следующее:\n"
                    "1. Проанализируй вакансию, выпиши ключевые требования и навыки и постарайся органично "
                    "встроить их в резюме и сопроводительное, не вря и не приписывая того, чего у меня нет.\n"
                    "2. Сформируй резюме в структуре, близкой к hh.ru:\n"
                    "   - краткое описание обо мне (2–3 предложения, кто я и чем полезен работодателю);\n"
                    "   - ключевые навыки (списком, с упором на требования вакансии);\n"
                    "   - опыт работы: для каждого места — должность, компания, период, 3–7 конкретных обязанностей "
                    "и 3–5 достижений, по возможности с цифрами;\n"
                    "   - образование;\n"
                    "   - доп. сведения (языки, технологии, инструменты, сертификаты и т.п.).\n"
                    "3. Упор делай на релевантность под эту вакансию: переформулируй задачи и достижения так, "
                    "чтобы было максимально понятно, что мой опыт подходит под указанные обязанности.\n"
                    "4. Сформируй отдельный текст сопроводительного письма (5–10 предложений), в котором:\n"
                    "   - есть 1–2 предложения о компании и позиции (почему она мне интересна);\n"
                    "   - есть 2–3 предложения, связывающие мой опыт и требования вакансии (с конкретикой, без общих фраз);\n"
                    "   - есть 1–2 примера достижений, важных именно для этой роли;\n"
                    "   - в конце — вежливое приглашение к диалогу/интервью.\n"
                    "5. Пиши на русском, деловым, но живым языком, без канцелярита и без воды.\n"
                    "6. Выведи результат в двух блоках с чёткими заголовками:\n"
                    "   «РЕЗЮМЕ ДЛЯ HH.RU» и ниже «СОПРОВОДИТЕЛЬНОЕ ПИСЬМО».\n"
                    "7. Если в моих данных чего‑то не хватает для сильного резюме, аккуратно придумай нейтральные "
                    "формулировки без конкретных цифр, не приписывая явной неправды."
                ),
                "attachments": attachments,
            },
        ],
        "temperature": 0.2,
        "max_tokens": 1024,
    }

    resp_chat = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=headers_chat,
        json=payload,
        verify=CA_BUNDLE,
    )
    resp_chat.raise_for_status()
    data = resp_chat.json()
    text = data["choices"][0]["message"]["content"]
    return text, resume_file_id, vacancy_file_id


def generate_resume_from_streams_and_texts(
    resume_stream: bytes | None,
    resume_filename: str | None,
    resume_mime: str | None,
    resume_text: str | None,
    vacancy_stream: bytes | None,
    vacancy_filename: str | None,
    vacancy_mime: str | None,
    vacancy_text: str | None,
) -> tuple[str, str | None, str | None]:
    """
    Обёртка с «говорящим» именем для использования в API.
    """
    return generate_resume(
        resume_stream=resume_stream,
        resume_filename=resume_filename,
        resume_mime=resume_mime,
        resume_text=resume_text,
        vacancy_stream=vacancy_stream,
        vacancy_filename=vacancy_filename,
        vacancy_mime=vacancy_mime,
        vacancy_text=vacancy_text,
    )
