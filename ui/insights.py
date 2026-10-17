import html
import time
import streamlit as st

WINDOW = 6


def _changes():
    last = st.session_state.get("last_fb")
    if last and time.time() - last["ts"] < WINDOW:
        return {t.lower(): d for t, d in last["changes"]}
    return {}


def _top_positive(user, n=6):
    """Only return topics the reader actually prefers (positive weight), sorted by preference."""
    interests = user.get("interests", {})
    pos = [(t, w) for t, w in interests.items() if w > 0]
    return sorted(pos, key=lambda x: -x[1])[:n]


def render(user):
    """Sidebar: your reading compass. Friendly, encouraging positive preferences only."""
    chg = _changes()
    rows = ""
    for t, w in _top_positive(user, 6):
        d = chg.get(t.lower(), 0)
        # Friendly positive status label instead of intimidating numbers
        if w >= 2.0:
            status = "★ Top Focus"
        elif w >= 1.3:
            status = "Prioritized"
        else:
            status = "Following"

        boost_tag = '<span class="delta up">▲ More</span>' if d > 0 else ""
        pct = min(100, max(25, int((w / 2.8) * 100)))
        rows += (
            f'<div class="wrow{" bump" if d > 0 else ""}">'
            f'<div class="wlabel"><span>{html.escape(t.title())}</span><b>{status}{boost_tag}</b></div>'
            f'<div class="wtrack"><div class="wfill" style="--to:{pct}%;width:{pct}%"></div></div>'
            f'</div>'
        )

    if not rows:
        rows = (
            '<div class="meta" style="font-size:0.78rem;opacity:0.8;padding:6px 0;line-height:1.4;">'
            'Like articles in today\'s edition to personalize your reading compass.'
            '</div>'
        )

    st.sidebar.markdown(
        '<div class="live-title"><span class="dot"></span>Your Reading Compass</div>' + rows,
        unsafe_allow_html=True,
    )


def strip(user):
    """Main page: clean, elegant badges for topics you prefer. Never show negative/scary formulas."""
    chg = _changes()
    chips = ""
    for t, w in _top_positive(user, 5):
        d = chg.get(t.lower(), 0)
        boost = " ▲ More" if d > 0 else ""
        chips += (
            f'<span class="chip{" bump" if d > 0 else ""}">'
            f'★ {html.escape(t.title())}{boost}</span>'
        )
    if chips:
        st.markdown(
            '<div class="strip"><span class="live-title" style="margin:0 8px 0 0;font-size:0.75rem;">'
            '<span class="dot"></span>Curated For You:</span>' + chips + '</div>',
            unsafe_allow_html=True,
        )