import streamlit as st
from utils import api

st.set_page_config(page_title="Players", page_icon="👥", layout="wide")

st.title("👥 Players")

tab1, tab2 = st.tabs(["Player Profile", "Add Player"])

with tab1:
    st.subheader("Show Player Stats")
    
    roster = api.get_players()
    name_list = [p["name"] for p in roster]
    option = st.selectbox("Player", name_list)

    if option:
        player = api.get_player(option)
        
        # Get seasons played in
        player_seasons = [s["season"] for s in player["stats"]]
        season = st.selectbox("Season", set(player_seasons))

        # Get current stats
        try:
            indoor_stats = next((item for item in player["stats"] 
                if item["match_type"] == "indoor" and item["season"] == season))
        except:
            indoor_stats = "No matches played yet!"

        try:
            beach_stats = next((item for item in player["stats"] 
                if item["match_type"] == "beach" and item["season"] == season))
        except:
            beach_stats = "No matches played yet!"

        # Get previous stats
        try:
            previous_indoor_stats = next((item for item in player["stats"] 
                if item["match_type"] == "indoor" and item["season"] == season - 1))
        except:
            previous_indoor_stats = None

        try:
            previous_beach_stats = next((item for item in player["stats"] 
                if item["match_type"] == "beach" and item["season"] == season - 1))
        except:
            previous_beach_stats = None

        indoor_col, beach_col = st.columns(2, border=True)
    
        with indoor_col:
            st.subheader("Indoor Statistics")
            if type(indoor_stats) != str:
                # Check if previous stats
                col1, col2, col3 = st.columns(3)

                with col1:
                    played = indoor_stats['played']
                    previous_played = previous_indoor_stats['played'] if previous_indoor_stats else None
                    delta_played = played - previous_played if previous_played else None

                    st.metric("Matches Played", played, delta=delta_played)
                    st.metric("Current Win Streak", indoor_stats['streak'])

                with col2:
                    winrate = round(indoor_stats['winrate'], 2) * 100
                    previous_winrate = previous_indoor_stats['winrate'] * 100 if previous_indoor_stats else None
                    delta_winrate = round(winrate - previous_winrate, 2) if previous_winrate else None

                    st.metric("Win Rate", f"{winrate}%", delta=delta_winrate)
                    st.metric("Highest Win Streak \U0001F525", indoor_stats['longest_streak'])
                with col3:
                    points = indoor_stats['points']
                    previous_points = previous_indoor_stats['points'] if previous_indoor_stats else None
                    delta_points = points - previous_points if previous_points else None

                    st.metric("Points", points, delta=delta_points)
            else:
                st.markdown(indoor_stats)

        with beach_col:
            st.subheader("Beach Statistics")
            if type(beach_stats) != str:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Matches Played", beach_stats['wins'])
                    st.metric("Current Win Streak", beach_stats['streak'])
                with col2:
                    st.metric("Win Rate", f"{round(beach_stats['winrate'] * 100, 2)}%")
                    st.metric("Highest Win Streak \U0001F525", beach_stats['longest_streak'])
                with col3:
                    st.metric("Points", beach_stats['points'])
            else:
                st.markdown(beach_stats)


with tab2:
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
