import os
import requests
import random
import numpy as np
import json
from dotenv import load_dotenv
from tqdm import tqdm

SYSTEM_ROLE = "Ти — медичний експерт, що використовує МКБ-10 для класифікації хвороб. Аналізуй симптоми та повертай структурований JSON з діагностичними припущеннями."

load_dotenv()
url = "https://api.x.ai/v1/chat/completions"
api_key = os.getenv("API_KEY_GROK")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# JSON-объект с симптомами и их значениями
SYMPTOMS_DATA = {
    "Какой день болеет": {"dtype": "<class 'numpy.float32'>", "is_integer": True, "items": [1, 42], "id": 30},
    "Температура": {"dtype": "<class 'numpy.float32'>", "is_integer": False, "items": [35.0, 43.0], "id": 68},
    "Боль в горле": {"dtype": "<class 'object'>", "is_integer": False,
                     "items": ["Да", "Нет", "Ни одно из перечисленных"], "id": 8},
    "Сыпь на коже": {"dtype": "<class 'object'>", "is_integer": False, "items": [
        "Мелкоточечная сыпь, расположена на гиперемированном фоне кожи с свободным от сыпи носогубным треугольником, сгущаясь в местах естественных складок, на боковых поверхностях туловища",
        "Нет", "Ни одно из перечисленных",
        "Пятнисто-папулезная сыпь красного цвета, обильная, может сливаться, располагается на неизмененном фоне кожи",
        "Пятнисто-папулезная сыпь, розового цвета, расположена на неизменённой коже. элементы сыпи не сливаются друг с другом, не образовщают большие пятна",
        "Сыпь везикулезная с прозрачным содержимым на теле и волосистой части головы",
        "Сыпь появляется в первый день болезни . геморрагическая. от ярко-красного до темно-красного или фиолетового цвета. звездчатая. неправильной формы. локализация сыпи: нижние конечности. ягодицы"
    ], "id": 65},
    "Кашель": {"dtype": "<class 'object'>", "is_integer": False, "items": [
        "Влажный , чаще ночью", "Грубый, сухой,\" лающий\"", "Нет", "Ни одно из перечисленных", "Отхаркивающий",
        "Отхаркивающий , чаще ночью",
        "Приступы спастического кашля; без возможности набрать воздуха; заканчивается глубоким вдохом с громким свистом. может возникать отек и посинение лица, глаза слезятся. при кашле: голова вытягивается вперед, язык высовывается до предела. приступ кашля заканчивается тягучей, вязкой мокроты и , возможно, рвотой.",
        "Сухой", "Сухой с охрипшим голосом", "Сухой, приступообразный, длительный", "Сухой, хриплый",
        "Сухой, чаще ночью"
    ], "id": 31}
}

MANDATORY_SYMPTOMS = ["Какой день болеет", "Температура"]
OPTIONAL_SYMPTOMS = [key for key in SYMPTOMS_DATA.keys() if key not in MANDATORY_SYMPTOMS]
EXCLUDED_VALUES = ["Нет", "Ни одно из перечисленных"]
NUM_TESTS = 10


def generate_symptom_value(symptom):
    data = SYMPTOMS_DATA[symptom]
    if data["is_integer"]:
        return np.random.randint(data["items"][0], data["items"][1] + 1)
    elif data["dtype"] == "<class 'numpy.float32'>" and not data["is_integer"]:
        return round(np.random.uniform(data["items"][0], data["items"][1]), 1)
    else:
        valid_items = [item for item in data["items"] if item not in EXCLUDED_VALUES]
        if not valid_items:
            return data["items"][0]
        return random.choice(valid_items)


# Функция для очистки ответа от Markdown
def clean_json_response(raw_response):
    cleaned = raw_response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


results = {"case": []}

with tqdm(total=NUM_TESTS, desc="Генерация случаев", bar_format="{l_bar}{bar:30}{r_bar}", ncols=100) as pbar:
    for _ in range(NUM_TESTS):
        observation = {symptom: generate_symptom_value(symptom) for symptom in MANDATORY_SYMPTOMS}
        num_additional = random.randint(0, len(OPTIONAL_SYMPTOMS))
        additional_symptoms = random.sample(OPTIONAL_SYMPTOMS, num_additional)
        for symptom in additional_symptoms:
            observation[symptom] = generate_symptom_value(symptom)

        symptoms_str = ", ".join([f"{k}: {v}" for k, v in observation.items()])

        CONTENT = f"""
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
        4. "additional_symptoms_to_check": список об'єктів (4-5 симптомів: тест на стрептококк, наліт, лімфовузли, кашель, утруднене ковтання, ймовірності 20-70%):
           - "symptom": симптом/аналіз.
           - "probability": відсоток значущості.
        5. "disclaimer": "Отказ від відповідальності: Я не лікар, це загальна інформація. Зверніться до лікаря."

        Інструкція:
        - Використовуй МКБ-10.
        - Температура 37°C — субфебрильна, підвищуй J02.9 до 70-75%, знижуй бактеріальні причини.
        - Дай 1-3 діагнози.
        - Виведи чистий JSON.

        Симптоми:
        "{symptoms_str}"
        """

        data = {
            "messages": [
                {"role": "system", "content": SYSTEM_ROLE},
                {"role": "user", "content": CONTENT}
            ],
            "model": "grok-2-1212",
            "stream": False,
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            raw_content = result["choices"][0]["message"]["content"]
            cleaned_content = clean_json_response(raw_content)
            try:
                parsed_content = json.loads(cleaned_content)
                observation_result = {
                    "observation": observation,
                    "response": parsed_content
                }
            except json.JSONDecodeError as e:
                observation_result = {
                    "observation": observation,
                    "response": f"Ошибка парсинга JSON после очистки: {str(e)}. Очищенный ответ: {cleaned_content}"
                }
            results["case"].append(observation_result)
        else:
            results["case"].append({
                "observation": observation,
                "response": f"Ошибка: {response.status_code} - {response.text}"
            })

        pbar.update(1)

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"Результаты сохранены в result.json. Сгенерировано {len(results['case'])} случаев.")