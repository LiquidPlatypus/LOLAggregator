import os
import json
from api.riot import get_summoner, get_champion_mastery, get_match_history, get_match

def get_all_match_ids(puuid, count=100):
    all_ids = []
    start = 0

    while True:
        batch = get_match_history(puuid, start=start, count=count)
        all_ids.extend(batch)
        print(f"Récupéré {len(all_ids)} match_ids (start={start})")

        if len(batch) < count:
            break

        start += count

    return all_ids

def scrape_profile(puuid):
    folder = f"data/scraped/{puuid}"
    os.makedirs(folder, exist_ok=True)

    summoner = get_summoner(puuid)
    with open(f"{folder}/summoner.json", "w", encoding="utf-8") as f:
        json.dump(summoner, f, ensure_ascii=False, indent=2)

    mastery = get_champion_mastery(puuid)
    with open(f"{folder}/mastery.json", "w", encoding="utf-8") as f:
        json.dump(mastery, f, ensure_ascii=False, indent=2)

def scrape_matches(puuid, match_ids):
    folder = "data/scraped/matches"
    os.makedirs(folder, exist_ok=True)

    for match_id in match_ids:
        filepath = f"{folder}/{match_id}.json"
        if os.path.exists(filepath):
            print(f"Skip {match_id} (already exists)")
            continue

        match = get_match(match_id)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(match, f, ensure_ascii=False, indent=2)
        print(f"Scraped {match_id} and saved to {filepath}")


def main(puuid="mrdJFW8Lvl17o5iW9498HaGiWTRONyQe47taTdtjo5iXaOemXiFFrzmrDy1A-GtzDhPDdT1JGirSxQ"):
    scrape_profile(puuid)
    match_ids = get_all_match_ids(puuid)
    scrape_matches(puuid, match_ids)


if __name__ == "__main__":
    main()