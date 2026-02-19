import streamlit as st
from utils import api

st.set_page_config(page_title="Players", page_icon="👥", layout="wide")

st.title("👥 Players")

tab1, tab2, tab3 = st.tabs(["Add Player", "Edit Player", "Show Player"])

with tab1:
    # Add new player
    st.subheader("Add New Player")
    with st.form("add_player"):
        player_name = st.text_input("Player Name")
        submit = st.form_submit_button("Add Player")

        if submit and player_name:
            try:
                api.create_player(player_name)
                st.success(f"✅ Added {player_name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


with tab2:
    st.subheader("Edit Player Name")



with tab3:
    st.subheader("Show Player Stats")
    
    roster = api.get_players()
    name_list = [p["name"] for p in roster]
    option = st.selectbox("Player", name_list)

    if option:
        player = api.get_player(option)
        
        # Get seasons played in
        player_seasons = [s["season"] for s in player["stats"]]
        season = st.selectbox("Season", set(player_seasons))

        indoor_stats = next((item for item in player["stats"] 
            if item["match_type"] == "indoor" and item["season"] == season))

        beach_stats = next((item for item in player["stats"] 
            if item["match_type"] == "beach" and item["season"] == season))

        indoor_col, beach_col = st.columns(2)
    
        with indoor_col:
            st.subheader("Indoor Statistics")
            st.markdown(f"Current Win Streak: {indoor_stats['streak']}")
            st.markdown(f"Highest Win Streak \U0001F525: {indoor_stats['longest_streak']}")
            st.markdown(f"Matches Played: {indoor_stats['played']}")
            st.markdown(f"Points: {indoor_stats['points']}")
            st.markdown(f"Win Rate: {round(indoor_stats['winrate'] * 100, 2)}%")

        with beach_col:
            st.subheader("Beach Statistics")
            st.markdown(f"Current Win Streak: {beach_stats['streak']}")
            st.markdown(f"Highest Win Streak \U0001F525: {beach_stats['longest_streak']}")
            st.markdown(f"Matches Played: {beach_stats['played']}")
            st.markdown(f"Points: {beach_stats['points']}")
            st.markdown(f"Win Rate: {round(beach_stats['winrate'] * 100, 2)}%")
