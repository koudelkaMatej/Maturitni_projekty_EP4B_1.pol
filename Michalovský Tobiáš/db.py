import sqlite3

DB_NAME = "dinnobird.db"

def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT NOT NULL,
            score INTEGER NOT NULL
        )
    """)

    # Remove duplicates keeping best score per player
    duplicates = db.execute(
        "SELECT player, MAX(score) AS best_score FROM scores GROUP BY player HAVING COUNT(*) > 1"
    ).fetchall()
    for player, best_score in duplicates:
        db.execute(
            "DELETE FROM scores WHERE player = ? AND score < ?",
            (player, best_score)
        )

    # Ensure player is unique in future inserts
    db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_scores_player ON scores (player)")

    db.commit()
    db.close()
