import os
import sqlite3
from flask import Flask, render_template_string, Response, url_for

# Konfigurace cesty k databázi
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "score.db")

app = Flask(__name__)

# ------------------------------------------------------------------------------
# 1. CENTRALIZOVANÉ CSS (Design stránek v jednom souboru)
# ------------------------------------------------------------------------------
CSS_CONTENT = """
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f4f4f9;
    color: #333;
    margin: 0;
    padding: 0;
    line-height: 1.6;
}

/* Navigační lišta */
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

/* Obsah stránek */
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

/* Tabulka Highscore */
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

/* Patička */
footer {
    text-align: center;
    padding: 20px;
    background-color: #2c3e50;
    color: #bdc3c7;
    margin-top: 40px;
    font-size: 0.9em;
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

# ------------------------------------------------------------------------------
# 2. HTML ŠABLONY (Base layout + jednotlivé stránky)
# ------------------------------------------------------------------------------

# Základní šablona (obsahuje hlavičku, menu a patičku, do které se vkládá obsah)
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
        <a href="/diagramy">Vývojové diagramy</a>
        <a href="/o-nas">O mně</a>
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

# ------------------------------------------------------------------------------
# 3. ROUTY (Logika aplikace)
# ------------------------------------------------------------------------------

@app.route("/style.css")
def style():
    """Slouží CSS soubor dynamicky."""
    return Response(CSS_CONTENT, mimetype="text/css")

@app.route("/")
def home():
    """Hlavní stránka: Základní info + Tabulka výsledků."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Načtení dat z databáze (z tvého score.db)
    try:
        cur.execute("""
            SELECT jmeno, skore, cas, obtiznost, vysledek
            FROM vysledky
            ORDER BY skore DESC, cas ASC
            LIMIT 20
        """)
        scores = cur.fetchall()
    except sqlite3.OperationalError:
        scores = [] # Ošetření chyby pokud tabulka neexistuje
    conn.close()

    # Vytvoření HTML pro tabulku
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
        table_html += f"""
        <tr>
            <td>{index}</td>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td>{row[2]}</td>
            <td>{row[3]}</td>
            <td>{row[4]}</td>
        </tr>
        """
    table_html += "</table>"
    
    if not scores:
        table_html += "<p><em>Zatím nejsou v databázi žádné výsledky. Zahrajte si hru!</em></p>"

    return render_template_string(BASE_TEMPLATE, title="Hlavní stránka", content=table_html)

@app.route("/o-hre")
def about_game():
    """Stránka O hře: Podrobné informace, pravidla a technické specifikace."""
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
        <li>Pravým tlačítkem myši lze označit pole vlaječkou, o kterém si hráč myslí, že skrývá minu.</li>
        <li>Číslo na políčku indikuje počet min v okolních 8 polích.</li>
    </ul>

    <h2>Funkční požadavky</h2>
    <ul>
        <li>Volba obtížnosti (Začátečník, Střední, Expert).</li>
        <li>mněření času hry.</li>
        <li>Počítání skóre na základě času a správně umístěných vlajek.</li>
        <li>Ukládání výsledků do lokální databáze.</li>
    </ul>

    <h2>Technické zpracování</h2>
    <p>Aplikace je rozdělena na desktopovou část (herní klient v Python/Tkinter) a tuto webovou část (Flask), 
    která slouží k prezentaci výsledků.</p>
    """
    return render_template_string(BASE_TEMPLATE, title="O hře", content=content)

@app.route("/diagramy")
def diagrams():
    """Stránka Vývojové diagramy: Algoritmy mechanik."""
    content = """
    <h1>Vývojové diagramy</h1>
    <p>Zde jsou vizualizovány klíčové algoritmy použité při vývoji hry.</p>

    <h2>1. Algoritmus generování min</h2>
    <p>Popisuje náhodné rozmístění min na hrací plochu s kontrolou duplicit.</p>
    <div class="diagram-placeholder">
        [Zde vložit obrázek: diagram_generovani_min.png]
    </div>

    <h2>2. Algoritmus odkrývání polí (Flood Fill)</h2>
    <p>Rekurzivní algoritmus, který automaticky odkryje prázdná pole v okolí kliknutí, pokud je pole bezpečné (hodnota 0).</p>
    <div class="diagram-placeholder">
        [Zde vložit obrázek: diagram_odkryvani.png]
    </div>
    """
    return render_template_string(BASE_TEMPLATE, title="Vývojové diagramy", content=content)

@app.route("/o-nas")
def about_us():
    """Stránka O mně: Informace o tvůrcích."""
    content = """
    <h1>O mně</h1>
    
    <h2>Autor projektu</h2>
    <p><strong>Jméno:</strong> Jakub Rais</p>
    <p><strong>Škola:</strong> SPŠ a VOŠ Jana Palacha 1840</p>
    <p><strong>Třída:</strong> EP4B</p>
    
    <h2>Kontakt</h2>
    <p>V případě dotazů nebo hlášení chyb mě kontaktujte na e-mailu: <a href="mailto:raisj@spskladno.cz">raisj@spskladno.cz</a></p>
    """
    return render_template_string(BASE_TEMPLATE, title="O mně", content=content)

if __name__ == "__main__":
    app.run(debug=True)