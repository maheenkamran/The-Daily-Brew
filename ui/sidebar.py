import streamlit as st
from config import TODAY
from core import edition
from core.db import list_edition_dates, update_theme, get_user_feedback
from ui.themes import THEMES

THEME_LABELS = {k: f"{v['emoji']} {v['name']}" for k, v in THEMES.items()}

def render(user):
    sb = st.sidebar
    
    # User Profile Card
    sb.markdown(
        f"""<div style="padding:10px 12px;border:1px solid var(--rule);border-radius:var(--radius);background:var(--card);margin-bottom:14px;">
            <div style="font-size:1.1rem;font-weight:800;font-family:var(--head);color:var(--ink);">👤 {user['name']}</div>
            <div style="font-size:0.75rem;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:0.06em;margin-top:2px;">{user['persona']}</div>
            <div style="font-size:0.72rem;color:var(--ink_muted);margin-top:4px;">
                Focus: {', '.join(user.get('declared', [])[:3]) if user.get('declared') else 'Broadsheet'}
            </div>
        </div>""",
        unsafe_allow_html=True
    )

    # Edition Selector
    dates = list_edition_dates(user["id"])
    if TODAY() not in dates:
        dates = [TODAY()] + dates
    day = sb.selectbox("📚 Edition Archive", dates,
                       format_func=lambda d: f"Today ({d})" if d == TODAY() else f"📅 {d}")

    # Theme Customization
    keys = list(THEMES.keys())
    # check session_state first in case changed via main-page quick picker
    current = st.session_state.get("active_theme") or user.get("theme") or "classic"
    if current not in keys:
        current = "classic"
        
    theme = sb.selectbox("🎨 Reading Theme", keys,
                         index=keys.index(current),
                         format_func=lambda k: THEME_LABELS.get(k, k),
                         help="Customize typography, palette, and reading atmosphere.")
    
    if theme != user.get("theme"):
        update_theme(user["id"], theme)
        user["theme"] = theme
        st.session_state["active_theme"] = theme
        st.rerun()
    else:
        st.session_state["active_theme"] = theme

    # Quick action buttons
    sb.markdown("---")
    c1, c2 = sb.columns(2)
    if c1.button("♻️ Rebuild", help="Regenerate today's layout with latest preferences"):
        edition.rebuild_today(user)
        st.rerun()
        
    if c2.button("👤 Switch", help="Switch reader profile"):
        st.session_state.pop("user_id", None)
        st.session_state.pop("step", None)
        st.session_state.pop("active_theme", None)
        st.query_params.clear()
        st.rerun()
        
    return day, theme