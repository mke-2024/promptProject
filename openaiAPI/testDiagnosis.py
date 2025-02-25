import os
import requests
from dotenv import load_dotenv

SYSTEM_ROLE = "Ти — медичний експерт, що використовує МКБ-10 для класифікації хвороб. Аналізуй симптоми та повертай структурований JSON з діагностичними припущеннями."

load_dotenv()
url = "https://api.openai.com/v1/chat/completions"
api_key = os.getenv("API_KEY_OPENAI")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

CONTENT = """
Аналізуй надані симптоми та створи JSON:
1. "input_data": список симптомів.
2. "recommendations": список об'єктів:
   - "diagnosis_code": код МКБ-10.
   - "diagnosis_description": опис українською.
   - "probability": відсоток як строка (наприклад, "70%"), сума до 100%.
   - "possible_causes": список причин (деталізуй віруси як 'риновіруси, аденовіруси', уточнюй меншу ймовірність бактерій при 37°C).
   - "general_treatment_recommendations": список (включай 'Тепле пиття', 'Льодяники', 'Спреї', 'Полоскання горла', 'Відпочинок', 'Увлажнення повітря').
   - "recommended_medications": список об'єктів:
     - "name": назва з дозуванням (вказуй max, наприклад, "Ібупрофен 200-400 мг кожні 6-8 годин, max 3,2 г/сутки"), для льодяників і спреїв додавай 'по інструкції' (наприклад, 'Стрепсілс по інструкції'), включай Парацетамол, льодяники, спреї, сольові розчини.
     - "self_administered": true/false.
   - "when_to_seek_medical_attention": список ознак із термінами "5-7 днів", включай 'Температура вище 38°C', 'Утруднене ковтання', специфічні (наліт, лімфовузли).
3. "red_flag": true при температурі 41°C, утрудненому диханні, інакше false.
4. "additional_symptoms_to_check": список об'єктів (4-5 симптомів: тест на стрептококк, наліт, лімфовузли, кашель, утруднене ковтання, ймовірності 20-70%)):
   - "symptom": симптом/аналіз.
   - "probability": відсоток значущості.
5. "disclaimer": "Отказ від відповідальності: Я не лікар, це загальна інформація. Зверніться до лікаря."

Інструкція:
- Використовуй МКБ-10.
- Температура 37°C — субфебрильна, підвищуй J02.9 до 70-75%, знижуй бактеріальні причини.
- Дай 1-3 діагнози.
- Виведи чистий JSON.

Симптоми:
"Боль в горле и температура 37°C"
"""

data = {
    "messages": [
        {"role": "developer", "content": SYSTEM_ROLE},
        {"role": "user", "content": CONTENT}
    ],
    "model": "gpt-4o",  # Рекомендую эту модель для точности
    "temperature": 0.7  # Для гибкости
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    print(result["choices"][0]["message"]["content"])
else:
    print(f"Ошибка: {response.status_code} - {response.text}")
