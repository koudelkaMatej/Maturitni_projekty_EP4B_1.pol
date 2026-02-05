import json
import os

SAVE_PATH = "savegame.json"

DEFAULT_SAVE = {
    "name": "Player",
    "best_depth": 0,
    "last_depth": 0,
    "oxygen": 100,
    "score": 0
}

def load_game():
    if not os.path.exists(SAVE_PATH):
        return DEFAULT_SAVE.copy()

    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SAVE.copy()

def save_game(data):
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass
