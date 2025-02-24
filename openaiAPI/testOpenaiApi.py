"""
Список моделей
https://platform.openai.com/docs/models#current-model-aliases
"""
import os
import requests
import json
from dotenv import load_dotenv
from data.llm_prompts.prompts import SYSTEM_CONTENT, USER_CONTENT, USER_CONTENT_2, USER_CONTENT_3
from data.llm_prompts.drug_instructions import INSTR1, INSTR2, INSTR3

USER_CONTENT_WITH_DRUG_INSTRUCTION = USER_CONTENT + f"\"{INSTR2}\""

# Загружаем переменные из .env
load_dotenv()

API_KEY = os.getenv("API_KEY_OPENAI")

URL = "https://api.openai.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "gpt-4o",
    "messages": [
        {"role": "developer", "content": SYSTEM_CONTENT},
        {"role": "user", "content": USER_CONTENT_WITH_DRUG_INSTRUCTION}
    ],
    "temperature": 0.1,
    "max_tokens": 1000
}

response = requests.post(URL, headers=headers, data=json.dumps(data))
result = response.json()

try:
    choices = result['choices']
    message = choices[0]['message']
    content = message['content']
    print(content)
except Exception as e:
    print(e)
    print(f"{result=}")


