import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import INTERESTS, MAX_ARTICLES
from core.db import init_db, existing_urls, save_articles, all_interests
from core.ingest import fetch_all
from core.enrich import enrich

def main():
    init_db()
    interests = list(dict.fromkeys(all_interests() or INTERESTS[:4]))
    print(f"[run_daily] interests: {interests}")

    raw = fetch_all(interests)
    seen = existing_urls()
    fresh = [a for a in raw if a.url not in seen][:MAX_ARTICLES]
    print(f"[run_daily] fetched {len(raw)}, new {len(fresh)}")

    if not fresh:
        print("[run_daily] nothing new"); return
    save_articles(enrich(fresh))
    print("[run_daily] done")

if __name__ == "__main__":
    main()