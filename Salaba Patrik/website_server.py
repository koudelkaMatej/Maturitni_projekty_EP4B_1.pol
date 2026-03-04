from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3

DB_NAME = "snake_game.db"

def connet_to_db():
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute("SELECT skore, datum FROM hry")
  data = c.fetchall()
  conn.close()
  return data

class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            scores = connet_to_db ()

            html = "<h1>Leaderboard</h1>"

            for name, score in scores:
                html += f"<p>{name}: {score}</p>"

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

server = HTTPServer(("localhost", 8000), MyServer)
server.serve_forever()
