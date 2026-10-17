from datetime import date, timedelta
from config import SECTIONS, TODAY, AI_POOL
from core import db
from core.rank import score_article
from core.editor import ai_editor

FRONT_N = 6
SECTION_N = 5

def _pool():
    since = (date.today() - timedelta(days=1)).isoformat()
    pool = db.get_articles_since(since)
    if not pool:                      # demo safety net: use latest day we have
        d = db.latest_article_date()
        pool = db.get_articles_by_date(d) if d else []
    return pool

def build_layout(user):
    # 1) Python first cut
    scored = []
    for a in _pool():
        r = score_article(a, user)
        if r:
            scored.append((r[0], a, r[1]))
    if not scored:
        return None
    scored.sort(key=lambda x: -x[0])

    # 2) Gemini editor re-ranks the top candidates (falls back silently)
    top, tail = scored[:AI_POOL], scored[AI_POOL:]
    picks = ai_editor(user, top)
    if picks:
        def blended(x):
            p = picks.get(x[1]["id"])
            return 0.5 * x[0] + 0.5 * p.priority if p else x[0]
        top.sort(key=lambda x: -blended(x))
    scored = top + tail

    # 3) Build the layout
    front, rest = scored[:FRONT_N], scored[FRONT_N:]
    buckets = {s: [] for s in SECTIONS if s != "Front Page"}
    for sc, a, m in rest:
        sec = a["section"] if a["section"] in buckets else "Quick Briefs"
        if len(buckets[sec]) < SECTION_N:
            buckets[sec].append((sc, a["id"]))

    order = sorted((s for s in buckets if buckets[s]),
                   key=lambda s: -sum(x[0] for x in buckets[s]))

    # 4) "Why this is in your paper": Gemini's reason first, Python's as backup
    why = {}
    for sc, a, m in scored:
        p = picks.get(a["id"])
        if p and p.why:
            why[str(a["id"])] = p.why
        elif m:
            why[str(a["id"])] = f"Because you follow {', '.join(m[:2])}"
        else:
            why[str(a["id"])] = "A top story across today's sources"

    return {
        "lead": front[0][1]["id"],
        "front": [a["id"] for _, a, _ in front],
        "sections": {s: [i for _, i in buckets[s]] for s in order},
        "section_order": order,
        "why": why,
    }

def _all_ids(layout):
    ids = set(layout["front"])
    for v in layout["sections"].values():
        ids.update(v)
    return ids

def load(user, day):
    """Return (layout, articles_by_id). Past editions come from the frozen table."""
    layout = db.get_edition(user["id"], day)
    if layout is None:
        if day != TODAY():
            return None
        layout = build_layout(user)
        if layout is None:
            return None
        db.save_edition(user["id"], day, layout)
    arts = {a["id"]: a for a in db.get_articles_by_ids(list(_all_ids(layout)))}
    return layout, arts

def rebuild_today(user):
    db.delete_edition(user["id"], TODAY())