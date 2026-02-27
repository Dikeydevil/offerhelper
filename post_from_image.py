import os
import requests

BASE_URL = "https://gigachat.devices.sberbank.ru/api/v1"

ACCESS_TOKEN = os.getenv("GIGACHAT_ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise RuntimeError("GIGACHAT_ACCESS_TOKEN не задан в окружении")

file_id = "d94fafb0-5320-416c-8c01-ce5c796dc1d3"  # подставь свой id

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

payload = {
    "model": "GigaChat-Pro",          # важно: vision в примере через Pro [web:31]
    "messages": [
        {
            "role": "user",
            "content": "Что изображено на рисунке?",
            "attachments": [file_id],  # сюда просто список id, без объектов
        }
    ],
    "stream": False,
    "update_interval": 0,
    "temperature": 0.1,
}

resp = requests.post(
    f"{BASE_URL}/chat/completions",
    headers=headers,
    json=payload,
    verify=False,
)

print(resp.status_code, resp.text)
