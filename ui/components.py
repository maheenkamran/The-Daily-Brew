import html
import streamlit as st
from core.db import log_feedback
from core import learn
import html, time
import streamlit as st
from core import learn
from core.db import log_feedback, get_deltas, get_user_feedback


WINDOW = 4   # seconds a reaction stays on screen



def _fb(uid, aid, action):
    log_feedback(uid, aid, action)
    learn.recompute(uid)

def article_card(a, uid, why="", lead=False, fb=None, prefix=""):
    fb = fb or set()
    k = "lead" if lead else "art"
    st.markdown(
        f"""<div class="card">
        <div class="{k}-title"><a href="{html.escape(a['url'])}" target="_blank">{html.escape(a['title'])}</a></div>
        <div class="meta">{html.escape(a['source'])} · {html.escape(a['section'])}</div>
        <div class="{k}-sum">{html.escape(a['summary'] or '')}</div>
        <div class="why">{html.escape(why)}</div></div>""",
        unsafe_allow_html=True)

    c1, c2, c3, _ = st.columns([1, 1, 1, 3])
    aid = a["id"]
    c1.button("👍", key=f"{prefix}like{aid}", help="More like this",
              type="primary" if "like" in fb else "secondary",
              on_click=_fb, args=(uid, aid, "like"))
    c2.button("👎", key=f"{prefix}dis{aid}", help="Less like this",
              type="primary" if "dislike" in fb else "secondary",
              on_click=_fb, args=(uid, aid, "dislike"))
    c3.button("✕", key=f"{prefix}skip{aid}", help="Hide this story",
              on_click=_fb, args=(uid, aid, "skip"))
    
def _recent():
    last = st.session_state.get("last_fb")
    return last if last and time.time() - last["ts"] < WINDOW else None

def ghost_id():
    """The article that was just disliked/skipped (kept on screen briefly so it can animate out)."""
    last = _recent()
    if last and last["active"] and last["action"] in ("dislike", "skip"):
        return last["aid"]
    return None

def _fb(uid, aid, action):
    before = get_deltas(uid)
    log_feedback(uid, aid, action)
    after = learn.recompute(uid)
    active = action in get_user_feedback(uid).get(aid, set())

    changes = [(t, after.get(t, 0) - before.get(t, 0)) for t in set(before) | set(after)]
    changes = sorted([c for c in changes if abs(c[1]) >= 0.05], key=lambda x: -abs(x[1]))[:3]

    st.session_state["last_fb"] = {"aid": aid, "action": action, "active": active,
                                   "changes": changes, "ts": time.time()}
    st.session_state["pending"] = st.session_state.get("pending", 0) + 1

def _pill(last):
    names = ", ".join(t.title() for t, _ in last["changes"][:2])
    if not last["active"]:
        return "neutral", "Preference removed. Back to normal."
    if last["action"] == "like":
        return "up", "Preferences updated! " + (f"More {names} coming your way." if names
                                                 else "We'll find more like this.")
    if last["action"] == "dislike":
        return "down", "Got it. " + (f"Showing you less of {names}." if names
                                      else "Showing you less like this.")
    return "down", "Removed. We'll show fewer stories like this."

def article_card(a, uid, why="", lead=False, fb=None, prefix=""):
    fb = fb or set()
    k = "lead" if lead else "art"
    last = _recent()
    mine = last if last and last["aid"] == a["id"] else None
    ghost = bool(mine and mine["active"] and mine["action"] in ("dislike", "skip"))

    st.markdown(
        f"""<div class="card{' card-out' if ghost else ''}">
        <div class="{k}-title"><a href="{html.escape(a['url'])}" target="_blank">{html.escape(a['title'])}</a></div>
        <div class="meta">{html.escape(a['source'])} · {html.escape(a['section'])}</div>
        <div class="{k}-sum">{html.escape(a['summary'] or '')}</div>
        <div class="why">{html.escape(why)}</div></div>""",
        unsafe_allow_html=True)

    if mine:
        kind, text = _pill(mine)
        st.markdown(f'<div class="pill {kind}">{html.escape(text)}</div>', unsafe_allow_html=True)
    if ghost:
        return                      # card is leaving, so no buttons

    c1, c2, c3, _ = st.columns([1, 1, 1, 3])
    aid = a["id"]
    c1.button("👍", key=f"{prefix}like{aid}", help="More like this",
              type="primary" if "like" in fb else "secondary",
              on_click=_fb, args=(uid, aid, "like"))
    c2.button("👎", key=f"{prefix}dis{aid}", help="Less like this",
              on_click=_fb, args=(uid, aid, "dislike"))
    c3.button("✕", key=f"{prefix}skip{aid}", help="Hide this story",
              on_click=_fb, args=(uid, aid, "skip"))