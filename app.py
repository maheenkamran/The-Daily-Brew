import streamlit as st
from core.db import init_db, get_user, list_users
from ui import onboarding, sidebar, reader, themes, insights


st.set_page_config(page_title="The Daily Brew — Personal Morning Paper", page_icon="📰", layout="wide")
init_db()

uid = st.session_state.get("user_id") or st.query_params.get("uid")
user = get_user(int(uid)) if uid else None

if not user:
    themes.apply("classic")
    existing = list_users()
    if existing:
        with st.sidebar:
            st.markdown("### 👤 Returning Readers")
            st.caption("Switch to an existing personalized profile:")
            for u in existing:
                if st.button(f"📰 {u['name']}", key=f"u{u['id']}", use_container_width=True):
                    st.session_state.user_id = u["id"]
                    st.query_params["uid"] = str(u["id"])
                    st.rerun()
    onboarding.render()
else:
    active_theme = st.session_state.get("active_theme") or user.get("theme") or "classic"
    themes.apply(active_theme)
    day, theme = sidebar.render(user)
    insights.render(user)
    reader.render(user, day)