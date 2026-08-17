import streamlit as st
from backend.api.riot import get_player, get_match_history, get_match
from backend.data.processor import process_matches
from backend.components.match_card import match_card

if "summoner" not in st.session_state:
    st.warning("Recherchez un jouer dans la barre latérale")
    st.stop()

@st.cache_data
def load_matches(summoner, tag, count=20):
    player = get_player(summoner, tag)
    match_ids = get_match_history(player["puuid"], count =count)
    matches_raw = [get_match(mid) for mid in match_ids]
    return player, process_matches(matches_raw)

player, df_matches = load_matches(
    st.session_state["summoner"],
    st.session_state["tag"],
)

st.title("Historique des matchs")

for _, row in df_matches.iterrows():
    match_card(row)