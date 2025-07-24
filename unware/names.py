import json
from typing import Optional

def get_name_by_id(id, json_path):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    for item in data:
        if str(item.get("id")) == str(id):
            return item.get("name").lower()
    return None
    
def get_model_from_ide(
    id_value: int,
    ide_path: str,
    id_index: int = 0,
    model_index: int = 1,
    skip_prefixes: tuple = ('#', 'cars')
) -> Optional[str]:
    """

    skin_model = get_model_from_ide(skin_id, SKINS_IDE_PATH, id_index=0, model_index=1, skip_prefixes=('#',))
    car_model = get_model_from_ide(car_id, CARS_IDE_PATH, id_index=0, model_index=1, skip_prefixes=('#', 'cars'))

    """

    with open(ide_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or any(line.startswith(pref) for pref in skip_prefixes):
                continue

            parts = [p.strip() for p in line.split(',')]
            if len(parts) <= max(id_index, model_index):
                continue

            try:
                cur_id = int(parts[id_index])
            except ValueError:
                continue

            if cur_id == id_value:
                return parts[model_index]

    return None
