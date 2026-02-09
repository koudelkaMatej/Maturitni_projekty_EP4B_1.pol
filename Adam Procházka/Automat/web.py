from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import json
from pathlib import Path

app = Flask(__name__)
app.secret_key = "maturita_secret_key_zmen_si_to"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
USERS_FILE = DATA_DIR / "users.json"
STATS_FILE = DATA_DIR / "stats.json"
LEADERBOARD_FILE = DATA_DIR / "leaderboard.json"


def load_json(path: Path, default):
    try:
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # když je soubor rozbitej, radši nespadni
        return default


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def current_user():
    return session.get("user")


@app.route("/")
def index():
    if current_user():
        return redirect(url_for("leaderboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        users = load_json(USERS_FILE, {})
        if username in users and check_password_hash(users[username]["password_hash"], password):
            session["user"] = username
            return redirect(url_for("leaderboard"))

        flash("Špatné jméno nebo heslo.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        if len(username) < 3:
            flash("Jméno musí mít alespoň 3 znaky.")
            return redirect(url_for("register"))
        if len(password) < 4:
            flash("Heslo musí mít alespoň 4 znaky.")
            return redirect(url_for("register"))
        if password != password2:
            flash("Hesla se neshodují.")
            return redirect(url_for("register"))

        users = load_json(USERS_FILE, {})
        if username in users:
            flash("Uživatel už existuje.")
            return redirect(url_for("register"))

        users[username] = {"password_hash": generate_password_hash(password)}
        save_json(USERS_FILE, users)

        session["user"] = username
        return redirect(url_for("leaderboard"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/leaderboard")
def leaderboard():
    if not current_user():
        return redirect(url_for("login"))

    lb = load_json(LEADERBOARD_FILE, [])
    rows = []
    if isinstance(lb, list):
        for item in lb:
            name = item.get("name") or item.get("user") or "?"
            score = item.get("score") or 0
            rows.append((name, score))
    elif isinstance(lb, dict):
        for name, score in lb.items():
            rows.append((name, score))

    rows.sort(key=lambda x: x[1], reverse=True)

    stats = load_json(STATS_FILE, {
        "total_spins": 0,
        "max_spins": 0,
        "jackpots": 0,
        "max_jackpot_streak": 0,
        "max_score_spin": 0,
        "lowest_score": None
    })

    return render_template("leaderboard.html", user=current_user(), rows=rows, stats=stats)

if __name__ == "__main__":
    app.run(debug=True)