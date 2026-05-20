import streamlit as st
from utils import api

st.title("🔐 Admin Login")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit and email and password:
            try:
                result = api.login(email, password)
                st.session_state.access_token = result["access_token"]
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.success("✅ Logged in!")
                st.rerun()
            except Exception as e:
                st.error("Login failed")
else:
    st.success(f"✅ Logged in as {st.session_state.user_email}")
    if st.button("Logout"):
        for key in ["access_token", "authenticated", "user_email"]:
            st.session_state.pop(key, None)
        st.rerun()
