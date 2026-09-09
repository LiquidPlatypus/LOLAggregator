import os, json

import os, json

def load_json(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} does not exist.")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_local_summoner(puuid):
    filepath = f"data/scraped/{puuid}/summoner.json"
    return load_json(filepath)

def load_local_mastery(puuid):
    filepath = f"data/scraped/{puuid}/mastery.json"
    return load_json(filepath)

def load_local_match_ids(puuid=None, start=0, count=1000):
    folder = "data/scraped/matches"
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Match folder {folder} does not exist.")

    match_ids = []
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            match_ids.append(filename[:-5])

    match_ids.sort(key=lambda mid: int(mid.split("_")[1]), reverse=True)

    return match_ids[start:start + count]

def load_local_match(match_id):
    filepath = f"data/scraped/matches/{match_id}.json"
    return load_json(filepath)