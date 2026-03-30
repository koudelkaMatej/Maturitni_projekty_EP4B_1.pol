import traceback, sys
from game.game import Game

if __name__ == '__main__':
    try:
        game = Game()
        game.run()
    except Exception:
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        with open('game_error.log', 'w', encoding='utf-8') as f:
            f.write(tb)
        try:
            input('An error occurred; press Enter to exit (traceback written to game_error.log)')
        except Exception:
            pass
