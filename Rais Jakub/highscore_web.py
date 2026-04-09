import os
import sqlite3
from flask import Flask, render_template_string, Response, url_for, session, redirect, request

# Cesta k databázi – stejná složka jako skript
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "score.db")

app = Flask(__name__)
app.secret_key = "minesweeper_secret_key_2026"

# CSS pro celou aplikaci definované jako string – Flask ho pak servíruje jako soubor
CSS_CONTENT = """
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f4f4f9;
    color: #333;
    margin: 0;
    padding: 0;
    line-height: 1.6;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

nav {
    background-color: #2c3e50;
    overflow: hidden;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

nav a {
    float: left;
    display: block;
    color: white;
    text-align: center;
    padding: 14px 20px;
    text-decoration: none;
    font-weight: bold;
    transition: background-color 0.3s;
}

nav a:hover {
    background-color: #1abc9c;
    color: white;
}

nav .brand {
    float: right;
    padding: 14px 20px;
    color: #bdc3c7;
    font-style: italic;
}

.container {
    max-width: 900px;
    margin: 30px auto;
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

h1 { color: #2c3e50; border-bottom: 2px solid #1abc9c; padding-bottom: 10px; }
h2 { color: #16a085; margin-top: 20px; }
p { margin-bottom: 15px; }
ul { margin-bottom: 20px; }

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

th, td {
    padding: 12px 15px;
    border: 1px solid #ddd;
    text-align: left;
}

th {
    background-color: #2c3e50;
    color: white;
}

tr:nth-child(even) { background-color: #f2f2f2; }
tr:hover { background-color: #e9e9e9; }

/* Zvýraznění řádků přihlášeného hráče */
tr.highlight {
    background-color: #d5f5e3 !important;
    font-weight: bold;
    border-left: 4px solid #1abc9c;
}
tr.highlight td:first-child {
    color: #1abc9c;
}

.login-form {
    max-width: 400px;
    margin: 40px auto;
    padding: 30px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.login-form input[type="text"] {
    width: 100%;
    padding: 12px;
    margin: 15px 0;
    border: 2px solid #ddd;
    border-radius: 6px;
    font-size: 16px;
    box-sizing: border-box;
    transition: border-color 0.3s;
}
.login-form input[type="text"]:focus {
    border-color: #1abc9c;
    outline: none;
}
.login-form button {
    width: 100%;
    padding: 12px;
    background-color: #1abc9c;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.3s;
}
.login-form button:hover {
    background-color: #16a085;
}

nav .user-info {
    float: right;
    padding: 14px 20px;
    color: #1abc9c;
    font-weight: bold;
}
nav .user-info a {
    color: #e74c3c;
    margin-left: 10px;
    font-weight: normal;
}
nav .user-info a:hover {
    background-color: #c0392b;
}

.legend {
    margin-top: 15px;
    padding: 10px 15px;
    background-color: #d5f5e3;
    border-left: 4px solid #1abc9c;
    border-radius: 4px;
    font-size: 0.9em;
    color: #2c3e50;
}

.error-msg {
    background-color: #fdf0f0;
    border-left: 4px solid #e74c3c;
    padding: 10px 15px;
    margin: 15px 0;
    border-radius: 4px;
    color: #c0392b;
    font-weight: bold;
}

footer {
    text-align: center;
    padding: 20px;
    background-color: #2c3e50;
    color: #bdc3c7;
    font-size: 0.9em;
    margin-top: auto;
}

.diagram-placeholder {
    width: 100%;
    height: 300px;
    background-color: #ecf0f1;
    border: 2px dashed #bdc3c7;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #7f8c8d;
    margin: 20px 0;
}
"""

# Základní HTML šablona – nav + container + footer, obsah se vkládá přes {{ content }}
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minesweeper - {{ title }}</title>
    <link rel="stylesheet" href="{{ url_for('style') }}">
</head>
<body>
    <nav>
        <a href="/">Hlavní stránka</a>
        <a href="/o-hre">O hře</a>
        <a href="/manual">Manuál</a>
        <a href="/diagramy">Vývojové diagramy</a>
        <a href="/o-nas">O mně</a>
        {% if logged_in %}
        <span class="user-info">
            🎮 {{ player_name }}
            <a href="/logout">Odhlásit se</a>
        </span>
        {% else %}
        <a href="/login" style="float:right;">Přihlásit se</a>
        {% endif %}
        <span class="brand">Maturitní projekt</span>
    </nav>

    <div class="container">
        {{ content | safe }}
    </div>

    <footer>
        &copy; 2026 Maturitní projekt - Hledání min
    </footer>
</body>
</html>
"""

# Routy aplikace

@app.route("/style.css")
def style():
    # CSS se servíruje jako soubor přímo z proměnné CSS_CONTENT
    return Response(CSS_CONTENT, mimetype="text/css")

@app.route("/")
def home():
    # Hlavní stránka – načte top 20 výsledků z DB a zobrazí tabulku
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT h.jmeno, v.skore, v.cas, v.obtiznost, v.vysledek, v.hrac_id
            FROM vysledky v
            LEFT JOIN hraci h ON v.hrac_id = h.id
            ORDER BY v.skore DESC, v.cas ASC
            LIMIT 20
        """)
        scores = cur.fetchall()
    except sqlite3.OperationalError:
        # Fallback pro starší DB bez tabulky hraci
        try:
            cur.execute("""
                SELECT jmeno, skore, cas, obtiznost, vysledek, NULL
                FROM vysledky
                ORDER BY skore DESC, cas ASC
                LIMIT 20
            """)
            scores = cur.fetchall()
        except sqlite3.OperationalError:
            scores = []
    conn.close()

    logged_player = session.get("player_name", None)
    logged_hrac_id = session.get("hrac_id", None)

    table_html = """
    <h1>Vítejte v Hledání min</h1>
    <p>Toto je webové rozhraní pro maturitní projekt hry Minesweeper. Níže naleznete aktuální žebříček nejlepších hráčů.</p>
    
    <h2>Tabulka nejlepších výsledků</h2>
    <table>
        <tr>
            <th>#</th>
            <th>Jméno</th>
            <th>Skóre</th>
            <th>Čas (s)</th>
            <th>Obtížnost</th>
            <th>Výsledek</th>
        </tr>
    """
    for index, row in enumerate(scores, 1):
        jmeno = row[0] if row[0] else "Neznámý"
        row_hrac_id = row[5]
        # Zvýraznění vlastních výsledků přihlášeného hráče
        row_class = ' class="highlight"' if logged_hrac_id and row_hrac_id == logged_hrac_id else ''
        table_html += f"""
        <tr{row_class}>
            <td>{index}</td>
            <td>{jmeno}</td>
            <td>{row[1]}</td>
            <td>{row[2]}</td>
            <td>{row[3]}</td>
            <td>{row[4]}</td>
        </tr>
        """
    table_html += "</table>"
    
    if logged_player:
        table_html += '<div class="legend">🎮 Vaše výsledky jsou zvýrazněny zeleně.</div>'
    
    if not scores:
        table_html += "<p><em>Zatím nejsou v databázi žádné výsledky. Zahrajte si hru!</em></p>"

    return render_template_string(BASE_TEMPLATE, title="Hlavní stránka", content=table_html,
                                 logged_in=bool(logged_player), player_name=logged_player)

@app.route("/login", methods=["GET", "POST"])
def login():
    # Přihlášení podle jména – hráč musí mít alespoň jeden zaznamenaný výsledek
    error = ""
    if request.method == "POST":
        jmeno = request.form.get("jmeno", "").strip()
        if jmeno:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT id FROM hraci WHERE jmeno = ? COLLATE NOCASE", (jmeno,))
            hrac = cur.fetchone()
            conn.close()
            if hrac:
                session["player_name"] = jmeno
                session["hrac_id"] = hrac[0]
                return redirect("/")
            else:
                error = f'Hráč "{jmeno}" nebyl nalezen. Nejdříve si musíte zahrát hru!'
    
    error_html = f'<div class="error-msg">{error}</div>' if error else ''
    content = f"""
    <h1>Přihlášení hráče</h1>
    <p>Zadejte své herní jméno, abyste viděli svá skóre zvýrazněná v tabulce.</p>
    {error_html}
    <div class="login-form">
        <form method="POST" action="/login">
            <label for="jmeno"><strong>Herní jméno:</strong></label>
            <input type="text" id="jmeno" name="jmeno" placeholder="Zadejte vaše jméno..." required>
            <button type="submit">Přihlásit se</button>
        </form>
    </div>
    """
    logged_player = session.get("player_name", None)
    return render_template_string(BASE_TEMPLATE, title="Přihlášení", content=content,
                                 logged_in=bool(logged_player), player_name=logged_player)

@app.route("/logout")
def logout():
    # Odstranění jména a ID hráče ze session
    session.pop("player_name", None)
    session.pop("hrac_id", None)
    return redirect("/")


@app.route("/o-hre")
def about_game():
    content = """
    <h1>O hře Minesweeper</h1>
    
    <h2>Popis projektu</h2>
    <p>Tento projekt vznikl jako samostatná maturitní práce z programování (4. ročník). 
    Hra je vytvořena v jazyce <strong>Python</strong> pomocí knihovny <strong>Tkinter</strong> 
    a využívá <strong>SQLite databázi</strong> pro ukládání výsledků.</p>

    <h2>Pravidla hry</h2>
    <ul>
        <li>Cílem hry je odkrýt všechna pole, která neobsahují minu.</li>
        <li>Pokud hráč klikne na minu, hra končí prohrou.</li>
        <li>Pravým tlačítkem myši lze vlaječkou označit pole, o kterém si hráč myslí, že skrývá minu.</li>
        <li>Číslo na políčku indikuje počet min v okolních 8 polích.</li>
    </ul>

    <h2>Funkční požadavky</h2>
    <ul>
        <li>Volba obtížnosti (Začátečník, Střední, Expert).</li>
        <li>Měření času hry.</li>
        <li>Počítání skóre na základě odkrytých polí, uplynulého času a penalizace za špatně umístěné vlajky.</li>
        <li>Ukládání výsledků do lokální databáze.</li>
    </ul>

    <h2>Technické zpracování</h2>
    <p>Aplikace je rozdělena na desktopovou část (herní klient v Python/Tkinter) a tuto webovou část (Flask), 
    která slouží k prezentaci výsledků.</p>
    """
    logged_player = session.get("player_name", None)
    return render_template_string(BASE_TEMPLATE, title="O hře", content=content,
                                 logged_in=bool(logged_player), player_name=logged_player)

@app.route("/manual")
def manual():
    content = """
    <h1>Uživatelská příručka</h1>
    
    <h2>1. Úvod</h2>
    <p>Aplikace se skládá ze dvou propojených částí:</p>
    <ul>
        <li><strong>Desktopová hra</strong> – Samotná hra Hledání min, ve které hráč hraje, měří se mu čas a počítá skóre.</li>
        <li><strong>Webové rozhraní</strong> – Slouží k zobrazení žebříčku nejlepších hráčů (Scoreboard) a k dokumentaci.</li>
    </ul>
    <p>Obě části sdílejí společnou lokální databázi (<code>score.db</code>).</p>

    <h2>2. Instalace a spuštění</h2>
    <p><strong>Systémové požadavky:</strong></p>
    <ul>
        <li>Nainstalovaný jazyk Python (verze 3.x).</li>
        <li>Pro webovou část je nutné mít nainstalovanou knihovnu Flask (<code>pip install flask</code>).</li>
    </ul>
    <p><strong>Spuštění aplikace:</strong></p>
    <ul>
        <li><strong>Hra:</strong> Spustí se souborem <code>game.py</code>. Hra se automaticky otevře v režimu celé obrazovky.</li>
        <li><strong>Webový žebříček:</strong> Spustí se souborem <code>highscore_web.py</code>. Následně otevřete webový prohlížeč na adrese <code>http://127.0.0.1:5000</code>.</li>
    </ul>

    <h2>3. Ovládání hry</h2>
    <p>Po spuštění hry se zobrazí hlavní menu s výběrem obtížnosti (Začátečník, Střední, Expert).</p>
    <p><strong>Herní mechaniky:</strong></p>
    <ul>
        <li><strong>Levé tlačítko myši:</strong> Odkryje zvolené pole. Pokud je pod ním mina, hra končí prohrou. Jinak se zobrazí číslo (počet min v okolí) nebo se automaticky odkryjí další prázdná pole.</li>
        <li><strong>Pravé tlačítko myši:</strong> Umístí nebo odebere vlaječku na pole s domnělou minou.</li>
        <li><strong>Klávesa ESC:</strong> Okamžitě ukončí aplikaci.</li>
    </ul>

    <h2>4. Hodnocení a webové rozhraní</h2>
    <p>Hra končí výbuchem miny nebo odkrytím všech bezpečných polí. Hráč je poté vyzván k zadání jména pro uložení výsledku.</p>
    <p><em>Poznámka ke skóre:</em> Získáváte +10 bodů za odkryté pole. Skóre se snižuje o čas v sekundách a o -5 bodů za každou špatně umístěnou vlaječku.</p>
    <p>Ve webovém rozhraní se můžete v záložce <strong>Přihlásit se</strong> identifikovat svým herním jménem, čímž se vaše výsledky v žebříčku zeleně zvýrazní.</p>
    """
    logged_player = session.get("player_name", None)
    return render_template_string(BASE_TEMPLATE, title="Manuál", content=content,
                                 logged_in=bool(logged_player), player_name=logged_player)

@app.route("/diagramy")
def diagrams():
    content = """
    <h1>Vývojové diagramy</h1>
    <p>Zde jsou vizualizovány klíčové algoritmy použité při vývoji hry. <br>
    <em>(Tip: Diagramy si můžete posouvat do strany, nebo na ně kliknout pro otevření v plné velikosti.)</em></p>

    <h2>1. Algoritmus generování min</h2>
    <p>Popisuje náhodné rozmístění min na hrací plochu s kontrolou duplicit.</p>
    <div style="overflow-x: auto; margin: 20px 0; padding-bottom: 10px;">
        <a href="/static/diagram_generovani_min.png" target="_blank" title="Klikni pro zvětšení">
            <img src="/static/diagram_generovani_min.png" alt="Diagram generování min" style="min-width: 900px; width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: block; margin: 0 auto;">
        </a>
    </div>

    <h2>2. Algoritmus odkrývání polí (Flood Fill)</h2>
    <p>Rekurzivní algoritmus, který automaticky odkryje prázdná pole v okolí kliknutí, pokud je pole bezpečné (hodnota 0).</p>
    <div style="overflow-x: auto; margin: 20px 0; padding-bottom: 10px;">
        <a href="/static/diagram_odkryvani.png" target="_blank" title="Klikni pro zvětšení">
            <img src="/static/diagram_odkryvani.png" alt="Diagram odkrývání polí" style="min-width: 900px; width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: block; margin: 0 auto;">
        </a>
    </div>
    """
    logged_player = session.get("player_name", None)
    return render_template_string(BASE_TEMPLATE, title="Vývojové diagramy", content=content,
                                 logged_in=bool(logged_player), player_name=logged_player)

@app.route("/o-nas")
def about_us():
    content = """
    <h1>O mně</h1>
    
    <h2>Autor projektu</h2>
    <p><strong>Jméno:</strong> Jakub Rais</p>
    <p><strong>Škola:</strong> SPŠ a VOŠ Jana Palacha 1840</p>
    <p><strong>Třída:</strong> EP4B</p>
    
    <h2>Kontakt</h2>
    <p>V případě dotazů nebo hlášení chyb mě kontaktujte na e-mailu: <a href="mailto:raisj@spskladno.cz">raisj@spskladno.cz</a></p>
    """
    logged_player = session.get("player_name", None)
    return render_template_string(BASE_TEMPLATE, title="O mně", content=content,
                                 logged_in=bool(logged_player), player_name=logged_player)

if __name__ == "__main__":
    app.run(debug=True)