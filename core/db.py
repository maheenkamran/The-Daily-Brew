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
        user["interests"] = {r["topic"]: r["weight"] for r in c.execute(
            "SELECT topic, weight FROM user_interests WHERE user_id=?", (uid,))}
        return user

def list_users():
    with get_conn() as c:
        return [dict(r) for r in c.execute("SELECT id, name FROM users")]