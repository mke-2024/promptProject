"""
Трансформирует в читабельный вид json файлы
"""
from core.utils import load_json, save_json
import settings
from pathlib import Path

# Определяем директории, используя pathlib
target_directory = Path(settings.DATA_DIR) / "backup"
src_directory = Path(settings.BACKUP_DIR)

# Если целевая директория не существует, создаём её
target_directory.mkdir(parents=True, exist_ok=True)

# Получаем список файлов в исходной директории
files = [f for f in src_directory.iterdir() if f.is_file()]

for src_path in files:
    # Загружаем JSON-данные из файла
    json_data = load_json(src_path)

    # Определяем путь для сохранения
    target_path = target_directory / src_path.name

    # Сохраняем JSON-данные в целевую директорию
    save_json(target_path, json_data)


