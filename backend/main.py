from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.riot import get_player as riot_get_player, get_summoner, get_champion_mastery, get_match_history, get_match
from api.dragon import load_champions
from data.processor import process_mastery, get_top_champs, process_matches

app = FastAPI()
app.mount("/static", StaticFiles(directory="dragontail-16.16.1/16.16.1/img"), name="static")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/player/{game_name}/{tag_line}")
def read_player(game_name: str, tag_line: str):
    player = riot_get_player(game_name, tag_line)
    summoner = get_summoner(player["puuid"])
    mastery_raw = get_champion_mastery(player["puuid"])
    champion_map = load_champions()
    mastery = process_mastery(mastery_raw, champion_map)
    top_mastery = get_top_champs(mastery, 5)

    match_ids = get_match_history(player["puuid"])
    matchs_raw = [get_match(mid) for mid in match_ids]
    matchs_history = process_matches(matchs_raw)

    ret_dict = {
        "player": player,
        "summoner": summoner,
        "mastery": mastery.to_dict(orient="records"),
        "top_mastery": top_mastery.to_dict(orient="records"),
        "matchs_history": matchs_history.to_dict(orient="records")}

    return ret_dict