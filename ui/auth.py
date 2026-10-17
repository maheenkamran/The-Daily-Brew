import re
from datetime import date
import streamlit as st
from core.db import register, login, issue_token
from ui import themes

CSS = """<style>
[data-testid="stSidebar"], [data-testid="collapsedControl"], header[data-testid="stHeader"] { display:none; }
.block-container { max-width: 1050px; padding-top: 1.6rem; }
@keyframes rise { from{opacity:0; transform:translateY(12px)} to{opacity:1; transform:none} }
.auth-wrap { animation: rise .7s ease both; }
.auth-bar { display:flex; justify-content:space-between; font-size:.7rem; text-transform:uppercase; letter-spacing:.16em; opacity:.7; padding-bottom:6px; }
.auth-mast { text-align:center; font-family:var(--head); font-weight:900; font-size:clamp(2.6rem,7vw,5rem); letter-spacing:.03em; line-height:1.05; border-top:5px double var(--rule); padding-top:12px; }
.auth-sub { text-align:center; font-size:.78rem; text-transform:uppercase; letter-spacing:.18em; border-top:1px solid var(--rule); border-bottom:5px double var(--rule); padding:7px 0; margin-bottom:22px; }
.orn { text-align:center; color:var(--accent); font-size:1.1rem; letter-spacing:.6em; margin:4px 0 12px; }
.tz-head { font-family:var(--head); text-transform:uppercase; letter-spacing:.2em; font-size:.8rem; font-weight:700; border-bottom:1px solid var(--rule); padding-bottom:5px; margin-bottom:6px; }
.tz { padding:12px 0; border-bottom:1px solid var(--rule); }
.tz-t { font-family:var(--head); font-weight:900; font-size:1.45rem; line-height:1.15; }
.tz-t::first-letter { color:var(--accent); }
.tz-d { font-size:.92rem; line-height:1.5; opacity:.8; margin-top:4px; }
.tz-k { font-size:.68rem; text-transform:uppercase; letter-spacing:.14em; color:var(--accent); font-weight:700; }
.quote { font-family:var(--head); font-style:italic; font-size:1.05rem; text-align:center; margin-top:16px; opacity:.85; }
.card-title { font-family:var(--head); font-weight:900; font-size:1.5rem; text-align:center; margin:2px 0 0; }
.card-sub { text-align:center; font-size:.82rem; font-style:italic; opacity:.7; margin-bottom:8px; }
div[data-testid="stForm"] { border:1px solid var(--ink); border-radius:0; background:var(--panel); padding:22px 24px; box-shadow:5px 5px 0 var(--rule); }
div[data-baseweb="input"], div[data-baseweb="input"] > div { border-radius:0 !important; background:var(--bg) !important; }
div[data-baseweb="input"] { border:1px solid var(--rule) !important; }
div[data-baseweb="input"]:focus-within { border-color:var(--accent) !important; box-shadow:0 0 0 1px var(--accent); }
div[data-baseweb="input"] input { color:var(--ink) !important; font-family:var(--body); }
[data-testid="InputInstructions"] { display:none; }
.stTextInput label p { font-family:var(--head); font-size:.72rem !important; text-transform:uppercase; letter-spacing:.14em; font-weight:700; }.stFormSubmitButton button { width:100%; border-radius:0; background:var(--ink); border:1px solid var(--ink); font-family:var(--head); letter-spacing:.18em; text-transform:uppercase; padding:.55rem 0; transition:all .25s ease; }
.stFormSubmitButton button, .stFormSubmitButton button p, .stFormSubmitButton button div { color:#950606 !important; }
.stFormSubmitButton button:hover { background:var(--accent); border-color:var(--accent); transform:translateY(-1px); }
button[role="tab"] { font-family:var(--head); letter-spacing:.14em; text-transform:uppercase; font-size:.85rem; }
button[role="tab"][aria-selected="true"] { color:var(--accent); }
[data-baseweb="tab-highlight"] { background:var(--accent) !important; }
.press { border:1px dashed var(--ink); padding:9px 14px; margin-top:16px; text-align:center; font-size:.78rem; line-height:1.6; background:var(--panel); }
.press b { font-family:var(--head); letter-spacing:.14em; text-transform:uppercase; font-size:.7rem; color:var(--accent); }
.auth-foot { text-align:center; font-size:.72rem; opacity:.55; margin-top:22px; font-style:italic; border-top:1px solid var(--rule); padding-top:10px; }
</style>"""

TEASERS = [
    ("Personal", "Your paper, not everyone's", "Pick your interests once. Every morning's front page is ranked for you, with a note on why each story is there."),
    ("Learns", "It gets smarter as you read", "Every like, dislike and skip reshapes tomorrow's edition, with live weights you can watch change."),
    ("Delivered", "Read it, print it, or hear it", "A full web edition, a broadsheet PDF, and a two-minute audio briefing for your coffee."),
]

def _enter(uid):
    st.session_state.user_id = uid
    st.query_params["t"] = issue_token(uid)
    st.rerun()

def _teasers():
    items = "".join(
        f'<div class="tz"><div class="tz-k">{k}</div><div class="tz-t">{t}</div><div class="tz-d">{d}</div></div>'
        for k, t, d in TEASERS)
    return ('<div class="tz-head">In this edition</div>' + items +
            '<div class="quote">&ldquo;All the news that fits you.&rdquo;</div>')

def render():
    themes.apply("classic")
    st.markdown(CSS, unsafe_allow_html=True)
    today = date.today().strftime("%A, %B %d, %Y")
    st.markdown(
        '<div class="auth-wrap">'
        '<div class="auth-bar"><span>Vol. I &nbsp;·&nbsp; No. 1</span><span>Late City Edition</span></div>'
        '<div class="auth-mast">THE DAILY BREW</div>'
        f'<div class="auth-sub">{today} &nbsp;·&nbsp; Est. 2026 &nbsp;·&nbsp; Your Personal Morning Paper</div>'
        '</div>', unsafe_allow_html=True)

    left, right = st.columns([1.1, 1], gap="large")

    with left:
        st.markdown(_teasers(), unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card-title">Reader Access</div>'
                    '<div class="card-sub">Sign in, or subscribe free in seconds.</div>',
                    unsafe_allow_html=True)
        signin, signup = st.tabs(["Sign In", "Subscribe"])

        with signin:
            with st.form("signin"):
                u = st.text_input("Username", key="si_u", placeholder="your username")
                p = st.text_input("Password", type="password", key="si_p", placeholder="••••••")
                if st.form_submit_button("Open my paper"):
                    uid = login(u, p)
                    if uid:
                        _enter(uid)
                    else:
                        st.error("Wrong username or password.")

        with signup:
            with st.form("signup"):
                u = st.text_input("Choose a username", key="su_u", placeholder="letters, numbers, _")
                p = st.text_input("Password", type="password", key="su_p", placeholder="6+ characters")
                p2 = st.text_input("Confirm password", type="password", key="su_p2")
                if st.form_submit_button("Subscribe, it's free"):
                    if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", u.strip()):
                        st.error("Username: 3-20 letters, numbers or underscores.")
                    elif len(p) < 6:
                        st.error("Password needs at least 6 characters.")
                    elif p != p2:
                        st.error("Passwords don't match.")
                    else:
                        uid, err = register(u, p)
                        if err:
                            st.error(err)
                        else:
                            _enter(uid)

        st.markdown('<div class="press"><b>Press pass · demo readers</b><br>'
                    'alex &nbsp;·&nbsp; sara &nbsp;·&nbsp; drkhan &nbsp;|&nbsp; password: demo123</div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="orn">❦ ❦ ❦</div>'
                '<div class="auth-foot">Summarized and edited by Gemini &nbsp;·&nbsp; Printed fresh every morning</div>',
                unsafe_allow_html=True)