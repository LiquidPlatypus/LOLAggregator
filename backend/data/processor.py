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

def process_matches(matches_raw, champion_id_to_name,  puuid):
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

    df["participant.championIdString"] = df["participant.championId"].map(lambda x: champion_id_to_name.get(x, {}).get("id", "Unknown"))

    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    other_cols = df.select_dtypes(exclude="number").columns
    df[other_cols] = df[other_cols].fillna("")

    return df


def process_champion_stats(df_matchs):
    # Grouper par championIdString et calculer les statistiques
    champion_stats = df_matchs.groupby("participant.championIdString").agg(
        total_matches=pd.NamedAgg(column="match.metadata.matchId", aggfunc="count"),
        total_wins=pd.NamedAgg(column="participant.win", aggfunc="sum"),
        total_kills=pd.NamedAgg(column="participant.kills", aggfunc="sum"),
        total_deaths=pd.NamedAgg(column="participant.deaths", aggfunc="sum"),
        total_assists=pd.NamedAgg(column="participant.assists", aggfunc="sum")
    ).reset_index()

    # Calculer le taux de victoire, KDA et autres statistiques
    champion_stats["win_rate"] = (champion_stats["total_wins"] / champion_stats["total_matches"]) * 100
    champion_stats["kda"] = (champion_stats["total_kills"] + champion_stats["total_assists"]) / champion_stats["total_deaths"].replace(0, 1)

    return champion_stats
