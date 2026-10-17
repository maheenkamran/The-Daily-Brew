import threading
from config import INTERESTS, MAX_ARTICLES, TODAY
from core import db
from core.ingest import fetch_all
from core.enrich import enrich

_lock = threading.Lock()

def prebuild_editions():
    """Build and freeze today's paper for every reader so it opens instantly."""
    from core import edition          # imported here to avoid a circular import
    for u in db.list_users():
        try:
            edition.load(db.get_user(u["id"]), TODAY())
        except Exception as ex:
            print(f"[pipeline] prebuild failed for {u['name']}: {ex}")

def run_pipeline():
    if not _lock.acquire(blocking=False):      # already running, skip
        print("[pipeline] already running"); return 0
    try:
        db.init_db()
        interests = list(dict.fromkeys(db.all_interests() or INTERESTS[:4]))
        raw = fetch_all(interests)
        seen = db.existing_urls()
        fresh = [a for a in raw if a.url not in seen][:MAX_ARTICLES]
        print(f"[pipeline] fetched {len(raw)}, new {len(fresh)}")
        if fresh:
            db.save_articles(enrich(fresh))
        prebuild_editions()
        return len(fresh)
    finally:
        _lock.release()