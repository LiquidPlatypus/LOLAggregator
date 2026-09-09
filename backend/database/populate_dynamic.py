from .connection import Session
from .models import User, Summoner, Champion, ChampionMastery, Match, Participation
from api.riot import get_summoner
from data.local_data import load_local_mastery, load_local_match_ids, load_local_match

session = Session()

try:
    puuid = "mrdJFW8Lvl17o5iW9498HaGiWTRONyQe47taTdtjo5iXaOemXiFFrzmrDy1A-GtzDhPDdT1JGirSxQ"

    # --- User ---
    existing_user = session.query(User).filter(User.puuid == puuid).first()

    if existing_user is None:
        user = User(
            puuid=puuid,
            game_name="Liquid Platypus",
            tag_line="FEET"
        )
        session.add(user)
        print("Sample user added to the database.")
    else:
        user = existing_user
        print("User already exists. Reusing existing entry.")

    # --- Summoner ---
    existing_summoner = session.query(Summoner).filter(Summoner.user_id == user.id).first()

    if existing_summoner is None:
        summoner_data = get_summoner(puuid)
        summoner = Summoner(
            user_id=user.id,
            profile_icon_id=summoner_data["profileIconId"],
            summoner_level=summoner_data["summonerLevel"]
        )
        session.add(summoner)
        print("Summoner added to the database.")
    else:
        print("Summoner already exists. Skipping.")

    for mastery_data in load_local_mastery(puuid):
        champion_id = mastery_data["championId"]

        # Skip si le champion n'existe pas dans la table Champion (ID fantôme type Arena)
        if session.get(Champion, champion_id) is None:
            print(f"Champion id {champion_id} not found in Champion table. Skipping.")
            continue

        existing_mastery = (session.query(ChampionMastery)
                            .filter(ChampionMastery.user_id == user.id,
                                    ChampionMastery.champion_id == champion_id).first())

        if existing_mastery is None:
            mastery = ChampionMastery(
                user_id=user.id,
                champion_id=champion_id,
                champion_level=mastery_data["championLevel"],
                champion_points=mastery_data["championPoints"]
            )
            session.add(mastery)
            print("Champion mastery added to the database.")
        else:
            mastery = existing_mastery
            print("Champion mastery already exists. Skipping.")

    for match_id in load_local_match_ids(puuid):
        match_data = load_local_match(match_id)
        existing_match = session.query(Match).filter(Match.match_id == match_id).first()

        if existing_match is None:
            match = Match(
                match_id=match_id,
                game_id=match_data["info"]["gameId"],
                game_duration=match_data["info"]["gameDuration"],
                game_creation=match_data["info"]["gameCreation"],
            )
            session.add(match)
            print(f"Match {match_id} added to the database.")
        else:
            match = existing_match
            print(f"Match {match_id} already exists. Skipping.")

        for participant in match_data["info"]["participants"]:
            if participant["puuid"] == puuid:
                break

        existing_participation = session.query(Participation).filter(
            Participation.user_id == user.id,
            Participation.match_id == match.id
        ).first()

        if existing_participation is None:
            participation = Participation(
                user_id=user.id,
                match_id=match.id,
                champion_name=participant["championName"],
                kills=participant["kills"],
                deaths=participant["deaths"],
                assists=participant["assists"],
                win=participant["win"],
            )
            session.add(participation)
            print(f"Participation for match {match_id} added to the database.")
        else:
            print(f"Participation for match {match_id} already exists. Skipping.")

    session.commit()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    session.close()