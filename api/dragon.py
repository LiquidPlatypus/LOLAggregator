import json

def load_champions(path="dragontail-16.13.1/16.13.1/data/fr_FR/champion.json"):
    with open(path) as f:
        champions_raw = json.load(f)

    return {
        int(champ["key"]): champ["name"]
        for champ in champions_raw["data"].values()
    }