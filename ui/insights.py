import html, time
import streamlit as st

WINDOW = 6

def _changes():
    last = st.session_state.get("last_fb")
    if last and time.time() - last["ts"] < WINDOW:
        return {t.lower(): d for t, d in last["changes"]}
    return {}

def _pct(w):
    return max(0.0, min(abs(w) / 3, 1.0)) * 100

def _top(user, n):
    return sorted(user["interests"].items(), key=lambda x: -abs(x[1]))[:n]

def render(user):
    """Sidebar: live weight bars. Changed topics slide, glow, and show a floating delta."""
    chg = _changes()
    rows = ""
    for t, w in _top(user, 8):
        d = chg.get(t.lower(), 0)
        frm, to = _pct(w - d), _pct(w)
        tag = (f'<span class="delta {"up" if d > 0 else "down"}">'
               f'{"▲" if d > 0 else "▼"} {d:+.1f}</span>') if d else ""
        rows += (f'<div class="wrow{" bump" if d else ""}">'
                 f'<div class="wlabel"><span>{html.escape(t.title())}</span><b>{w:.1f}{tag}</b></div>'
                 f'<div class="wtrack"><div class="wfill{" neg" if w < 0 else ""}" '
                 f'style="--from:{frm:.0f}%;--to:{to:.0f}%"></div></div></div>')
    if not rows:
        rows = '<div class="meta">Like or hide a few stories to start tuning.</div>'
    st.sidebar.markdown(
        '<div class="live-title"><span class="dot"></span>Your Active Personalization Weights</div>' + rows,
        unsafe_allow_html=True)

def strip(user):
    """Main page: chips for the top topics. Changed ones flash with their delta."""
    chg = _changes()
    chips = ""
    for t, w in _top(user, 6):
        d = chg.get(t.lower(), 0)
        arrow = f' {"▲" if d > 0 else "▼"} {d:+.1f}' if d else ""
        chips += (f'<span class="chip{" bump" if d else ""}{" neg" if w < 0 else ""}">'
                  f'{html.escape(t.title())} · {w:.1f}{arrow}</span>')
    if chips:
        st.markdown('<div class="strip"><span class="live-title" style="margin:0 8px 0 0">'
                    '<span class="dot"></span>AI tuning</span>' + chips + '</div>',
                    unsafe_allow_html=True)