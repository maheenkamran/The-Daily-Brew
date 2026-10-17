import html
import json
import time
import streamlit as st
from core import learn
from core.db import log_feedback, get_deltas, get_user_feedback
from core.broadcast import get_story_audio

WINDOW = 6   # seconds a reaction stays on screen


def _clean_html(s: str) -> str:
    """Strips all leading/trailing whitespace from every line so Markdown NEVER interprets it as an indented code block."""
    return "\n".join(line.strip() for line in s.strip().splitlines() if line.strip())


def _recent():
    last = st.session_state.get("last_fb")
    return last if last and time.time() - last["ts"] < WINDOW else None


def ghost_id():
    """The article that was just disliked/skipped (kept on screen briefly so it can animate out)."""
    last = _recent()
    if last and last["active"] and last["action"] in ("dislike", "skip"):
        return last["aid"]
    return None


def _fb(uid, aid, action, topics=None):
    before = get_deltas(uid)
    log_feedback(uid, aid, action)
    after = learn.recompute(uid)
    active = action in get_user_feedback(uid).get(aid, set())

    changes = [(t, after.get(t, 0) - before.get(t, 0)) for t in set(before) | set(after)]
    changes = sorted([c for c in changes if abs(c[1]) >= 0.05], key=lambda x: -abs(x[1]))[:3]

    st.session_state["last_fb"] = {
        "aid": aid,
        "action": action,
        "active": active,
        "changes": changes,
        "ts": time.time(),
    }
    st.session_state["pending"] = st.session_state.get("pending", 0) + 1

    # Encouraging, friendly toast notifications (not scary math)
    top_name = topics[0].title() if (topics and isinstance(topics, list) and len(topics) > 0) else "this topic"
    if action == "like":
        if active:
            st.toast(f"☕ Noted! We will curate more stories on {top_name} in your morning paper.", icon="👍")
        else:
            st.toast("Preference reset to standard curation.", icon="↩️")
    elif action in ("dislike", "skip"):
        st.toast(f"✕ Understood. We'll show fewer stories on {top_name}.", icon="🗞️")


def _pill(last):
    names = ", ".join(t.title() for t, _ in last["changes"][:2])
    if not last["active"]:
        return "neutral", "Preference reset. Standard weighting restored."
    if last["action"] == "like":
        return "up", f"★ Preference saved! Prioritizing more {names}." if names else "★ Preference saved! Finding more stories like this."
    if last["action"] == "dislike":
        return "down", f"Understood. Showing fewer stories on {names}." if names else "Understood. Showing fewer stories like this."
    return "down", "Removed from today's edition. Adjusting future editions."


@st.dialog("📖 The Reading Room · Full Dispatch")
def show_reading_room(a: dict, uid: int, why: str, fb: set):
    """Distraction-free reading view for a single story with instant audio narration."""
    modal_header = f"""
    <div style="font-family:var(--head);font-size:1.55rem;font-weight:900;line-height:1.2;margin-bottom:8px;color:var(--ink);">
    {html.escape(a['title'])}
    </div>
    <div class="meta-row" style="margin-bottom:14px;">
    <span class="source-badge">🗞️ {html.escape(a.get('source', 'The Wire'))}</span> · 
    <span class="read-pill">📂 {html.escape(a.get('section', 'General'))}</span> · 
    <span class="topic-tag">★ Journalistic Rigor {int(float(a.get('quality_score', 0.5)) * 100)}%</span>
    </div>
    """
    st.markdown(_clean_html(modal_header), unsafe_allow_html=True)

    # Audio Narration Player
    with st.spinner("Tuning wireless audio narration..."):
        try:
            story_audio = get_story_audio(a)
            st.markdown(
                '<div style="font-family:var(--head);font-size:0.78rem;font-weight:800;letter-spacing:0.15em;text-transform:uppercase;color:var(--accent);margin:10px 0 4px;">'
                '🎧 Audio Narration (Voice Dispatch)</div>',
                unsafe_allow_html=True,
            )
            st.audio(story_audio, format="audio/mp3")
        except Exception as ex:
            st.caption(f"Audio narration currently offline: {ex}")

    summary_html = f"""
    <div style="font-family:var(--body);font-size:1.02rem;line-height:1.6;margin:16px 0;background:var(--panel);padding:14px 18px;border-radius:var(--radius);border-left:4px solid var(--accent);color:var(--ink);">
    <b>Editorial Summary:</b><br>{html.escape(a.get('summary') or 'No summary provided.')}
    </div>
    """
    st.markdown(_clean_html(summary_html), unsafe_allow_html=True)

    if why:
        why_html = f'<div class="curator-box" style="margin-bottom:14px;">❦ <b>Why this was curated for you:</b> {html.escape(why)}</div>'
        st.markdown(_clean_html(why_html), unsafe_allow_html=True)

    # Action row in modal
    topics = a.get("topics") or []
    if isinstance(topics, str):
        try:
            topics = json.loads(topics)
        except Exception:
            topics = []

    c_link, c_like, c_dis = st.columns([3, 1, 1])
    c_link.link_button("🌐 Open Original Publication ↗", a["url"], use_container_width=True)
    c_like.button(
        "👍 Prioritize",
        key=f"modal_like_{a['id']}",
        type="primary" if "like" in fb else "secondary",
        on_click=_fb,
        args=(uid, a["id"], "like", topics),
        use_container_width=True,
    )
    c_dis.button(
        "👎 Less of this",
        key=f"modal_dis_{a['id']}",
        on_click=_fb,
        args=(uid, a["id"], "dislike", topics),
        use_container_width=True,
    )


def article_card(a, uid, why="", lead=False, fb=None, prefix=""):
    fb = fb or set()
    last = _recent()
    mine = last if last and last["aid"] == a["id"] else None
    ghost = bool(mine and mine["active"] and mine["action"] in ("dislike", "skip"))

    # Word count and reading time
    summary_text = a.get("summary") or ""
    words = len(summary_text.split())
    read_mins = max(1, round(words / 45))

    topics = a.get("topics") or []
    if isinstance(topics, str):
        try:
            topics = json.loads(topics)
        except Exception:
            topics = []
    topics_html = "".join(f'<span class="topic-tag">{html.escape(t.title())}</span>' for t in topics[:3])

    card_class = "lead-card" if lead else "card"
    if ghost:
        card_class += " card-out"

    lead_badge_html = '<div class="lead-badge">★ TODAY\'S LEAD STORY · CHIEF EDITOR\'S SELECTION</div>' if lead else ''
    title_class = "lead-title" if lead else "art-title"
    sum_class = "lead-sum drop-cap" if lead else "art-sum"

    why_html = f'<div class="curator-box">❦ <b>Editor\'s Note:</b> {html.escape(why)}</div>' if why else ''
    topic_row = f'<div class="topic-tags">{topics_html}</div>' if topics_html else ''

    card_html = f"""
    <div class="{card_class}">
    {lead_badge_html}
    <div class="{title_class}">
    <a href="{html.escape(a['url'])}" target="_blank">{html.escape(a['title'])}</a>
    </div>
    <div class="meta-row">
    <span class="source-badge">🗞️ {html.escape(a.get('source', 'Wire'))}</span> · 
    <span class="read-pill">⏱️ ~{read_mins} MIN READ</span> · 
    <span class="read-pill">📂 {html.escape(a.get('section', 'Briefs'))}</span>
    </div>
    <div class="{sum_class}">{html.escape(summary_text)}</div>
    {why_html}
    {topic_row}
    </div>
    """
    st.markdown(_clean_html(card_html), unsafe_allow_html=True)

    if mine:
        kind, text = _pill(mine)
        st.markdown(_clean_html(f'<div class="pill {kind}">{html.escape(text)}</div>'), unsafe_allow_html=True)

    if ghost:
        return  # card animating out

    # Sleek compact action ribbon
    aid = a["id"]
    c1, c2, c3, c_read = st.columns([1, 1, 1, 2.2], gap="small")

    c1.button(
        "👍",
        key=f"{prefix}like{aid}",
        help="Prioritize more stories like this",
        type="primary" if "like" in fb else "secondary",
        on_click=_fb,
        args=(uid, aid, "like", topics),
        use_container_width=True,
    )
    c2.button(
        "👎",
        key=f"{prefix}dis{aid}",
        help="Deprioritize stories like this",
        on_click=_fb,
        args=(uid, aid, "dislike", topics),
        use_container_width=True,
    )
    c3.button(
        "✕",
        key=f"{prefix}skip{aid}",
        help="Hide this story from today's paper",
        on_click=_fb,
        args=(uid, aid, "skip", topics),
        use_container_width=True,
    )

    if c_read.button("📖 Read", key=f"{prefix}open{aid}", help="Open distraction-free reading room with audio narration", use_container_width=True):
        show_reading_room(a, uid, why, fb)