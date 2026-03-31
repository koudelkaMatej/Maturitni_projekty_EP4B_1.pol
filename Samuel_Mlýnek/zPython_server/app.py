"""
Muskets & Swords: New Dawn — Unified Server
Flask backend serving the game portal website AND the Godot game API.

Run:   python app.py
Open:  http://localhost:5000
"""

from flask import Flask, request, jsonify, render_template, session
import sqlite3
import json
import hashlib
import secrets
import re
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)   # change to a fixed string in production!

DB_PATH = "zPython_server/database.db"

# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def validate_username(u: str) -> str | None:
    """Return error string or None if valid."""
    if not u or len(u) < 3:
        return "Username must be at least 3 characters."
    if len(u) > 32:
        return "Username must be 32 characters or fewer."
    if not re.match(r'^[A-Za-z0-9_\-\.]+$', u):
        return "Username may only contain letters, numbers, _ - and ."
    return None

def validate_password(p: str) -> str | None:
    if not p or len(p) < 6:
        return "Password must be at least 6 characters."
    if len(p) > 128:
        return "Password too long."
    return None

def require_token(f):
    """Decorator — checks X-Auth-Token header against tokens table."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-Auth-Token") or request.json.get("token") if request.is_json else None
        if not token:
            return jsonify({"status": "error", "msg": "Missing auth token"}), 401
        conn = get_db()
        row = conn.execute("SELECT player_id FROM tokens WHERE token=?", (token,)).fetchone()
        conn.close()
        if not row:
            return jsonify({"status": "error", "msg": "Invalid or expired token"}), 401
        request.player_id = row["player_id"]
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────────────────────────────────────────
#  DATABASE INIT
# ─────────────────────────────────────────────────────────────────────────────

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name     TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS tokens (
        token     TEXT PRIMARY KEY,
        player_id INTEGER NOT NULL,
        created   DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(player_id) REFERENCES players(id)
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS levels (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        level_number INTEGER,
        grid         TEXT,
        enemy_gold   INTEGER,
        turn_type    TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS player_levels (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id   INTEGER NOT NULL,
        level_id    INTEGER NOT NULL,
        player_gold INTEGER DEFAULT 0,
        turn_number INTEGER DEFAULT 0,
        completed   INTEGER DEFAULT 0,
        score       INTEGER DEFAULT 0,
        save_data   TEXT,
        FOREIGN KEY(player_id) REFERENCES players(id),
        FOREIGN KEY(level_id)  REFERENCES levels(id)
    )""")

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
#  WEBSITE ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

# ─────────────────────────────────────────────────────────────────────────────
#  WEBSITE API  (called by the frontend JS)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/leaderboard")
def api_leaderboard():
    conn = get_db()
    rows = conn.execute("""
        SELECT
            p.name                            AS username,
            COALESCE(SUM(pl.score), 0)        AS score,
            COALESCE(SUM(pl.completed), 0)    AS levels_completed
        FROM players p
        LEFT JOIN player_levels pl ON pl.player_id = p.id
        GROUP BY p.id
        ORDER BY score DESC, levels_completed DESC
        LIMIT 20
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/stats/<username>")
def api_stats(username):
    conn = get_db()
    player = conn.execute("SELECT id FROM players WHERE name=?", (username,)).fetchone()
    if not player:
        conn.close()
        return jsonify({"status": "error", "msg": "Player not found"}), 404

    rows = conn.execute("""
        SELECT
            pl.level_id,
            pl.player_gold,
            pl.turn_number,
            pl.completed,
            pl.score
        FROM player_levels pl
        WHERE pl.player_id=?
        ORDER BY pl.level_id
    """, (player["id"],)).fetchall()
    conn.close()
    return jsonify({
        "status":   "ok",
        "username": username,
        "levels":   [dict(r) for r in rows]
    })

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    err = validate_username(username) or validate_password(password)
    if err:
        return jsonify({"ok": False, "message": err})

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO players (name, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"ok": False, "message": "Username already taken."})
    conn.close()
    return jsonify({"ok": True, "message": f"Welcome to the front, Commander {username}!"})

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"ok": False, "message": "Fill in all fields."})

    conn = get_db()
    player = conn.execute(
        "SELECT id FROM players WHERE name=? AND password=?",
        (username, hash_password(password))
    ).fetchone()

    if not player:
        conn.close()
        return jsonify({"ok": False, "message": "Invalid username or password."})

    token = secrets.token_hex(32)
    conn.execute("INSERT INTO tokens (token, player_id) VALUES (?, ?)", (token, player["id"]))
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "username": username, "token": token})

# ─────────────────────────────────────────────────────────────────────────────
#  GAME API  (called by Godot via HTTPRequest)
#  All protected routes expect header:  X-Auth-Token: <token>
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/game/login", methods=["POST"])
def game_login():
    """Godot login — returns a token the game stores and sends with every request."""
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    print(f"[LOGIN] attempt → username='{username}'")

    if not username or not password:
        print(f"[LOGIN] FAIL — missing credentials")
        return jsonify({"status": "error", "msg": "Missing credentials"}), 400

    conn = get_db()
    player = conn.execute(
        "SELECT id FROM players WHERE name=? AND password=?",
        (username, hash_password(password))
    ).fetchone()

    if not player:
        conn.close()
        print(f"[LOGIN] FAIL — wrong username or password for '{username}'")
        return jsonify({"status": "error", "msg": "Invalid credentials"}), 401

    token = secrets.token_hex(32)
    conn.execute("INSERT INTO tokens (token, player_id) VALUES (?, ?)", (token, player["id"]))
    conn.commit()
    conn.close()
    print(f"[LOGIN] OK — '{username}' logged in, player_id={player['id']}")
    return jsonify({"status": "ok", "username": username, "token": token})

@app.route("/game/register", methods=["POST"])
def game_register():
    """Godot registration."""
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    print(f"[REGISTER] attempt → username='{username}'")

    err = validate_username(username) or validate_password(password)
    if err:
        print(f"[REGISTER] FAIL — validation error: {err}")
        return jsonify({"status": "error", "msg": err}), 400

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO players (name, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        print(f"[REGISTER] FAIL — username '{username}' already taken")
        return jsonify({"status": "error", "msg": "Username already taken"}), 400
    conn.close()
    print(f"[REGISTER] OK — '{username}' registered successfully")
    return jsonify({"status": "ok"})

@app.route("/game/save", methods=["POST"])
@require_token
def game_save():
    """Save game state. Godot sends X-Auth-Token header."""
    data = request.json or {}
    save     = data.get("save") or {}
    level_id = int(data.get("level_id", 1))
    score    = int(data.get("score", 0))

    print(f"[SAVE] player_id={request.player_id} level_id={level_id} score={score} turn={save.get('turn_number')} gold={save.get('player_gold')}")

    conn = get_db()
    conn.execute("""
        DELETE FROM player_levels
        WHERE player_id=? AND level_id=?
    """, (request.player_id, level_id))

    conn.execute("""
        INSERT INTO player_levels
            (player_id, level_id, player_gold, turn_number, completed, score, save_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        request.player_id,
        level_id,
        save.get("player_gold", 0),
        save.get("turn_number", 0),
        int(save.get("completed", 0)),
        score,
        json.dumps(save)
    ))
    conn.commit()
    conn.close()
    print(f"[SAVE] OK — saved to database")
    return jsonify({"status": "ok"})

@app.route("/game/load", methods=["POST"])
@require_token
def game_load():
    """Load game state."""
    data     = request.json or {}
    level_id = int(data.get("level_id", 1))

    print(f"[LOAD] player_id={request.player_id} level_id={level_id}")

    conn = get_db()
    row = conn.execute("""
        SELECT save_data FROM player_levels
        WHERE player_id=? AND level_id=?
    """, (request.player_id, level_id)).fetchone()
    conn.close()

    if not row or not row["save_data"]:
        print(f"[LOAD] no save found for player_id={request.player_id} level_id={level_id}")
        return jsonify({"status": "empty"})

    print(f"[LOAD] OK — save data found and returned")
    return jsonify({"status": "ok", "save": json.loads(row["save_data"])})

@app.route("/game/result", methods=["POST"])
@require_token
def game_result():
    """Record final level result from Godot."""
    data = request.json or {}
    print(f"[RESULT] player_id={request.player_id} data={data}")
    return jsonify({"status": "ok"})

# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("""
  ╔═══════════════════════════════════════════════════╗
  ║  Muskets & Swords: New Dawn  —  Unified Server    ║
  ║  Website  →  http://localhost:5000                ║
  ║  Game API →  http://localhost:5000/game/...       ║
  ║  Press Ctrl+C to stop                             ║
  ╚═══════════════════════════════════════════════════╝
""")
    app.run(debug=True, port=5000)
