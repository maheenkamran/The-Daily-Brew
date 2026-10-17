from collections import defaultdict
from core import db

SIGNAL = {"like": 0.20, "dislike": -0.25, "skip": -0.10}
CAP = 1.5          # no single topic can move more than this
MIN_SHOWN = 0.15   # ignore tiny noise

def recompute(uid):
    """Rebuild a user's learned topic deltas from their full feedback history."""
    deltas = defaultdict(float)
    for action, topics in db.feedback_with_topics(uid):
        d = SIGNAL.get(action)
        if d is None:
            continue
        for t in topics:
            deltas[t.lower()] += d
    final = {t: max(-CAP, min(CAP, d)) for t, d in deltas.items() if abs(d) >= MIN_SHOWN}
    db.replace_deltas(uid, final)
    return final