from game.player import Player
from game.settings import OXYGEN_MAX
def test_oxygen_bounds():
    p = Player(0,0); p.oxygen = OXYGEN_MAX; p.oxygen -= 5
    assert 0 <= p.oxygen <= OXYGEN_MAX
