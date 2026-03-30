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
    db.commit()
    db.close()
