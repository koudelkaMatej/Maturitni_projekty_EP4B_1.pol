from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import sqlite3
import hashlib
import secrets
import json
import os

DB_NAME = "snake_game.db"

# Aktivní sessions: { token: username }
sessions = {}


def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS uzivatele (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            datum_registrace TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS hry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skore INTEGER NOT NULL,
            datum TEXT DEFAULT (datetime('now','localtime')),
            username TEXT
        )
    """)

    try:
        c.execute("ALTER TABLE hry ADD COLUMN username TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_session_user(cookie_header):
    if not cookie_header:
        return None
    for part in cookie_header.split(";"):
        part = part.strip()
        if part.startswith("session="):
            token = part[8:]
            return sessions.get(token)
    return None


def uloz_session(username, token):
    with open("session.json", "w", encoding="utf-8") as f:
        json.dump({"username": username, "token": token}, f)


def smaz_session():
    if os.path.exists("session.json"):
        os.remove("session.json")


BASE_STYLE = """
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
  }
  .container {
    width: 100%;
    max-width: 720px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px;
    padding: 32px;
  }
  h1 { color: #22c55e; font-size: 2rem; text-align: center; margin-bottom: 8px; }
  .subtitle { text-align: center; color: #94a3b8; margin-bottom: 24px; }
  nav { display: flex; gap: 10px; justify-content: center; margin-bottom: 24px; flex-wrap: wrap; }
  nav a {
    color: #86efac;
    text-decoration: none;
    padding: 6px 16px;
    border: 1px solid rgba(34,197,94,0.4);
    border-radius: 8px;
    font-size: 0.9rem;
    transition: 0.2s;
  }
  nav a:hover { background: rgba(34,197,94,0.15); }
  nav a.active { background: rgba(34,197,94,0.25); }
  .form-group { margin-bottom: 16px; }
  label { display: block; color: #94a3b8; font-size: 0.85rem; margin-bottom: 6px; }
  input[type=text], input[type=password] {
    width: 100%;
    padding: 10px 14px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 8px;
    color: white;
    font-size: 1rem;
  }
  input:focus { outline: none; border-color: #22c55e; }
  .btn {
    display: inline-block;
    padding: 10px 24px;
    background: #22c55e;
    color: #0f172a;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: bold;
    cursor: pointer;
    text-decoration: none;
    transition: 0.2s;
  }
  .btn:hover { background: #16a34a; }
  .btn-secondary {
    background: transparent;
    color: #86efac;
    border: 1px solid rgba(34,197,94,0.4);
  }
  .btn-secondary:hover { background: rgba(34,197,94,0.15); }
  .error { color: #f87171; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.3); border-radius: 8px; padding: 10px 14px; margin-bottom: 16px; font-size: 0.9rem; }
  .success { color: #86efac; background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); border-radius: 8px; padding: 10px 14px; margin-bottom: 16px; font-size: 0.9rem; }
  table { width: 100%; border-collapse: collapse; margin-top: 8px; }
  th, td { padding: 12px 14px; text-align: left; }
  th { background: rgba(34,197,94,0.2); color: #86efac; font-size: 0.9rem; }
  tr { background: rgba(255,255,255,0.04); }
  tr:nth-child(even) { background: rgba(255,255,255,0.07); }
  tr:hover { background: rgba(34,197,94,0.12); }
  td { color: #e2e8f0; border-bottom: 1px solid rgba(255,255,255,0.06); }
  .medal { font-size: 1.1rem; }
  .empty { text-align: center; color: #94a3b8; padding: 20px; }
  .footer { text-align: center; color: #475569; font-size: 0.8rem; margin-top: 24px; }
  .form-card { max-width: 400px; margin: 0 auto; }
  .form-footer { text-align: center; margin-top: 16px; color: #94a3b8; font-size: 0.9rem; }
  .form-footer a { color: #86efac; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
  .badge-you { background: rgba(34,197,94,0.2); color: #86efac; border: 1px solid rgba(34,197,94,0.4); }
  .logged-in-info { text-align: center; color: #86efac; font-size: 0.85rem; margin-bottom: 16px; padding: 8px; background: rgba(34,197,94,0.08); border-radius: 8px; }
</style>
"""


def nav_html(current_user):
    if current_user:
        return f"""
        <nav>
          <a href="/" class="active">Žebříček</a>
          <a href="/moje">Moje skóre</a>
          <a href="/logout" class="btn-secondary" style="padding:6px 16px">Odhlásit ({current_user})</a>
        </nav>"""
    else:
        return """
        <nav>
          <a href="/" class="active">Žebříček</a>
          <a href="/login">Přihlásit se</a>
          <a href="/register">Registrace</a>
        </nav>"""


def page(title, body, current_user=None):
    return f"""<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} – Snake</title>
  {BASE_STYLE}
</head>
<body>
<div class="container">
  <h1>🐍 Snake Leaderboard</h1>
  {nav_html(current_user)}
  {body}
  <div class="footer">Snake game databáze</div>
</div>
</body>
</html>"""


def page_leaderboard(current_user):
    conn = get_conn()
    rows = conn.execute(
        "SELECT skore, datum, username FROM hry ORDER BY skore DESC LIMIT 50"
    ).fetchall()
    conn.close()

    medals = ["🥇", "🥈", "🥉"]

    if current_user:
        info = f'<div class="logged-in-info">Přihlášen jako <strong>{current_user}</strong> – tvoje skóre se ukládají automaticky</div>'
    else:
        info = '<div class="logged-in-info" style="color:#94a3b8;">Nejsi přihlášen – skóre se ukládají anonymně</div>'

    if rows:
        table = """<table>
          <tr><th>Pořadí</th><th>Hráč</th><th>Skóre</th><th>Datum</th></tr>"""
        for i, row in enumerate(rows, 1):
            medal = medals[i - 1] if i <= 3 else f"{i}."
            uname = row["username"] or "?"
            you = f' <span class="badge badge-you">ty</span>' if uname == current_user else ""
            table += f"""
          <tr>
            <td><span class="medal">{medal}</span></td>
            <td>{uname}{you}</td>
            <td><strong>{row['skore']}</strong></td>
            <td style="color:#94a3b8;font-size:0.85rem">{row['datum']}</td>
          </tr>"""
        table += "</table>"
    else:
        table = '<div class="empty">Zatím nejsou žádné výsledky.</div>'

    return page("Žebříček", info + table, current_user)


def page_my_scores(current_user):
    if not current_user:
        return None

    conn = get_conn()
    rows = conn.execute(
        "SELECT skore, datum FROM hry WHERE username=? ORDER BY skore DESC",
        (current_user,)
    ).fetchall()
    best = conn.execute(
        "SELECT MAX(skore) as m FROM hry WHERE username=?", (current_user,)
    ).fetchone()
    conn.close()

    best_score = best["m"] or 0

    html = f"""
    <div style="margin-bottom:20px;padding:16px;background:rgba(34,197,94,0.08);border-radius:12px;border:1px solid rgba(34,197,94,0.2);">
      <div style="color:#94a3b8;font-size:0.85rem;margin-bottom:4px;">Tvoje nejlepší skóre</div>
      <div style="font-size:2rem;font-weight:bold;color:#22c55e;">{best_score}</div>
    </div>"""

    if rows:
        html += """<table>
          <tr><th>#</th><th>Skóre</th><th>Datum</th></tr>"""
        for i, row in enumerate(rows, 1):
            html += f"<tr><td>{i}.</td><td><strong>{row['skore']}</strong></td><td style='color:#94a3b8;font-size:0.85rem'>{row['datum']}</td></tr>"
        html += "</table>"
    else:
        html += '<div class="empty">Zatím nemáš žádné výsledky.</div>'

    return page("Moje skóre", html, current_user)


def page_login(error=None):
    err = f'<div class="error">{error}</div>' if error else ""
    body = f"""<div class="form-card">
      <div class="subtitle">Přihlásit se do Snake</div>
      {err}
      <form method="POST" action="/login">
        <div class="form-group"><label>Uživatelské jméno</label><input type="text" name="username" required autofocus></div>
        <div class="form-group"><label>Heslo</label><input type="password" name="password" required></div>
        <button type="submit" class="btn" style="width:100%">Přihlásit se</button>
      </form>
      <div class="form-footer">Nemáš účet? <a href="/register">Registruj se</a></div>
    </div>"""
    return page("Přihlášení", body)


def page_register(error=None):
    err = f'<div class="error">{error}</div>' if error else ""
    body = f"""<div class="form-card">
      <div class="subtitle">Vytvořit nový účet</div>
      {err}
      <form method="POST" action="/register">
        <div class="form-group"><label>Uživatelské jméno</label><input type="text" name="username" required autofocus></div>
        <div class="form-group"><label>Heslo</label><input type="password" name="password" required></div>
        <div class="form-group"><label>Heslo znovu</label><input type="password" name="password2" required></div>
        <button type="submit" class="btn" style="width:100%">Registrovat se</button>
      </form>
      <div class="form-footer">Máš účet? <a href="/login">Přihlásit se</a></div>
    </div>"""
    return page("Registrace", body)


class Handler(BaseHTTPRequestHandler):

    def send_html(self, html, status=200, extra_headers=None):
        encoded = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(encoded)

    def redirect(self, location, extra_headers=None):
        self.send_response(302)
        self.send_header("Location", location)
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length).decode("utf-8")

    def current_user(self):
        return get_session_user(self.headers.get("Cookie"))

    def do_GET(self):
        path = urlparse(self.path).path
        user = self.current_user()

        if path == "/":
            self.send_html(page_leaderboard(user))

        elif path == "/login":
            if user:
                self.redirect("/")
            else:
                self.send_html(page_login())

        elif path == "/register":
            if user:
                self.redirect("/")
            else:
                self.send_html(page_register())

        elif path == "/moje":
            if not user:
                self.redirect("/login")
            else:
                self.send_html(page_my_scores(user))

        elif path == "/logout":
            cookie = self.headers.get("Cookie", "")
            for part in cookie.split(";"):
                part = part.strip()
                if part.startswith("session="):
                    token = part[8:]
                    sessions.pop(token, None)
            smaz_session()
            self.redirect("/", {"Set-Cookie": "session=; Max-Age=0; Path=/"})

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        body = self.read_body()
        params = parse_qs(body)

        def p(name):
            return params.get(name, [""])[0].strip()

        if path == "/login":
            username = p("username")
            password = p("password")

            conn = get_conn()
            row = conn.execute(
                "SELECT password_hash FROM uzivatele WHERE username=?",
                (username,)
            ).fetchone()
            conn.close()

            if row and row["password_hash"] == hash_password(password):
                token = secrets.token_hex(32)
                sessions[token] = username
                uloz_session(username, token)
                self.redirect("/", {"Set-Cookie": f"session={token}; Path=/; HttpOnly"})
            else:
                self.send_html(page_login("Špatné jméno nebo heslo."))

        elif path == "/register":
            username = p("username")
            password = p("password")
            password2 = p("password2")

            if len(username) < 3:
                self.send_html(page_register("Jméno musí mít alespoň 3 znaky."))
                return
            if len(password) < 4:
                self.send_html(page_register("Heslo musí mít alespoň 4 znaky."))
                return
            if password != password2:
                self.send_html(page_register("Hesla se neshodují."))
                return

            conn = get_conn()
            try:
                conn.execute(
                    "INSERT INTO uzivatele (username, password_hash) VALUES (?, ?)",
                    (username, hash_password(password))
                )
                conn.commit()
                conn.close()

                token = secrets.token_hex(32)
                sessions[token] = username
                uloz_session(username, token)
                self.redirect("/", {"Set-Cookie": f"session={token}; Path=/; HttpOnly"})
            except sqlite3.IntegrityError:
                conn.close()
                self.send_html(page_register("Toto jméno je již obsazené."))

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    init_db()
    print("Server běží na http://localhost:8000")
    HTTPServer(("localhost", 8000), Handler).serve_forever()
