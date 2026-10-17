import html
import re
import time
import streamlit as st
from config import PERSONAS, INTERESTS, AVOID_SUGGESTIONS
from core.db import save_profile
from ui import themes

ARCHETYPES = {
    "Founder & Builder": {
        "persona": "Founder",
        "icon": "🚀",
        "tagline": "Startups · Frontier AI · Disruption",
        "desc": "Frontier AI, venture funding, early-stage playbooks, and tech market disruption.",
        "topics": ["Tech & AI", "Startups", "Cybersecurity"],
    },
    "Venture & Markets Investor": {
        "persona": "Investor",
        "icon": "💼",
        "tagline": "Markets · VC Deals · Global Trade",
        "desc": "Macro economics, venture capital deals, public market shifts, and global trade flows.",
        "topics": ["Global Markets", "Startups", "Tech & AI"],
    },
    "AI Researcher & Scientist": {
        "persona": "AI Researcher",
        "icon": "🔬",
        "tagline": "Frontier Models · Labs · Space",
        "desc": "Frontier neural architectures, deep learning papers, scientific breakthroughs, and space.",
        "topics": ["Tech & AI", "Science", "Space"],
    },
    "Software Engineer": {
        "persona": "Software Engineer",
        "icon": "💻",
        "tagline": "Systems · Dev Tools · Security",
        "desc": "Systems architecture, developer tooling, cloud infrastructure, and cybersecurity.",
        "topics": ["Tech & AI", "Cybersecurity", "Science"],
    },
    "Global Affairs & Policy": {
        "persona": "Academic",
        "icon": "🌍",
        "tagline": "Geopolitics · Climate · Culture",
        "desc": "International affairs, climate policy, energy transition, and societal culture.",
        "topics": ["World News", "Climate", "Culture"],
    },
    "Curious Polymath": {
        "persona": "Curious Reader",
        "icon": "☕",
        "tagline": "Eclectic Blend · Science · Ideas",
        "desc": "An expansive, intellectually rich morning blend across science, tech, history, and culture.",
        "topics": ["World News", "Tech & AI", "Science", "Culture"],
    },
}

TOPIC_KEYWORDS = {
    "Tech & AI": ["tech", "ai", "llm", "neural", "machine learning", "software", "code", "coding", "agent"],
    "Global Markets": ["market", "markets", "finance", "stocks", "economy", "invest", "crypto", "banking", "macro"],
    "Startups": ["startup", "startups", "founder", "venture", "vc", "seed", "fundraising", "entrepreneur"],
    "Science": ["science", "physics", "quantum", "biology", "chemistry", "research", "lab", "breakthrough"],
    "Climate": ["climate", "energy", "green", "sustainability", "solar", "battery", "carbon", "clean tech"],
    "World News": ["world", "geopolitics", "international", "global", "diplomacy", "foreign policy", "nations"],
    "Health": ["health", "biotech", "medicine", "pharma", "clinical", "genetics", "medical"],
    "Space": ["space", "nasa", "astronomy", "spacex", "mars", "satellite", "orbit", "cosmos"],
    "Cybersecurity": ["cyber", "cybersecurity", "security", "privacy", "hacking", "infosec", "vulnerability"],
    "Culture": ["culture", "art", "philosophy", "history", "books", "literature", "society"],
}

AVOID_KEYWORDS = {
    "Celebrity Gossip": ["gossip", "celebrity", "tabloid", "hollywood", "paparazzi", "drama"],
    "Local Politics": ["politics", "local politics", "city council", "mayoral", "municipal"],
    "Sports": ["sports", "football", "basketball", "cricket", "nba", "soccer", "tennis", "championship"],
    "Crime": ["crime", "violence", "murder", "theft", "assault", "police blotter"],
    "Entertainment": ["entertainment", "movies", "tv shows", "box office", "red carpet"],
    "Elections": ["election", "elections", "campaign", "voting", "polls", "ballot"],
}

ARCHETYPE_LOOKUP = {
    "founder": "Founder & Builder",
    "founders": "Founder & Builder",
    "founding": "Founder & Builder",
    "startup": "Founder & Builder",
    "startups": "Founder & Builder",
    "builder": "Founder & Builder",
    "builders": "Founder & Builder",
    "investor": "Venture & Markets Investor",
    "investors": "Venture & Markets Investor",
    "investing": "Venture & Markets Investor",
    "finance": "Venture & Markets Investor",
    "vc": "Venture & Markets Investor",
    "vcs": "Venture & Markets Investor",
    "research": "AI Researcher & Scientist",
    "researcher": "AI Researcher & Scientist",
    "researchers": "AI Researcher & Scientist",
    "scientist": "AI Researcher & Scientist",
    "scientists": "AI Researcher & Scientist",
    "academic": "AI Researcher & Scientist",
    "academics": "AI Researcher & Scientist",
    "engineer": "Software Engineer",
    "engineers": "Software Engineer",
    "engineering": "Software Engineer",
    "developer": "Software Engineer",
    "developers": "Software Engineer",
    "coder": "Software Engineer",
    "coders": "Software Engineer",
    "programmer": "Software Engineer",
    "programmers": "Software Engineer",
    "policy": "Global Affairs & Policy",
    "diplomat": "Global Affairs & Policy",
    "scholar": "Global Affairs & Policy",
    "global": "Global Affairs & Policy",
    "world": "Global Affairs & Policy",
    "polymath": "Curious Polymath",
    "reader": "Curious Polymath",
    "student": "Curious Polymath",
    "students": "Curious Polymath",
}


def _clean_html(raw_html: str) -> str:
    return "\n".join(line.lstrip() for line in raw_html.strip().splitlines())


def parse_natural_lens(text: str):
    """Instant deterministic parser that converts free-form text into structured profile filters."""
    low = text.lower()
    matched_interests = set()
    for topic, kws in TOPIC_KEYWORDS.items():
        if any(re.search(r"\b" + re.escape(kw) + r"\b", low) for kw in kws):
            matched_interests.add(topic)

    matched_avoid = set()
    for topic, kws in AVOID_KEYWORDS.items():
        if any(re.search(r"\b" + re.escape(kw) + r"\b", low) for kw in kws):
            matched_avoid.add(topic)

    matched_arch = None
    for kw, arch_name in ARCHETYPE_LOOKUP.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", low):
            matched_arch = arch_name
            break

    # Stopwords to avoid adding normal conversational prose as custom topics
    stopwords = {
        "about", "after", "also", "because", "building", "could", "doing", "first",
        "great", "having", "interested", "just", "like", "make", "more", "most",
        "much", "omit", "only", "other", "over", "people", "really", "should",
        "skip", "some", "than", "that", "their", "them", "then", "there", "these",
        "they", "thing", "think", "this", "those", "time", "very", "want", "well",
        "were", "what", "when", "where", "which", "while", "will", "with", "work",
        "working", "would", "your", "today", "focus", "looking", "please", "daily",
        "paper", "morning", "edition", "reader", "researcher", "engineer", "founder",
        "keep", "posted", "networks", "network", "news", "articles", "stories", "deals", "deal"
    }

    words = re.findall(r"\b[a-zA-Z]{4,15}\b", low)
    custom_candidates = []
    for w in words:
        if (
            w not in stopwords
            and not any(w in kws for kws in TOPIC_KEYWORDS.values())
            and not any(w in kws for kws in AVOID_KEYWORDS.values())
            and not any(w == k for k in ARCHETYPE_LOOKUP.keys())
        ):
            if w.title() not in custom_candidates:
                custom_candidates.append(w.title())

    return matched_arch, list(matched_interests), list(matched_avoid), custom_candidates[:3]


ONBOARDING_CSS = """<style>
.ob-wrap {
    max-width: 1220px;
    margin: 0 auto;
    padding-top: 0.5rem;
}

.ob-mast-banner {
    text-align: center;
    border-top: 4px double var(--rule);
    border-bottom: 2px solid var(--rule);
    padding: 16px 0 12px;
    margin-bottom: 24px;
}

.ob-motto {
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 4px;
}

.ob-masthead {
    font-family: var(--head);
    font-size: clamp(2.4rem, 5.5vw, 4rem);
    font-weight: 900;
    letter-spacing: 0.05em;
    line-height: 1.05;
    color: var(--ink);
}

.ob-sub {
    font-size: 0.84rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink_muted);
    font-style: italic;
    margin-top: 5px;
}

/* Stepper Tabs */
.ob-stepper {
    display: flex;
    justify-content: center;
    gap: 14px;
    margin-bottom: 24px;
}

.ob-step-pill {
    font-family: var(--head);
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 6px 18px;
    border: 1px solid var(--rule);
    background: var(--panel);
    color: var(--ink_muted);
    border-radius: var(--radius);
    transition: all 0.2s ease;
}

.ob-step-pill.active {
    background: var(--accent);
    color: #ffffff !important;
    border-color: var(--accent);
    box-shadow: 2px 2px 0 var(--rule);
}

/* Left Form Box */
.ob-form-card {
    background: var(--card);
    border: 1px solid var(--rule);
    border-radius: var(--radius);
    padding: 22px 26px;
    box-shadow: 4px 4px 0 var(--rule);
    margin-bottom: 16px;
}

.ob-sec-title {
    font-family: var(--head);
    font-size: 1.25rem;
    font-weight: 900;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 4px;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 6px;
}

.ob-sec-sub {
    font-size: 0.84rem;
    color: var(--ink_muted);
    margin-bottom: 16px;
    line-height: 1.45;
}

/* Right Column: Live Broadsheet Press Pass */
.press-pass-box {
    background: var(--panel);
    border: 2px solid var(--rule);
    outline: 3px double var(--rule);
    outline-offset: 4px;
    border-radius: var(--radius);
    padding: 22px 22px 18px;
    box-shadow: 6px 6px 0 var(--rule);
    position: relative;
    overflow: hidden;
    margin-top: 4px;
}

.press-pass-ribbon {
    position: absolute;
    top: 14px;
    right: -32px;
    background: var(--accent);
    color: #ffffff !important;
    font-size: 0.55rem;
    font-weight: 900;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    padding: 3px 38px;
    transform: rotate(45deg);
    box-shadow: 0 2px 5px rgba(0,0,0,0.25);
    z-index: 2;
}

.press-pass-header {
    text-align: center;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 10px;
    margin-bottom: 14px;
}

.press-pass-seal {
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.24em;
    color: var(--accent);
    text-transform: uppercase;
}

.press-pass-title {
    font-family: var(--head);
    font-size: 1.25rem;
    font-weight: 900;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--ink);
    margin-top: 2px;
}

.press-pass-sub {
    font-size: 0.68rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--ink_muted);
    font-style: italic;
}

.press-pass-identity {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 14px;
}

.press-pass-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    border: 2px solid var(--accent);
    outline: 2px solid var(--accent);
    outline-offset: 3px;
    background: var(--card);
    color: var(--accent);
    font-family: var(--head);
    font-weight: 900;
    font-size: 1.85rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.press-pass-details {
    flex: 1;
}

.press-pass-name {
    font-family: var(--head);
    font-weight: 900;
    font-size: 1.45rem;
    line-height: 1.1;
    color: var(--ink);
}

.press-pass-role {
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent);
    margin-top: 3px;
}

.press-pass-num {
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    color: var(--ink_muted);
    margin-top: 3px;
}

.press-pass-divider {
    border-top: 1px dotted var(--rule);
    margin: 12px 0;
}

.press-pass-sec-label {
    font-size: 0.66rem;
    font-weight: 800;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink_muted);
    margin-bottom: 8px;
}

.press-pass-pills-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    min-height: 48px;
    margin-bottom: 12px;
}

.press-pass-pill {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    background: var(--accent_bg);
    color: var(--accent);
    border: 1px solid var(--accent);
    border-radius: 4px;
    padding: 3px 9px;
}

.press-pass-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    background: var(--card);
    border: 1px solid var(--rule);
    border-radius: var(--radius);
    padding: 10px 14px;
    margin-top: 12px;
}

.press-pass-grid-item {
    display: flex;
    flex-direction: column;
}

.press-pass-grid-lbl {
    font-size: 0.6rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--ink_muted);
}

.press-pass-grid-val {
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--ink);
    margin-top: 2px;
}

.press-pass-wax-seal {
    text-align: center;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--accent);
    margin-top: 14px;
    border-top: 1px solid var(--rule);
    padding-top: 10px;
}

/* Magic Lens Prompt Box */
.magic-lens-box {
    background: var(--panel);
    border: 1px dashed var(--accent);
    border-radius: var(--radius);
    padding: 12px 16px;
    margin: 14px 0 18px;
}

.magic-lens-title {
    font-family: var(--head);
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 4px;
}

.magic-lens-desc {
    font-size: 0.78rem;
    color: var(--ink_muted);
    margin-bottom: 8px;
    line-height: 1.4;
}
</style>"""


def render(user):
    # 1. Apply vintage palette
    themes.apply(user.get("theme", "classic"))
    st.markdown(ONBOARDING_CSS, unsafe_allow_html=True)

    ss = st.session_state
    ss.setdefault("ob_step", 1)
    ss.setdefault("ob_name", user.get("name") or "Alex Turing")

    # Initial archetype matching based on user's current persona or default
    current_persona = user.get("persona") or "Founder"
    default_arch = next(
        (k for k, v in ARCHETYPES.items() if v["persona"] == current_persona),
        "Founder & Builder",
    )
    ss.setdefault("ob_archetype", default_arch)

    # Initial interests
    existing_interests = list(user.get("interests", {}).keys()) if user.get("interests") else None
    if not existing_interests and user.get("declared"):
        existing_interests = user.get("declared")
    ss.setdefault("ob_interests", existing_interests or ARCHETYPES[ss.ob_archetype]["topics"])
    ss.setdefault("ob_avoid", user.get("avoid_topics") or [])
    ss.setdefault("ob_custom", "")
    ss.setdefault("ob_vibe", "📰 Classic Broadsheet")

    # Top Masthead
    is_editing = bool(ss.get("edit_profile"))
    motto_text = "★ RE-TUNING EDITORIAL WIRE & NOISE FILTERS ★" if is_editing else "★ THE PERSONALIZED MORNING PAPER · EDITORIAL ACCREDITATION ★"
    subtitle_text = "Update your curated broadsheet parameters" if is_editing else "Configure your tailored morning newspaper in under 30 seconds"

    masthead_html = f"""
    <div class="ob-wrap">
    <div class="ob-mast-banner">
    <div class="ob-motto">{motto_text}</div>
    <div class="ob-masthead">THE DAILY BREW</div>
    <div class="ob-sub">{subtitle_text}</div>
    </div>
    </div>
    """
    st.markdown(_clean_html(masthead_html), unsafe_allow_html=True)

    # Cancel button if editing an existing profile
    if is_editing:
        c_cancel, _ = st.columns([1, 4])
        with c_cancel:
            if st.button("← Return to Paper", key="cancel_retune"):
                ss.pop("edit_profile", None)
                st.rerun()

    # Step Indicators
    step1_cls = "ob-step-pill active" if ss.ob_step == 1 else "ob-step-pill"
    step2_cls = "ob-step-pill active" if ss.ob_step == 2 else "ob-step-pill"
    stepper_html = f"""
    <div class="ob-stepper">
    <div class="{step1_cls}">01 · Press Identity & Archetype</div>
    <div class="{step2_cls}">02 · Curate Wire & Delivery</div>
    </div>
    """
    st.markdown(_clean_html(stepper_html), unsafe_allow_html=True)

    # Side-by-side: Interactive Setup (Left) & Live Broadsheet Press Pass (Right)
    col_left, col_right = st.columns([1.25, 0.95], gap="large")

    # =========================================================================
    # LEFT COLUMN: Interactive Editorial Registration
    # =========================================================================
    with col_left:
        if ss.ob_step == 1:
            st.markdown(
                '<div class="ob-sec-title">Step 1: Your Identity & Archetype</div>'
                '<div class="ob-sec-sub">Select your professional focus to automatically seed your morning edition. You can fine-tune every topic in the next step.</div>',
                unsafe_allow_html=True,
            )

            # Name input
            name_input = st.text_input(
                "Subscriber / Byline Name",
                value=ss.ob_name,
                placeholder="e.g. Alex Turing",
                help="Your name as it appears on the masthead and editorial press pass",
            )
            if name_input.strip() and name_input != ss.ob_name:
                ss.ob_name = name_input.strip()

            # Archetype Selector (One-click presets)
            arch_keys = list(ARCHETYPES.keys())
            current_index = arch_keys.index(ss.ob_archetype) if ss.ob_archetype in arch_keys else 0

            selected_arch = st.radio(
                "Choose Your Reader Archetype",
                options=arch_keys,
                index=current_index,
                format_func=lambda k: f"{ARCHETYPES[k]['icon']} {k} — {ARCHETYPES[k]['tagline']}",
                help="Selecting an archetype automatically populates your baseline editorial topics",
            )

            if selected_arch != ss.ob_archetype:
                ss.ob_archetype = selected_arch
                # Auto-seed topics from chosen archetype
                ss.ob_interests = list(ARCHETYPES[selected_arch]["topics"])
                st.rerun()

            arch_info = ARCHETYPES[ss.ob_archetype]
            st.caption(f"**Archetype Lens:** {arch_info['desc']}")

            # Innovative Natural Language Lens (Magic AI / Keyword Lens)
            with st.expander("🪄 Magic Lens: Express your focus in your own words"):
                st.markdown(
                    '<div class="magic-lens-title">Instant Editorial Lens</div>'
                    '<div class="magic-lens-desc">Type your role, current focus, and what to omit in plain English. Our local parser will instantly configure your wire.</div>',
                    unsafe_allow_html=True,
                )
                lens_text = st.text_input(
                    "Describe your ideal morning paper",
                    placeholder="e.g. I run an AI robotics startup, focus on tech and venture funding, skip celebrity gossip and sports",
                    key="magic_lens_input",
                )
                if st.button("✨ Auto-Tune Wire From Text", key="btn_magic_tune"):
                    if lens_text.strip():
                        matched_arch, matched_ints, matched_avd, custom_kws = parse_natural_lens(lens_text)
                        if matched_arch:
                            ss.ob_archetype = matched_arch
                        if matched_ints:
                            ss.ob_interests = list(dict.fromkeys(ss.ob_interests + matched_ints))
                        if matched_avd:
                            ss.ob_avoid = list(dict.fromkeys(ss.ob_avoid + matched_avd))
                        if custom_kws:
                            existing_custom = [x.strip() for x in ss.ob_custom.split(",") if x.strip()]
                            ss.ob_custom = ", ".join(list(dict.fromkeys(existing_custom + custom_kws)))
                        st.toast(f"★ Wire tuned! Archetype: {ss.ob_archetype} with {len(ss.ob_interests)} topics.", icon="✨")
                        st.rerun()

            # Navigation buttons
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            c1, c2 = st.columns([1.2, 1])
            with c1:
                if st.button("Fine-Tune Wire Topics →", type="primary", use_container_width=True):
                    ss.ob_step = 2
                    st.rerun()
            with c2:
                if st.button("⚡ 1-Click Quick Mint", help="Start reading right away with chosen archetype defaults", use_container_width=True):
                    _complete_onboarding(user, ss.ob_name, ARCHETYPES[ss.ob_archetype]["persona"], ss.ob_interests, ss.ob_avoid)

        else:
            # Step 2: Fine-Tuning Topics & Delivery
            st.markdown(
                '<div class="ob-sec-title">Step 2: Curate Wire & Delivery</div>'
                '<div class="ob-sec-sub">Customize the signals and noise filters that shape your morning front page.</div>',
                unsafe_allow_html=True,
            )

            # Topic Pills
            st.markdown("**🗞️ Primary Wire Topics (Click to Toggle):**")
            picked_topics = st.pills(
                "Primary Interests",
                options=INTERESTS,
                selection_mode="multi",
                default=ss.ob_interests,
                label_visibility="collapsed",
            ) or []
            ss.ob_interests = picked_topics

            # Custom keywords
            custom_input = st.text_input(
                "Specialized Topics & Search Queries (comma-separated)",
                value=ss.ob_custom,
                placeholder="e.g. Quantum Computing, Clean Energy, Autonomous Agents",
                help="These specialized keywords are fed directly into the Google News live wire fetcher",
            )
            ss.ob_custom = custom_input

            # Avoid Topics
            st.markdown("**🛡️ Noise Reduction: Topics to Filter Out:**")
            picked_avoid = st.pills(
                "Avoid Topics",
                options=AVOID_SUGGESTIONS,
                selection_mode="multi",
                default=ss.ob_avoid,
                label_visibility="collapsed",
            ) or []
            ss.ob_avoid = picked_avoid

            # Delivery style / reading vibe
            st.markdown("**☕ Morning Delivery Cadence:**")
            picked_vibe = st.segmented_control(
                "Preferred Cadence",
                options=["☕ 3-Min Espresso Scan", "📰 Classic Broadsheet", "📻 Wireless Audio First"],
                default=ss.ob_vibe,
                label_visibility="collapsed",
            )
            if picked_vibe:
                ss.ob_vibe = picked_vibe

            # Navigation
            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
            c_back, c_mint = st.columns([1, 1.4])
            with c_back:
                if st.button("← Back to Archetypes", use_container_width=True):
                    ss.ob_step = 1
                    st.rerun()
            with c_mint:
                extras = [x.strip() for x in ss.ob_custom.split(",") if x.strip()]
                final_interests = list(dict.fromkeys(ss.ob_interests + extras))
                mint_disabled = len(final_interests) == 0

                btn_label = "Update My Wire 🗞️" if is_editing else "Mint My First Edition 🗞️"
                if st.button(btn_label, type="primary", disabled=mint_disabled, use_container_width=True):
                    _complete_onboarding(user, ss.ob_name, ARCHETYPES[ss.ob_archetype]["persona"], final_interests, ss.ob_avoid)

    # =========================================================================
    # RIGHT COLUMN: Live Broadsheet Press Pass & Masthead Preview
    # =========================================================================
    with col_right:
        # Calculate live preview data
        persona_name = ARCHETYPES.get(ss.ob_archetype, {}).get("persona", "Reader")
        monogram = (ss.ob_name.strip()[:1] or "R").upper()
        custom_extras = [x.strip() for x in ss.ob_custom.split(",") if x.strip()]
        active_interests = list(dict.fromkeys(ss.ob_interests + custom_extras))

        # Topic badges HTML
        if active_interests:
            badges_html = "".join(f'<span class="press-pass-pill">★ {html.escape(t)}</span>' for t in active_interests[:7])
            if len(active_interests) > 7:
                badges_html += f'<span class="press-pass-pill">+{len(active_interests)-7} more</span>'
        else:
            badges_html = '<span style="font-size:0.75rem;font-style:italic;color:var(--ink_muted);">Select at least one wire topic on the left...</span>'

        est_time = max(3, len(active_interests) * 2)
        noise_count = len(ss.ob_avoid)
        filter_status = f"{noise_count} Filters Active" if noise_count > 0 else "Unfiltered Wire"
        pass_number = f"DB-{user['id']:04d}"

        pass_html = f"""
        <div class="press-pass-box">
        <div class="press-pass-ribbon">Press Pass</div>
        <div class="press-pass-header">
        <div class="press-pass-seal">★ THE DAILY BREW ★</div>
        <div class="press-pass-title">Official Subscriber Press Pass</div>
        <div class="press-pass-sub">Accreditation Bureau · Late City BroadSheet Edition</div>
        </div>

        <div class="press-pass-identity">
        <div class="press-pass-avatar">{monogram}</div>
        <div class="press-pass-details">
        <div class="press-pass-name">{html.escape(ss.ob_name or 'Accredited Reader')}</div>
        <div class="press-pass-role">🗞️ {html.escape(persona_name.upper())} DESK</div>
        <div class="press-pass-num">CREDENTIAL NO. {pass_number} · VOL. CXXIV</div>
        </div>
        </div>

        <div class="press-pass-divider"></div>

        <div class="press-pass-sec-label">Active Editorial Wire Frequencies ({len(active_interests)}):</div>
        <div class="press-pass-pills-wrap">
        {badges_html}
        </div>

        <div class="press-pass-divider"></div>

        <div class="press-pass-grid">
        <div class="press-pass-grid-item">
        <span class="press-pass-grid-lbl">Morning Cadence</span>
        <span class="press-pass-grid-val">{html.escape(ss.ob_vibe)}</span>
        </div>
        <div class="press-pass-grid-item">
        <span class="press-pass-grid-lbl">Est. Reading Time</span>
        <span class="press-pass-grid-val">~{est_time} Minutes</span>
        </div>
        <div class="press-pass-grid-item">
        <span class="press-pass-grid-lbl">Noise Barrier</span>
        <span class="press-pass-grid-val">{filter_status}</span>
        </div>
        <div class="press-pass-grid-item">
        <span class="press-pass-grid-lbl">Curation Engine</span>
        <span class="press-pass-grid-val">Gemini AI Editor</span>
        </div>
        </div>

        <div class="press-pass-wax-seal">
        🪶 VERIFIED EDITORIAL ACCREDITATION · READY TO TYPESET
        </div>
        </div>
        """
        st.markdown(_clean_html(pass_html), unsafe_allow_html=True)


# =============================================================================
# Typesetting Ceremony & Profile Save
# =============================================================================
def _complete_onboarding(user, name, persona, interests, avoid):
    """Executes an authentic broadsheet typesetting ceremony before transitioning to the reader."""
    uid = user["id"]
    name_clean = name.strip() or "Reader"

    with st.status("🗞️ Casting BroadSheet & Minting Your Edition...", expanded=True) as status:
        st.write(f"⚙️ Typesetting broadsheet galleys for **{name_clean}** ({persona})...")
        time.sleep(0.4)
        top_focus = ", ".join(interests[:3]) if interests else "General Wire"
        st.write(f"⚖️ Calibrating AI editorial weights to prioritize **{top_focus}**...")
        time.sleep(0.4)
        st.write("☕ Ink is fresh. Typesetting complete. Opening your morning paper...")
        time.sleep(0.3)
        status.update(label="★ BroadSheet Minted Successfully!", state="complete")

    save_profile(uid, name_clean, persona, interests, avoid)

    # Clean up onboarding session state
    for k in ("ob_step", "ob_name", "ob_archetype", "ob_interests", "ob_avoid", "ob_custom", "ob_vibe", "edit_profile"):
        st.session_state.pop(k, None)

    st.rerun()