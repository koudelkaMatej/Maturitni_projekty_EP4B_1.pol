import os, sys, traceback
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root not in sys.path:
    sys.path.insert(0, root)

from game.game import Game
from game.menu import Menu

if __name__ == '__main__':
    use_cli = '--cli' in sys.argv
    if not use_cli:
        try:
            import pygame
            pygame.display.init()
        except Exception:
            use_cli = True
    if use_cli:
        action, sound_settings, user = Menu.cli_menu()
        if action != 'start':
            sys.exit(0)
        try:
            game = Game()
            game.menu.sound = sound_settings
            game.menu.user = user
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
    else:
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
