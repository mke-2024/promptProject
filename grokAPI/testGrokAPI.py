import os
import requests
from dotenv import load_dotenv
from data.llm_prompts.prompts import SYSTEM_CONTENT, USER_CONTENT, USER_CONTENT_2, USER_CONTENT_3
from data.llm_prompts.drug_instructions import INSTR1, INSTR2, INSTR3

load_dotenv()
url = "https://api.x.ai/v1/chat/completions"
api_key = os.getenv("API_KEY_GROK")

USER_CONTENT_WITH_DRUG_INSTRUCTION = USER_CONTENT + f"\"{INSTR2}\""

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "messages": [
        {"role": "system", "content": SYSTEM_CONTENT},
        {"role": "user", "content": USER_CONTENT_WITH_DRUG_INSTRUCTION}
    ],
    "model": "grok-2", # grok-beta, grok-2-1212
    "stream": False,
    "temperature": 0.1
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    print(result["choices"][0]["message"]["content"])
else:
    print(f"Ошибка: {response.status_code} - {response.text}")