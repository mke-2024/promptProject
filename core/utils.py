import json


def save_json(filepath: str, data: list | dict):
    with open(filepath, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)
        print(f"Data saved:'{filepath}'")


def load_json(filepath: str) -> dict:
    with open(filepath, "r", encoding='utf-8') as fp:
        return json.load(fp)
