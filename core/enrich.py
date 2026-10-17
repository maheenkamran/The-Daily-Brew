import json, time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL, INTERESTS, AVOID_SUGGESTIONS, BATCH_SIZE, TODAY
from core.models import RawArticle, EnrichedItem

client = genai.Client(api_key=GEMINI_API_KEY)
VOCAB = INTERESTS + AVOID_SUGGESTIONS

SYSTEM = f"""You are the editor of a daily newspaper. For each article, return:
- idx: the same idx given
- summary: exactly 2 punchy sentences, in your own words, no clickbait
- section: one of "Front Page" (biggest, most important news), "Tech & Code" (tech/engineering/AI),
  "Deep Dives" (analysis, long reads, research), "Quick Briefs" (minor or light items)
- topics: 1-4 tags. Prefer these exact labels when they fit: {VOCAB}.
  Add a short specific tag too (e.g. "quantum computing").
- quality_score: 0.0-1.0 for importance and credibility. Penalize clickbait, rumors, and fluff."""

def _fallback(a):
    return dict(summary=(a.snippet[:200] or a.title), section="Quick Briefs",
                topics=[], quality_score=0.3)

def _enrich_batch(batch):
    payload = [{"idx": i, "title": a.title, "source": a.source, "snippet": a.snippet[:300]}
               for i, a in enumerate(batch)]
    for attempt in range(3):
        try:
            resp = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=json.dumps(payload),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM,
                    response_mime_type="application/json",
                    response_schema=list[EnrichedItem],
                    temperature=0.3))
            return {it.idx: it for it in resp.parsed}
        except Exception as ex:
            print(f"[enrich] attempt {attempt+1} failed: {ex}")
            time.sleep(4 * (attempt + 1))
    return {}

def enrich(articles: list[RawArticle]):
    rows, day = [], TODAY()
    for i in range(0, len(articles), BATCH_SIZE):
        batch = articles[i:i + BATCH_SIZE]
        result = _enrich_batch(batch)
        for j, a in enumerate(batch):
            it = result.get(j)
            data = (dict(summary=it.summary, section=it.section, topics=it.topics,
                         quality_score=max(0.0, min(1.0, it.quality_score)))
                    if it else _fallback(a))
            rows.append(dict(url=a.url, title=a.title, source=a.source,
                             published=a.published, summary=data["summary"],
                             section=data["section"], topics=json.dumps(data["topics"]),
                             quality_score=data["quality_score"], fetched_date=day))
        print(f"[enrich] {min(i + BATCH_SIZE, len(articles))}/{len(articles)}")
        time.sleep(2)  # be nice to free-tier rate limits
    return rows