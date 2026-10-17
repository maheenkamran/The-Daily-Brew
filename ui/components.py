import html
import streamlit as st
from core.db import log_feedback

def _fb(uid, aid, action):
    log_feedback(uid, aid, action)

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