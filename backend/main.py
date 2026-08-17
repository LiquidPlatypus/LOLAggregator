# from api.riot import get_player, get_champion_mastery, get_match_history, get_match
# from api.dragon import load_champions
# from data.processor import process_mastery, process_matches
# from config import REGION
#
# SUMMONER_NAME = "Liquid Platypus"
# TAG_LINE = "FEET"
#
# # Joueur
# player = get_player(SUMMONER_NAME, TAG_LINE)
# puuid = player["puuid"]
#
# # Mastery
# mastery_raw = get_champion_mastery(puuid)
# champion_map = load_champions()
# df_mastery = process_mastery(mastery_raw, champion_map)
# df_mastery.to_csv("player_mastery.csv", index=False)
#
# # Matchs
# match_ids = get_match_history(puuid)
# matches_raw = [get_match(mid) for mid in match_ids]
# df_matches = process_matches(matches_raw)
# df_matches.to_csv("matches_history.csv", index=False)

from fastapi import FastAPI

from backend.api.riot import get_player as riot_get_player, get_champion_mastery
from backend.api.dragon import load_champions
from backend.data.processor import process_mastery

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/player/{game_name}/{tag_line}")
def read_player(game_name: str, tag_line: str):
    player = riot_get_player(game_name, tag_line)
    mastery_raw = get_champion_mastery(player["puuid"])
    champion_map = load_champions()
    mastery = process_mastery(mastery_raw, champion_map)

    ret_dict = {
        "player": player,
        "mastery": mastery.to_dict(orient="records")}

    return ret_dict