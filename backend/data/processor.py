import pandas as pd

def process_mastery(mastery_raw, champion_id_to_name):
    df = pd.json_normalize(mastery_raw)
    df["championName"] = df["championId"].map(lambda x: champion_id_to_name.get(x, {}).get("name", "Unknown"))
    df["championIdString"] = df["championId"].map(lambda x: champion_id_to_name.get(x, {}).get("id", "Unknown"))
    df = df.fillna(0)
    df["lastPlayTime"] = pd.to_datetime(df["lastPlayTime"], unit="ms").dt.strftime("%d-%m-%Y %H:%M:%S")
    df.drop(columns=["puuid"], inplace=True)

    # Mettre championName en première colonne
    cols = ["championName"] + [c for c in df.columns if c != "championName"]
    return df[cols]

def get_top_champs(df_mastery, nb_to_show = 5):
    return df_mastery.nlargest(nb_to_show, "championPoints")

def process_matches(matches_raw, puuid):
    matches_with_participant = []

    for match in matches_raw:
        participant = next(
            (p for p in match["info"]["participants"] if p["puuid"] == puuid),
            None
        )
        matches_with_participant.append({
            "match": match,
            "participant": participant
        })

    df = pd.json_normalize(matches_with_participant)

    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    other_cols = df.select_dtypes(exclude="number").columns
    df[other_cols] = df[other_cols].fillna("")

    return df
