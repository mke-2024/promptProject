import os
import json

# Список папок и файлов, которые НЕ будут добавлены в JSON
IGNORE_LIST = {
    "folders": {".git", "__pycache__", "venv", "migrations", "backup", "llm_prompts", "grokAPI", "openaiAPI", ".idea"},
    "files": {"project_structure.json", "generate_structure.py"}
}


def get_directory_structure(root_dir):
    """
    Рекурсивно собирает структуру проекта в формате {"папка": ["file1", "file2", {"subfolder": [...]}]}
    Исключает папки и файлы из IGNORE_LIST.
    """
    def build_structure(directory):
        items = []
        for item in sorted(os.listdir(directory)):  # Сортируем для удобства
            full_path = os.path.join(directory, item)
            if os.path.isdir(full_path):
                if item not in IGNORE_LIST["folders"]:
                    items.append({item: build_structure(full_path)})  # Добавляем вложенную папку
            else:
                if item not in IGNORE_LIST["files"]:
                    items.append(item)  # Добавляем файл
        return items

    project_name = os.path.basename(root_dir)  # Определяем имя корневой папки
    return {project_name: build_structure(root_dir)}


def print_structure(structure, indent=0, output_lines=None):
    """
    Функция рекурсивно печатает структуру проекта в виде дерева и записывает в список output_lines.
    """
    if output_lines is None:
        output_lines = []

    for folder, contents in structure.items():
        root_line = " " * indent + f"📂 {folder}"  # Корневая папка
        print(root_line)
        output_lines.append(root_line)
        for item in contents:
            if isinstance(item, dict):
                print_structure(item, indent + 4, output_lines)  # Рекурсивно печатаем папку
            else:
                line = " " * (indent + 4) + f"📄 {item}"  # Файл
                print(line)
                output_lines.append(line)

    return output_lines


def save_structure():
    """
    Собирает и сохраняет структуру проекта в JSON и текстовый файл.
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))  # Корневая папка проекта
    structure = get_directory_structure(root_dir)

    # Сохраняем в JSON
    with open("project_structure.json", "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=4, ensure_ascii=False)

    # Выводим в консоль и сохраняем в текстовый файл
    print("📦 Проектная структура:")
    output_lines = print_structure(structure)  # Берем корневую папку
    with open("project_structure.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"\n✅ Структура проекта сохранена в 'project_structure.json' и 'project_structure.txt'")


if __name__ == "__main__":
    save_structure()


