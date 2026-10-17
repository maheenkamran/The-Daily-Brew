import streamlit as st
from config import PERSONAS, INTERESTS, AVOID_SUGGESTIONS
from core.db import save_profile

def render(user):
    ss = st.session_state
    ss.setdefault("step", 1)
    ss.setdefault("ob", {"name": user["name"], "persona": PERSONAS[0],
                         "interests": [], "avoid": []})
    ob = ss.ob

    st.markdown(
        '<div style="text-align:center;margin-bottom:1rem;">'
        '<div style="font-size:2.4rem;font-weight:900;letter-spacing:0.04em;">📰 THE DAILY BREW</div>'
        '<div style="font-size:0.9rem;opacity:0.75;text-transform:uppercase;letter-spacing:0.12em;">'
        'Your personal morning paper</div></div>',
        unsafe_allow_html=True)
    st.progress(ss.step / 3, text=f"Step {ss.step} of 3")

    # Step 1: Identity
    if ss.step == 1:
        st.subheader("Who is this paper for?")
        ob["name"] = st.text_input("Your name", ob["name"], placeholder="e.g. Alex Turing")
        ob["persona"] = st.selectbox("Your role", PERSONAS, index=PERSONAS.index(ob["persona"]))
        if st.button("Next →", disabled=not ob["name"].strip(), type="primary"):
            ss.step = 2
            st.rerun()

    # Step 2: Interests
    elif ss.step == 2:
        st.subheader("What do you want to read about?")
        st.caption("Pick at least 2. The paper will learn and adapt over time.")
        ob["interests"] = st.pills("Interests", INTERESTS, selection_mode="multi",
                                   default=ob["interests"]) or []
        custom = st.text_input("Anything else? (comma-separated)",
                               placeholder="e.g. Quantum Computing, Biotech")
        c1, c2 = st.columns(2)
        if c1.button("← Back"):
            ss.step = 1
            st.rerun()
        if c2.button("Next →", disabled=len(ob["interests"]) < 2, type="primary"):
            extras = [x.strip() for x in custom.split(",") if x.strip()]
            ob["interests"] = list(dict.fromkeys(ob["interests"] + extras))
            ss.step = 3
            st.rerun()

    # Step 3: Avoid
    else:
        st.subheader("What should we keep out?")
        st.caption("Optional, but it keeps your paper clean.")
        picked = st.pills("Avoid", AVOID_SUGGESTIONS, selection_mode="multi",
                          default=ob["avoid"]) or []
        custom = st.text_input("Other topics to avoid (comma-separated)",
                               placeholder="e.g. Clickbait, Drama")
        extras = [x.strip() for x in custom.split(",") if x.strip()]
        c1, c2 = st.columns(2)
        if c1.button("← Back"):
            ss.step = 2
            st.rerun()
        if c2.button("Create my paper 🗞️", type="primary"):
            save_profile(user["id"], ob["name"].strip(), ob["persona"],
                         ob["interests"], list(dict.fromkeys(picked + extras)))
            ss.pop("step", None)
            ss.pop("ob", None)
            st.rerun()