from flask import Flask, render_template, request, redirect, url_for, session, flash
import os, sys
from werkzeug.security import generate_password_hash, check_password_hash
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.database import top_scores, save_score, ensure_db, create_user, get_user, prune_scores_older_than
import threading, time
ensure_db()
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')


@app.route('/')
def index():
    scores = top_scores()
    user = session.get('user')
    return render_template('index.html', scores=scores, user=user)


@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return redirect(url_for('index'))
    ph = generate_password_hash(password)
    ok = create_user(username, ph)
    if ok:
        session['user'] = username
    else:
        flash('Username already taken')
    return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    row = get_user(username)
    if row and check_password_hash(row[2], password):
        session['user'] = username
    else:
        flash('Invalid username or password')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/submit', methods=['POST'])
def submit():
    session_user = session.get('user')
    name = session_user or request.form.get('name', 'Player')
    depth = int(request.form.get('depth', 0))
    try:
        oxygen = int(request.form.get('oxygen', 0))
    except Exception:
        oxygen = 0
# pokud je uživatel přihlášen přes relaci, přijme; jinak vyžaduje API token
    if session_user:
        save_score(name, depth, oxygen)
        return redirect(url_for('index'))
# anonymní odeslání musí poskytnout token odpovídající POTAPEC_WEB_TOKEN
    token = request.form.get('token', '')
    expected = os.environ.get('POTAPEC_WEB_TOKEN', '')
    if expected and token and token == expected:
        save_score(name, depth, oxygen)
    else:
        flash('Missing or invalid API token for anonymous submit')
    return redirect(url_for('index'))
    return redirect(url_for('index'))


if __name__ == '__main__':
    try:
        port = int(os.environ.get('POTAPEC_WEB_PORT', os.environ.get('PORT', 5000)))
    except Exception:
        port = 5000
# zahájit vlákno prořezávání pozadí pro odstranění skóre starších než 24 hodin
    def _prune_loop():
# spustit ihned jednou, poté každou hodinu
        while True:
            try:
                ok = prune_scores_older_than(24)
                print(f"[prune] prune_scores_older_than ran, success={ok}")
            except Exception as e:
                print(f"[prune] error: {e}")
            time.sleep(3600)

    t = threading.Thread(target=_prune_loop, daemon=True)
    t.start()

    app.run(debug=True, port=port)
