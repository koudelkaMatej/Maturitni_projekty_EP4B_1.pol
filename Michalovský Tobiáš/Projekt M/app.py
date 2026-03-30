from flask import Flask, render_template, jsonify
import sqlite3
import webbrowser

app = Flask(__name__)

def get_scores():
    db = sqlite3.connect("dinnobird.db")
    scores = db.execute(
        "SELECT player, score FROM scores ORDER BY score DESC"
    ).fetchall()
    db.close()
    return scores


@app.route('/scores.json')
def scores_json():
    rows = get_scores()
    # rows are (player, score)
    return jsonify([{"player": r[0], "score": r[1]} for r in rows])

@app.route("/")
def home():
    return render_template("index.html", scores=get_scores())

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000)
