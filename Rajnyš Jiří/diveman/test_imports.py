import sys

print('cwd', sys.path[0])
try:
    from game.sound import SoundManager
    from game.player import Player
    print('import succeeded')
except Exception as e:
    print('import failure', e)
