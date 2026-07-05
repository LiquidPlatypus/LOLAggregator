import pandas as pd

def process_mastery(mastery_raw, champion_id_to_name):
    df = pd.json_normalize(mastery_raw)
    df["championName"] = df["championId"].map(champion_id_to_name)
    df["lastPlayTime"] = pd.to_datetime(df["lastPlayTime"], unit="ms").dt.strftime("%d-%m-%Y %H:%M:%S")
    df.drop(columns=["championId", "puuid"], inplace=True)

    # Mettre championName en première colonne
    cols = ["championName"] + [c for c in df.columns if c != "championName"]
    return df[cols]

def process_matches(matches_raw):
    return pd.json_normalize(matches_raw)