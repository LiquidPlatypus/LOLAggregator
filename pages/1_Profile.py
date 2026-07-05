import streamlit as st
import plotly.express as px
from api.riot import get_player, get_champion_mastery
from api.dragon import load_champions
from data.processor import process_mastery

if "summoner" not in st.session_state:
    st.warning("Recherchez un joueur dans la barre latérale")
    st.stop()

@st.cache_data
def load_profile(summoner, tag):
    player = get_player(summoner, tag)
    mastery_raw = get_champion_mastery(player["puuid"])
    champion_map = load_champions()
    df = process_mastery(mastery_raw, champion_map)
    return player, df

player, df_mastery = load_profile(
    st.session_state["summoner"],
    st.session_state["tag"],
)

st.title(f"Profil — {player['gameName']}#{player['tagLine']}")
st.dataframe(df_mastery, use_container_width=True)

top10 = df_mastery.nlargest(10, "championPoints")

fig = px.pie(
    top10,
    values="championPoints",
    names="championName",
    title="Top 10 champions par points de maîtrise"
)
st.plotly_chart(fig, use_container_width=False)