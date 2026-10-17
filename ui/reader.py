import html
from datetime import datetime
import streamlit as st
from core import edition
from core.db import get_user_feedback
from core.broadcast import get_or_create_broadcast, ask_editor
from export.pdf import build_pdf
from ui.components import article_card, ghost_id, _clean_html
from ui import insights, sidebar


# ----------------------------------------------------------------------------
# Section rendering
# ----------------------------------------------------------------------------
def _section(name, ids, arts, layout, uid, fb, hidden):
    ids = [i for i in ids if i in arts and i not in hidden]
    if not ids:
        return

    is_bubble = "bubble" in name.lower() or "outside" in name.lower()
    bubble_class = " section-head-bubble" if is_bubble else ""
    bubble_icon = "🔭 " if is_bubble else ""
    count_label = f'{len(ids)} {"story" if len(ids) == 1 else "stories"}'

    head_html = f"""
    <div class="section-head{bubble_class}">
    <span>{bubble_icon}{name.upper()}</span>
    <span class="section-count">{count_label}</span>
    </div>
    """
    st.markdown(_clean_html(head_html), unsafe_allow_html=True)

    if is_bubble:
        seal_html = """
        <div class="bubble-seal-banner">
        <div class="bubble-seal-icon">🪶</div>
        <div>
        <div class="bubble-seal-title">★ The Serendipity Wire · Perspective Broadener ★</div>
        <div class="bubble-seal-desc">
        Hand-selected high-rigor journalism purposefully chosen outside your customary reading circle to disrupt algorithmic echo chambers.
        </div>
        </div>
        </div>
        """
        st.markdown(_clean_html(seal_html), unsafe_allow_html=True)

    for i in ids:
        article_card(
            arts[i], uid,
            layout.get("why", {}).get(str(i), ""),
            fb=fb.get(i),
            prefix=f"{name}_",
        )


# ----------------------------------------------------------------------------
# Skeleton loader
# ----------------------------------------------------------------------------
def _skeleton(day=None):
    nice_date = datetime.strptime(day, "%Y-%m-%d").strftime("%A, %B %d, %Y") if day else "Today's Edition"
    block = (
        '<div class="sk sk-title"></div>'
        '<div class="sk sk-line"></div>'
        '<div class="sk sk-line"></div>'
        '<div class="sk sk-line" style="width:70%"></div>'
    )
    skel_html = f"""
    <div class="masthead-wrap">
    <div class="motto">★ THE PERSONALIZED MORNING PAPER · PREPARING EDITION ★</div>
    <div class="masthead">THE DAILY BREW</div>
    <div class="dateline">📅 PRINTING EDITION FOR {nice_date.upper()} · TYPESETTING BROADSHEET...</div>
    </div>
    <div class="sk sk-lead" style="height:55px;margin:18px auto 14px;"></div>
    <div class="sk-cols" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-top:14px;">
    <div>{block * 2}</div>
    <div>{block * 3}</div>
    <div>{block * 2}</div>
    </div>
    """
    return _clean_html(skel_html)


# ----------------------------------------------------------------------------
# "The Daily 3: What You Learned Today"
# ----------------------------------------------------------------------------
def _render_daily_learnings(layout, arts):
    """Solves the problem statement directly: reader can always name three things they learned."""
    takeaways = layout.get("takeaways") or []
    if not takeaways:
        front_ids = layout.get("front", [])[:3]
        takeaways = []
        for i in front_ids:
            if i in arts:
                a = arts[i]
                sum_text = a.get("summary") or a.get("title") or ""
                first_sent = sum_text.split(". ")[0].strip()
                if first_sent and not first_sent.endswith("."):
                    first_sent += "."
                takeaways.append({
                    "id": a["id"],
                    "title": a["title"],
                    "source": a.get("source", "The Wire"),
                    "takeaway": first_sent or a["title"],
                })

    if not takeaways:
        return

    cards_html = ""
    for idx, item in enumerate(takeaways[:3], 1):
        if isinstance(item, dict):
            source = item.get("source", "Dispatch")
            takeaway_text = item.get("takeaway", "")
            title_text = item.get("title", "")
        else:
            source = "Editorial Dispatch"
            takeaway_text = str(item)
            title_text = "Key Takeaway"

        cards_html += f"""
        <div class="takeaway-card">
        <span class="takeaway-badge">[ 0{idx} · {html.escape(source)} ]</span>
        <div class="takeaway-text">{html.escape(takeaway_text)}</div>
        <div class="takeaway-source">{html.escape(title_text)}</div>
        </div>
        """

    box_html = f"""
    <div class="takeaways-box">
    <div class="takeaways-head">
    <div class="takeaways-title">❦ Today's Three Key Learnings ❦</div>
    <div class="takeaways-sub">The essential takeaways distilled from today's global wire</div>
    </div>
    <div class="takeaway-grid">
    {cards_html}
    </div>
    </div>
    """
    st.markdown(_clean_html(box_html), unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# The Morning Wireless Broadcast Player
# ----------------------------------------------------------------------------
def _render_broadcast_player(user, day, layout, arts):
    """Renders the authentic vintage Valve Radio player with audio narration and transcript."""
    nice_date = datetime.strptime(day, "%Y-%m-%d").strftime("%b %d")
    try:
        from core.broadcast import AUDIO_DIR
        audio_file = AUDIO_DIR / f"broadcast_{user['id']}_{day}.mp3"
        if not audio_file.exists():
            with st.spinner(f"📻 Tuning morning wireless broadcast for {nice_date}..."):
                audio_bytes, transcript = get_or_create_broadcast(user, day, layout, arts)
        else:
            audio_bytes, transcript = get_or_create_broadcast(user, day, layout, arts)
    except Exception as ex:
        st.warning(f"Wireless broadcast tuning notice: {ex}")
        return

    radio_header_html = """
    <div class="radio-station-box">
    <div class="radio-topbar">
    <div class="radio-station-name">
    <span>📻 THE DAILY BREW WIRELESS DESK</span>
    <span class="radio-frequency">98.4 FM</span>
    </div>
    <div class="radio-on-air">
    <span class="radio-lamp"></span>
    <span>ON AIR · 90-SEC AUDIO BRIEFING</span>
    </div>
    </div>
    <div class="radio-sub">
    Listen to your curated morning broadcast while enjoying your morning coffee or commuting. Narrated by our vintage wireless anchor.
    </div>
    </div>
    """
    st.markdown(_clean_html(radio_header_html), unsafe_allow_html=True)

    c_audio, c_down = st.columns([4, 1.3])
    with c_audio:
        st.audio(audio_bytes, format="audio/mp3")
    with c_down:
        st.download_button(
            "⬇️ Download Audio",
            data=audio_bytes,
            file_name=f"wireless-broadcast-{user['name'].lower()}-{day}.mp3",
            mime="audio/mp3",
            use_container_width=True,
            help="Download audio file for listening offline during commute",
        )

    with st.expander("📜 Read Wireless Broadcast Wire Script"):
        transcript_html = f'<div class="radio-transcript-wrap">{html.escape(transcript)}</div>'
        st.markdown(_clean_html(transcript_html), unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# The Telegraph Wire: Ask Your Morning Editor
# ----------------------------------------------------------------------------
def _render_telegraph_desk(user, layout, arts):
    """Interactive AI Editor Q&A: reader can inquire about today's edition."""
    desk_header_html = """
    <div class="telegraph-box">
    <div class="telegraph-head">
    <div class="telegraph-title">✉️ The Telegraph Desk · Inquire With Your Editor</div>
    <div class="telegraph-badge">DIRECT WIRE TO CHIEF EDITOR</div>
    </div>
    <div class="telegraph-sub">
    Have a question regarding today's developments? Send a telegraph dispatch to your personal editor for an informed briefing.
    </div>
    </div>
    """
    st.markdown(_clean_html(desk_header_html), unsafe_allow_html=True)

    suggested = [
        f"How does today's top story impact my role as {user['persona']}?",
        "Give me a 3-bullet summary of today's tech developments.",
        "What is the key takeaway from the story outside my bubble?",
    ]

    pill_choice = st.pills(
        "Suggested Inquiries",
        options=suggested,
        label_visibility="collapsed",
        key="telegraph_pill",
    )

    with st.form("telegraph_form", clear_on_submit=False):
        default_val = pill_choice if pill_choice else ""
        query = st.text_input(
            "Your Telegraph Dispatch",
            value=default_val,
            placeholder="e.g. What are the key market implications in today's paper?",
            key="telegraph_input",
        )
        submit = st.form_submit_button("Transmit Telegraph 📨")

    if submit and query.strip():
        with st.spinner("Chief Editor is reviewing today's dispatches..."):
            reply = ask_editor(user, query, layout, arts)
            st.session_state["last_editor_reply"] = {"query": query, "reply": reply}

    if st.session_state.get("last_editor_reply"):
        item = st.session_state["last_editor_reply"]
        reply_html = f"""
        <div class="telegraph-reply">
        <div class="telegraph-reply-head">❦ Telegraph Dispatch From Chief Editor · Regarding: "{html.escape(item['query'])}"</div>
        {item['reply']}
        </div>
        """
        st.markdown(_clean_html(reply_html), unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Main reader render
# ----------------------------------------------------------------------------
def render(user, day):
    is_date_change = (st.session_state.get("active_day") != day)

    # 1. Load edition behind an authentic typesetting skeleton
    ph = st.empty()
    if is_date_change:
        ph.markdown(_skeleton(day), unsafe_allow_html=True)
        import time
        time.sleep(0.35)  # Smooth transition so typeset skeleton is clearly visible

    result = edition.load(user, day)
    ph.empty()
    st.session_state["active_day"] = day

    if result is None:
        st.warning(
            "No articles fetched for today yet. "
            "Run `python scripts/run_daily.py` to populate."
        )
        return

    layout, arts = result
    uid = user["id"]
    fb = get_user_feedback(uid)

    # Ghost article stays visible one tick so it can animate out
    hidden_all = {i for i, acts in fb.items() if acts & {"skip", "dislike"}}
    g = ghost_id()
    hidden = hidden_all - ({g} if g else set())

    # 2. Edition stats
    visible_ids = [aid for aid in arts if aid not in hidden_all]
    total_articles = len(visible_ids)
    total_words = sum(len((arts[aid].get("summary") or "").split()) for aid in visible_ids)
    est_reading_time = max(3, total_words // 130)

    # 3. Sidebar: single download action
    pdf_bytes = build_pdf(user, day, layout, arts, hidden)
    st.sidebar.download_button(
        "⬇️  Download Broadsheet PDF",
        data=pdf_bytes,
        file_name=f"morning-paper-{user['name'].lower()}-{day}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    # 4. Grand BroadSheet Masthead & Dateline
    interests = user.get("interests", {})
    focus = max(interests, key=interests.get) if interests else "General"
    nice_date = datetime.strptime(day, "%Y-%m-%d").strftime("%A, %B %d, %Y")

    masthead_html = f"""
    <div class="masthead-wrap">
    <div class="motto">★ THE PERSONALIZED MORNING PAPER · CURATED FOR {user['name'].upper()} ★</div>
    <div class="masthead">THE DAILY BREW</div>
    <div class="dateline">
    <span class="dateline-part">📅 {nice_date}</span>
    <span class="dateline-part">🗞️ {focus.upper()} DESK · {user['persona'].upper()}</span>
    <span class="dateline-part">⏱️ ~{est_reading_time} MIN READ · {total_articles} DISPATCHES</span>
    </div>
    </div>
    """
    st.markdown(_clean_html(masthead_html), unsafe_allow_html=True)

    # 5. Live AI tuning strip (encouraging positive focus only)
    insights.strip(user)

    # 6. "The Daily 3: What You Learned Today" (Distilled Executive Bulletin)
    _render_daily_learnings(layout, arts)

    # 7. The Morning Wireless Broadcast Player (Audio Narration & Transcript)
    _render_broadcast_player(user, day, layout, arts)

    # 8. View Mode / Section Navigator
    order = layout.get("section_order", [])
    view_options = ["📰 Broadsheet Front Page", "☕ 3-Min Espresso Scan", "🔭 Outside Your Bubble"] + order
    selected_view = st.pills(
        "Edition Section View",
        options=view_options,
        default="📰 Broadsheet Front Page",
        label_visibility="collapsed",
    )

    # 9. Render Content according to Selected View
    if selected_view == "☕ 3-Min Espresso Scan":
        _render_espresso_scan(layout, arts, uid, fb, hidden)
    elif selected_view == "🔭 Outside Your Bubble":
        _render_outside_bubble(layout, arts, uid, fb, hidden)
    elif selected_view == "📰 Broadsheet Front Page":
        _render_broadsheet(layout, arts, uid, fb, hidden, order)
    else:
        _render_single_section(selected_view, layout, arts, uid, fb, hidden)

    # 10. The Telegraph Wire: Interactive Q&A with Editor
    st.markdown('<div class="vintage-flourish">❦ ❖ ❦</div>', unsafe_allow_html=True)
    _render_telegraph_desk(user, layout, arts)

    # 11. Sidebar footer
    sidebar.footer(user)


# ----------------------------------------------------------------------------
# Content Renderers
# ----------------------------------------------------------------------------
def _render_espresso_scan(layout, arts, uid, fb, hidden):
    """Quick 3-minute morning coffee view focusing strictly on the lead and top front stories."""
    lead = layout["lead"]
    header_html = """
    <div style="font-family:var(--head);font-size:1.1rem;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;color:var(--accent);margin:10px 0 16px;border-bottom:2px solid var(--rule);padding-bottom:6px;">
    ☕ THE 3-MINUTE ESPRESSO SCAN · TOP PRIORITIES ONLY
    </div>
    """
    st.markdown(_clean_html(header_html), unsafe_allow_html=True)

    if lead in arts and lead not in hidden:
        article_card(
            arts[lead], uid,
            layout.get("why", {}).get(str(lead), ""),
            lead=True,
            fb=fb.get(lead),
            prefix="espresso_lead_",
        )

    front_ids = [i for i in layout.get("front", []) if i != lead and i not in hidden][:3]
    c1, c2 = st.columns(2, gap="medium")
    for idx, aid in enumerate(front_ids):
        col = c1 if idx % 2 == 0 else c2
        with col:
            article_card(
                arts[aid], uid,
                layout.get("why", {}).get(str(aid), ""),
                fb=fb.get(aid),
                prefix=f"espresso_front_{idx}_",
            )


def _render_outside_bubble(layout, arts, uid, fb, hidden):
    """Dedicated perspective-broadening view."""
    explore_ids = layout.get("sections", {}).get("Outside Your Bubble", [])
    _section("Outside Your Bubble", explore_ids, arts, layout, uid, fb, hidden)


def _render_single_section(view, layout, arts, uid, fb, hidden):
    if view in layout.get("sections", {}):
        _section(view, layout["sections"][view], arts, layout, uid, fb, hidden)


def _render_broadsheet(layout, arts, uid, fb, hidden, order):
    """Harmonious, uncluttered 3-column vintage newspaper broadsheet layout."""
    # 1. Hero Lead Article across center or top
    lead = layout["lead"]
    if lead in arts and lead not in hidden:
        article_card(
            arts[lead], uid,
            layout.get("why", {}).get(str(lead), ""),
            lead=True,
            fb=fb.get(lead),
            prefix="lead_hero_",
        )

    # 2. Balanced 3-column newspaper grid
    left, center, right = st.columns([1, 1, 1], gap="large")

    # Distribute front page stories and categorical sections
    front_others = [i for i in layout.get("front", []) if i != lead and i not in hidden]

    with left:
        _section("Front Page Wire", front_others[:3], arts, layout, uid, fb, hidden)
        if order:
            _section(order[0], layout["sections"].get(order[0], []), arts, layout, uid, fb, hidden)

    with center:
        if len(front_others) > 3:
            _section("Front Page Continued", front_others[3:], arts, layout, uid, fb, hidden)
        if len(order) > 1:
            _section(order[1], layout["sections"].get(order[1], []), arts, layout, uid, fb, hidden)

    with right:
        for s in order[2:]:
            _section(s, layout["sections"].get(s, []), arts, layout, uid, fb, hidden)