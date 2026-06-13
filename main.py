import requests
import pandas as pd
import json

from utils import create_url

REGION = "europe"       # Régional
PLATFORM = "euw1"       # Plateforme
SUMMONER_NAME = "Liquid Platypus"
TAG_LINE = "FEET"

player_data = requests.get(**create_url(
    "/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}",
    region=REGION,
    gameName=SUMMONER_NAME,
    tagLine=TAG_LINE
)).json()

player_mastery = requests.get(**create_url(
    "/lol/champion-mastery/v4/champion-masteries/by-puuid/{encryptedPUUID}",
    region=PLATFORM,
    encryptedPUUID=player_data["puuid"]
)).json()

with open("dragontail-16.12.1/16.12.1/data/fr_FR/champion.json") as f:
    champions_raw = json.load(f)

champion_id_to_name = {
    int(champ["key"]): champ["name"]
    for champ in champions_raw["data"].values()
}

df = pd.json_normalize(player_mastery)
df["championName"] = df["championId"].map(champion_id_to_name)

df.drop(columns=["championId"], inplace=True)
df.drop(columns=["puuid"], inplace=True)
df = df.iloc[:, [-1] + list(range(df.shape[1] - 1))]
df.to_csv("player_mastery.csv", index=False)
