import sqlite3, os
try:
    from game.settings import DB_FILE
except Exception:
    try:
        from potapec.game.settings import DB_FILE
    except Exception:
        DB_FILE = os.environ.get('POTAPEC_DB_FILE', 'potapec_scores.db')
def ensure_db(path=DB_FILE):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    con = sqlite3.connect(path); cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY, name TEXT, depth INTEGER, oxygen INTEGER, created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password_hash TEXT,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    con.commit(); con.close()
def save_score(name, depth, oxygen, path=DB_FILE):
    con = sqlite3.connect(path); cur = con.cursor()
    cur.execute('INSERT INTO scores (name, depth, oxygen) VALUES (?,?,?)', (name, depth, oxygen))
    con.commit(); con.close()
def top_scores(limit=10, path=DB_FILE):
    con = sqlite3.connect(path); cur = con.cursor()
    # Získejte pouze nejlepší skóre na hráče a seřaďte je podle hloubky sestupně
    cur.execute('''
        SELECT name, depth, oxygen, created FROM scores 
        WHERE (name, depth) IN (
            SELECT name, MAX(depth) FROM scores GROUP BY name
        )
        ORDER BY depth DESC LIMIT ?
    ''', (limit,))
    rows = cur.fetchall(); con.close(); return rows

def create_user(username, password_hash, path=DB_FILE):
    con = sqlite3.connect(path); cur = con.cursor()
    try:
        cur.execute('INSERT INTO users (username, password_hash) VALUES (?,?)', (username, password_hash))
        con.commit()
        return True
    except Exception:
        return False
    finally:
        con.close()

def get_user(username, path=DB_FILE):
    con = sqlite3.connect(path); cur = con.cursor()
    cur.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
    row = cur.fetchone(); con.close(); return row


def prune_scores_older_than(hours=24, path=DB_FILE):
    """Delete scores older than `hours` hours from the database.

    Uses SQLite datetime('now', '-{hours} hours') to compare the `created` timestamp.
    """
    try:
        con = sqlite3.connect(path); cur = con.cursor()
        modifier = f'-{int(hours)} hours'
        cur.execute("DELETE FROM scores WHERE created < datetime('now', ?)", (modifier,))
        con.commit()
        con.close()
        return True
    except Exception:
        try:
            con.close()
        except Exception:
            pass
        return False
