import streamlit as st

THEMES = {
    "classic": {"bg": "#f6f0e1", "ink": "#111111", "rule": "#111111", "panel": "#efe7d2",
                "card": "transparent", "accent": "#8b1a1a", "radius": "0px",
                "head": "'Playfair Display', Georgia, serif", "body": "Georgia, 'Times New Roman', serif"},
    "dark":    {"bg": "#0f1115", "ink": "#e8e8ec", "rule": "rgba(255,255,255,0.14)", "panel": "#161920",
                "card": "rgba(255,255,255,0.05)", "accent": "#7aa2ff", "radius": "12px",
                "head": "'Inter', sans-serif", "body": "'Inter', sans-serif"},
}

SHARED = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;600;800&display=swap');
.stApp { background: var(--bg); }
section[data-testid="stSidebar"] { background: var(--panel); }
.block-container { max-width: 1300px; padding-top: 1.2rem; }
.stApp, .stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3,
div[data-testid="stMarkdownContainer"] { color: var(--ink); font-family: var(--body); }
.masthead { text-align: center; font-family: var(--head); font-weight: 900; font-size: 3.4rem;
            letter-spacing: .02em; border-top: 4px double var(--rule); padding-top: 8px; line-height: 1.1; }
.dateline { text-align: center; font-size: .85rem; text-transform: uppercase; letter-spacing: .1em;
            border-top: 1px solid var(--rule); border-bottom: 4px double var(--rule);
            padding: 6px 0; margin-bottom: 14px; }
.section-head { font-family: var(--head); text-transform: uppercase; letter-spacing: .14em; font-size: .8rem;
                font-weight: 700; border-top: 2px solid var(--rule); border-bottom: 1px solid var(--rule);
                padding: 4px 0; margin: 14px 0 8px; }
.card { background: var(--card); border-bottom: 1px solid var(--rule); border-radius: var(--radius);
        padding: 8px 10px 6px; margin-bottom: 4px; }
.lead-title { font-family: var(--head); font-weight: 900; font-size: 2.4rem; line-height: 1.08; }
.art-title  { font-family: var(--head); font-weight: 700; font-size: 1.15rem; line-height: 1.2; }
.lead-title a, .art-title a { color: inherit; text-decoration: none; }
.lead-title a:hover, .art-title a:hover { text-decoration: underline; }
.meta { font-size: .72rem; text-transform: uppercase; letter-spacing: .06em; opacity: .65; margin: 4px 0; }
.lead-sum { font-size: 1.1rem; line-height: 1.5; margin: 6px 0; }
.art-sum  { font-size: .92rem; line-height: 1.45; margin: 4px 0; }
.why { font-size: .75rem; font-style: italic; color: var(--accent); }
"""

def apply(theme):
    v = THEMES.get(theme, THEMES["classic"])
    vars_css = ";".join(f"--{k}:{val}" for k, val in v.items())
    st.markdown(f"<style>:root{{{vars_css}}}{SHARED}</style>", unsafe_allow_html=True)