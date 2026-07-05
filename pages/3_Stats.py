import streamlit as st
import plotly.express as px
from api.riot import get_player, get_match_history, get_match
from data.processor import process_matches

if "summoner" not in st.session_state:
    st.warning("Recherchez un jouer dans la barre latérale")
    st.stop()

@st.cache_data
def load_stats(summoner, tag):
    player = get_player(summoner, tag)
    match_ids = get_match_history(player["puuid"])
    matches_raw = [get_match(mid) for mid in match_ids]
    return process_matches(matches_raw)

df = load_stats(st.session_state["summoner"], st.session_state["tag"])

st.title("Statistiques")

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(df, x="info.gameDuration", title="Durée des parties")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(df, x="info.gameMode", title="Modes de jeu")
    st.plotly_chart(fig, use_container_width=True)