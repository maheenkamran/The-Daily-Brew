from datetime import datetime
import streamlit as st
from core import edition
from core.db import get_user_feedback, update_theme
from export.pdf import build_pdf
from ui.components import article_card, ghost_id
from ui.themes import THEMES
from ui import insights

def _section(name, ids, arts, layout, uid, fb, hidden):
    ids = [i for i in ids if i in arts and i not in hidden]
    if not ids:
        return
    is_bubble = "bubble" in name.lower() or "outside" in name.lower()
    bubble_class = " section-head-bubble" if is_bubble else ""
    bubble_icon = "🔭 " if is_bubble else ""
    
    st.markdown(
        f'<div class="section-head{bubble_class}">'
        f'<span>{bubble_icon}{name.upper()}</span>'
        f'<span style="font-size:0.7rem;font-weight:600;opacity:0.7;">{len(ids)} {"story" if len(ids)==1 else "stories"}</span>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    if is_bubble:
        st.markdown(
            '<div style="font-size:0.75rem;font-style:italic;color:var(--accent);margin:-4px 0 10px 2px;">'
            'Serendipitous stories beyond your normal reading circle to broaden your horizons.'
            '</div>',
            unsafe_allow_html=True
        )

    for i in ids:
        article_card(arts[i], uid, layout["why"].get(str(i), ""), fb=fb.get(i), prefix=f"{name}_")

def render(user, day):
    with st.spinner("Your editor is curating today's edition..."):
        result = edition.load(user, day)
        
    if result is None:
        st.warning("No articles fetched for today yet. Run `python scripts/run_daily.py` to populate.")
        return
        
    layout, arts = result
    uid = user["id"]
    fb = get_user_feedback(uid)

    hidden_all = {i for i, acts in fb.items() if acts & {"skip", "dislike"}}
    g = ghost_id()
    hidden = hidden_all - ({g} if g else set())   # ghost stays on screen briefly to animate out

    # Calculate edition stats
    visible_art_ids = [aid for aid in arts if aid not in hidden_all]
    total_articles = len(visible_art_ids)
    est_reading_time = max(3, sum(len((arts[aid].get("summary") or "").split()) for aid in visible_art_ids) // 130)

    # Sidebar PDF Download
    pdf_bytes = build_pdf(user, day, layout, arts, hidden)
    st.sidebar.download_button(
        "⬇️ Download PDF Edition",
        data=pdf_bytes,
        file_name=f"morning-paper-{user['name'].lower()}-{day}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    # 1. Top Quick Theme & Action Toolbar
    top_col1, top_col2 = st.columns([2.5, 3])
    with top_col1:
        st.caption(f"☕ Good morning, {user['name']} · Issue for {day}")
    with top_col2:
        # Quick theme pill selector
        active_theme = st.session_state.get("active_theme") or user.get("theme") or "classic"
        theme_names = list(THEMES.keys())
        theme_labels = {k: f"{THEMES[k]['emoji']} {THEMES[k]['name'].split()[0]}" for k in theme_names}
        
        sel_theme = st.pills(
            "Theme",
            options=theme_names,
            format_func=lambda k: theme_labels[k],
            default=active_theme if active_theme in theme_names else "classic",
            label_visibility="collapsed"
        )
        if sel_theme and sel_theme != active_theme:
            update_theme(uid, sel_theme)
            user["theme"] = sel_theme
            st.session_state["active_theme"] = sel_theme
            st.rerun()

    # 2. Grand Masthead & Dateline
    interests = user.get("interests", {})
    focus = max(interests, key=interests.get) if interests else "General"
    nice_date = datetime.strptime(day, "%Y-%m-%d").strftime("%A, %B %d, %Y")

    st.markdown(
        f"""<div class="masthead-wrap">
            <div class="motto">★ The Personalized Morning Paper · Algorithmic & AI Curated ★</div>
            <div class="masthead">THE {user['name'].upper()} CHRONICLE</div>
            <div class="dateline">
                <span class="dateline-part">📅 {nice_date}</span>
                <span class="dateline-part">🗞️ {focus.upper()} FOCUS · {user['persona'].upper()}</span>
                <span class="dateline-part">⏱️ ~{est_reading_time} MIN READ · {total_articles} STORIES</span>
            </div>
        </div>""",
        unsafe_allow_html=True
    )

    # 3. AI Tuning Strip (Live weights on main page)
    insights.strip(user)

    # 4. Morning Briefing / Editorial Pulse
    top_interests = [t.title() for t in sorted(interests, key=lambda k: -interests[k])[:3]]
    brief_focus = ", ".join(top_interests) if top_interests else "today's top headlines"
    st.markdown(
        f"""<div class="morning-brief">
            <div class="morning-brief-icon">☀️</div>
            <div class="morning-brief-content">
                <div class="morning-brief-title">Morning Editorial Dispatch</div>
                <div class="morning-brief-text">
                    Curated for your role as <b>{user['persona']}</b>. Today's blend prioritizes stories in <b>{brief_focus}</b>,
                    balanced with fresh perspectives across the global wire. Every like and skip refines tomorrow's paper.
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True
    )

    # 5. Section Filter or Broadsheet View
    order = layout.get("section_order", [])
    sections_available = ["📰 All Sections", "★ Front Page"] + order
    selected_view = st.pills(
        "Jump to section",
        options=sections_available,
        default="📰 All Sections",
        label_visibility="collapsed"
    )

    # 6. Render Newspaper Content
    if selected_view != "📰 All Sections":
        # Single Section Focus View
        if selected_view == "★ Front Page":
            lead = layout["lead"]
            if lead in arts and lead not in hidden:
                article_card(arts[lead], uid, layout["why"].get(str(lead), ""),
                             lead=True, fb=fb.get(lead), prefix="hero_lead_")
            _section("Front Page Stories", [i for i in layout["front"] if i != lead],
                     arts, layout, uid, fb, hidden)
        else:
            sec_name = selected_view
            if sec_name in layout["sections"]:
                _section(sec_name, layout["sections"][sec_name], arts, layout, uid, fb, hidden)
    else:
        # Full 3-Column Broadsheet Newspaper Layout
        left, center, right = st.columns([1, 2, 1.2], gap="large")

        with center:
            lead = layout["lead"]
            if lead in arts and lead not in hidden:
                article_card(arts[lead], uid, layout["why"].get(str(lead), ""),
                             lead=True, fb=fb.get(lead), prefix="center_lead_")
            _section("Front Page", [i for i in layout["front"] if i != lead],
                     arts, layout, uid, fb, hidden)

        with left:
            if order:
                _section(order[0], layout["sections"][order[0]], arts, layout, uid, fb, hidden)

        with right:
            for s in order[1:]:
                _section(s, layout["sections"][s], arts, layout, uid, fb, hidden)