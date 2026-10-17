import re, urllib.parse
from difflib import SequenceMatcher
import feedparser
from config import FEEDS, GOOGLE_NEWS, MAX_PER_FEED, MAX_PER_INTEREST
from core.models import RawArticle

def _clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()[:500]

def _parse(url, source, limit):
    out = []
    try:
        feed = feedparser.parse(url)
        for e in feed.entries[:limit]:
            link, title = e.get("link"), _clean(e.get("title"))
            if not link or not title:
                continue
            # Google News appends " - Publisher" to titles
            if source.startswith("Google News") and " - " in title:
                title, pub = title.rsplit(" - ", 1)
                src = pub
            else:
                src = source
            out.append(RawArticle(
                url=link, title=title, source=src,
                published=e.get("published", ""),
                snippet=_clean(e.get("summary", ""))))
    except Exception as ex:
        print(f"[ingest] {source} failed: {ex}")
    return out

def _dedupe(articles, threshold=0.8):
    kept = []
    for a in articles:
        if any(SequenceMatcher(None, a.title.lower(), k.title.lower()).ratio() > threshold
               for k in kept):
            continue
        kept.append(a)
    return kept

def fetch_all(user_interests):
    """Generic feeds + one Google News search per user interest."""
    articles = []
    for name, url in FEEDS.items():
        articles += _parse(url, name, MAX_PER_FEED)
    for topic in user_interests:
        q = urllib.parse.quote_plus(topic)
        articles += _parse(GOOGLE_NEWS.format(q=q), f"Google News", MAX_PER_INTEREST)
    # exact-URL dedupe first, then fuzzy title dedupe
    unique = list({a.url: a for a in articles}.values())
    return _dedupe(unique)