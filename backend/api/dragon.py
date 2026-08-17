import json
import os
from config import DRAGON_PATH

def load_champions(path=None):
    if path is None:
        path = os.path.join(DRAGON_PATH, "champion.json")
    with open(path, encoding="utf-8") as f:
        champions_raw = json.load(f)

    return {
        int(champ["key"]): champ["name"]
        for champ in champions_raw["data"].values()
    }