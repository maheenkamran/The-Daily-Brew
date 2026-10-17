import sqlite3, json
from config import DB_PATH
import hashlib, os, secrets

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    persona TEXT,
    avoid_topics TEXT DEFAULT '[]',
    theme TEXT DEFAULT 'classic',
    password_hash TEXT,
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
    migrate_auth()
    
def create_user(name, persona, interests, avoid, password_hash=None, theme="classic"):
    with get_conn() as c:
        cur = c.execute(
            "INSERT INTO users (name, persona, avoid_topics, password_hash, theme) VALUES (?,?,?,?,?)",
            (name, persona, json.dumps(avoid), password_hash, theme))
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
        user["avoid_topics"] = json.loads(user["avoid_topics"] or "[]")
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

def get_user_by_name(name):
    if not name:
        return None
    with get_conn() as c:
        row = c.execute("SELECT id FROM users WHERE LOWER(name) = LOWER(?)", (name.strip(),)).fetchone()
        if not row:
            return None
        return get_user(row["id"])

def update_user_password(uid, password_hash):
    with get_conn() as c:
        c.execute("UPDATE users SET password_hash=? WHERE id=?", (password_hash, uid))

def list_users():
    with get_conn() as c:
        return [dict(r) for r in c.execute("SELECT id, name, persona FROM users")]
    
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
        
# ---------- auth ----------
def migrate_auth():
    with get_conn() as c:
        cols = {r["name"] for r in c.execute("PRAGMA table_info(users)")}
        for col in ("username", "pw_hash", "token"):
            if col not in cols:
                c.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username)")

def _hash(pw, salt=None):
    salt = salt or os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 200_000)
    return salt.hex() + ":" + h.hex()

def _verify(pw, stored):
    salt_hex, h = stored.split(":")
    return secrets.compare_digest(_hash(pw, bytes.fromhex(salt_hex)).split(":")[1], h)

def register(username, password):
    """Returns (user_id, error)."""
    username = username.strip().lower()
    try:
        with get_conn() as c:
            cur = c.execute("INSERT INTO users (name, username, pw_hash) VALUES (?,?,?)",
                            (username.title(), username, _hash(password)))
            return cur.lastrowid, None
    except sqlite3.IntegrityError:
        return None, "That username is already taken."

def login(username, password):
    with get_conn() as c:
        r = c.execute("SELECT id, pw_hash FROM users WHERE username=?",
                      (username.strip().lower(),)).fetchone()
    if not r or not r["pw_hash"] or not _verify(password, r["pw_hash"]):
        return None
    return r["id"]

def set_credentials(uid, username, password):
    with get_conn() as c:
        c.execute("UPDATE users SET username=?, pw_hash=? WHERE id=?",
                  (username.strip().lower(), _hash(password), uid))

def issue_token(uid):
    t = secrets.token_urlsafe(24)
    with get_conn() as c:
        c.execute("UPDATE users SET token=? WHERE id=?", (t, uid))
    return t

def clear_token(uid):
    with get_conn() as c:
        c.execute("UPDATE users SET token=NULL WHERE id=?", (uid,))

def user_by_token(t):
    with get_conn() as c:
        r = c.execute("SELECT id FROM users WHERE token=?", (t,)).fetchone()
    return get_user(r["id"]) if r else None

def save_profile(uid, name, persona, interests, avoid):
    with get_conn() as c:
        c.execute("UPDATE users SET name=?, persona=?, avoid_topics=? WHERE id=?",
                  (name, persona, json.dumps(avoid), uid))
        c.execute("DELETE FROM user_interests WHERE user_id=?", (uid,))
        c.executemany("INSERT INTO user_interests (user_id, topic, weight) VALUES (?,?,1.0)",
                      [(uid, t) for t in interests])