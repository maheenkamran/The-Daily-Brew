import sqlite3, json
from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    persona TEXT,
    avoid_topics TEXT DEFAULT '[]',
    theme TEXT DEFAULT 'classic',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS user_interests (
    user_id INTEGER, topic TEXT, weight REAL DEFAULT 1.0,
    PRIMARY KEY (user_id, topic)
);
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE, title TEXT, source TEXT, published TEXT,
    summary TEXT, section TEXT, topics TEXT DEFAULT '[]',
    quality_score REAL DEFAULT 0.5, fetched_date TEXT
);
CREATE TABLE IF NOT EXISTS editions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, date TEXT, layout TEXT,
    UNIQUE (user_id, date)
);
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, article_id INTEGER, action TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS interest_deltas (
    user_id INTEGER, topic TEXT, delta REAL,
    PRIMARY KEY (user_id, topic)
);
"""

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as c:
        c.executescript(SCHEMA)

def create_user(name, persona, interests, avoid):
    with get_conn() as c:
        cur = c.execute(
            "INSERT INTO users (name, persona, avoid_topics) VALUES (?,?,?)",
            (name, persona, json.dumps(avoid)))
        uid = cur.lastrowid
        c.executemany(
            "INSERT INTO user_interests (user_id, topic, weight) VALUES (?,?,1.0)",
            [(uid, t) for t in interests])
    return uid

def get_user(uid):
    with get_conn() as c:
        row = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        if not row:
            return None
        user = dict(row)
        user["avoid_topics"] = json.loads(user["avoid_topics"])
        base = {r["topic"]: r["weight"] for r in c.execute(
            "SELECT topic, weight FROM user_interests WHERE user_id=?", (uid,))}
        deltas = {r["topic"]: r["delta"] for r in c.execute(
            "SELECT topic, delta FROM interest_deltas WHERE user_id=?", (uid,))}

    lower = {t.lower(): t for t in base}
    interests = dict(base)
    for t, d in deltas.items():
        key = lower.get(t.lower(), t)        # merge into a declared interest if same name
        interests[key] = interests.get(key, 0.0) + d
    user["interests"] = interests            # what rank.py and the editor see
    user["declared"] = list(base)            # what the user picked in onboarding
    return user

def list_users():
    with get_conn() as c:
        return [dict(r) for r in c.execute("SELECT id, name FROM users")]
    
def existing_urls():
    with get_conn() as c:
        return {r["url"] for r in c.execute("SELECT url FROM articles")}

def save_articles(rows):
    """rows: list of dicts with article columns."""
    with get_conn() as c:
        c.executemany(
            """INSERT OR IGNORE INTO articles
               (url, title, source, published, summary, section, topics, quality_score, fetched_date)
               VALUES (:url,:title,:source,:published,:summary,:section,:topics,:quality_score,:fetched_date)""",
            rows)

def get_articles_by_date(day):
    with get_conn() as c:
        rows = [dict(r) for r in c.execute(
            "SELECT * FROM articles WHERE fetched_date=?", (day,))]
    for r in rows:
        r["topics"] = json.loads(r["topics"])
    return rows

def all_interests():
    with get_conn() as c:
        return [r["topic"] for r in c.execute("SELECT DISTINCT topic FROM user_interests")]
    
def get_articles_since(day_iso):
    with get_conn() as c:
        rows = [dict(r) for r in c.execute(
            "SELECT * FROM articles WHERE fetched_date>=?", (day_iso,))]
    for r in rows:
        r["topics"] = json.loads(r["topics"] or "[]")
    return rows

def latest_article_date():
    with get_conn() as c:
        return c.execute("SELECT MAX(fetched_date) AS d FROM articles").fetchone()["d"]

def get_articles_by_ids(ids):
    if not ids:
        return []
    q = ",".join("?" * len(ids))
    with get_conn() as c:
        rows = [dict(r) for r in c.execute(f"SELECT * FROM articles WHERE id IN ({q})", list(ids))]
    for r in rows:
        r["topics"] = json.loads(r["topics"] or "[]")
    return rows

# ---- editions (frozen) ----
def save_edition(uid, day, layout):
    with get_conn() as c:
        c.execute("INSERT OR REPLACE INTO editions (user_id, date, layout) VALUES (?,?,?)",
                  (uid, day, json.dumps(layout)))

def get_edition(uid, day):
    with get_conn() as c:
        r = c.execute("SELECT layout FROM editions WHERE user_id=? AND date=?", (uid, day)).fetchone()
    return json.loads(r["layout"]) if r else None

def delete_edition(uid, day):
    with get_conn() as c:
        c.execute("DELETE FROM editions WHERE user_id=? AND date=?", (uid, day))

def list_edition_dates(uid):
    with get_conn() as c:
        return [r["date"] for r in c.execute(
            "SELECT date FROM editions WHERE user_id=? ORDER BY date DESC", (uid,))]

# ---- feedback + theme ----
def log_feedback(uid, aid, action):
    with get_conn() as c:
        if action in ("like", "dislike"):
            same = c.execute(
                "SELECT id FROM feedback WHERE user_id=? AND article_id=? AND action=?",
                (uid, aid, action)).fetchone()
            c.execute("DELETE FROM feedback WHERE user_id=? AND article_id=? AND action IN ('like','dislike')",
                      (uid, aid))
            if same:          # clicking again toggles it off
                return
        c.execute("INSERT INTO feedback (user_id, article_id, action) VALUES (?,?,?)",
                  (uid, aid, action))

def get_user_feedback(uid):
    out = {}
    with get_conn() as c:
        for r in c.execute("SELECT article_id, action FROM feedback WHERE user_id=?", (uid,)):
            out.setdefault(r["article_id"], set()).add(r["action"])
    return out

def update_theme(uid, theme):
    with get_conn() as c:
        c.execute("UPDATE users SET theme=? WHERE id=?", (theme, uid))
        
def feedback_with_topics(uid):
    with get_conn() as c:
        rows = c.execute(
            """SELECT f.action, a.topics FROM feedback f
               JOIN articles a ON a.id = f.article_id
               WHERE f.user_id=?""", (uid,)).fetchall()
    return [(r["action"], json.loads(r["topics"] or "[]")) for r in rows]

def replace_deltas(uid, deltas):
    with get_conn() as c:
        c.execute("DELETE FROM interest_deltas WHERE user_id=?", (uid,))
        c.executemany(
            "INSERT INTO interest_deltas (user_id, topic, delta) VALUES (?,?,?)",
            [(uid, t, d) for t, d in deltas.items()])
        
def get_deltas(uid):
    with get_conn() as c:
        return {r["topic"]: r["delta"] for r in c.execute(
            "SELECT topic, delta FROM interest_deltas WHERE user_id=?", (uid,))}