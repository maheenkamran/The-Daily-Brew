import streamlit as st
from core.db import init_db, get_user, list_users
from ui import onboarding

st.set_page_config(page_title="Morning Paper", page_icon="📰", layout="wide")
init_db()

# Persistence: uid in URL or session = returning user
uid = st.session_state.get("user_id") or st.query_params.get("uid")
user = get_user(int(uid)) if uid else None

if not user:
    # optional: let returning users pick their profile
    existing = list_users()
    if existing:
        with st.sidebar:
            st.write("Returning reader?")
            for u in existing:
                if st.button(u["name"], key=f"u{u['id']}"):
                    st.session_state.user_id = u["id"]
                    st.query_params["uid"] = str(u["id"])
                    st.rerun()
    onboarding.render()
else:
    st.session_state.user_id = user["id"]
    st.title(f"The {user['name']} Chronicle")
    st.write("Interests:", user["interests"])
    st.write("Avoiding:", user["avoid_topics"])
    st.info("Reader goes here (Phase 3).")