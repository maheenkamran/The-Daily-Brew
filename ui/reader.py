from datetime import datetime
import streamlit as st
from core import edition
from core.db import get_user_feedback
from export.pdf import build_pdf
from ui.components import article_card, ghost_id
from ui.insights import strips
from ui.components import article_card

def _section(name, ids, arts, layout, uid, fb, hidden):
    ids = [i for i in ids if i in arts and i not in hidden]
    if not ids:
        return
    st.markdown(f'<div class="section-head">{name}</div>', unsafe_allow_html=True)
    for i in ids:
        article_card(arts[i], uid, layout["why"].get(str(i), ""), fb=fb.get(i), prefix=f"{name}_")

def render(user, day):
    with st.spinner("Your editor is putting together today's paper..."):
        result = edition.load(user, day)
    if result is None:
        st.warning("No articles yet. Run `python scripts/run_daily.py` and refresh.")
        return
    layout, arts = result
    uid = user["id"]
    fb = get_user_feedback(uid)
    
    hidden_all = {i for i, acts in fb.items() if acts & {"skip", "dislike"}}
    g = ghost_id()
    hidden = hidden_all - ({g} if g else set())   # the card that's animating out stays for a moment
    
    st.sidebar.download_button(
    "⬇️ Download PDF",
    data=build_pdf(user, day, layout, arts, hidden),
    file_name=f"morning-paper-{day}.pdf",
    mime="application/pdf")

    interests = user["interests"]
    focus = max(interests, key=interests.get) if interests else "General"
    nice = datetime.strptime(day, "%Y-%m-%d").strftime("%A, %B %d, %Y")

    st.markdown(f'<div class="masthead">THE {user["name"].upper()} CHRONICLE</div>'
                f'<div class="dateline">{nice} &nbsp;·&nbsp; {focus} Edition &nbsp;·&nbsp; {user["persona"]}</div>',
                unsafe_allow_html=True)

    left, center, right = st.columns([1, 2, 1.2], gap="large")
    order = layout["section_order"]

    with center:
        lead = layout["lead"]
        if lead in arts and lead not in hidden:
            article_card(arts[lead], uid, layout["why"].get(str(lead), ""),
                         lead=True, fb=fb.get(lead), prefix="lead_")
        _section("Front Page", [i for i in layout["front"] if i != lead],
                 arts, layout, uid, fb, hidden)

    with left:
        if order:
            _section(order[0], layout["sections"][order[0]], arts, layout, uid, fb, hidden)
    with right:
        for s in order[1:]:
            _section(s, layout["sections"][s], arts, layout, uid, fb, hidden)