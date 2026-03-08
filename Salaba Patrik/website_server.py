from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3

DB_NAME = "snake_game.db"

def connect_to_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT skore, datum FROM hry ORDER BY skore DESC")
    data = c.fetchall()
    conn.close()
    return data

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            scores = connect_to_db()

            html = """
            <!DOCTYPE html>
            <html lang="cs">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Snake Leaderboard</title>
                <style>
                    body {
                        margin: 0;
                        font-family: Arial, sans-serif;
                        background: linear-gradient(135deg, #0f172a, #1e293b);
                        color: white;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                    }

                    .container {
                        width: 90%;
                        max-width: 700px;
                        background: rgba(255, 255, 255, 0.08);
                        border: 1px solid rgba(255, 255, 255, 0.15);
                        border-radius: 20px;
                        padding: 30px;
                        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
                        backdrop-filter: blur(8px);
                    }

                    h1 {
                        text-align: center;
                        margin-bottom: 25px;
                        font-size: 2.2rem;
                        color: #22c55e;
                        text-shadow: 0 0 12px rgba(34, 197, 94, 0.5);
                    }

                    .subtitle {
                        text-align: center;
                        color: #cbd5e1;
                        margin-bottom: 25px;
                        font-size: 0.95rem;
                    }

                    table {
                        width: 100%;
                        border-collapse: collapse;
                        overflow: hidden;
                        border-radius: 12px;
                    }

                    th, td {
                        padding: 14px 16px;
                        text-align: left;
                    }

                    th {
                        background-color: rgba(34, 197, 94, 0.2);
                        color: #86efac;
                        font-size: 1rem;
                        letter-spacing: 0.5px;
                    }

                    tr {
                        background-color: rgba(255, 255, 255, 0.04);
                        transition: 0.2s;
                    }

                    tr:nth-child(even) {
                        background-color: rgba(255, 255, 255, 0.07);
                    }

                    tr:hover {
                        background-color: rgba(34, 197, 94, 0.15);
                    }

                    td {
                        color: #e2e8f0;
                        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                    }

                    .empty {
                        text-align: center;
                        padding: 20px;
                        color: #cbd5e1;
                    }

                    .footer {
                        text-align: center;
                        margin-top: 20px;
                        font-size: 0.85rem;
                        color: #94a3b8;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🐍 Snake Leaderboard</h1>
                    <div class="subtitle">Přehled nejlepších výsledků z databáze</div>
            """

            if scores:
                html += """
                    <table>
                        <tr>
                            <th>Pořadí</th>
                            <th>Skóre</th>
                            <th>Datum</th>
                        </tr>
                """
                for i, (score, datum) in enumerate(scores, start=1):
                    html += f"""
                        <tr>
                            <td>{i}.</td>
                            <td>{score}</td>
                            <td>{datum}</td>
                        </tr>
                    """
                html += "</table>"
            else:
                html += '<div class="empty">Zatím nejsou uložené žádné výsledky.</div>'

            html += """
                    <div class="footer">Snake game databáze</div>
                </div>
            </body>
            </html>
            """

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

server = HTTPServer(("localhost", 8000), MyServer)
server.serve_forever()
