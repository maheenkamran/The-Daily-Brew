import streamlit as st

THEMES = {
    "classic": {
        "name": "Classic Broadsheet",
        "desc": "Vintage newsprint, double rules, crimson accent",
        "emoji": "📰",
        "bg": "#f6f0e1",
        "panel": "#ede5cf",
        "card": "#ffffff",
        "card_border": "rgba(17, 17, 17, 0.25)",
        "card_hover": "#ffffff",
        "ink": "#111111",
        "ink_muted": "#555555",
        "rule": "#111111",
        "accent": "#8b1a1a",
        "accent_bg": "rgba(139, 26, 26, 0.08)",
        "accent_border": "#8b1a1a",
        "tag_bg": "rgba(17, 17, 17, 0.06)",
        "tag_ink": "#111111",
        "radius": "2px",
        "shadow": "0 2px 8px rgba(0,0,0,0.06)",
        "head": "'Playfair Display', Georgia, serif",
        "body": "Georgia, 'Times New Roman', serif",
        "btn_bg": "#ffffff",
        "btn_ink": "#111111",
        "btn_border": "#111111",
    },
    "dark": {
        "name": "Modern Midnight",
        "desc": "Deep obsidian slate, sleek borders, electric cyan",
        "emoji": "🌙",
        "bg": "#0c0f17",
        "panel": "#141824",
        "card": "#161c2a",
        "card_border": "rgba(255, 255, 255, 0.1)",
        "card_hover": "#1d2538",
        "ink": "#f1f5f9",
        "ink_muted": "#94a3b8",
        "rule": "rgba(255, 255, 255, 0.14)",
        "accent": "#38bdf8",
        "accent_bg": "rgba(56, 189, 248, 0.12)",
        "accent_border": "#38bdf8",
        "tag_bg": "rgba(56, 189, 248, 0.12)",
        "tag_ink": "#7dd3fc",
        "radius": "10px",
        "shadow": "0 4px 18px rgba(0,0,0,0.4)",
        "head": "'Inter', -apple-system, sans-serif",
        "body": "'Inter', -apple-system, sans-serif",
        "btn_bg": "#1e2638",
        "btn_ink": "#f1f5f9",
        "btn_border": "rgba(255, 255, 255, 0.18)",
    },
    "financial": {
        "name": "Financial Salmon",
        "desc": "FT peach newsprint, deep navy ink, sharp rules",
        "emoji": "📈",
        "bg": "#fbf0e4",
        "panel": "#f2e1cf",
        "card": "rgba(255, 255, 255, 0.65)",
        "card_border": "rgba(15, 29, 46, 0.22)",
        "card_hover": "#ffffff",
        "ink": "#0f1d2e",
        "ink_muted": "#475569",
        "rule": "#0f1d2e",
        "accent": "#990000",
        "accent_bg": "rgba(153, 0, 0, 0.08)",
        "accent_border": "#990000",
        "tag_bg": "rgba(15, 29, 46, 0.08)",
        "tag_ink": "#0f1d2e",
        "radius": "0px",
        "shadow": "0 2px 6px rgba(15,29,46,0.06)",
        "head": "'Playfair Display', 'Baskerville', serif",
        "body": "Georgia, serif",
        "btn_bg": "rgba(255, 255, 255, 0.8)",
        "btn_ink": "#0f1d2e",
        "btn_border": "rgba(15, 29, 46, 0.3)",
    },
    "espresso": {
        "name": "Morning Roast",
        "desc": "Warm cream foam, espresso brown ink, amber glow",
        "emoji": "☕",
        "bg": "#fbf8f1",
        "panel": "#f1e9db",
        "card": "rgba(255, 255, 255, 0.8)",
        "card_border": "rgba(41, 30, 23, 0.16)",
        "card_hover": "#ffffff",
        "ink": "#2b1e16",
        "ink_muted": "#6b5c52",
        "rule": "#3d2a20",
        "accent": "#d97706",
        "accent_bg": "rgba(217, 119, 6, 0.12)",
        "accent_border": "#d97706",
        "tag_bg": "rgba(217, 119, 6, 0.1)",
        "tag_ink": "#b45309",
        "radius": "8px",
        "shadow": "0 3px 12px rgba(43,30,22,0.07)",
        "head": "'Lora', Georgia, serif",
        "body": "'Lora', Georgia, serif",
        "btn_bg": "rgba(255, 255, 255, 0.9)",
        "btn_ink": "#2b1e16",
        "btn_border": "rgba(41, 30, 23, 0.22)",
    },
    "nordic": {
        "name": "Nordic Minimalist",
        "desc": "Crisp alpine paper, graphite slate, emerald green",
        "emoji": "❄️",
        "bg": "#f8fafc",
        "panel": "#f1f5f9",
        "card": "#ffffff",
        "card_border": "rgba(15, 23, 42, 0.09)",
        "card_hover": "#ffffff",
        "ink": "#0f172a",
        "ink_muted": "#64748b",
        "rule": "rgba(15, 23, 42, 0.15)",
        "accent": "#059669",
        "accent_bg": "rgba(5, 150, 105, 0.09)",
        "accent_border": "#059669",
        "tag_bg": "rgba(5, 150, 105, 0.08)",
        "tag_ink": "#047857",
        "radius": "8px",
        "shadow": "0 2px 10px rgba(0,0,0,0.05)",
        "head": "'Plus Jakarta Sans', 'Inter', sans-serif",
        "body": "'Inter', -apple-system, sans-serif",
        "btn_bg": "#ffffff",
        "btn_ink": "#0f172a",
        "btn_border": "rgba(15, 23, 42, 0.16)",
    },
    "cyber": {
        "name": "Cyber Terminal",
        "desc": "Hacker matrix obsidian, phosphor green, monospace",
        "emoji": "⚡",
        "bg": "#0a0e14",
        "panel": "#0f1520",
        "card": "#111827",
        "card_border": "rgba(16, 185, 129, 0.25)",
        "card_hover": "#172236",
        "ink": "#e2e8f0",
        "ink_muted": "#94a3b8",
        "rule": "rgba(16, 185, 129, 0.3)",
        "accent": "#10b981",
        "accent_bg": "rgba(16, 185, 129, 0.12)",
        "accent_border": "#10b981",
        "tag_bg": "rgba(16, 185, 129, 0.12)",
        "tag_ink": "#34d399",
        "radius": "4px",
        "shadow": "0 0 15px rgba(16, 185, 129, 0.08)",
        "head": "'JetBrains Mono', monospace",
        "body": "'Inter', -apple-system, sans-serif",
        "btn_bg": "#151e2e",
        "btn_ink": "#34d399",
        "btn_border": "rgba(16, 185, 129, 0.3)",
    },
}

RECOMMENDED_THEMES = {
    "Software Engineer": "dark",
    "AI Researcher":     "cyber",
    "Investor":          "financial",
    "Academic":          "classic",
    "Founder":           "nordic",
    "Curious Reader":    "espresso",
    "Student":           "nordic",
}

SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,900;1,400;1,700&family=Inter:wght@300;400;500;600;700;800&family=Lora:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Plus+Jakarta+Sans:wght@500;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

/* ---- Base App Styling ---- */
.stApp {
    background: var(--bg) !important;
    color: var(--ink) !important;
    font-family: var(--body) !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

section[data-testid="stSidebar"] {
    background: var(--panel) !important;
    border-right: 1px solid var(--rule) !important;
}

div[data-testid="stSidebarContent"] {
    color: var(--ink) !important;
}

.block-container {
    max-width: 1320px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 3rem !important;
}

.stApp, .stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3,
div[data-testid="stMarkdownContainer"] {
    color: var(--ink);
    font-family: var(--body);
}

/* ---- Masthead & Header ---- */
.masthead-wrap {
    text-align: center;
    margin-bottom: 8px;
}

.motto {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.22em;
    font-weight: 700;
    color: var(--ink_muted);
    margin-bottom: 4px;
}

.masthead {
    text-align: center;
    font-family: var(--head);
    font-weight: 900;
    font-size: 3.4rem;
    letter-spacing: 0.02em;
    border-top: 4px double var(--rule);
    padding-top: 8px;
    line-height: 1.05;
    color: var(--ink);
}

.dateline {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-top: 1px solid var(--rule);
    border-bottom: 4px double var(--rule);
    padding: 6px 4px;
    margin-bottom: 14px;
    color: var(--ink);
    font-weight: 600;
}

.dateline-part {
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* ---- The Morning Pulse / Editorial Briefing ---- */
.morning-brief {
    background: var(--card);
    border: 1px solid var(--card_border);
    border-left: 4px solid var(--accent);
    border-radius: var(--radius);
    padding: 12px 18px;
    margin-bottom: 16px;
    box-shadow: var(--shadow);
    display: flex;
    align-items: flex-start;
    gap: 14px;
}

.morning-brief-icon {
    font-size: 1.5rem;
    line-height: 1;
    margin-top: 2px;
}

.morning-brief-content {
    flex: 1;
}

.morning-brief-title {
    font-family: var(--head);
    font-weight: 800;
    font-size: 0.88rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent);
    margin-bottom: 3px;
}

.morning-brief-text {
    font-size: 0.88rem;
    line-height: 1.45;
    color: var(--ink);
    margin: 0;
}

/* ---- Section Headers ---- */
.section-head {
    font-family: var(--head);
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-size: 0.82rem;
    font-weight: 800;
    border-top: 2px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    padding: 5px 2px;
    margin: 16px 0 10px;
    color: var(--ink);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.section-head-bubble {
    border-color: var(--accent);
    color: var(--accent);
}

/* ---- Article Cards ---- */
.card {
    background: var(--card);
    border: 1px solid var(--card_border);
    border-radius: var(--radius);
    padding: 14px 16px 12px;
    margin-bottom: 12px;
    box-shadow: var(--shadow);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    position: relative;
}

.card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
}

.lead-card {
    background: var(--card);
    border: 2px solid var(--accent);
    border-radius: var(--radius);
    padding: 20px 22px 16px;
    margin-bottom: 18px;
    box-shadow: var(--shadow);
    position: relative;
}

.lead-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 999px;
    background: var(--accent);
    color: #ffffff !important;
    margin-bottom: 10px;
}

.lead-title {
    font-family: var(--head);
    font-weight: 900;
    font-size: 2.2rem;
    line-height: 1.1;
    color: var(--ink);
    margin-bottom: 8px;
}

.art-title {
    font-family: var(--head);
    font-weight: 700;
    font-size: 1.15rem;
    line-height: 1.25;
    color: var(--ink);
    margin-bottom: 6px;
}

.lead-title a, .art-title a {
    color: inherit;
    text-decoration: none;
    transition: color 0.15s ease;
}

.lead-title a:hover, .art-title a:hover {
    color: var(--accent);
}

.meta-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    font-size: 0.74rem;
    color: var(--ink_muted);
    margin: 6px 0 8px;
}

.source-badge {
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--ink);
}

.read-pill {
    display: inline-flex;
    align-items: center;
    opacity: 0.85;
}

.topic-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin: 6px 0 8px;
}

.topic-tag {
    font-size: 0.68rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 999px;
    background: var(--tag_bg);
    color: var(--tag_ink);
    border: 1px solid var(--rule);
    opacity: 0.9;
}

.lead-sum {
    font-size: 1.05rem;
    line-height: 1.5;
    margin: 8px 0;
    color: var(--ink);
}

.art-sum {
    font-size: 0.92rem;
    line-height: 1.45;
    margin: 6px 0;
    color: var(--ink);
}


.curator-box, .why {
    font-size: 0.8rem;
    font-style: italic;
    color: var(--ink);
    background: var(--accent_bg);
    border-left: 3px solid var(--accent);
    padding: 6px 12px;
    margin: 8px 0 6px;
    border-radius: 0 var(--radius) var(--radius) 0;
    line-height: 1.4;
}

/* Vintage Drop Cap for Lead Article */
.drop-cap::first-letter {
    font-family: var(--head);
    font-size: 3.2rem;
    float: left;
    line-height: 0.85;
    margin-right: 8px;
    color: var(--accent);
    font-weight: 900;
}

/* ---- Vintage Radio Broadcast Player ---- */
.radio-station-box {
    background: var(--panel);
    border: 2px solid var(--accent);
    border-radius: var(--radius);
    padding: 16px 20px;
    margin-bottom: 20px;
    box-shadow: 4px 4px 0 var(--rule), var(--shadow);
    position: relative;
    overflow: hidden;
}

.radio-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px dashed var(--rule);
    padding-bottom: 8px;
    margin-bottom: 12px;
    flex-wrap: wrap;
    gap: 8px;
}

.radio-station-name {
    font-family: var(--head);
    font-size: 0.95rem;
    font-weight: 900;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--accent);
    display: flex;
    align-items: center;
    gap: 8px;
}

.radio-frequency {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    background: var(--accent_bg);
    color: var(--accent);
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid var(--accent);
}

.radio-on-air {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #c0392b;
}

.radio-lamp {
    width: 9px;
    height: 9px;
    background: #e74c3c;
    border-radius: 50%;
    box-shadow: 0 0 8px #e74c3c;
    animation: pulse 1.2s infinite;
}

.radio-sub {
    font-size: 0.84rem;
    line-height: 1.45;
    margin-bottom: 12px;
    color: var(--ink);
}

.radio-transcript-wrap {
    margin-top: 10px;
    font-size: 0.82rem;
    line-height: 1.5;
    background: var(--card);
    padding: 12px 16px;
    border-radius: var(--radius);
    border-left: 3px solid var(--accent);
    font-family: var(--body);
}

/* ---- The Daily 3 Takeaways Bulletin ---- */
.takeaways-box {
    background: var(--card);
    border: 2px solid var(--rule);
    border-radius: var(--radius);
    padding: 16px 20px;
    margin-bottom: 22px;
    box-shadow: 4px 4px 0 var(--rule);
}

.takeaways-head {
    text-align: center;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 8px;
    margin-bottom: 14px;
}

.takeaways-title {
    font-family: var(--head);
    font-size: 1.15rem;
    font-weight: 900;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 2px;
}

.takeaways-sub {
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--ink_muted);
    font-style: italic;
}

.takeaway-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 16px;
}

.takeaway-card {
    border-left: 3px solid var(--accent);
    background: var(--panel);
    padding: 10px 14px;
    border-radius: 0 var(--radius) var(--radius) 0;
    transition: transform 0.15s ease;
}

.takeaway-card:hover {
    transform: translateY(-2px);
}

.takeaway-badge {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 4px;
}

.takeaway-text {
    font-size: 0.88rem;
    font-weight: 600;
    line-height: 1.4;
    color: var(--ink);
    margin-bottom: 4px;
}

.takeaway-source {
    font-size: 0.72rem;
    color: var(--ink_muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ---- Outside Your Bubble Wax Seal ---- */
.bubble-seal-banner {
    background: var(--panel);
    border: 1px dashed var(--accent);
    border-radius: var(--radius);
    padding: 10px 14px;
    margin: 10px 0 14px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.bubble-seal-icon {
    font-size: 1.6rem;
    line-height: 1;
}

.bubble-seal-title {
    font-family: var(--head);
    font-size: 0.84rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 2px;
}

.bubble-seal-desc {
    font-size: 0.78rem;
    line-height: 1.35;
    color: var(--ink_muted);
}

/* ---- Telegraph Desk (Ask Your Editor) ---- */
.telegraph-box {
    background: var(--panel);
    border: 2px solid var(--rule);
    border-radius: var(--radius);
    padding: 18px 22px;
    margin-top: 36px;
    margin-bottom: 20px;
    box-shadow: 4px 4px 0 var(--rule);
}

.telegraph-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 8px;
    margin-bottom: 12px;
}

.telegraph-title {
    font-family: var(--head);
    font-weight: 900;
    font-size: 1.05rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--accent);
}

.telegraph-badge {
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink_muted);
    font-weight: 700;
}

.telegraph-sub {
    font-size: 0.84rem;
    line-height: 1.45;
    color: var(--ink);
    margin-bottom: 12px;
}

.telegraph-reply {
    background: var(--card);
    border: 1px solid var(--accent);
    border-left: 4px solid var(--accent);
    padding: 14px 18px;
    margin-top: 14px;
    border-radius: 0 var(--radius) var(--radius) 0;
    font-size: 0.88rem;
    line-height: 1.5;
    color: var(--ink);
}

.telegraph-reply-head {
    font-family: var(--head);
    font-size: 0.76rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 6px;
}

/* ---- Compact Article Card Action Ribbon ---- */
.card-action-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 8px;
    margin-top: 8px;
    border-top: 1px dotted var(--rule);
}

.vintage-flourish {
    text-align: center;
    color: var(--accent);
    font-size: 1.2rem;
    letter-spacing: 0.5em;
    margin: 18px 0;
    opacity: 0.85;
}

/* ---- Streamlit Widgets Overrides for Theme Consistency & High Contrast ---- */
button,
div[data-testid="stButton"] button,
button[kind="secondary"],
button[kind="primary"],
button[data-testid="baseButton-secondary"],
button[data-testid="baseButton-primary"] {
    border-radius: var(--radius) !important;
    font-family: var(--body) !important;
    font-size: 0.84rem !important;
    font-weight: 700 !important;
    transition: all 0.15s ease !important;
    background: var(--btn_bg) !important;
    color: var(--btn_ink) !important;
    border: 1px solid var(--btn_border) !important;
    box-shadow: 1px 1px 0 var(--rule) !important;
}

button *,
div[data-testid="stButton"] button *,
button[kind="secondary"] *,
button[data-testid="baseButton-secondary"] * {
    color: var(--btn_ink) !important;
    font-weight: 700 !important;
}

button:hover,
div[data-testid="stButton"] button:hover {
    border-color: var(--accent) !important;
    background: var(--accent) !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
}

button:hover *,
div[data-testid="stButton"] button:hover * {
    color: #ffffff !important;
}

/* Primary buttons (e.g. Active reactions or main CTA) */
button[kind="primary"],
button[data-testid="baseButton-primary"] {
    background: var(--accent) !important;
    color: #ffffff !important;
    border-color: var(--accent) !important;
}

button[kind="primary"] *,
button[data-testid="baseButton-primary"] * {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* Download buttons ("Download Audio", "Download Broadsheet PDF") */
div[data-testid="stDownloadButton"] > button,
div[data-testid="stDownloadButton"] button {
    background: var(--accent) !important;
    color: #ffffff !important;
    border: 1px solid var(--accent) !important;
    font-family: var(--head) !important;
    font-weight: 800 !important;
    letter-spacing: 0.08em !important;
    border-radius: var(--radius) !important;
    box-shadow: 2px 2px 0 var(--rule) !important;
    text-transform: uppercase !important;
}

div[data-testid="stDownloadButton"] > button *,
div[data-testid="stDownloadButton"] button * {
    color: #ffffff !important;
    font-weight: 800 !important;
}

div[data-testid="stDownloadButton"] > button:hover {
    filter: brightness(1.15) !important;
    transform: translateY(-1px) !important;
}

/* Link buttons ("Read Original Article") */
.stLinkButton > a,
div[data-testid="stLinkButton"] > a {
    border-radius: var(--radius) !important;
    font-family: var(--body) !important;
    font-size: 0.84rem !important;
    font-weight: 700 !important;
    background: var(--btn_bg) !important;
    color: var(--btn_ink) !important;
    border: 1px solid var(--btn_border) !important;
    transition: all 0.15s ease !important;
    box-shadow: 1px 1px 0 var(--rule) !important;
}

.stLinkButton > a *,
div[data-testid="stLinkButton"] > a * {
    color: var(--btn_ink) !important;
    font-weight: 700 !important;
}

.stLinkButton > a:hover {
    border-color: var(--accent) !important;
    background: var(--accent) !important;
    color: #ffffff !important;
}

.stLinkButton > a:hover * {
    color: #ffffff !important;
}

/* ---- Section Navigator Pills (st.pills) ---- */
div[data-testid="stSegmentedControl"],
div[data-testid="stButtonGroup"],
div[role="radiogroup"] {
    background: transparent !important;
    gap: 6px !important;
}

div[data-testid="stSegmentedControl"] button,
div[data-testid="stButtonGroup"] button,
button[data-testid="stPillsOption"],
div[role="radiogroup"] button {
    background: var(--card) !important;
    color: var(--ink) !important;
    border: 1px solid var(--rule) !important;
    border-radius: var(--radius) !important;
    font-family: var(--head) !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.05em !important;
    padding: 6px 14px !important;
    transition: all 0.15s ease !important;
    box-shadow: 1px 1px 0 var(--rule) !important;
}

div[data-testid="stSegmentedControl"] button *,
div[data-testid="stButtonGroup"] button *,
button[data-testid="stPillsOption"] *,
div[role="radiogroup"] button * {
    color: var(--ink) !important;
    font-weight: 700 !important;
}

div[data-testid="stSegmentedControl"] button:hover,
div[data-testid="stButtonGroup"] button:hover,
button[data-testid="stPillsOption"]:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

div[data-testid="stSegmentedControl"] button:hover *,
div[data-testid="stButtonGroup"] button:hover *,
button[data-testid="stPillsOption"]:hover * {
    color: var(--accent) !important;
}

/* Selected active pill */
div[data-testid="stSegmentedControl"] button[aria-checked="true"],
div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
div[data-testid="stSegmentedControl"] button[data-checked="true"],
div[data-testid="stButtonGroup"] button[aria-checked="true"],
div[data-testid="stButtonGroup"] button[aria-pressed="true"],
button[data-testid="stPillsOption"][aria-selected="true"],
button[data-testid="stPillsOption"][data-checked="true"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #ffffff !important;
}

div[data-testid="stSegmentedControl"] button[aria-checked="true"] *,
div[data-testid="stSegmentedControl"] button[aria-pressed="true"] *,
div[data-testid="stSegmentedControl"] button[data-checked="true"] *,
div[data-testid="stButtonGroup"] button[aria-checked="true"] *,
div[data-testid="stButtonGroup"] button[aria-pressed="true"] *,
button[data-testid="stPillsOption"][aria-selected="true"] *,
button[data-testid="stPillsOption"][data-checked="true"] * {
    color: #ffffff !important;
    font-weight: 800 !important;
}

/* ---- Streamlit Expander ("Read Wireless Script") ---- */
div[data-testid="stExpander"] {
    background: var(--panel) !important;
    border: 1px solid var(--rule) !important;
    border-radius: var(--radius) !important;
    margin-top: 10px !important;
    box-shadow: 2px 2px 0 var(--rule) !important;
}

div[data-testid="stExpander"] details {
    background: transparent !important;
}

div[data-testid="stExpander"] details summary {
    background: var(--card) !important;
    color: var(--ink) !important;
    font-family: var(--head) !important;
    font-weight: 800 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    font-size: 0.82rem !important;
    padding: 10px 14px !important;
    border-radius: var(--radius) !important;
}

div[data-testid="stExpander"] details summary * {
    color: var(--ink) !important;
    font-weight: 800 !important;
}

div[data-testid="stExpander"] details summary svg {
    fill: var(--accent) !important;
    stroke: var(--accent) !important;
}

div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    background: var(--panel) !important;
    color: var(--ink) !important;
    padding: 14px 16px !important;
}

div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] * {
    color: var(--ink) !important;
}

/* ---- Form inputs & text fields ---- */
div[data-testid="stTextInput"] input,
div[data-baseweb="input"] input {
    background: var(--card) !important;
    color: var(--ink) !important;
    border: 1px solid var(--rule) !important;
    border-radius: var(--radius) !important;
    font-family: var(--body) !important;
    font-size: 0.92rem !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-baseweb="input"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}

/* ---- Toast Notification Styling ---- */
div[data-testid="stToast"] {
    background: var(--panel) !important;
    color: var(--ink) !important;
    border: 2px solid var(--accent) !important;
    border-radius: var(--radius) !important;
    box-shadow: 4px 4px 0 var(--rule) !important;
    font-family: var(--body) !important;
    font-size: 0.9rem !important;
}

div[data-testid="stToast"] * {
    color: var(--ink) !important;
}

/* ---- Smooth Card Dismissal Animation ---- */
@keyframes cardSmoothOut {
    0%   { opacity: 1; transform: translateY(0) scale(1); max-height: 800px; margin-bottom: 12px; }
    40%  { opacity: 0.3; transform: translateX(-25px) scale(0.98); }
    100% { opacity: 0; transform: translateX(-60px) scale(0.92); max-height: 0; margin-bottom: 0; padding: 0; border: 0; overflow: hidden; }
}

.card-out {
    animation: cardSmoothOut 0.65s cubic-bezier(0.4, 0, 0.2, 1) forwards !important;
    overflow: hidden;
    pointer-events: none;
}

@keyframes pillLife {
    0%   { opacity: 0; transform: translateY(-8px) scale(0.95); }
    12%  { opacity: 1; transform: none; }
    82%  { opacity: 1; max-height: 60px; }
    100% { opacity: 0; max-height: 0; margin: 0; padding: 0; border-width: 0; transform: translateY(-4px); }
}
.pill {
    display: block;
    width: fit-content;
    max-width: 100%;
    padding: 5px 14px;
    margin: 6px 0 10px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid;
    animation: pillLife 4.5s ease both;
    animation-delay: 0.1s;
    overflow: hidden;
}
.pill.up {
    color: #2e8b57;
    border-color: #2e8b57;
    background: rgba(46, 139, 87, 0.12);
}
.pill.down {
    color: #c0392b;
    border-color: #c0392b;
    background: rgba(192, 57, 43, 0.12);
}
.pill.neutral {
    color: var(--ink);
    border-color: var(--rule);
    background: rgba(128, 128, 128, 0.12);
}
.card-out + .pill {
    animation-delay: 0.5s;
}

/* ---- Live Weights in Sidebar ---- */
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
.live-title {
    font-family: var(--head);
    font-weight: 700;
    font-size: 0.82rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 10px 0 10px;
    color: var(--ink);
    display: flex;
    align-items: center;
}
.dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent);
    margin-right: 7px;
    animation: pulse 1.4s infinite;
}
.wrow { margin: 8px 0; }
.wlabel {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    margin-bottom: 3px;
    color: var(--ink);
}
.wtrack {
    height: 8px;
    border-radius: 6px;
    background: rgba(128, 128, 128, 0.22);
    overflow: hidden;
}
.wfill {
    height: 100%;
    border-radius: 6px;
    background: var(--accent);
    width: var(--to);
    animation: wgrow 0.9s ease-out;
}
.wfill.neg { background: #c0392b; }
@keyframes wgrow { from { width: var(--from); } to { width: var(--to); } }
@keyframes bump  { 0% { transform: scale(1); } 40% { transform: scale(1.15); } 100% { transform: scale(1); } }
@keyframes glow  { 0%, 100% { filter: none; } 40% { filter: brightness(1.4) drop-shadow(0 0 6px var(--accent)); } }
@keyframes fade  { 0% { opacity: 0; transform: translateY(4px); } 15% { opacity: 1; transform: none; } 80% { opacity: 1; } 100% { opacity: 0; } }
.wrow.bump .wlabel { animation: bump 0.8s ease; }
.wrow.bump .wfill  { animation: wgrow 0.9s ease-out, glow 1.4s ease; }
.delta { font-weight: 700; margin-left: 4px; animation: fade 4s ease both; }
.delta.up { color: #2e8b57; }
.delta.down { color: #c0392b; }

/* ---- Main Page Tuning Strip ---- */
@keyframes flash { 0% { background: var(--accent); color: #fff; } 100% { background: var(--card); } }
.strip {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    background: var(--card);
    border: 1px solid var(--rule);
    border-radius: var(--radius);
    margin-bottom: 14px;
}
.chip {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border: 1px solid var(--rule);
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 600;
    background: var(--tag_bg);
    color: var(--ink);
}
.chip.neg {
    border-color: #c0392b;
    color: #c0392b;
}
.chip.bump {
    animation: bump 0.8s ease, flash 1.6s ease;
}

/* ---- Quick Theme Switcher Pill Row ---- */
.theme-selector-bar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 6px;
    margin-bottom: 10px;
}

.theme-pill-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 600;
    text-decoration: none;
    border: 1px solid var(--rule);
    color: var(--ink);
    background: var(--card);
    cursor: pointer;
    transition: all 0.15s ease;
}
.theme-pill-btn:hover {
    border-color: var(--accent);
    color: var(--accent);
}
.theme-pill-btn.active {
    background: var(--accent);
    color: #ffffff;
    border-color: var(--accent);
}

@keyframes shimmer { from{background-position:200% 0} to{background-position:-200% 0} }
.sk { background:linear-gradient(90deg,rgba(128,128,128,.15) 25%,rgba(128,128,128,.32) 50%,rgba(128,128,128,.15) 75%);
      background-size:200% 100%; animation:shimmer 1.4s linear infinite; border-radius:2px; }
.sk-line { height:12px; margin:9px 0; }
.sk-title { height:22px; width:90%; margin:16px 0 8px; }
.sk-lead { height:44px; width:80%; margin:14px auto 10px; }
.sk-cols { display:grid; grid-template-columns:1fr 2fr 1.2fr; gap:28px; margin-top:18px; }
.sk-status { position:relative; height:1.6em; text-align:center; margin:10px 0 4px;
             font-family:var(--head); font-style:italic; font-size:1.05rem; }
@keyframes msg { 0%{opacity:0} 6%{opacity:1} 30%{opacity:1} 36%{opacity:0} 100%{opacity:0} }
.sk-msg { position:absolute; left:0; right:0; opacity:0; animation:msg 9s infinite; }
"""

def apply(theme_name):
    """Injects the CSS variables and base stylesheet for the chosen theme."""
    v = THEMES.get(theme_name, THEMES["classic"])
    vars_css = ";".join(f"--{k}:{val}" for k, val in v.items() if isinstance(val, str))
    st.markdown(f"<style>:root{{{vars_css}}}{SHARED_CSS}</style>", unsafe_allow_html=True)