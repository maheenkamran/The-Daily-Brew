import os
from pathlib import Path
from datetime import datetime
from gtts import gTTS
from config import BASE_DIR, GEMINI_API_KEY, GEMINI_MODEL

AUDIO_DIR = BASE_DIR / "data" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
_GEMINI_AVAILABLE = True


def _clean_text_for_speech(text: str) -> str:
    """Prepares text for natural speech synthesis."""
    if not text:
        return ""
    # Remove markdown formatting, excessive punctuation, brackets
    text = text.replace("**", "").replace("*", "").replace("`", "")
    text = text.replace("[", "").replace("]", "").replace("—", ", ")
    text = text.replace("&amp;", "and").replace("&", "and")
    return " ".join(text.split())


def build_broadcast_script(user: dict, day: str, layout: dict, arts: dict) -> str:
    """Generates an authentic, engaging vintage radio broadcast script for the day's paper."""
    nice_date = datetime.strptime(day, "%Y-%m-%d").strftime("%A, %B %d, %Y")
    lead_id = layout.get("lead")
    lead_art = arts.get(lead_id)

    lead_title = lead_art.get("title", "") if lead_art else "Today's top headline"
    lead_sum = lead_art.get("summary", "") if lead_art else ""
    lead_source = lead_art.get("source", "the global wire") if lead_art else "the wire"

    # Front stories
    front_ids = [i for i in layout.get("front", []) if i != lead_id and i in arts][:2]
    front_stories = [arts[i] for i in front_ids]

    # Outside bubble / Explore story
    explore_ids = layout.get("sections", {}).get("Outside Your Bubble", [])
    explore_art = arts.get(explore_ids[0]) if explore_ids and explore_ids[0] in arts else None

    # Try Gemini flash first if quota available, otherwise use our deterministic broadcaster
    global _GEMINI_AVAILABLE
    if _GEMINI_AVAILABLE:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=GEMINI_API_KEY)
            prompt = f"""Write a charismatic 90-second vintage radio morning news dispatch script.
Broadcaster: The Daily Brew Radio Desk (vintage 1940s BBC wireless style).
Listener: {user['name']}, who is a {user['persona']}.
Date: {nice_date}.
Lead Story ({lead_source}): {lead_title}. Summary: {lead_sum}.
Other front stories: {'; '.join(a['title'] + ' (' + a['source'] + ')' for a in front_stories)}.
Outside their circle: {explore_art['title'] if explore_art else 'N/A'}.

Instructions:
- Keep it under 200 words.
- Address {user['name']} warmly at the start.
- Give the big picture takeaways concisely.
- No asterisks, markdown, or sound effect brackets. Pure spoken sentences."""
            resp = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.4)
            )
            script = resp.text.strip()
            if len(script) > 80:
                return _clean_text_for_speech(script)
        except Exception:
            _GEMINI_AVAILABLE = False

    # Authoritative vintage radio algorithmic fallback
    paragraphs = []
    paragraphs.append(
        f"Good morning, {user['name']}. This is The Daily Brew Wireless Dispatch for {nice_date}, "
        f"reporting live to your desk for your morning coffee."
    )
    if lead_art:
        paragraphs.append(
            f"Leading today's front page from {lead_source}: {lead_title}. "
            f"{lead_sum}"
        )
    for a in front_stories:
        sum_first = (a.get("summary") or "").split(". ")[0].strip()
        paragraphs.append(
            f"Across the wire from {a.get('source', 'the wire')}: {a['title']}. {sum_first}."
        )
    if explore_art:
        explore_sum = (explore_art.get("summary") or "").split(". ")[0].strip()
        paragraphs.append(
            f"Broadening your horizon today outside your customary reading circle: {explore_art['title']}, "
            f"reported by {explore_art.get('source', 'our international correspondents')}. {explore_sum}."
        )
    paragraphs.append(
        f"That concludes your morning audio dispatch. Your personal broadsheet edition is laid out below. "
        f"Have a productive and inspired day."
    )
    return _clean_text_for_speech(" ".join(paragraphs))


def get_or_create_broadcast(user: dict, day: str, layout: dict, arts: dict) -> tuple[bytes, str]:
    """Returns (audio_bytes, transcript_text). Uses disk caching for instantaneous loading."""
    uid = user["id"]
    audio_path = AUDIO_DIR / f"broadcast_{uid}_{day}.mp3"
    txt_path = AUDIO_DIR / f"broadcast_{uid}_{day}.txt"

    if audio_path.exists() and txt_path.exists():
        try:
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            with open(txt_path, "r", encoding="utf-8") as f:
                transcript = f.read()
            if len(audio_bytes) > 1000:
                return audio_bytes, transcript
        except Exception:
            pass

    # Generate script
    script = build_broadcast_script(user, day, layout, arts)

    # Synthesize audio with crisp British morning wireless accent
    tts = gTTS(text=script, lang="en", tld="co.uk")
    tts.save(str(audio_path))

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(script)

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    return audio_bytes, script


def get_story_audio(article: dict) -> bytes:
    """Generates a 15-second individual audio narration for a single article."""
    aid = article["id"]
    audio_path = AUDIO_DIR / f"story_{aid}.mp3"

    if audio_path.exists():
        try:
            with open(audio_path, "rb") as f:
                data = f.read()
            if len(data) > 1000:
                return data
        except Exception:
            pass

    title = article.get("title", "")
    source = article.get("source", "The wire")
    summary = article.get("summary", "")
    text = f"{title}. Reported by {source}. {summary}"
    clean = _clean_text_for_speech(text)

    tts = gTTS(text=clean, lang="en", tld="co.uk")
    tts.save(str(audio_path))

    with open(audio_path, "rb") as f:
        return f.read()


def ask_editor(user: dict, question: str, layout: dict, arts: dict) -> str:
    """Answers a reader's question about today's edition like an authentic chief editor."""
    question = question.strip()
    if not question:
        return "Please send a dispatch question to the editor."

    # Prepare context from today's edition
    articles_context = []
    for aid, a in arts.items():
        articles_context.append(
            f"Title: {a.get('title')}\nSource: {a.get('source')}\nSummary: {a.get('summary')}\nSection: {a.get('section')}\nTopics: {a.get('topics')}"
        )
    context_str = "\n---\n".join(articles_context[:14])

    global _GEMINI_AVAILABLE
    if _GEMINI_AVAILABLE:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            prompt = f"""You are the Chief Editor of 'The Daily Brew', the personal morning newspaper for {user['name']} ({user['persona']}).
Answer the reader's inquiry in a witty, distinguished, authoritative vintage editorial voice.
Ground your response directly in the stories published in today's edition. Mention specific sources or article titles where applicable.

Reader's Question: {question}

Today's Edition Articles:
{context_str}

Format your reply concisely (2 to 4 sentences or 3 sharp bullet points)."""
            resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            if resp.text:
                return resp.text.strip()
        except Exception:
            _GEMINI_AVAILABLE = False

    # Intelligent semantic fallback
    q_lower = question.lower()
    matches = []
    for aid, a in arts.items():
        text = f"{a.get('title', '')} {a.get('summary', '')} {' '.join(a.get('topics', []))}".lower()
        score = sum(1 for word in q_lower.split() if len(word) > 3 and word in text)
        if score > 0:
            matches.append((score, a))

    matches.sort(key=lambda x: -x[0])

    if matches:
        top_matches = [m[1] for m in matches[:2]]
        bullets = []
        for a in top_matches:
            bullets.append(f"• **{a.get('source')}**: *{a.get('title')}* — {a.get('summary')}")
        reply = (
            f"From the News Desk regarding **'{question}'**:\n\n"
            f"Our correspondents are following relevant developments in today's paper:\n\n"
            + "\n\n".join(bullets)
            + f"\n\n*Editorial note for {user['persona']}*: These shifts directly influence your industry compass. We will monitor the wire for tomorrow's edition."
        )
        return reply

    lead_id = layout.get("lead")
    lead_art = arts.get(lead_id)
    return (
        f"Telegram from the Chief Editor:\n\n"
        f"Thank you for your dispatch regarding *'{question}'*. Today's lead coverage centers on "
        f"**{lead_art.get('title')}** reported by {lead_art.get('source')}. "
        f"We have noted your interest and will deploy our wire correspondents to capture deeper updates for tomorrow's morning edition."
    )
