import streamlit as st
from core.db import init_db, get_user, user_by_token
from ui import auth, onboarding, sidebar, reader, themes, insights

st.set_page_config(page_title="The Daily Brew", page_icon="📰", layout="wide")
init_db()

user = None
if st.session_state.get("user_id"):
    user = get_user(st.session_state.user_id)
elif st.query_params.get("t"):
    user = user_by_token(st.query_params["t"])
    if user:
        st.session_state.user_id = user["id"]

if not user:
    auth.render()
    st.stop()

if not user["declared"] or st.session_state.get("edit_profile"):
    onboarding.render(user)
    st.stop()

day, theme = sidebar.render(user)
insights.render(user)
themes.apply(theme)
reader.render(user, day)