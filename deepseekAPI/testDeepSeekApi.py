import os
import requests
import json
from dotenv import load_dotenv
from data.llm_prompts.prompts import SYSTEM_CONTENT, USER_CONTENT, USER_CONTENT_2, USER_CONTENT_3
from data.llm_prompts.drug_instructions import INSTR1, INSTR2, INSTR3

USER_CONTENT_WITH_DRUG_INSTRUCTION = USER_CONTENT_2 + f"\"{INSTR2}\""

# Загружаем переменные из .env
load_dotenv()

API_KEY = os.getenv("API_KEY_DEEPSEEK")

# URL API
URL = "https://api.deepseek.com/v1/chat/completions"

# Заголовки запроса
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Данные для отправки
data = {
    "model": "deepseek-chat",  # Укажите модель
    "messages": [
        {"role": "system", "content": SYSTEM_CONTENT},
        {"role": "user", "content": USER_CONTENT_WITH_DRUG_INSTRUCTION}
    ]
}

# Отправка POST-запроса
response = requests.post(URL, headers=headers, data=json.dumps(data))

# Проверка статуса ответа
if response.status_code == 200:
    # Получение и вывод ответа
    result = response.json()
    print(result['choices'][0]['message']['content'])
else:
    print(f"Ошибка: {response.status_code}")
    print(response.text)
