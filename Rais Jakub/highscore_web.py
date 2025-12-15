import os
import sqlite3
from flask import render_template_string
from flask import Flask

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "score.db")
# Flask is not defined because it is not imported.
# Add this import at the top of your file:
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>Minesweeper Highscore</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f0f0; }
        h1 { text-align: center; }
        table { margin: auto; border-collapse: collapse; background: white; }
        th, td { padding: 8px 16px; border: 1px solid #ccc; }
        th { background: #eee; }
    </style>
</head>
<body>
    <h1>Minesweeper Highscore</h1>
    <table>
        <tr>
            <th>#</th>
            <th>Jméno</th>
            <th>Skóre</th>
            <th>Čas (s)</th>
            <th>Obtížnost</th>
            <th>Výsledek</th>
        </tr>
        {% for row in scores %}
        <tr>
            <td>{{ loop.index }}</td>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
            <td>{{ row[2] }}</td>
            <td>{{ row[3] }}</td>
            <td>{{ row[4] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/")
def highscore():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT jmeno, skore, cas, obtiznost, vysledek
        FROM vysledky
        ORDER BY skore DESC, cas ASC
        LIMIT 20
    """)
    scores = cur.fetchall()
    conn.close()
    return render_template_string(HTML, scores=scores)

if __name__ == "__main__":
    app.run(debug=True)
