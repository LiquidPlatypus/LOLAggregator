import requests
from config import API_KEY, REGION, PLATFORM

HEADERS = {"X-Riot-Token": API_KEY}
REGIONAL_BASE = f"https://{REGION}.api.riotgames.com"
PLATFORM_BASE = f"https://{PLATFORM}.api.riotgames.com"

def _get(base, endpoint, **kwargs):
    url = f"{base}{endpoint.format(**kwargs)}"
    return requests.get(url, headers=HEADERS).json()

def get_player(game_name, tag_line):
    return _get(
        REGIONAL_BASE,
        "/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}",
        gameName=game_name,
        tagLine=tag_line
    )

def get_champion_mastery(puuid):
    return _get(
        PLATFORM_BASE,
        "/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}",
        puuid=puuid
    )

def get_match_history(puuid, count=20):
    return _get(
        REGIONAL_BASE,
        "/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}",
        puuid=puuid,
        count=count
    )

def get_match(match_id):
    return _get(
        REGIONAL_BASE,
        "/lol/match/v5/matches/{matchId}",
        matchId=match_id
    )