import sys, os, random, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from config import SECTIONS
from core import db
from core.rank import score_article

FRONT_N, SECTION_N, EXPLORE_N = 6, 5, 2
EXPLORE = "Outside Your Bubble"

DEMO_USERS = [
    dict(name="Alex", persona="Software Engineer",
         interests=["Tech & AI", "Cybersecurity", "Startups"],
         avoid=["Sports", "Celebrity Gossip"]),
    dict(name="Sara", persona="Investor",
         interests=["Global Markets", "Startups", "World News"],
         avoid=["Celebrity Gossip", "Local Politics"]),
    dict(name="Dr. Khan", persona="Academic",
         interests=["Science", "Climate", "Space"],
         avoid=["Sports", "Entertainment"]),
]

def ensure_demo_users():
    existing = {u["name"] for u in db.list_users()}
    for u in DEMO_USERS:
        if u["name"] not in existing:
            db.create_user(u["name"], u["persona"], u["interests"], u["avoid"])
            print(f"[seed] created demo reader: {u['name']}")

def build_past(user, day, pool):
    rng = random.Random(f"{user['id']}-{day}")   # same day + user = same edition every run
    scored = []
    for a in pool:
        r = score_article(a, user)
        if r:
            scored.append((r[0] + rng.uniform(0, 0.3), a, r[1]))   # noise makes each day differ
    if len(scored) < FRONT_N:
        return None
    scored.sort(key=lambda x: -x[0])

    front, rest = scored[:FRONT_N], scored[FRONT_N:]
    buckets = {s: [] for s in SECTIONS if s != "Front Page"}
    for sc, a, m in rest:
        sec = a["section"] if a["section"] in buckets else "Quick Briefs"
        if len(buckets[sec]) < SECTION_N:
            buckets[sec].append((sc, a["id"]))
    order = sorted((s for s in buckets if buckets[s]),
                   key=lambda s: -sum(x[0] for x in buckets[s]))

    used = {a["id"] for _, a, _ in front} | {i for v in buckets.values() for _, i in v}
    explore = sorted((x for x in rest if not x[2] and x[1]["id"] not in used),
                     key=lambda x: -x[1]["quality_score"])[:EXPLORE_N]
    if explore:
        buckets[EXPLORE] = [(sc, a["id"]) for sc, a, _ in explore]
        order.append(EXPLORE)

    why = {}
    for sc, a, m in scored:
        why[str(a["id"])] = (f"Because you follow {', '.join(m[:2])}" if m
                             else "A top story across that day's sources")
    for _, a, _ in explore:
        why[str(a["id"])] = "Outside your usual interests, but too important to miss"

    takeaways = [(a["summary"] or a["title"]).split(". ")[0].strip() for _, a, _ in front[:3]]

    return {
        "lead": front[0][1]["id"],
        "front": [a["id"] for _, a, _ in front],
        "sections": {s: [i for _, i in buckets[s]] for s in order},
        "section_order": order,
        "why": why,
        "takeaways": takeaways,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=4, help="how many past days to fill")
    ap.add_argument("--reset", action="store_true", help="overwrite existing past editions")
    args = ap.parse_args()

    db.init_db()
    pool = db.get_articles_since("1970-01-01")      # every article in the database
    if not pool:
        print("[seed] no articles yet. Run: python scripts/run_daily.py"); return

    ensure_demo_users()
    made = 0
    for u in db.list_users():
        user = db.get_user(u["id"])
        for k in range(1, args.days + 1):
            day = (date.today() - timedelta(days=k)).isoformat()
            if db.get_edition(user["id"], day) and not args.reset:
                continue
            layout = build_past(user, day, pool)
            if layout:
                db.save_edition(user["id"], day, layout)
                made += 1
    print(f"[seed] saved {made} past editions")

if __name__ == "__main__":
    main()