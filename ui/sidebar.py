import streamlit as st
from config import TODAY
from core import edition
from core.db import list_edition_dates, update_theme

THEME_LABELS = {"classic": "Classic Broadsheet", "dark": "Modern Dark"}

def render(user):
    sb = st.sidebar
    sb.header(f"👤 {user['name']}")

    dates = list_edition_dates(user["id"])
    if TODAY() not in dates:
        dates = [TODAY()] + dates
    day = sb.selectbox("📚 Past editions", dates,
                       format_func=lambda d: "Today" if d == TODAY() else d)

    keys = list(THEME_LABELS)
    current = user["theme"] if user["theme"] in keys else "classic"
    theme = sb.radio("🎨 Theme", keys, index=keys.index(current),
                     format_func=THEME_LABELS.get)
    if theme != current:
        update_theme(user["id"], theme)

    if sb.button("♻️ Rebuild today's edition"):
        edition.rebuild_today(user)
        st.rerun()
        
    if sb.button("Switch reader"):
        st.session_state.pop("user_id", None)
        st.session_state.pop("step", None)
        st.query_params.clear()
        st.rerun()
    return day, theme