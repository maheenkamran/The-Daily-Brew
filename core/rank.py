from config import PERSONA_FOCUS

def _match(topic, tags, text):
    t = topic.lower()
    if t in tags or t in text:
        return True
    return any(len(g) > 3 and (g in t or t in g) for g in tags)

def score_article(a, user):
    """Returns (score, matched_interests), or None if filtered out."""
    tags = [g.lower() for g in a["topics"]]
    text = (a["title"] + " " + (a["summary"] or "")).lower()

    for bad in user["avoid_topics"]:          # negative filtering
        b = bad.lower()
        if b in tags or b in text or any(len(g) > 3 and (g in b or b in g) for g in tags):
            return None

    matched, total = [], 0.0
    for topic, weight in user["interests"].items():
        if _match(topic, tags, text):
            matched.append(topic)
            total += weight

    persona_bonus = 0.08 if any(_match(f, tags, text)
                                for f in PERSONA_FOCUS.get(user["persona"], [])) else 0
    front_bonus = 0.10 if a["section"] == "Front Page" else 0

    score = 0.45 * a["quality_score"] + 0.55 * min(total, 2.0) / 2 + persona_bonus + front_bonus
    return score, matched