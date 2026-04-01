from flask import Flask, render_template, jsonify, request, redirect, session, url_for
import sqlite3
import webbrowser
import hashlib

app = Flask(__name__)
app.secret_key = 'supersecret_localhost_1234'  # change to a secure key for production


def init_db():
    db = sqlite3.connect("dinnobird.db")
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT NOT NULL UNIQUE,
            score INTEGER NOT NULL
        )
    """)
    db.commit()
    db.close()


def get_scores():
    db = sqlite3.connect("dinnobird.db")
    scores = db.execute(
        "SELECT player, score FROM scores ORDER BY score DESC"
    ).fetchall()
    db.close()
    return scores


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def get_user(username):
    db = sqlite3.connect("dinnobird.db")
    row = db.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,)).fetchone()
    db.close()
    return row


def create_user(username, password):
    db = sqlite3.connect("dinnobird.db")
    pw_hash = hash_password(password)
    try:
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
        db.commit()
    except sqlite3.IntegrityError:
        db.close()
        return False
    db.close()
    return True


def update_score(player, score):
    db = sqlite3.connect("dinnobird.db")
    existing = db.execute("SELECT score FROM scores WHERE player = ?", (player,)).fetchone()
    if existing is None:
        db.execute("INSERT INTO scores (player, score) VALUES (?, ?)", (player, score))
    else:
        if score > existing[0]:
            db.execute("UPDATE scores SET score = ? WHERE player = ?", (score, player))
    db.commit()
    db.close()


@app.route('/scores.json')
def scores_json():
    rows = get_scores()
    return jsonify([{"player": r[0], "score": r[1]} for r in rows])


@app.route('/auth', methods=['POST'])
def auth():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    mode = request.form.get('mode', 'login')

    if not username or not password:
        return redirect(url_for('home', error='Vyplňte uživatelské jméno i heslo.'))

    user = get_user(username)

    if mode == 'register':
        if user is not None:
            return redirect(url_for('home', error='Uživatel již existuje.'))
        if not create_user(username, password):
            return redirect(url_for('home', error='Registrace selhala.'))
        session['username'] = username
        return redirect(url_for('home'))

    # login mode
    if user is None:
        return redirect(url_for('home', error='Uživatel není registrován.'))
    if hash_password(password) != user[2]:
        return redirect(url_for('home', error='Nesprávné heslo.'))

    session['username'] = username
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route("/")
def home():
    username = session.get('username')
    error = request.args.get('error')
    if username:
        return render_template("index.html", scores=get_scores(), username=username, error=error)
    else:
        return render_template("index.html", scores=[], username=None, error=error)


if __name__ == "__main__":
    init_db()
    webbrowser.open("http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000)
#Hotovo
