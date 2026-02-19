import streamlit as st
import pandas as pd
from utils import api

st.set_page_config(page_title="Leaderboard", page_icon="🏆", layout="wide")

st.title("🏆 Leaderboard")

try:
    players = api.get_players()
    
    if not players:
        st.info("No players yet!")
    else:
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            match_type = st.selectbox("Match Type", ["indoor", "beach"])
        with col2:
            season = st.number_input("Season", min_value=2020, max_value=2030, value=2025)
        
        # Build dataframe
        leaderboard_data = []
        for player in players:
            for stat in player.get('stats', []):
                if stat['match_type'] == match_type and stat['season'] == season:
                    leaderboard_data.append({
                        'Player': player['name'],
                        'Played': stat['played'],
                        'Wins': stat['wins'],
                        'Losses': stat['losses'],
                        'OTL': stat['otl'],
                        'Points': stat['points'],
                        'Win Rate': f"{stat['winrate']:.1%}"
                    })
        
        if not leaderboard_data:
            st.info(f"No stats for {match_type} in season {season}")
        else:
            df = pd.DataFrame(leaderboard_data)
            df = df.sort_values('Points', ascending=False).reset_index(drop=True)
            df.index += 1  # Start rank at 1
            
            st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load leaderboard: {e}")
