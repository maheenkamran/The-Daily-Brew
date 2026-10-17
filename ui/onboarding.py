import streamlit as st
from config import PERSONAS, INTERESTS, AVOID_SUGGESTIONS
from core.db import create_user

def render():
    ss = st.session_state
    ss.setdefault("step", 1)
    ss.setdefault("ob", {"name": "", "persona": PERSONAS[0], "interests": [], "avoid": []})
    ob = ss.ob

    st.title("📰 Your Personal Morning Paper")
    st.progress(ss.step / 3, text=f"Step {ss.step} of 3")

    if ss.step == 1:
        st.subheader("Who is this paper for?")
        ob["name"] = st.text_input("Your name", ob["name"])
        ob["persona"] = st.selectbox("Your role", PERSONAS, index=PERSONAS.index(ob["persona"]))
        if st.button("Next →", disabled=not ob["name"].strip(), type="primary"):
            ss.step = 2; st.rerun()

    elif ss.step == 2:
        st.subheader("What do you want to read about?")
        st.caption("Pick at least 2. You can change these later.")
        ob["interests"] = st.pills("Interests", INTERESTS, selection_mode="multi",
                                   default=ob["interests"]) or []
        custom = st.text_input("Anything else? (comma-separated)", placeholder="quantum computing, F1 tech")
        c1, c2 = st.columns(2)
        if c1.button("← Back"): ss.step = 1; st.rerun()
        if c2.button("Next →", disabled=len(ob["interests"]) < 2, type="primary"):
            extras = [x.strip() for x in custom.split(",") if x.strip()]
            ob["interests"] = list(dict.fromkeys(ob["interests"] + extras))
            ss.step = 3; st.rerun()

    else:
        st.subheader("What should we keep out?")
        st.caption("Optional, but it keeps your paper clean.")
        picked = st.pills("Avoid", AVOID_SUGGESTIONS, selection_mode="multi",
                          default=ob["avoid"]) or []
        custom = st.text_input("Other topics to avoid (comma-separated)")
        extras = [x.strip() for x in custom.split(",") if x.strip()]
        c1, c2 = st.columns(2)
        if c1.button("← Back"): ss.step = 2; st.rerun()
        if c2.button("Create my paper 🗞️", type="primary"):
            uid = create_user(ob["name"].strip(), ob["persona"], ob["interests"], picked + extras)
            st.query_params["uid"] = str(uid)
            ss.user_id = uid
            st.rerun()