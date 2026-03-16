#!/usr/bin/env python3
"""
Muskets and Swords: New Dawn — Official Game Portal
Pure Python, zero dependencies (stdlib only).

Run:   python server.py
Open:  http://localhost:8080
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

PORT = 8080

# ─────────────────────────────────────────────────────────────────────────────
#  DATABASE STUBS  — wire up your SQLite here
# ─────────────────────────────────────────────────────────────────────────────

def get_leaderboard():
    """
    Replace with your SQLite query, e.g.:

        import sqlite3
        conn = sqlite3.connect("game.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT username, score, levels_completed "
            "FROM players ORDER BY score DESC LIMIT 20"
        )
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    """
    return [
        {"username": "General_Moreau",  "score": 48200, "levels_completed": 12},
        {"username": "IronDuke88",       "score": 41750, "levels_completed": 11},
        {"username": "BlüchersWrath",    "score": 39100, "levels_completed": 10},
        {"username": "SabreRattle",      "score": 35600, "levels_completed": 10},
        {"username": "CannonKing",       "score": 32400, "levels_completed":  9},
        {"username": "TacticalMarshal", "score": 29800, "levels_completed":  8},
        {"username": "MusketMaster",     "score": 27100, "levels_completed":  7},
        {"username": "CavalryCharge",    "score": 24500, "levels_completed":  7},
        {"username": "ArtilleryAce",     "score": 21300, "levels_completed":  6},
        {"username": "FortDefender",     "score": 18900, "levels_completed":  5},
    ]


def register_user(username, password):
    """
    Replace with:

        import sqlite3, hashlib
        conn = sqlite3.connect("game.db")
        hashed = hashlib.sha256(password.encode()).hexdigest()
        try:
            conn.execute(
                "INSERT INTO players (username, password_hash) VALUES (?,?)",
                (username, hashed)
            )
            conn.commit()
            conn.close()
            return {"ok": True, "message": "Commander registered!"}
        except sqlite3.IntegrityError:
            return {"ok": False, "message": "Username already taken."}
    """
    if len(username) < 3:
        return {"ok": False, "message": "Username must be at least 3 characters."}
    if len(password) < 6:
        return {"ok": False, "message": "Password must be at least 6 characters."}
    return {"ok": True, "message": f"Welcome to the front, Commander {username}!"}


def login_user(username, password):
    """
    Replace with:

        import sqlite3, hashlib
        conn = sqlite3.connect("game.db")
        hashed = hashlib.sha256(password.encode()).hexdigest()
        row = conn.execute(
            "SELECT username FROM players WHERE username=? AND password_hash=?",
            (username, hashed)
        ).fetchone()
        conn.close()
        if row:
            return {"ok": True, "username": row[0]}
        return {"ok": False, "message": "Invalid username or password."}
    """
    if username and password:
        return {"ok": True, "username": username}
    return {"ok": False, "message": "Invalid credentials."}


# ─────────────────────────────────────────────────────────────────────────────
#  HTML PAGE
# ─────────────────────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Muskets &amp; Swords: New Dawn</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}

:root{
  --ink:      #12100a;
  --bg:       #16110a;
  --surf:     #1e170e;
  --surf2:    #261e12;
  --border:   rgba(200,146,42,.2);
  --gold:     #c8922a;
  --gold2:    #e8b84b;
  --gold-dim: #7a5c1e;
  --red:      #8b1a1a;
  --parch:    #f0e4c8;
  --parch2:   #d9c9a3;
  --smoke:    #5a4e38;
  --smoke2:   #7a6b50;
  --fhead:    'Cinzel', serif;
  --fbody:    'Crimson Pro', serif;
  --fmono:    'DM Mono', monospace;
  --r:        6px;
}

::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--gold-dim);border-radius:99px}

body{
  background:var(--bg);
  color:var(--parch);
  font-family:var(--fbody);
  font-size:17px;
  line-height:1.7;
  min-height:100vh;
  overflow-x:hidden;
}

/* diagonal map-line texture */
body::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background:
    repeating-linear-gradient(-45deg,
      transparent,transparent 30px,
      rgba(200,146,42,.025) 30px,
      rgba(200,146,42,.025) 31px
    );
}

/* ── NAV ───────────────────── */
nav{
  position:sticky;top:0;z-index:200;
  background:rgba(18,16,10,.97);
  border-bottom:1px solid var(--border);
  backdrop-filter:blur(8px);
  padding:.7rem 2.5rem;
  display:flex;align-items:center;justify-content:space-between;
  animation:navIn .5s ease both;
}
@keyframes navIn{from{transform:translateY(-100%);opacity:0}to{transform:translateY(0);opacity:1}}

.nav-brand{
  font-family:var(--fhead);font-weight:900;font-size:1rem;
  letter-spacing:.12em;text-transform:uppercase;color:var(--gold2);
  display:flex;align-items:center;gap:.55rem;
}

.nav-links{display:flex;align-items:center;gap:2rem;list-style:none}
.nav-links a{
  font-family:var(--fhead);font-size:.62rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--parch2);text-decoration:none;
  opacity:.65;transition:all .2s;
}
.nav-links a:hover{opacity:1;color:var(--gold2)}

.nav-btns{display:flex;gap:.5rem}

.nbtn{
  font-family:var(--fhead);font-size:.62rem;letter-spacing:.14em;
  text-transform:uppercase;padding:.42rem 1.1rem;
  border-radius:var(--r);cursor:pointer;transition:all .2s;border:1px solid;
}
.nbtn-out{background:transparent;color:var(--gold);border-color:var(--gold-dim)}
.nbtn-out:hover{background:rgba(200,146,42,.1);border-color:var(--gold)}
.nbtn-fill{background:var(--gold);color:var(--ink);border-color:var(--gold);font-weight:700}
.nbtn-fill:hover{background:var(--gold2);border-color:var(--gold2)}

/* ── HERO ──────────────────── */
.hero{
  position:relative;z-index:1;
  min-height:91vh;
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  text-align:center;padding:5rem 2rem;overflow:hidden;
}

/* vignette */
.hero::after{
  content:'';position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(ellipse 80% 60% at 50% 50%, transparent 40%, rgba(12,10,6,.7));
}

.hero-deco{
  font-size:2.2rem;color:var(--gold-dim);
  letter-spacing:.4em;margin-bottom:1.5rem;
  animation:fadeUp .7s .1s ease both;
}
@keyframes fadeUp{from{transform:translateY(22px);opacity:0}to{transform:translateY(0);opacity:1}}

.hero-eye{
  font-family:var(--fhead);font-size:.65rem;letter-spacing:.35em;
  text-transform:uppercase;color:var(--gold);margin-bottom:.9rem;
  animation:fadeUp .7s .15s ease both;
}

.hero h1{
  font-family:var(--fhead);font-weight:900;
  font-size:clamp(3rem,8vw,6rem);
  line-height:.95;letter-spacing:.05em;
  text-transform:uppercase;color:var(--parch);
  text-shadow:0 4px 50px rgba(200,146,42,.35),0 0 120px rgba(200,146,42,.1);
  animation:fadeUp .7s .2s ease both;
}

.hero-subtitle{
  font-family:var(--fhead);font-weight:400;
  font-size:clamp(.9rem,2vw,1.4rem);
  letter-spacing:.3em;text-transform:uppercase;
  color:var(--gold);margin-top:.6rem;margin-bottom:1.8rem;
  animation:fadeUp .7s .25s ease both;
}

.hero-rule{
  display:flex;align-items:center;gap:.8rem;
  color:var(--gold-dim);font-size:1rem;
  width:min(420px,90%);margin-bottom:1.8rem;
  animation:fadeUp .7s .3s ease both;
}
.hero-rule::before,.hero-rule::after{
  content:'';flex:1;height:1px;
  background:linear-gradient(90deg,transparent,var(--gold-dim),transparent);
}

.hero-desc{
  font-size:1.1rem;color:var(--parch2);
  max-width:560px;line-height:1.9;font-style:italic;
  margin-bottom:2.5rem;opacity:.85;
  animation:fadeUp .7s .35s ease both;
}

.hero-cta{
  display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;
  animation:fadeUp .7s .4s ease both;
}

.hbtn{
  font-family:var(--fhead);font-size:.7rem;letter-spacing:.18em;
  text-transform:uppercase;padding:.8rem 2.2rem;
  border-radius:var(--r);cursor:pointer;border:1px solid;transition:all .25s;
}
.hbtn-gold{
  background:var(--gold);color:var(--ink);border-color:var(--gold);font-weight:700;
  box-shadow:0 4px 32px rgba(200,146,42,.4);
}
.hbtn-gold:hover{background:var(--gold2);box-shadow:0 6px 44px rgba(200,146,42,.55);transform:translateY(-2px)}
.hbtn-ghost{background:transparent;color:var(--parch);border-color:rgba(200,146,42,.35)}
.hbtn-ghost:hover{background:rgba(200,146,42,.08);border-color:var(--gold)}

/* ── DIVIDER ───────────────── */
.divider{
  position:relative;z-index:1;
  display:flex;align-items:center;gap:1rem;
  color:var(--gold-dim);font-size:.95rem;
  padding:0 2.5rem;max-width:1100px;margin:0 auto;
}
.divider::before,.divider::after{
  content:'';flex:1;height:1px;
  background:linear-gradient(90deg,transparent,rgba(200,146,42,.22),transparent);
}

/* ── SECTION ───────────────── */
.sec{
  position:relative;z-index:1;
  padding:4.5rem 2.5rem;
  max-width:1100px;margin:0 auto;
  scroll-margin-top:4rem;
}

.sec-hd{text-align:center;margin-bottom:2.8rem}

.sec-eye{
  font-family:var(--fhead);font-size:.62rem;letter-spacing:.3em;
  text-transform:uppercase;color:var(--gold);margin-bottom:.6rem;
}

.sec-title{
  font-family:var(--fhead);font-weight:700;
  font-size:clamp(1.5rem,3vw,2.2rem);
  letter-spacing:.08em;text-transform:uppercase;color:var(--parch);
}

.sec-rule{
  display:flex;align-items:center;gap:.7rem;
  justify-content:center;color:var(--gold-dim);
  font-size:.85rem;margin-top:.9rem;
}
.sec-rule::before,.sec-rule::after{
  content:'';width:60px;height:1px;
  background:linear-gradient(90deg,transparent,var(--gold-dim));
}
.sec-rule::after{background:linear-gradient(90deg,var(--gold-dim),transparent)}

/* ── ABOUT GRID ────────────── */
.about-grid{
  display:grid;grid-template-columns:1fr 1fr;gap:1.25rem;
}

.acard{
  background:rgba(245,234,200,.03);
  border:1px solid var(--border);
  border-radius:var(--r);padding:1.75rem;
  transition:all .25s;
}
.acard:hover{
  background:rgba(245,234,200,.06);
  border-color:rgba(200,146,42,.4);
  box-shadow:0 8px 40px rgba(0,0,0,.3);
}
.acard-icon{font-size:1.6rem;display:block;margin-bottom:.65rem}
.acard h3{
  font-family:var(--fhead);font-size:.75rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--gold2);margin-bottom:.45rem;
}
.acard p{font-size:.95rem;color:var(--parch2);opacity:.8;line-height:1.8}

/* ── MECHANICS ─────────────── */
.mech-grid{
  display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;
}

.mcard{
  background:rgba(139,26,26,.07);
  border:1px solid rgba(139,26,26,.25);
  border-radius:var(--r);padding:1.4rem;
  position:relative;overflow:hidden;
  transition:all .2s;
}
.mcard::after{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--red),var(--gold),var(--red));
  opacity:0;transition:opacity .2s;
}
.mcard:hover{background:rgba(139,26,26,.14);border-color:rgba(200,146,42,.35)}
.mcard:hover::after{opacity:1}

.mcard-num{
  font-family:var(--fhead);font-size:.6rem;letter-spacing:.22em;
  color:var(--gold-dim);margin-bottom:.35rem;
}
.mcard h3{
  font-family:var(--fhead);font-size:.74rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--parch);margin-bottom:.4rem;
}
.mcard p{font-size:.88rem;color:var(--parch2);opacity:.72;line-height:1.6}

/* ── LEADERBOARD ───────────── */
.lb-wrap{
  background:rgba(245,234,200,.025);
  border:1px solid var(--border);
  border-radius:var(--r);overflow:hidden;
}

.lb-bar{
  display:flex;justify-content:space-between;align-items:center;
  padding:.85rem 1.5rem;
  background:rgba(200,146,42,.06);
  border-bottom:1px solid var(--border);
}

.lb-bar-title{
  font-family:var(--fhead);font-size:.65rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--gold);
}

.btn-sm{
  font-family:var(--fhead);font-size:.6rem;letter-spacing:.12em;
  text-transform:uppercase;padding:.3rem .85rem;
  border-radius:4px;cursor:pointer;
  background:transparent;color:var(--gold);
  border:1px solid rgba(200,146,42,.3);transition:all .2s;
}
.btn-sm:hover{background:rgba(200,146,42,.12);border-color:var(--gold)}

table{width:100%;border-collapse:collapse}

thead th{
  text-align:left;padding:.65rem 1.5rem;
  font-family:var(--fhead);font-size:.58rem;letter-spacing:.22em;
  text-transform:uppercase;color:var(--gold-dim);
  border-bottom:1px solid rgba(200,146,42,.12);
  background:rgba(0,0,0,.12);
}

tbody tr{
  border-bottom:1px solid rgba(200,146,42,.07);
  transition:background .15s;
}
tbody tr:last-child{border-bottom:none}
tbody tr:hover{background:rgba(200,146,42,.07)}

tbody td{
  padding:.8rem 1.5rem;
  font-size:.95rem;color:var(--parch2);
  vertical-align:middle;
}

.rank-badge{
  display:inline-flex;align-items:center;justify-content:center;
  width:26px;height:26px;border-radius:50%;
  font-family:var(--fhead);font-size:.68rem;font-weight:700;
}
.r1{background:var(--gold);color:var(--ink)}
.r2{background:#b0b0b0;color:var(--ink)}
.r3{background:#b06820;color:var(--ink)}
.rn{background:rgba(245,234,200,.07);color:var(--smoke2);border:1px solid rgba(200,146,42,.18)}

.u-name{
  font-family:var(--fhead);font-size:.78rem;
  letter-spacing:.04em;color:var(--parch);
}
.u-score{font-family:var(--fmono);font-size:.82rem;color:var(--gold2);font-weight:500}
.u-lvl{font-family:var(--fmono);font-size:.82rem;color:var(--parch2)}

.lb-empty{
  text-align:center;padding:3rem;
  color:var(--smoke2);font-size:.95rem;font-style:italic;
}

/* ── FOOTER ────────────────── */
footer{
  position:relative;z-index:1;
  border-top:1px solid var(--border);
  padding:2.5rem;text-align:center;
}
.foot-brand{
  font-family:var(--fhead);font-size:.72rem;letter-spacing:.22em;
  text-transform:uppercase;color:var(--gold-dim);margin-bottom:.4rem;
}
.foot-text{font-size:.88rem;color:var(--smoke2);font-style:italic}
.foot-chips{display:flex;justify-content:center;gap:.5rem;flex-wrap:wrap;margin-top:.9rem}
.chip{
  font-family:var(--fmono);font-size:.62rem;letter-spacing:.08em;
  padding:.18rem .6rem;border-radius:3px;
  background:rgba(200,146,42,.07);
  border:1px solid rgba(200,146,42,.18);color:var(--gold-dim);
}

/* ── MODAL ─────────────────── */
.overlay{
  position:fixed;inset:0;z-index:500;
  background:rgba(8,6,2,.88);
  backdrop-filter:blur(7px);
  display:flex;align-items:center;justify-content:center;
  opacity:0;pointer-events:none;transition:opacity .3s;
}
.overlay.open{opacity:1;pointer-events:all}

.modal{
  background:#1e170e;
  border:1px solid rgba(200,146,42,.35);
  border-radius:10px;
  padding:2.5rem 2.5rem 2rem;
  width:min(410px,94vw);
  transform:translateY(18px);
  transition:transform .3s;
  position:relative;
}
.overlay.open .modal{transform:translateY(0)}

.modal-deco{
  text-align:center;font-size:1.6rem;
  color:var(--gold-dim);margin-bottom:.4rem;letter-spacing:.3em;
}
.modal-title{
  font-family:var(--fhead);font-weight:700;
  font-size:1.15rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--parch);
  text-align:center;margin-bottom:.2rem;
}
.modal-sub{
  text-align:center;font-size:.88rem;color:var(--smoke2);
  margin-bottom:1.6rem;font-style:italic;
}

.tabs{display:flex;border-bottom:1px solid var(--border);margin-bottom:1.6rem}
.tab{
  flex:1;font-family:var(--fhead);font-size:.65rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--smoke2);
  background:none;border:none;padding:.6rem;cursor:pointer;
  border-bottom:2px solid transparent;transition:all .2s;
}
.tab.active{color:var(--gold);border-bottom-color:var(--gold)}

.field{display:flex;flex-direction:column;gap:.35rem;margin-bottom:1rem}
.flabel{
  font-family:var(--fhead);font-size:.6rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--gold-dim);
}
.finput{
  background:rgba(245,234,200,.04);
  border:1px solid rgba(200,146,42,.22);
  border-radius:5px;padding:.6rem .9rem;
  font-family:var(--fbody);font-size:.95rem;
  color:var(--parch);outline:none;
  transition:border-color .2s;width:100%;
}
.finput:focus{border-color:var(--gold)}
.finput::placeholder{color:var(--smoke);opacity:.7}

.fsubmit{
  width:100%;font-family:var(--fhead);font-size:.7rem;
  letter-spacing:.18em;text-transform:uppercase;
  padding:.78rem;border-radius:5px;
  background:var(--gold);color:var(--ink);
  border:none;cursor:pointer;font-weight:700;
  transition:all .2s;margin-top:.4rem;
}
.fsubmit:hover{background:var(--gold2);box-shadow:0 4px 28px rgba(200,146,42,.45)}

.fmsg{
  text-align:center;font-size:.85rem;
  margin-top:.7rem;min-height:1.2rem;font-style:italic;
}
.ok{color:#7ecf9a}
.err{color:#cf6a6a}

.mclose{
  position:absolute;top:.85rem;right:1rem;
  background:none;border:none;
  color:var(--smoke2);font-size:1.1rem;
  cursor:pointer;transition:color .2s;line-height:1;
}
.mclose:hover{color:var(--parch)}

/* ── RESPONSIVE ────────────── */
@media(max-width:780px){
  nav{padding:.65rem 1.2rem}
  .nav-links{display:none}
  .sec{padding:3rem 1.5rem}
  .about-grid{grid-template-columns:1fr}
  .mech-grid{grid-template-columns:1fr 1fr}
  .divider{padding:0 1.5rem}
}
@media(max-width:480px){
  .mech-grid{grid-template-columns:1fr}
  .hero-cta{flex-direction:column;align-items:center}
}
</style>
</head>
<body>

<!-- ══ NAV ══════════════════════════════════════ -->
<nav>
  <div class="nav-brand">⚔ Muskets &amp; Swords</div>
  <ul class="nav-links">
    <li><a href="#about">About</a></li>
    <li><a href="#mechanics">Mechanics</a></li>
    <li><a href="#leaderboard">Leaderboard</a></li>
  </ul>
  <div class="nav-btns">
    <button class="nbtn nbtn-out"  onclick="openModal('login')">Sign In</button>
    <button class="nbtn nbtn-fill" onclick="openModal('register')">Enlist</button>
  </div>
</nav>

<!-- ══ HERO ═════════════════════════════════════ -->
<section class="hero">
  <div class="hero-deco">✦ ✦ ✦</div>
  <div class="hero-eye">Official Game Portal</div>
  <h1>Muskets &amp; Swords</h1>
  <div class="hero-subtitle">New Dawn</div>
  <div class="hero-rule">⚔</div>
  <p class="hero-desc">
    Command your armies across the blood-soaked fields of 18th century Europe.
    Deploy infantry, unleash cannon fire, and outmanoeuvre your foes in this
    Napoleonic turn-based strategy — built in Godot.
  </p>
  <div class="hero-cta">
    <button class="hbtn hbtn-gold" onclick="openModal('register')">Enlist Now</button>
    <button class="hbtn hbtn-ghost" onclick="document.getElementById('leaderboard').scrollIntoView({behavior:'smooth'})">View Leaderboard</button>
  </div>
</section>

<div class="divider">✦</div>

<!-- ══ ABOUT ════════════════════════════════════ -->
<div class="sec" id="about">
  <div class="sec-hd">
    <div class="sec-eye">The Campaign</div>
    <div class="sec-title">About the Game</div>
    <div class="sec-rule">⚔</div>
  </div>
  <div class="about-grid">
    <div class="acard">
      <span class="acard-icon">🏰</span>
      <h3>Defend Your Nation</h3>
      <p>You are placed in the role of an army commander whose sole duty is to protect your homeland from relentless enemy advances. Every decision — from your first musketeer to the final cavalry charge — shapes the fate of your nation.</p>
    </div>
    <div class="acard">
      <span class="acard-icon">⏳</span>
      <h3>Turn-Based Strategy</h3>
      <p>Plan each move with patience and precision. Study the battlefield, anticipate your enemy's next advance, and strike at the perfect moment. Brute force alone will not carry the day.</p>
    </div>
    <div class="acard">
      <span class="acard-icon">🎯</span>
      <h3>Napoleonic Era</h3>
      <p>Rooted in the military doctrine of 18th century Europe. Field musket infantry, cavalry sabres, and cannon batteries across terrain that dictates the ebb and flow of battle — just as the great generals did.</p>
    </div>
    <div class="acard">
      <span class="acard-icon">⚙</span>
      <h3>Built in Godot</h3>
      <p>Developed using the Godot engine with a pure Python &amp; SQLite backend powering this portal. Scores and progress sync via JSON between the game client and this leaderboard.</p>
    </div>
  </div>
</div>

<div class="divider">✦</div>

<!-- ══ MECHANICS ════════════════════════════════ -->
<div class="sec" id="mechanics">
  <div class="sec-hd">
    <div class="sec-eye">Field Manual</div>
    <div class="sec-title">Game Mechanics</div>
    <div class="sec-rule">⚔</div>
  </div>
  <div class="mech-grid">
    <div class="mcard">
      <div class="mcard-num">I</div>
      <h3>Unit Spawning</h3>
      <p>Deploy infantry, cavalry, and artillery from your reserve. Manage your supplies wisely — every formation fielded has a cost.</p>
    </div>
    <div class="mcard">
      <div class="mcard-num">II</div>
      <h3>Unit Control</h3>
      <p>Issue precise movement orders to each formation. Flanking, retreating, and holding ground are all tools of the trade.</p>
    </div>
    <div class="mcard">
      <div class="mcard-num">III</div>
      <h3>Combat &amp; Attack</h3>
      <p>Engage via musket volley, cannon bombardment, or brutal melee charge. Terrain and unit type determine the outcome.</p>
    </div>
    <div class="mcard">
      <div class="mcard-num">IV</div>
      <h3>Enemy AI</h3>
      <p>Face a smart opposing commander that flanks, retreats, and reinforces — keeping every battle fresh and unpredictable.</p>
    </div>
    <div class="mcard">
      <div class="mcard-num">V</div>
      <h3>Level Progression</h3>
      <p>Battle through escalating campaigns. Each level completed unlocks harder scenarios and contributes to your final score.</p>
    </div>
    <div class="mcard">
      <div class="mcard-num">VI</div>
      <h3>Score &amp; Glory</h3>
      <p>Performance is recorded and posted here. Speed, efficiency, and casualties all factor into your place on the leaderboard.</p>
    </div>
  </div>
</div>

<div class="divider">✦</div>

<!-- ══ LEADERBOARD ══════════════════════════════ -->
<div class="sec" id="leaderboard">
  <div class="sec-hd">
    <div class="sec-eye">Hall of Fame</div>
    <div class="sec-title">Leaderboard</div>
    <div class="sec-rule">⚔</div>
  </div>
  <div class="lb-wrap">
    <div class="lb-bar">
      <span class="lb-bar-title">Top Commanders</span>
      <button class="btn-sm" onclick="loadLB()">&#8635; Refresh</button>
    </div>
    <div id="lb"></div>
  </div>
</div>

<!-- ══ FOOTER ════════════════════════════════════ -->
<footer>
  <div class="foot-brand">Muskets &amp; Swords: New Dawn</div>
  <div class="foot-text">A Napoleonic turn-based strategy — built with Godot, Python &amp; SQLite</div>
  <div class="foot-chips">
    <span class="chip">Godot Engine</span>
    <span class="chip">Python</span>
    <span class="chip">SQLite</span>
    <span class="chip">JSON</span>
    <span class="chip">http.server</span>
  </div>
</footer>

<!-- ══ AUTH MODAL ════════════════════════════════ -->
<div class="overlay" id="overlay" onclick="bgClick(event)">
  <div class="modal">
    <button class="mclose" onclick="closeModal()">✕</button>
    <div class="modal-deco">⚔</div>
    <div class="modal-title">Commander Portal</div>
    <div class="modal-sub">Sign in or enlist to track your glory</div>
    <div class="tabs">
      <button class="tab active" id="t-login"    onclick="switchTab('login')">Sign In</button>
      <button class="tab"        id="t-register" onclick="switchTab('register')">Register</button>
    </div>

    <!-- Login -->
    <div id="f-login">
      <div class="field">
        <label class="flabel">Username</label>
        <input class="finput" id="l-user" type="text" placeholder="Your commander name"/>
      </div>
      <div class="field">
        <label class="flabel">Password</label>
        <input class="finput" id="l-pass" type="password" placeholder="••••••••"/>
      </div>
      <button class="fsubmit" onclick="doLogin()">March to Battle</button>
      <div class="fmsg" id="l-msg"></div>
    </div>

    <!-- Register -->
    <div id="f-register" style="display:none">
      <div class="field">
        <label class="flabel">Commander Name</label>
        <input class="finput" id="r-user" type="text" placeholder="Choose your name"/>
      </div>
      <div class="field">
        <label class="flabel">Password</label>
        <input class="finput" id="r-pass" type="password" placeholder="Min. 6 characters"/>
      </div>
      <button class="fsubmit" onclick="doRegister()">Enlist</button>
      <div class="fmsg" id="r-msg"></div>
    </div>
  </div>
</div>

<script>
/* ── Leaderboard ─────────────────────────── */
async function loadLB() {
  const el = document.getElementById('lb');
  try {
    const data = await fetch('/api/leaderboard').then(r => r.json());
    if (!data.length) {
      el.innerHTML = '<div class="lb-empty">No commanders on record yet. Be the first!</div>';
      return;
    }
    const cls = i => ['r1','r2','r3'][i] ?? 'rn';
    const rows = data.map((p, i) => `
      <tr>
        <td><span class="rank-badge ${cls(i)}">${i+1}</span></td>
        <td class="u-name">${p.username}</td>
        <td class="u-score">${Number(p.score).toLocaleString()}</td>
        <td class="u-lvl">${p.levels_completed}</td>
      </tr>`).join('');
    el.innerHTML = `
      <table>
        <thead><tr>
          <th>Rank</th><th>Commander</th><th>Score</th><th>Levels</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>`;
  } catch {
    el.innerHTML = '<div class="lb-empty">Could not load leaderboard.</div>';
  }
}
loadLB();

/* ── Modal ───────────────────────────────── */
function openModal(tab) { switchTab(tab); document.getElementById('overlay').classList.add('open'); }
function closeModal()   { document.getElementById('overlay').classList.remove('open'); }
function bgClick(e)     { if (e.target === document.getElementById('overlay')) closeModal(); }

function switchTab(t) {
  document.getElementById('f-login').style.display    = t==='login'    ? '' : 'none';
  document.getElementById('f-register').style.display = t==='register' ? '' : 'none';
  document.getElementById('t-login').classList.toggle('active',    t==='login');
  document.getElementById('t-register').classList.toggle('active', t==='register');
}

function msg(id, text, ok) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = 'fmsg ' + (ok ? 'ok' : 'err');
}

async function doLogin() {
  const u = document.getElementById('l-user').value.trim();
  const p = document.getElementById('l-pass').value;
  if (!u || !p) { msg('l-msg','Fill in all fields.',false); return; }
  try {
    const d = await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})}).then(r=>r.json());
    msg('l-msg', d.ok ? `Welcome back, ${d.username}!` : d.message, d.ok);
    if (d.ok) setTimeout(closeModal, 1400);
  } catch { msg('l-msg','Server error.',false); }
}

async function doRegister() {
  const u = document.getElementById('r-user').value.trim();
  const p = document.getElementById('r-pass').value;
  if (!u || !p) { msg('r-msg','Fill in all fields.',false); return; }
  try {
    const d = await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})}).then(r=>r.json());
    msg('r-msg', d.message, d.ok);
    if (d.ok) setTimeout(closeModal, 1600);
  } catch { msg('r-msg','Server error.',false); }
}

document.addEventListener('keydown', e => { if(e.key==='Escape') closeModal(); });
</script>
</body>
</html>
"""

# ─────────────────────────────────────────────────────────────────────────────
#  REQUEST HANDLER
# ─────────────────────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} → {fmt % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html, status=200):
        body = html.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            self.send_html(HTML)
        elif path == "/api/leaderboard":
            self.send_json(get_leaderboard())
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        path = self.path.split("?")[0]
        body = self.read_body()
        if path == "/api/register":
            self.send_json(register_user(body.get("username", ""), body.get("password", "")))
        elif path == "/api/login":
            self.send_json(login_user(body.get("username", ""), body.get("password", "")))
        else:
            self.send_json({"error": "Not found"}, 404)


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    server = HTTPServer(("", PORT), Handler)
    print(f"""
  ╔═══════════════════════════════════════════════╗
  ║  Muskets & Swords: New Dawn  —  Game Portal   ║
  ║  http://localhost:{PORT}                          ║
  ║  Press Ctrl+C to stop                         ║
  ╚═══════════════════════════════════════════════╝
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()