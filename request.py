import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

# читаем токен из файла
with open("token.txt", "r", encoding="utf-8") as f:
    auth_token = f.read().strip()  # одна строка с токеном без переводов строки

payload = {
    "model": "GigaChat-2-Max",
    "stream": False,
    "update_interval": 0,
    "messages": [
        {
            "role": "system",
            "content": "Ты мастер написания резюме. Вносишь правки в резюме на основе вакансии, можешь приукрасить"
        },
        {
            "role": "user",
            "content": "Напиши мне резюме Full Stack Python-разработчика"
        }
    ],
    "temperature": 0.3,
    "max_tokens": 512
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {auth_token}",
}

response = requests.post(
    url,
    headers=headers,
    data=json.dumps(payload),
    verify=False
)

print(response.status_code)
print(response.text)
