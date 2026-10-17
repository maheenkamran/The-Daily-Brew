import streamlit as st
from config import PERSONAS, INTERESTS, AVOID_SUGGESTIONS
from core.db import create_user
from ui.themes import THEMES, RECOMMENDED_THEMES

def render():
    ss = st.session_state
    ss.setdefault("step", 1)
    ss.setdefault("ob", {
        "name": "",
        "persona": PERSONAS[0],
        "interests": [],
        "avoid": [],
        "theme": "classic"
    })
    ob = ss.ob

    st.markdown(
        """<div style="text-align:center;margin-bottom:1.5rem;">
            <div style="font-size:2.4rem;font-weight:900;letter-spacing:0.04em;">📰 THE DAILY BREW</div>
            <div style="font-size:0.95rem;opacity:0.75;text-transform:uppercase;letter-spacing:0.12em;">
                Personal Morning Paper Tailored To Your Mind
            </div>
        </div>""",
        unsafe_allow_html=True
    )
    
    st.progress(ss.step / 4, text=f"Step {ss.step} of 4")

    # Step 1: Persona & Identity
    if ss.step == 1:
        st.subheader("Who is this morning paper for?")
        ob["name"] = st.text_input("Your Name", ob["name"], placeholder="e.g. Alex Turing")
        ob["persona"] = st.selectbox("Your Primary Role", PERSONAS, index=PERSONAS.index(ob["persona"]))
        
        # Pre-set recommended theme based on persona
        recommended_theme = RECOMMENDED_THEMES.get(ob["persona"], "classic")
        ob["theme"] = recommended_theme
        
        st.caption(f"💡 Recommended theme for {ob['persona']}: **{THEMES[recommended_theme]['emoji']} {THEMES[recommended_theme]['name']}**")
        
        if st.button("Next: Choose Interests →", disabled=not ob["name"].strip(), type="primary"):
            ss.step = 2
            st.rerun()

    # Step 2: Interests
    elif ss.step == 2:
        st.subheader("What do you want to read about?")
        st.caption("Pick at least 2 key topics. The AI will learn and adapt over time.")
        ob["interests"] = st.pills("Curated Topics", INTERESTS, selection_mode="multi",
                                   default=ob["interests"]) or []
        custom = st.text_input("Custom niches or keywords (comma-separated)", placeholder="e.g. Quantum Computing, AI Agents, Biotech")
        
        c1, c2 = st.columns(2)
        if c1.button("← Back"):
            ss.step = 1
            st.rerun()
        if c2.button("Next: Noise Filtering →", disabled=len(ob["interests"]) < 2, type="primary"):
            extras = [x.strip() for x in custom.split(",") if x.strip()]
            ob["interests"] = list(dict.fromkeys(ob["interests"] + extras))
            ss.step = 3
            st.rerun()

    # Step 3: Avoid / Noise Filtering
    elif ss.step == 3:
        st.subheader("What should we keep out?")
        st.caption("Keep your daily briefing high-signal by removing unwanted noise.")
        picked = st.pills("Topics to Avoid", AVOID_SUGGESTIONS, selection_mode="multi",
                          default=ob["avoid"]) or []
        custom = st.text_input("Other topics or terms to avoid (comma-separated)", placeholder="e.g. Clickbait, Drama")
        extras = [x.strip() for x in custom.split(",") if x.strip()]
        
        c1, c2 = st.columns(2)
        if c1.button("← Back"):
            ss.step = 2
            st.rerun()
        if c2.button("Next: Choose Aesthetic →", type="primary"):
            ob["avoid"] = list(dict.fromkeys(picked + extras))
            ss.step = 4
            st.rerun()

    # Step 4: Theme / Reading Style
    else:
        st.subheader("Choose your reading aesthetic")
        st.caption("Pick how your morning paper looks and feels. You can switch themes anytime.")

        theme_keys = list(THEMES.keys())
        default_theme = ob.get("theme", "classic")
        if default_theme not in theme_keys:
            default_theme = "classic"

        # Theme preview cards
        cols = st.columns(3)
        for idx, (tk, tv) in enumerate(THEMES.items()):
            col = cols[idx % 3]
            is_selected = (tk == default_theme)
            card_border = tv["accent"] if is_selected else tv["card_border"]
            badge = " ⭐ Recommended" if tk == RECOMMENDED_THEMES.get(ob["persona"]) else ""
            
            with col:
                st.markdown(
                    f"""<div style="background:{tv['card']};border:2px solid {card_border};border-radius:{tv['radius']};padding:12px;margin-bottom:8px;box-shadow:{tv['shadow']};min-height:110px;">
                        <div style="font-family:{tv['head']};font-size:1.05rem;font-weight:800;color:{tv['ink']};">
                            {tv['emoji']} {tv['name']}
                        </div>
                        <div style="font-size:0.75rem;color:{tv['ink_muted']};margin-top:4px;">
                            {tv['desc']}{badge}
                        </div>
                    </div>""",
                    unsafe_allow_html=True
                )

        selected_theme = st.radio(
            "Select Theme",
            options=theme_keys,
            index=theme_keys.index(default_theme),
            format_func=lambda k: f"{THEMES[k]['emoji']} {THEMES[k]['name']}",
            label_visibility="collapsed"
        )
        ob["theme"] = selected_theme

        c1, c2 = st.columns(2)
        if c1.button("← Back"):
            ss.step = 3
            st.rerun()
        if c2.button("Create My Morning Paper 🗞️", type="primary"):
            uid = create_user(
                name=ob["name"].strip(),
                persona=ob["persona"],
                interests=ob["interests"],
                avoid=ob["avoid"],
                theme=ob["theme"]
            )
            st.query_params["uid"] = str(uid)
            ss.user_id = uid
            ss.active_theme = ob["theme"]
            st.rerun()