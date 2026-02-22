import streamlit as st
from utils import api
from datetime import date

st.set_page_config(page_title="Matches", page_icon="🏐", layout="wide")

st.title("🏐 Matches")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Create Match", "Draft Matches", "Completed Matches"])

# TAB 1: Create new match
with tab1:
    st.subheader("Create New Match")
    
    try:
        players = api.get_players()
        player_names = [p['name'] for p in players]
        
        if len(player_names) < 2:
            st.warning("⚠️ Need at least 2 players to create a match. Add players first!")
        else:
            match_type = st.selectbox("Match Type", ["indoor", "beach"])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔵 Blue Team**")
                blue_team = st.multiselect("Select Blue Team", player_names, key="blue")
            
            with col2:
                st.markdown("**🔴 Red Team**")
                # Filter out players already on blue team
                available_for_red = [p for p in player_names if p not in blue_team]
                red_team = st.multiselect("Select Red Team", available_for_red, key="red")
            
            if st.button("Create Match", type="primary"):
                if not blue_team or not red_team:
                    st.error("Both teams need at least one player!")
                else:
                    try:
                        match = api.create_match({
                            "match_type": match_type,
                            "blue_team": blue_team,
                            "red_team": red_team
                        })
                        st.success("✅ Match created!")
                        
                        blue, red = st.columns(2, border=True)

                        with blue:
                            st.subheader("Blue Team")
                            blue_players = [p["name"] for p in match["blue_team"]]

                            team_str = ""
                            for player in blue_players:
                                team_str += player + ","

                            st.markdown(team_str[:-1])
                            st.metric("Odds", match["blue_odds"])
                            st.metric("MVP", match['blue_mvp'])

                        with red:
                            st.subheader("Red Team")
                            red_players = [p["name"] for p in match["red_team"]]
                            team_str = ""
                            for player in red_players:
                                team_str += player + ","

                            st.markdown(team_str[:-1])

                            st.metric("Odds", match["red_odds"])
                            st.metric("MVP", match['red_mvp'])

                    except Exception as e:
                        st.error(f"Error: {e}")
    
    except Exception as e:
        st.error(f"Failed to load players: {e}")

# TAB 2: Draft matches
with tab2:
    st.subheader("Draft Matches (Not Played Yet)")
    
    try:
        drafts = api.get_matches(status="draft")
        
        if not drafts:
            st.info("No draft matches. Create one in the 'Create Match' tab!")
        else:
            for match in drafts:
                with st.expander(f"Match {match['id'][:8]} - {match['match_type'].upper()}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🔵 Blue Team**")
                        for player in match['blue_team']:
                            st.text(f"- {player['name']} ({player.get('points', 0)} pts)")
                    
                    with col2:
                        st.markdown("**🔴 Red Team**")
                        for player in match['red_team']:
                            st.text(f"- {player['name']} ({player.get('points', 0)} pts)")
                    
                    st.markdown("---")
                    st.markdown("**Submit Results**")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        blue_score = st.number_input("Blue Score", min_value=None, value=None, key=f"blue_{match['id']}")
                    with col_b:
                        red_score = st.number_input("Red Score", min_value=None, value=None, key=f"red_{match['id']}")
                    with col_c:
                        if st.button("Submit Results", key=f"submit_{match['id']}"):
                            try:
                                result = api.submit_match_results(match['id'], blue_score, red_score)
                                st.success("✅ Results submitted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

                        elif st.button("Delete Draft", key=f"delete_{match['id']}"):
                            try:
                                result = api.delete_match(match['id'])
                                st.success("✅ Draft deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
    
    except Exception as e:
        st.error(f"Failed to load draft matches: {e}")

# TAB 3: Completed matches
with tab3:
    st.subheader("Completed Matches")
   
    date_range = st.date_input(
        "Select range of dates",
        min_value=date(date.today().year, 1, 1),
        max_value=date(date.today().year, 12, 31),
        value=date.today()
    )

    try:
        completed = api.get_matches(status="completed")
        
        if not completed:
            st.info("No completed matches yet.")
        else:
            for match in completed:
                winner_emoji = "🔵" if match['winner'] == "blue" else "🔴"
                ot_badge = "⏱️ OT" if match['is_overtime'] else ""
                
                with st.expander(f"{winner_emoji} {match['blue_score']}-{match['red_score']} {ot_badge} - {match['match_type'].upper()}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**🔵 Blue Team - {match['blue_score']}**")
                        for player in match['blue_team']:
                            st.text(f"- {player['name']}")
                    
                    with col2:
                        st.markdown(f"**🔴 Red Team - {match['red_score']}**")
                        for player in match['red_team']:
                            st.text(f"- {player['name']}")
                    
                    st.caption(f"Played: {match['created_at']}")
    
    except Exception as e:
        st.error(f"Failed to load completed matches: {e}")
