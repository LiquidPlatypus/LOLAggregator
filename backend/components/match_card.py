import streamlit as st

def match_card(match):
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"🎮 `{match.get('metadata.matchId', 'N/A')}`")
        with col2:
            st.write(f"⏱ {match.get('info.gameDuration', 0) // 60} min")
        with col3:
            st.write(f"🗺 {match.get('info.gameMode', 'N/A')}")