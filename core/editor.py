import json
from google import genai
from google.genai import types
from pydantic import BaseModel
from config import GEMINI_API_KEY, GEMINI_MODEL

_client = genai.Client(api_key=GEMINI_API_KEY)

class Pick(BaseModel):
    id: int
    priority: float   # 0-1: how much THIS reader should care
    why: str          # one line, max 12 words

def ai_editor(user, candidates):
    """candidates: list of (score, article, matched). Returns {id: Pick}, or {} on any failure."""
    payload = [{"id": a["id"], "title": a["title"], "summary": a["summary"],
                "topics": a["topics"]} for _, a, _ in candidates]
    prompt = f"""You are the personal editor of a daily newspaper for {user['name']}, a {user['persona']}.
Their interests, with learned weights (higher = cares more): {user['interests']}
Topics they want to avoid: {user['avoid_topics']}

For each article, return its id, a priority from 0 to 1 for how much THIS reader would want it
on their front page, and a "why" of at most 12 words, addressed to the reader ("Because...").
Judge by meaning and relevance to their role, not just keywords.

Articles: {json.dumps(payload)}"""
    try:
        resp = _client.models.generate_content(
            model=GEMINI_MODEL, contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[Pick], temperature=0.2))
        return {p.id: p for p in resp.parsed}
    except Exception as ex:
        print(f"[editor] failed, using python ranking: {ex}")
        return {}