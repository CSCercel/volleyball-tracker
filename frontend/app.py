import streamlit as st

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

st.info("💡 Make sure your FastAPI backend is running on http://localhost:8000")
