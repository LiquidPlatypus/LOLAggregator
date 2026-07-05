from api.riot import get_player, get_champion_mastery, get_match_history, get_match
from api.dragon import load_champions
from data.processor import process_mastery, process_matches
from config import REGION

SUMMONER_NAME = "Liquid Platypus"
TAG_LINE = "FEET"

# Joueur
player = get_player(SUMMONER_NAME, TAG_LINE)
puuid = player["puuid"]

# Mastery
mastery_raw = get_champion_mastery(puuid)
champion_map = load_champions()
df_mastery = process_mastery(mastery_raw, champion_map)
df_mastery.to_csv("player_mastery.csv", index=False)

# Matchs
match_ids = get_match_history(puuid)
matches_raw = [get_match(mid) for mid in match_ids]
df_matches = process_matches(matches_raw)
df_matches.to_csv("matches_history.csv", index=False)