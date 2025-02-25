import os
import json
import random
import requests
import re
from dotenv import load_dotenv
from tqdm import tqdm

# Загрузка переменных окружения
load_dotenv()

# API параметры
url = "https://api.openai.com/v1/chat/completions"
api_key = os.getenv("API_KEY_OPENAI")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Исходный JSON с возможными симптомами
symptom_data = {
    "Какой день болеет": {"dtype": "<class 'numpy.float32'>", "is_integer": True, "items": [1, 42], "id": 30},
    "Температура": {"dtype": "<class 'numpy.float32'>", "is_integer": False, "items": [35.0, 43.0], "id": 68},
    "Боль в горле": {"dtype": "<class 'object'>", "is_integer": False,
                     "items": ["Да", "Нет", "Ни одно из перечисленных"], "id": 8},
    "Сыпь на коже": {"dtype": "<class 'object'>", "is_integer": False, "items": [
        "Мелкоточечная сыпь, расположена на гиперемированном фоне кожи с свободным от сыпи носогубным треугольником",
        "Нет", "Ни одно из перечисленных",
        "Пятнисто-папулезная сыпь красного цвета, обильная, может сливаться"
    ], "id": 65},
    "Кашель": {"dtype": "<class 'object'>", "is_integer": False, "items": [
        "Влажный , чаще ночью", "Грубый, сухой, 'лающий'", "Нет", "Сухой",
        "Сухой, хриплый", "Сухой, чаще ночью"
    ], "id": 31}
}

# Константа с неинформативными значениями
EXCLUDED_VALUES = ["Нет", "Ни одно из перечисленных"]

# Обязательные симптомы
required_symptoms = ["Какой день болеет", "Температура"]
# Дополнительные случайные симптомы
optional_symptoms = [symptom for symptom in symptom_data.keys() if symptom not in required_symptoms]

# Количество тестов
num_tests = 1

# Сохранение результатов
results = {"case": []}


def generate_random_value(symptom):
    """Генерация случайного значения для симптома"""
    data = symptom_data[symptom]
    if data["dtype"] == "<class 'numpy.float32'>":
        min_val, max_val = data["items"]
        if data["is_integer"]:
            return random.randint(min_val, max_val)
        else:
            return round(random.uniform(min_val, max_val), 1)
    else:
        valid_items = [item for item in data["items"] if item not in EXCLUDED_VALUES]
        return random.choice(valid_items) if valid_items else None


def extract_json(text):
    """Извлекает JSON из ответа модели"""
    match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
    return match.group(1) if match else text


for _ in tqdm(range(num_tests), desc="Генерация тестов", ncols=100,
              bar_format="{l_bar}{bar} {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"):
    observation = {}

    for symptom in required_symptoms:
        observation[symptom] = generate_random_value(symptom)

    selected_optional = random.sample(optional_symptoms, random.randint(1, len(optional_symptoms)))
    for symptom in selected_optional:
        value = generate_random_value(symptom)
        if value is not None:
            observation[symptom] = value

    symptoms_str = json.dumps([f"{k}: {v}" for k, v in observation.items()], ensure_ascii=False)
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
             - "name": назва з дозуванням.
             - "self_administered": true/false.
           - "when_to_seek_medical_attention": список ознак.
        3. "red_flag": true при температурі 41°C, утрудненому диханні, інакше false.
        4. "additional_symptoms_to_check": список об'єктів.
        5. "disclaimer": "Отказ від відповідальності: Я не лікар, це загальна інформація. Зверніться до лікаря."
        Симптоми:
        {symptoms_str}
    """

    data = {"messages": [
        {"role": "system", "content": "Ти — медичний експерт, що використовує МКБ-10 для класифікації хвороб."},
        {"role": "user", "content": CONTENT}],
            "model": "gpt-4o",
            "temperature": 0.3}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        raw_content = response.json()["choices"][0]["message"]["content"]
        json_content = extract_json(raw_content)
        try:
            result = json.loads(json_content)
            results["case"].append({"observation": observation, "response": result})
        except json.JSONDecodeError:
            results["case"].append({"observation": observation, "error": "Invalid JSON response"})
    else:
        results["case"].append({"observation": observation, "error": f"Ошибка API: {response.status_code}"})

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("Тестирование завершено. Результаты сохранены в result.json")
