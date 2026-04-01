from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3, random, os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'pixel_bj_stand_2025'
DB = 'stand.db'

# ── Database ──────────────────────────────────────────────────────────────────
def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ── Admin credentials — change these! ─────────────────────────────────────────
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'Bober1234!'   # <-- změň si heslo!

def init_db():
    # Migrate: add columns if upgrading from old DB
    with db() as conn:
        cols = [r[1] for r in conn.execute('PRAGMA table_info(users)').fetchall()]
        for col, defn in [
            ('password_hash', 'TEXT NOT NULL DEFAULT ""'),
            ('is_admin',      'INTEGER DEFAULT 0'),
            ('is_banned',     'INTEGER DEFAULT 0'),
        ]:
            if col not in cols:
                conn.execute(f'ALTER TABLE users ADD COLUMN {col} {defn}')
        conn.commit()
    # Create / update admin account
    with db() as conn:
        ph = generate_password_hash(ADMIN_PASSWORD)
        existing = conn.execute('SELECT id FROM users WHERE username=?',(ADMIN_USERNAME,)).fetchone()
        if not existing:
            conn.execute('INSERT INTO users (username,password_hash,is_admin) VALUES (?,?,1)',
                         (ADMIN_USERNAME, ph))
        else:
            conn.execute('UPDATE users SET is_admin=1, password_hash=? WHERE username=?',
                         (ph, ADMIN_USERNAME))
        conn.commit()
    with db() as c:
        c.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL DEFAULT '',
                chips INTEGER DEFAULT 500,
                is_admin INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                result TEXT NOT NULL,
                player_score INTEGER,
                dealer_score INTEGER,
                bet INTEGER DEFAULT 0,
                net INTEGER DEFAULT 0,
                had_blackjack INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, key),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')

# ── Achievements ──────────────────────────────────────────────────────────────
ACH = {
    'first_game':      {'name':'Začátečník','desc':'Zahraj svou první hru','icon':'🎮','color':'#40ff80','rarity':'Běžné'},
    'blackjack_master':{'name':'Blackjack Mistr','desc':'Udělej přirozený Blackjack (Eso + 10)','icon':'⚡','color':'#ffd700','rarity':'Vzácné'},
    'high_roller':     {'name':'Vysoký Sázkaře','desc':'Vyhraj více než 500 žetonů v jedné hře','icon':'💰','color':'#ff6b6b','rarity':'Epické'},
    'on_a_roll':       {'name':'Vítězná série','desc':'Vyhraj 3 hry za sebou','icon':'🔥','color':'#ff9f43','rarity':'Vzácné'},
    'survivor':        {'name':'Přeživší','desc':'Vyhraj s přesně 21 (bez přirozeného BJ)','icon':'🛡️','color':'#a29bfe','rarity':'Neobvyklé'},
    'veteran':         {'name':'Veterán','desc':'Zahraj celkem 10 her','icon':'⭐','color':'#74b9ff','rarity':'Neobvyklé'},
    'comeback_kid':    {'name':'Comeback','desc':'Vyhraj hru s méně než 100 žetony','icon':'🔄','color':'#fd79a8','rarity':'Epické'},
    'double_trouble':  {'name':'Dvojnásobek','desc':'Vyhraj po zdvojení sázky','icon':'✌️','color':'#00cec9','rarity':'Neobvyklé'},
}

# ── Card logic ────────────────────────────────────────────────────────────────
SUITS = ['S','H','D','C']
RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

def new_deck():
    d = [{'rank':r,'suit':s} for s in SUITS for r in RANKS]
    random.shuffle(d)
    return d

def cv(c):
    if c['rank'] in ('J','Q','K'): return 10
    if c['rank'] == 'A': return 11
    return int(c['rank'])

def hv(hand):
    t = sum(cv(c) for c in hand)
    a = sum(1 for c in hand if c['rank']=='A')
    while t > 21 and a: t -= 10; a -= 1
    return t

def is_bj(hand): return len(hand)==2 and hv(hand)==21

# ── Auth ──────────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def w(*a,**k):
        if 'uid' not in session: return redirect(url_for('login'))
        return f(*a,**k)
    return w

def admin_required(f):
    @wraps(f)
    def w(*a,**k):
        if 'uid' not in session: return redirect(url_for('login'))
        with db() as c:
            u = c.execute('SELECT is_admin FROM users WHERE id=?',(session['uid'],)).fetchone()
        if not u or not u['is_admin']:
            return redirect(url_for('game'))
        return f(*a,**k)
    return w

# ── Achievement check ─────────────────────────────────────────────────────────
def check_ach(uid, result, net, pbj, pv, pc, doubled, chips_before):
    unlocked = []
    with db() as c:
        existing = {r['key'] for r in c.execute('SELECT key FROM achievements WHERE user_id=?',(uid,)).fetchall()}
        total = c.execute('SELECT COUNT(*) as n FROM games WHERE user_id=?',(uid,)).fetchone()['n']
        def unlock(k):
            if k not in existing:
                c.execute('INSERT OR IGNORE INTO achievements (user_id,key) VALUES (?,?)',(uid,k))
                unlocked.append(k); existing.add(k)
        if total >= 1: unlock('first_game')
        if total >= 10: unlock('veteran')
        if pbj: unlock('blackjack_master')
        if net > 500: unlock('high_roller')
        if result=='win' and pv==21 and not pbj and pc>2: unlock('survivor')
        if result=='win' and doubled: unlock('double_trouble')
        if chips_before < 100 and result=='win': unlock('comeback_kid')
        last3 = c.execute('SELECT result FROM games WHERE user_id=? ORDER BY id DESC LIMIT 3',(uid,)).fetchall()
        if len(last3)==3 and all(g['result']=='win' for g in last3): unlock('on_a_roll')
        c.commit()
    return unlocked

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('game') if 'uid' in session else url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    err = None
    if request.method == 'POST':
        name     = request.form.get('username','').strip()
        password = request.form.get('password','')
        action   = request.form.get('action','login')  # 'login' or 'register'

        # Validate username
        if len(name) < 2:
            err = 'Jméno musí mít alespoň 2 znaky!'
        elif len(name) > 16:
            err = 'Max 16 znaků!'
        elif not name.replace('_','').replace('-','').isalnum():
            err = 'Jen písmena, čísla, - a _'
        elif len(password) < 4:
            err = 'Heslo musí mít alespoň 4 znaky!'
        else:
            with db() as c:
                u = c.execute('SELECT * FROM users WHERE username=?',(name,)).fetchone()

                if action == 'register':
                    # --- Registrace ---
                    if u:
                        err = 'Jméno už existuje — přihlas se!'
                    else:
                        ph = generate_password_hash(password)
                        c.execute('INSERT INTO users (username, password_hash) VALUES (?,?)',(name, ph))
                        c.commit()
                        u = c.execute('SELECT * FROM users WHERE username=?',(name,)).fetchone()
                        session['uid']      = u['id']
                        session['uname']    = u['username']
                        session['is_admin'] = bool(u['is_admin'])
                        session['new']      = True
                        return redirect(url_for('game'))

                else:
                    # --- Přihlášení ---
                    if not u:
                        err = 'Účet neexistuje — zaregistruj se!'
                    elif not check_password_hash(u['password_hash'], password):
                        err = 'Špatné heslo!'
                    elif u['is_banned']:
                        err = '🚫 Tvůj účet byl zablokován administrátorem!'
                    else:
                        session['uid']   = u['id']
                        session['uname'] = u['username']
                        session['is_admin'] = bool(u['is_admin'])
                        session['new']   = False
                        return redirect(url_for('game'))

    return render_template('login.html', err=err)

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))

@app.route('/game')
@login_required
def game():
    with db() as c:
        u = c.execute('SELECT * FROM users WHERE id=?',(session['uid'],)).fetchone()
    new = session.pop('new', False)
    return render_template('game.html', user=u, is_new=new)

# ── Game API ──────────────────────────────────────────────────────────────────
@app.route('/api/deal', methods=['POST'])
@login_required
def deal():
    data = request.get_json() or {}
    try: bet = max(1, int(data.get('bet', 50)))
    except: return jsonify({'error':'Neplatná sázka'}), 400
    with db() as c:
        u = c.execute('SELECT * FROM users WHERE id=?',(session['uid'],)).fetchone()
        if bet > u['chips']: return jsonify({'error':'Nemáš dost žetonů!'}), 400
        c.execute('UPDATE users SET chips=chips-? WHERE id=?',(bet,session['uid']))
        c.commit()
    deck = new_deck()
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]
    session['game'] = {'deck':deck,'player':player,'dealer':dealer,'bet':bet,
                       'status':'playing','doubled':False,'chips_before':u['chips']}
    if is_bj(player) or is_bj(dealer): return _finish(is_bj(player), is_bj(dealer))
    return jsonify(_state(True))

@app.route('/api/hit', methods=['POST'])
@login_required
def hit():
    g = session.get('game')
    if not g or g['status']!='playing': return jsonify({'error':'Žádná aktivní hra'}), 400
    g['player'].append(g['deck'].pop()); session['game'] = g
    if hv(g['player']) > 21: return _finish(False, False, bust=True)
    if hv(g['player']) == 21: return _dealer_play()
    return jsonify(_state(True))

@app.route('/api/stand', methods=['POST'])
@login_required
def stand():
    g = session.get('game')
    if not g or g['status']!='playing': return jsonify({'error':'Žádná aktivní hra'}), 400
    return _dealer_play()

@app.route('/api/double', methods=['POST'])
@login_required
def double():
    g = session.get('game')
    if not g or g['status']!='playing': return jsonify({'error':'Žádná aktivní hra'}), 400
    with db() as c:
        u = c.execute('SELECT chips FROM users WHERE id=?',(session['uid'],)).fetchone()
        if u['chips'] < g['bet']: return jsonify({'error':'Nemáš dost žetonů na zdvojení!'}), 400
        c.execute('UPDATE users SET chips=chips-? WHERE id=?',(g['bet'],session['uid']))
        c.commit()
    g['bet'] *= 2; g['doubled'] = True
    g['player'].append(g['deck'].pop()); session['game'] = g
    if hv(g['player']) > 21: return _finish(False, False, bust=True)
    return _dealer_play()

@app.route('/api/refill', methods=['POST'])
@login_required
def refill():
    with db() as c:
        u = c.execute('SELECT chips FROM users WHERE id=?',(session['uid'],)).fetchone()
        if u['chips'] > 0: return jsonify({'error':'Stále máš žetony!'}), 400
        c.execute('UPDATE users SET chips=500 WHERE id=?',(session['uid'],)); c.commit()
    return jsonify({'chips':500})

@app.route('/api/chips')
@login_required
def chips():
    with db() as c:
        u = c.execute('SELECT chips FROM users WHERE id=?',(session['uid'],)).fetchone()
    return jsonify({'chips':u['chips']})

def _dealer_play():
    g = session['game']
    while hv(g['dealer']) < 17: g['dealer'].append(g['deck'].pop())
    session['game'] = g
    return _finish(False, False)

def _finish(pbj=False, dbj=False, bust=False):
    g = session['game']
    pv = hv(g['player']); dv = hv(g['dealer']); bet = g['bet']
    if bust:         result, msg, wins = 'lose','💀 BUST! Přetáhl jsi!', 0
    elif pbj and dbj:result, msg, wins = 'push','🤝 Oba Blackjack — Push!', bet
    elif pbj:        result, msg, wins = 'win', '⚡ BLACKJACK! Výplata 3:2!', int(bet*2.5)
    elif dbj:        result, msg, wins = 'lose','😤 Dealer Blackjack!', 0
    elif dv > 21:    result, msg, wins = 'win', '🎉 Dealer přetáhl — vyhráváš!', bet*2
    elif pv > dv:    result, msg, wins = 'win', '🏆 Výhra!', bet*2
    elif pv == dv:   result, msg, wins = 'push',"🤝 Remíza!", bet
    else:            result, msg, wins = 'lose','😞 Dealer vyhrál…', 0
    net = wins - bet
    with db() as c:
        c.execute('UPDATE users SET chips=chips+? WHERE id=?',(wins,session['uid']))
        c.execute('INSERT INTO games (user_id,result,player_score,dealer_score,bet,net,had_blackjack) VALUES (?,?,?,?,?,?,?)',
            (session['uid'],result,pv,dv,bet,net,1 if pbj else 0))
        c.commit()
        new_chips = c.execute('SELECT chips FROM users WHERE id=?',(session['uid'],)).fetchone()['chips']
    unlocked = check_ach(session['uid'],result,net,pbj,pv,len(g['player']),g.get('doubled',False),g.get('chips_before',9999))
    g['status'] = result; session['game'] = g
    s = _state(False)
    s.update({'message':msg,'result':result,'chips':new_chips,
              'new_achievements':[{**ACH[k],'key':k} for k in unlocked if k in ACH]})
    return jsonify(s)

def _state(hide):
    g = session.get('game', {})
    if not g: return {}
    d = g['dealer']
    dd = [d[0],{'rank':'?','suit':'?'}] if hide else d
    dv = cv(d[0]) if hide else hv(d)
    return {'player':g['player'],'dealer':dd,'pv':hv(g['player']),'dv':dv,
            'bet':g['bet'],'status':g['status'],'hidden':hide,'doubled':g.get('doubled',False)}

# ── Pages ─────────────────────────────────────────────────────────────────────
@app.route('/leaderboard')
@login_required
def leaderboard():
    with db() as c:
        rows = c.execute('''
            SELECT u.username, u.chips,
                COUNT(g.id) as played,
                SUM(CASE WHEN g.result='win' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN g.had_blackjack=1 THEN 1 ELSE 0 END) as blackjacks,
                CASE WHEN COUNT(g.id)>0
                     THEN ROUND(SUM(CASE WHEN g.result='win' THEN 1 ELSE 0 END)*100.0/COUNT(g.id))
                     ELSE 0 END as win_rate
            FROM users u LEFT JOIN games g ON u.id=g.user_id
            GROUP BY u.id ORDER BY u.chips DESC LIMIT 20
        ''').fetchall()
    return render_template('leaderboard.html', rows=rows, me=session['uname'])

@app.route('/profile/<username>')
@login_required
def profile(username):
    with db() as c:
        u = c.execute('SELECT * FROM users WHERE username=?',(username,)).fetchone()
        if not u: return redirect(url_for('leaderboard'))
        games = c.execute('SELECT * FROM games WHERE user_id=? ORDER BY timestamp DESC LIMIT 20',(u['id'],)).fetchall()
        stats = c.execute('''SELECT COUNT(*) as total,
            SUM(CASE WHEN result='win' THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN result='lose' THEN 1 ELSE 0 END) as losses,
            SUM(CASE WHEN result='push' THEN 1 ELSE 0 END) as pushes,
            SUM(CASE WHEN had_blackjack=1 THEN 1 ELSE 0 END) as blackjacks,
            MAX(net) as best_win, SUM(net) as total_net
            FROM games WHERE user_id=?''',(u['id'],)).fetchone()
        ua = {r['key'] for r in c.execute('SELECT key FROM achievements WHERE user_id=?',(u['id'],)).fetchall()}
    ach = [{**v,'key':k,'unlocked':k in ua} for k,v in ACH.items()]
    return render_template('profile.html', pu=u, games=games, stats=stats, achievements=ach, me=session['uname'])

# ── Admin routes ──────────────────────────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin():
    with db() as c:
        users = c.execute('''
            SELECT u.id, u.username, u.chips, u.is_admin, u.is_banned, u.created_at,
                COUNT(g.id) as played,
                SUM(CASE WHEN g.result='win' THEN 1 ELSE 0 END) as wins
            FROM users u LEFT JOIN games g ON u.id=g.user_id
            GROUP BY u.id ORDER BY u.chips DESC
        ''').fetchall()
        total_games = c.execute('SELECT COUNT(*) as n FROM games').fetchone()['n']
        total_chips = c.execute('SELECT SUM(chips) as s FROM users').fetchone()['s'] or 0
    return render_template('admin.html', users=users,
        total_games=total_games, total_chips=total_chips, me=session['uname'])

@app.route('/admin/delete/<int:uid>', methods=['POST'])
@admin_required
def admin_delete(uid):
    with db() as c:
        u = c.execute('SELECT username,is_admin FROM users WHERE id=?', (uid,)).fetchone()
        if u and not u['is_admin']:   # can't delete another admin
            c.execute('DELETE FROM achievements WHERE user_id=?', (uid,))
            c.execute('DELETE FROM games WHERE user_id=?', (uid,))
            c.execute('DELETE FROM users WHERE id=?', (uid,))
            c.commit()
    return redirect(url_for('admin'))

@app.route('/admin/ban/<int:uid>', methods=['POST'])
@admin_required
def admin_ban(uid):
    with db() as c:
        u = c.execute('SELECT is_admin,is_banned FROM users WHERE id=?', (uid,)).fetchone()
        if u and not u['is_admin']:
            new_state = 0 if u['is_banned'] else 1
            c.execute('UPDATE users SET is_banned=? WHERE id=?', (new_state, uid))
            c.commit()
    return redirect(url_for('admin'))

@app.route('/admin/reset_chips/<int:uid>', methods=['POST'])
@admin_required
def admin_reset_chips(uid):
    with db() as c:
        u = c.execute('SELECT is_admin FROM users WHERE id=?', (uid,)).fetchone()
        if u and not u['is_admin']:
            c.execute('UPDATE users SET chips=500 WHERE id=?', (uid,))
            c.commit()
    return redirect(url_for('admin'))

@app.route('/admin/reset_stats/<int:uid>', methods=['POST'])
@admin_required
def admin_reset_stats(uid):
    with db() as c:
        u = c.execute('SELECT is_admin FROM users WHERE id=?', (uid,)).fetchone()
        if u and not u['is_admin']:
            c.execute('DELETE FROM games WHERE user_id=?', (uid,))
            c.execute('DELETE FROM achievements WHERE user_id=?', (uid,))
            c.execute('UPDATE users SET chips=500 WHERE id=?', (uid,))
            c.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    print('\n🎰 Pixel Blackjack Stand spuštěn!')
    print('   Otevři http://127.0.0.1:5000\n')
    app.run(debug=True)
