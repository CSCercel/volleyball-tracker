import streamlit as st
from utils import api

st.set_page_config(page_title="Players", page_icon="👥", layout="wide")

st.title("👥 Players")
st.markdown("---")

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

st.markdown("---")

# Display all players
st.subheader("Current Players")
try:
    players = api.get_players()
    
    if not players:
        st.info("No players yet. Add some above!")
    else:
        # Display in columns
        cols = st.columns(3)
        for idx, player in enumerate(players):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### {player['name']}")
                    st.caption(f"ID: {player['id']}")
                    
                    # Show stats summary
                    if player.get('stats'):
                        for stat in player['stats']:
                            st.text(f"{stat['match_type']}: {stat['wins']}W-{stat['losses']}L-{stat['otl']}OTL")
                    
                    # Delete button
                    if st.button("🗑️ Delete", key=f"del_{player['id']}"):
                        try:
                            api.delete_player(player['id'])
                            st.success(f"Deleted {player['name']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

except Exception as e:
    st.error(f"Failed to load players: {e}")
