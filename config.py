import os
from pathlib import Path
from dotenv import load_dotenv

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

SECTIONS = ["Front Page", "Tech & Code", "Deep Dives", "Quick Briefs"]