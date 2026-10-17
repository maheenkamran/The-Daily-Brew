import html
from datetime import datetime
import streamlit as st
from config import TODAY
from core.db import list_edition_dates, update_theme, clear_token

THEME_LABELS = {"classic": "Classic", "dark": "Dark"}

CSS = """<style>
section[data-testid="stSidebar"] { border-right:3px double var(--rule);
  background-image:repeating-linear-gradient(0deg, transparent 0, transparent 27px, rgba(128,128,128,.09) 27px, rgba(128,128,128,.09) 28px); }
section[data-testid="stSidebar"] > div { padding-top:.6rem; }
.sb-plate { text-align:center; border-top:3px double var(--rule); border-bottom:1px solid var(--rule); padding:6px 0 5px; margin-bottom:14px; }
.sb-plate b { font-family:var(--head); font-weight:900; font-size:1.05rem; letter-spacing:.22em; }
.sb-plate span { display:block; font-size:.56rem; letter-spacing:.3em; text-transform:uppercase; opacity:.6; margin-top:2px; }
.sb-card { position:relative; border:1px solid var(--ink); background:var(--card); border-radius:var(--radius); padding:16px 12px 12px; text-align:center; box-shadow:4px 4px 0 var(--rule); }
.sb-card::before { content:"SUBSCRIBER"; position:absolute; top:-8px; left:50%; transform:translateX(-50%); background:var(--bg); padding:0 8px; font-size:.55rem; letter-spacing:.3em; font-weight:700; color:var(--accent); }
.sb-avatar { width:54px; height:54px; line-height:50px; margin:0 auto 8px; border-radius:50%; border:2px solid var(--accent); outline:1px solid var(--accent); outline-offset:3px; color:var(--accent); font-family:var(--head); font-weight:900; font-size:1.7rem; }
.sb-name { font-family:var(--head); font-weight:900; font-size:1.3rem; line-height:1.1; }
.sb-role { font-size:.66rem; text-transform:uppercase; letter-spacing:.18em; opacity:.7; margin-top:5px; }
.sb-meta { display:flex; justify-content:space-between; border-top:1px dotted var(--rule); margin-top:10px; padding-top:6px; font-size:.62rem; letter-spacing:.12em; text-transform:uppercase; opacity:.65; }
.sb-label { font-family:var(--head); font-weight:700; font-size:.7rem; text-transform:uppercase; letter-spacing:.22em; margin:20px 0 8px; display:flex; align-items:center; gap:8px; }
.sb-label::before, .sb-label::after { content:""; flex:1; border-top:1px solid var(--rule); }
.sb-label i { color:var(--accent); font-style:normal; }

/* archive list */
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] { gap:0; max-height:230px; overflow-y:auto; border-top:1px solid var(--rule); }
section[data-testid="stSidebar"] .stRadio label { width:100%; margin:0; padding:7px 10px; border-left:3px solid transparent; border-bottom:1px dotted var(--rule); cursor:pointer; transition:all .2s ease; }
section[data-testid="stSidebar"] .stRadio label > div:first-child { display:none; }
section[data-testid="stSidebar"] .stRadio label p { font-size:.88rem; color:var(--ink) !important; }
section[data-testid="stSidebar"] .stRadio label:hover { background:var(--card); padding-left:14px; }
section[data-testid="stSidebar"] .stRadio label:has(input:checked) { border-left-color:var(--accent); background:var(--card); }
section[data-testid="stSidebar"] .stRadio label:has(input:checked) p { color:var(--accent) !important; font-weight:700; }

/* theme switch (segmented control) */
section[data-testid="stSidebar"] [data-testid="stButtonGroup"] button { border-radius:0; background:transparent; border:1px solid var(--rule); font-family:var(--head); letter-spacing:.14em; text-transform:uppercase; font-size:.74rem; }
section[data-testid="stSidebar"] [data-testid="stButtonGroup"] button,
section[data-testid="stSidebar"] [data-testid="stButtonGroup"] button * { color:var(--ink) !important; }
section[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[aria-checked="true"],
section[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[aria-pressed="true"],
section[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[kind="segmented_controlActive"] { background:var(--accent) !important; border-color:var(--accent); }
section[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[aria-checked="true"] *,
section[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[aria-pressed="true"] *,
section[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[kind="segmented_controlActive"] * { color:#ffffff !important; }

/* sign out: outlined button, label always readable */
section[data-testid="stSidebar"] .stButton button { width:100%; border-radius:0; background:transparent; border:1px solid var(--ink); font-family:var(--head); letter-spacing:.2em; text-transform:uppercase; font-size:.74rem; transition:all .25s ease; }
section[data-testid="stSidebar"] .stButton button,
section[data-testid="stSidebar"] .stButton button * { color:var(--ink) !important; }
section[data-testid="stSidebar"] .stButton button:hover { background:var(--accent); border-color:var(--accent); }
section[data-testid="stSidebar"] .stButton button:hover * { color:#ffffff !important; }

/* download PDF: accent fill with white label in both themes */
section[data-testid="stSidebar"] .stDownloadButton button { width:100%; border-radius:0; background:var(--accent); border:1px solid var(--accent); font-family:var(--head); letter-spacing:.2em; text-transform:uppercase; font-size:.74rem; transition:all .25s ease; }
section[data-testid="stSidebar"] .stDownloadButton button,
section[data-testid="stSidebar"] .stDownloadButton button * { color:#ffffff !important; }
section[data-testid="stSidebar"] .stDownloadButton button:hover { filter:brightness(1.15); transform:translateY(-1px); }

.sb-foot { text-align:center; font-size:.6rem; letter-spacing:.22em; text-transform:uppercase; opacity:.5; margin-top:12px; }
</style>"""

def _label(text, mark="❦"):
    st.sidebar.markdown(f'<div class="sb-label"><i>{mark}</i>{text}<i>{mark}</i></div>',
                        unsafe_allow_html=True)

def _nice(d):
    if d == TODAY():
        return "Today's Edition"
    return datetime.strptime(d, "%Y-%m-%d").strftime("%a  ·  %b %d")

def render(user):
    sb = st.sidebar
    sb.markdown(CSS, unsafe_allow_html=True)
    sb.markdown('<div class="sb-plate"><b>THE DAILY BREW</b><span>Your personal morning paper</span></div>',
                unsafe_allow_html=True)

    since = str(user.get("created_at") or "")[:4] or "2026"
    sb.markdown(
        f'<div class="sb-card"><div class="sb-avatar">{html.escape(user["name"][:1].upper() or "R")}</div>'
        f'<div class="sb-name">{html.escape(user["name"])}</div>'
        f'<div class="sb-role">{html.escape(user["persona"] or "Reader")}</div>'
        f'<div class="sb-meta"><span>No. {user["id"]:04d}</span><span>Since {since}</span></div></div>',
        unsafe_allow_html=True)

    _label("The Archive")
    dates = list_edition_dates(user["id"])
    if TODAY() not in dates:
        dates = [TODAY()] + dates
    day = sb.radio("Edition", dates, index=0, key="archive",
                   label_visibility="collapsed", format_func=_nice)

    _label("Paper Style", "✦")
    keys = list(THEME_LABELS)
    current = user["theme"] if user["theme"] in keys else "classic"
    picked = sb.segmented_control("Theme", keys, default=current, key="theme_pick",
                                  label_visibility="collapsed", format_func=THEME_LABELS.get)
    theme = picked or current
    if theme != current:
        update_theme(user["id"], theme)

    return day, theme

def footer(user):
    """Call last in app.py so it sits under the weights and the PDF button."""
    sb = st.sidebar
    _label("Account", "✦")
    if sb.button("Sign out", key="signout"):
        clear_token(user["id"])
        for k in ("user_id", "step", "ob", "last_fb", "pending", "diff", "archive", "theme_pick"):
            st.session_state.pop(k, None)
        st.query_params.clear()
        st.rerun()
    sb.markdown('<div class="sb-foot">❦ Printed fresh every morning ❦</div>', unsafe_allow_html=True)