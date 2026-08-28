import json
import os
from config import DRAGON_PATH

def load_champions(path=None):
    if path is None:
        path = os.path.join(DRAGON_PATH, "champion.json")
    with open(path, encoding="utf-8") as f:
        champions_raw = json.load(f)

    return {
        int(champ["key"]): {
            "id": champ["id"],
            "name": champ["name"],}
        for champ in champions_raw["data"].values()
    }

def load_items(path=None):
    if path is None:
        path = os.path.join(DRAGON_PATH, "item.json")
    with open(path, encoding="utf-8") as f:
        items_raw = json.load(f)

    return {
        int(item_id): {
            "id": int(item_id),
            "name": item["name"],
            "description": item["description"],
            "plaintext": item.get("plaintext", ""),
            "gold": item.get("gold", {}),
            "tags": item.get("tags", []),
            "stats": item.get("stats", {}),
        }
        for item_id, item in items_raw["data"].items()
    }