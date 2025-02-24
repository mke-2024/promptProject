"""
Трансформирует JSON-файлы в читабельный вид и сохраняет их в целевую директорию
"""
from pprint import pprint
from pathlib import Path
from core.utils import load_json
import settings


# Определяем директории, используя pathlib
target_directory = Path(settings.DATA_DIR) / "backup"
src_directory = Path(settings.BACKUP_DIR)
diagnosis_list_path = src_directory / "diagnosis_list.json"

# Если целевая директория не существует, создаём её
target_directory.mkdir(parents=True, exist_ok=True)

# Получаем список JSON-файлов в исходной директории
files = [f for f in src_directory.iterdir() if f.is_file() and f.suffix == '.json']

# Загружаем список диагнозов с обработкой ошибок
try:
    diagnosis_list = {diagnosis['name'] for diagnosis in load_json(diagnosis_list_path)}
except FileNotFoundError:
    print(f"Ошибка: Файл {diagnosis_list_path} не найден.")
    exit(1)
except (KeyError, TypeError) as e:
    print(f"Ошибка: Некорректная структура в {diagnosis_list_path}: {e}")
    exit(1)
except Exception as e:
    print(f"Неизвестная ошибка при загрузке {diagnosis_list_path}: {e}")
    exit(1)

i = 0
# Обрабатываем файлы
for src_path in files:
    file_name_no_ext = src_path.name.replace('.json', '')
    if file_name_no_ext in diagnosis_list:
        try:
            # Загружаем JSON-данные из файла
            json_data = load_json(src_path)
        except Exception as e:
            print(f"Ошибка при загрузке {src_path.name}: {e}")
            continue

        regulations = json_data['regulations']
        print(file_name_no_ext, len(regulations))

        for regulation in regulations:
            i += 1
            drug = regulation['drug']
            product_name = drug['product_name']
            src_url = drug['url']
            usage_dosages = drug['usagedosage']
            tokens = []
            for usage_dosage in usage_dosages:
                tokens.append(len(usage_dosage['text']))
                usage_dosage.update({"recommendations": "any"})
            print(f"\t{product_name} {len(usage_dosages)} {tokens=} {src_url=}")
            if i == 1:
                pprint(regulation, width=130)
                exit(1)

    # # Определяем путь для сохранения
    # target_path = target_directory / src_path.name
    #
    # # Сохраняем JSON-данные в читабельном виде
    # try:
    #     save_json(target_path, json_data)
    #     if file_name_no_ext in diagnosis_list:
    #         print(f"Обработан и соответствует списку диагнозов: {src_path.name}")
    #     else:
    #         print(f"Обработан: {src_path.name}")
    # except Exception as e:
    #     print(f"Ошибка при сохранении {target_path.name}: {e}")


