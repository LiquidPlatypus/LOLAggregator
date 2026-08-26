from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
import requests

from api.riot import get_player as riot_get_player, get_summoner, get_champion_mastery, get_match_history, get_match
from api.dragon import load_champions
from data.processor import process_mastery, get_top_champs, process_matches

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000",]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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

    ret_dict = {
        "player": player,
        "summoner": summoner,
        "mastery": mastery.to_dict(orient="records"),
        "top_mastery": top_mastery.to_dict(orient="records"),
    }

    return ret_dict

@app.get("/matchs/{puuid}")
def read_match(puuid: str, page: int = 1, count: int = 10):
    start = (page - 1) * count

    try:
        match_ids = get_match_history(puuid, start=start, count=count)
        champion_map = load_champions()
        with ThreadPoolExecutor() as executor:
            matchs_raw = list(executor.map(get_match, match_ids))
        matchs_history = process_matches(matchs_raw, champion_map, puuid)
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else 500
        raise HTTPException(status_code=status, detail="Too much requests to Riot API. Please try again later.")

    return matchs_history.to_dict(orient="records")