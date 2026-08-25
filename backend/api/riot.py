import requests
from config import API_KEY, REGION, PLATFORM

HEADERS = {"X-Riot-Token": API_KEY}
REGIONAL_BASE = f"https://{REGION}.api.riotgames.com"
PLATFORM_BASE = f"https://{PLATFORM}.api.riotgames.com"

def _get(base, endpoint, **kwargs):
    url = f"{base}{endpoint.format(**kwargs)}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_player(game_name, tag_line):
    return _get(
        REGIONAL_BASE,
        "/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}",
        gameName=game_name,
        tagLine=tag_line
    )

def get_summoner(puuid):
    return _get(
        PLATFORM_BASE,
        "/lol/summoner/v4/summoners/by-puuid/{puuid}",
        puuid=puuid
    )

def get_champion_mastery(puuid):
    return _get(
        PLATFORM_BASE,
        "/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}",
        puuid=puuid
    )

def get_match_history(puuid, start=0, count=10):
    return _get(
        REGIONAL_BASE,
        "/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}",
        puuid=puuid,
        start=start,
        count=count
    )

def get_match(match_id):
    return _get(
        REGIONAL_BASE,
        "/lol/match/v5/matches/{matchId}",
        matchId=match_id
    )