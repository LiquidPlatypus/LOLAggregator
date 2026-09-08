from .connection import Base, engine
from .models import User, Summoner, ChampionMastery, Champion, Item, Match, Participation, ParticipationItem

Base.metadata.create_all(engine)