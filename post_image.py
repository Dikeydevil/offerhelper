import uuid
from pathlib import Path
import requests

NGW_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
BASE_URL = "https://gigachat.devices.sberbank.ru/api/v1"
CA_BUNDLE = "certs/ca.pem"
AUTH_KEY = "OWJmNGNiNDItYjFjNC00OTJlLWEzMDYtMDAzMzFlNzQzODE5OjM3ZTM1NTExLWMzZTgtNDBiNS1hMzVjLWM3YzU3Y2FlMzAzMg=="


def get_access_token() -> str:
    payload = "scope=GIGACHAT_API_PERS"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {AUTH_KEY}",
    }
    resp = requests.post(NGW_URL, headers=headers, data=payload, verify=CA_BUNDLE)
    print("oauth:", resp.status_code, resp.text)
    resp.raise_for_status()
    return resp.json()["access_token"]


def upload_file(path: Path, mime: str, access_token: str) -> str:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    with path.open("rb") as f:
        files = {
            "file": (path.name, f, mime)
        }
        data = {"purpose": "general"}
        resp = requests.post(
            f"{BASE_URL}/files",
            headers=headers,
            files=files,
            data=data,
            verify=CA_BUNDLE,
        )
    print(f"upload {path.name}:", resp.status_code, resp.text)
    resp.raise_for_status()
    return resp.json()["id"]


access_token = get_access_token()

# 1. резюме: сначала пробуем pdf, если нет — txt
resume_pdf_path = Path(__file__).with_name("resume.pdf")
resume_txt_path = Path(__file__).with_name("resume.txt")

if resume_pdf_path.exists():
    resume_path = resume_pdf_path
    resume_mime = "application/pdf"
else:
    resume_path = resume_txt_path
    resume_mime = "text/plain"

resume_file_id = upload_file(resume_path, resume_mime, access_token)
print("resume_file_id:", resume_file_id)

# 2. вакансия — всегда картинка
vacancy_path = Path(__file__).with_name("vacancy.jpg")
vacancy_file_id = upload_file(vacancy_path, "image/jpeg", access_token)
print("vacancy_file_id:", vacancy_file_id)

# 3. запрос к модели с обоими файлами
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
                "Ты мастер написания резюме. Глубоко анализируешь прикрепленные резюме и вакансии, "
                "пишешь новое резюме с нуля под вакансию, из старого берешь только контакты кандидата."
            ),
        },
        {
            "role": "user",
            "content": (
                "Вот мое резюме (в прикрепленном файле: pdf или текст) и вакансия (на картинке). "
                "Возьми из моего резюме только контакты, остальное придумай с нуля так, "
                "чтобы идеально подходило под эту вакансию. В конце кратко опиши, про что была вакансия."
            ),
            "attachments": [resume_file_id, vacancy_file_id],
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

print("chat:", resp_chat.status_code, resp_chat.text)
