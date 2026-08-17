import streamlit as st

st.set_page_config(
    page_title=" Lol Aggregator",
    page_icon="🦶",
    layout="wide",
)

st.title("🦶 Lol Aggregator")

# Recherche globale dans la sidebar, accessible sur toutes les pages
with st.sidebar:
    st.header("Recherche")
    summoner = st.text_input("Nom du joueur")
    tag = st.text_input("Tag")

    if st.button("Rechercher"):
        # Stocké en session pour toutes les pages
        st.session_state["summoner"] = summoner
        st.session_state["tag"] = tag

st.write("Recherchez un joueur dans la barre latérale")