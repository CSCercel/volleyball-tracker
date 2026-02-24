import streamlit as st
import pandas as pd
from datetime import datetime
from utils import api
from utils.misc_functions import calculate_mmr, get_rank


st.set_page_config(
    page_title="Volleyball Tracker",
    page_icon="🏐",
    layout="wide"
)

st.title("🏐 Volleyball Tracker")
st.markdown("---")

st.markdown("""
### Welcome to the Volleyball Tracker!

Use the sidebar to navigate:
- **Players** - Manage your player roster
- **Matches** - Create matches and submit results
- **Leaderboard** - View stats and rankings
""")

st.markdown("---")
st.header("🏆 Leaderboard")

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
            current_year = datetime.utcnow().year
            season = st.number_input("Season", min_value=2024, max_value=current_year, value=current_year)
        
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
                        'Win Rate': f"{stat['winrate']:.1%}",
                        "Avg Points": stat['avg_points'],
                        "Efficiency": stat['efficiency']
                    })
        
        if not leaderboard_data:
            st.info(f"No stats for {match_type} in season {season}")
        else:
            df = pd.DataFrame(leaderboard_data)
            df['MMR'] = df.apply(lambda row: calculate_mmr(row['Avg Points'], row['Efficiency']), axis=1)
            df['Rank'] = df.apply(lambda row: get_rank(row['MMR'], row['Played']), axis=1)
            df = df.sort_values('MMR', ascending=False).reset_index(drop=True)
            df.index += 1  # Start rank at 1
            
            st.dataframe(df, use_container_width=True, 
                         column_config={"Avg Points": None, "Efficiency" : None, "MMR": None}
            )

except Exception as e:
    st.error(f"Failed to load leaderboard: {e}")
