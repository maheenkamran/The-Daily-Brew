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
:root { --bad:#c0392b; --good:#2e8b57; }

/* ---- card leaving ---- */
@keyframes cardOut {
  0%   { opacity:1; max-height:700px; transform:none; }
  45%  { opacity:0; transform:translateX(-40px); }
  100% { opacity:0; max-height:0; margin:0; padding:0; border:0; transform:translateX(-40px); }
}
.card-out { animation: cardOut 1s ease forwards; overflow:hidden; }

/* ---- reaction pill ---- */
@keyframes pillLife {
  0%   { opacity:0; transform:translateY(-8px) scale(.95); }
  10%  { opacity:1; transform:none; }
  80%  { opacity:1; max-height:60px; }
  100% { opacity:0; max-height:0; margin:0; padding:0; border-width:0; transform:translateY(-4px); }
}
.pill { display:block; width:fit-content; max-width:100%; padding:5px 12px; margin:4px 0 8px;
        border-radius:999px; font-size:.8rem; font-weight:600; border:1px solid;
        animation: pillLife 4.5s ease both; animation-delay:.1s; overflow:hidden; }
.pill.up      { color:var(--good); border-color:var(--good); background:rgba(46,139,87,.12); }
.pill.down    { color:var(--bad);  border-color:var(--bad);  background:rgba(192,57,43,.12); }
.pill.neutral { color:var(--ink);  border-color:var(--rule); background:rgba(128,128,128,.12); }
.card-out + .pill { animation-delay:.6s; }   /* wait for the card to leave */

/* ---- live weights ---- */
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
.live-title { font-family:var(--head); font-weight:700; font-size:.8rem; letter-spacing:.1em;
              text-transform:uppercase; margin:6px 0 10px; }
.dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--bad);
       margin-right:6px; animation:pulse 1.4s infinite; }
.wrow { margin:8px 0; }
.wlabel { display:flex; justify-content:space-between; font-size:.8rem; margin-bottom:3px; }
.wtrack { height:9px; border-radius:6px; background:rgba(128,128,128,.25); overflow:hidden; }
.wfill { height:100%; border-radius:6px; background:var(--accent); width:var(--to);
         animation: wgrow .9s ease-out; }
.wfill.neg { background:var(--bad); }
@keyframes wgrow { from{width:var(--from)} to{width:var(--to)} }
@keyframes bump  { 0%{transform:scale(1)} 40%{transform:scale(1.2)} 100%{transform:scale(1)} }
@keyframes glow  { 0%,100%{filter:none} 40%{filter:brightness(1.5) drop-shadow(0 0 6px var(--accent))} }
@keyframes fade  { 0%{opacity:0;transform:translateY(5px)} 15%{opacity:1;transform:none}
                   80%{opacity:1} 100%{opacity:0} }
.wrow.bump .wlabel { animation: bump .8s ease; }
.wrow.bump .wfill  { animation: wgrow .9s ease-out, glow 1.4s ease; }
.delta { font-weight:700; margin-left:4px; animation: fade 4s ease both; }
.delta.up { color:var(--good); } .delta.down { color:var(--bad); }

/* ---- main-page tuning strip ---- */
@keyframes flash { 0%{background:var(--accent);color:#fff} 100%{background:transparent} }
.strip { display:flex; flex-wrap:wrap; align-items:center; gap:4px; padding:6px 0 10px;
         border-bottom:1px solid var(--rule); margin-bottom:10px; }
.chip { display:inline-block; padding:3px 11px; border:1px solid var(--rule); border-radius:999px;
        font-size:.78rem; }
.chip.neg { border-color:var(--bad); color:var(--bad); }
.chip.bump { animation: bump .8s ease, flash 1.6s ease; }

"""

def apply(theme):
    v = THEMES.get(theme, THEMES["classic"])
    vars_css = ";".join(f"--{k}:{val}" for k, val in v.items())
    st.markdown(f"<style>:root{{{vars_css}}}{SHARED}</style>", unsafe_allow_html=True)