# Potapec

Run game:
  python -m venv venv
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  pip install -r requirements.txt
  python main.py

Alternate CLI menu:
  python main.py --cli      # text‑based menu (useful on headless machines)

Leaderboard:
  python web/app.py

Tests:
  pytest -q

## Audio

The game now loads all files from `assets/sounds`. Background music (currently
`water-bubbles`) and sound effects (clicks, jumps, chomps, etc.) are played
during gameplay. Use the in‑menu **Sound…** option to toggle menu music,
ingame music and VFX on or off.  If your environment doesn't support audio,
the mixer gracefully falls back without crashing.
