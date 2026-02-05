from game.player import Player
def test_player_impulse():
    p = Player(100,100); y0 = p.world_y
    p.apply_impulse(0,-5); p.update()
    assert p.world_y < y0
