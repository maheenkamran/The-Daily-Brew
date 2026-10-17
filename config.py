import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import date

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "morning_paper.db"
DATA_DIR.mkdir(exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"  # verify against current docs

PERSONAS = ["Software Engineer", "Investor", "Academic", "AI Researcher",
            "Student", "Founder", "Curious Reader"]


INTERESTS = ["Tech & AI", "Global Markets", "Startups", "Science",
             "Climate", "World News", "Health", "Space", "Cybersecurity", "Culture"]

AVOID_SUGGESTIONS = ["Celebrity Gossip", "Local Politics", "Sports",
                     "Crime", "Entertainment", "Elections"]

PERSONA_FOCUS = {
    "Software Engineer": ["Tech & AI", "Cybersecurity"],
    "Investor":          ["Global Markets", "Startups"],
    "Academic":          ["Science", "Climate"],
    "AI Researcher":     ["Tech & AI", "Science"],
    "Student":           ["Science", "World News"],
    "Founder":           ["Startups", "Tech & AI"],
    "Curious Reader":    ["World News", "Culture"],
}

SECTIONS = ["Front Page", "Tech & Code", "Deep Dives", "Quick Briefs"]

TODAY = lambda: date.today().isoformat()

FEEDS = {
    "BBC News":     "https://feeds.bbci.co.uk/news/world/rss.xml",
    "BBC Tech":     "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "NPR":          "https://feeds.npr.org/1001/rss.xml",
    "Al Jazeera":   "https://www.aljazeera.com/xml/rss/all.xml",
    "TechCrunch":   "https://techcrunch.com/feed/",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
    "The Verge":    "https://www.theverge.com/rss/index.xml",
    "Hacker News":  "https://hnrss.org/frontpage",
}

GOOGLE_NEWS = "https://news.google.com/rss/search?q={q}+when:2d&hl=en-US&gl=US&ceid=US:en"

MAX_PER_FEED = 10        # per generic feed
MAX_PER_INTEREST = 8     # per Google News interest search
BATCH_SIZE = 15          # articles per Gemini call
MAX_ARTICLES = 90        # hard cap per run, protects free-tier quota

from datetime import date

TODAY = lambda: date.today().isoformat()      # from Phase 2

SECTIONS = ["Front Page", "Tech & Code", "Deep Dives", "Quick Briefs"]   # from Phase 1

AI_POOL = 20                                  # new in Phase 3

TIMEZONE = "Asia/Karachi"
REFRESH_HOUR = 9 # 9 am 
