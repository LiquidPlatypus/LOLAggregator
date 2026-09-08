from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Any
from .connection import Base


class User(Base):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    puuid: Mapped[str] = mapped_column(String(100), unique=True)
    game_name: Mapped[str] = mapped_column(String(100))
    tag_line: Mapped[str] = mapped_column(String(10))


class Summoner(Base):
    __tablename__ = "Summoner"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("User.id"))
    summoner_level: Mapped[int] = mapped_column(Integer)
    profile_icon_id: Mapped[int] = mapped_column(Integer)


class ChampionMastery(Base):
    __tablename__ = "ChampionMastery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("User.id"))
    champion_id: Mapped[int] = mapped_column(Integer, ForeignKey("Champion.id"))
    champion_points: Mapped[int] = mapped_column(Integer)
    champion_level: Mapped[int] = mapped_column(Integer)


class Champion(Base):
    __tablename__ = "Champion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name : Mapped[str] = mapped_column(String(100))
    normalized_name : Mapped[str] = mapped_column(String(100))


class Item(Base):
    __tablename__ = "Item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    plaintext: Mapped[str] = mapped_column(Text)
    gold: Mapped[int] = mapped_column(Integer)
    tags: Mapped[list[str]] = mapped_column(JSON)
    stats: Mapped[dict[str, Any]] = mapped_column(JSON)


class Match(Base):
    __tablename__ = "Match"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(Integer, unique=True)
    match_id: Mapped[str] = mapped_column(String(50), unique=True)
    game_duration: Mapped[int] = mapped_column(Integer)
    game_creation: Mapped[int] = mapped_column(Integer)


class Participation(Base):
    __tablename__ = "Participation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("User.id"))
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey("Match.id"))
    champion_name: Mapped[str] = mapped_column(String(50))
    kills: Mapped[int] = mapped_column(Integer)
    deaths: Mapped[int] = mapped_column(Integer)
    assists: Mapped[int] = mapped_column(Integer)
    win: Mapped[bool] = mapped_column()


class ParticipationItem(Base):
    __tablename__ = "Participation_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    participation_id: Mapped[int] = mapped_column(Integer, ForeignKey("Participation.id"))
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("Item.id"))