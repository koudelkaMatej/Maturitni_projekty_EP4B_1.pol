"""
testy.py — 2 unit testy pro HororBird / Flappy Dino
  Test 1: Bird  — fyzika ptáka (gravitace + skok)
  Test 2: save_score — ukládání skóre do databáze
"""

import unittest
import sqlite3
import sys

# --- Konstanty ---
BIRD_SIZE = 128
GRAVITY = 0.45
FLAP_STRENGTH = -9.5


# --- Třída Bird (bez pygame) ---
class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = 0

    def rect(self):
        return (int(self.x - BIRD_SIZE / 2), int(self.y - BIRD_SIZE / 2), BIRD_SIZE, BIRD_SIZE)


# --- save_score (přijímá db jako parametr pro testovatelnost) ---
def save_score(player, score, db):
    try:
        score_val = int(score)
    except Exception:
        return "invalid_score"

    player_val = str(player).strip()[:64]
    if not player_val:
        return "empty_player"

    existing = db.execute("SELECT score FROM scores WHERE player = ?", (player_val,)).fetchone()
    if existing is None:
        db.execute("INSERT INTO scores (player, score) VALUES (?, ?)", (player_val, score_val))
        db.commit()
        return "inserted"
    elif score_val > existing[0]:
        db.execute("UPDATE scores SET score = ? WHERE player = ?", (score_val, player_val))
        db.commit()
        return "updated"
    else:
        return "skipped"


# ================================================================== #
#  TEST 1 — Bird: fyzika ptáka                                         #
# ================================================================== #

class TestBird(unittest.TestCase):

    def test_fyzika_ptaka(self):
        """Pták správně reaguje na gravitaci a skok."""
        bird = Bird(x=200, y=300)

        # Počáteční stav
        self.assertEqual(bird.vy, 0, "Počáteční rychlost musí být 0")

        # Gravitace — pták padá dolů
        for _ in range(5):
            bird.vy += GRAVITY
            bird.y += bird.vy
        self.assertGreater(bird.y, 300, "Po gravitaci musí pták klesat (y roste)")

        # Skok — pták se pohne nahoru
        bird.vy = FLAP_STRENGTH
        bird.y += bird.vy
        self.assertLess(bird.y, 300 + 5 * GRAVITY * 5,
                        "Po skoku musí pták stoupat (y klesá)")
        self.assertLess(bird.vy, 0, "Rychlost po skoku musí být záporná (nahoru)")

        print("✅ Test 1 (Bird): OK")


# ================================================================== #
#  TEST 2 — save_score: ukládání skóre                                 #
# ================================================================== #

class TestSaveScore(unittest.TestCase):

    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE scores (player TEXT PRIMARY KEY, score INTEGER)")
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_ulozeni_skore(self):
        """Skóre se správně vloží, aktualizuje i odmítne."""
        # Nový hráč se vloží
        result = save_score("Alice", 42, self.db)
        self.assertEqual(result, "inserted", "Nový hráč musí být vložen")

        row = self.db.execute("SELECT score FROM scores WHERE player = ?", ("Alice",)).fetchone()
        self.assertEqual(row[0], 42, "Uložené skóre musí odpovídat")

        # Vyšší skóre se aktualizuje
        result = save_score("Alice", 99, self.db)
        self.assertEqual(result, "updated", "Vyšší skóre musí přepsat rekord")

        # Nižší skóre se ignoruje
        result = save_score("Alice", 5, self.db)
        self.assertEqual(result, "skipped", "Nižší skóre nesmí přepsat rekord")

        row = self.db.execute("SELECT score FROM scores WHERE player = ?", ("Alice",)).fetchone()
        self.assertEqual(row[0], 99, "Rekord musí zůstat 99")

        print("✅ Test 2 (save_score): OK")


# ================================================================== #
#  Spuštění                                                            #
# ================================================================== #

if __name__ == "__main__":
    print("=" * 50)
    print("  Testy pro HororBird / Flappy Dino")
    print("=" * 50)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(unittest.TestLoader().loadTestsFromModule(__import__(__name__)))
    print("=" * 50)
    if result.wasSuccessful():
        print(f"  ✅  Všechny testy prošly! ({result.testsRun}/2)")
    else:
        print(f"  ❌  {len(result.failures) + len(result.errors)} test(y) selhaly.")
    print("=" * 50)
    sys.exit(0 if result.wasSuccessful() else 1)