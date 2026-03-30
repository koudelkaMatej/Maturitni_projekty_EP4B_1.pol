import sys
import builtins
import pytest
import pygame

from potapec.game.menu import Menu


def test_cli_menu_start(monkeypatch, capsys):
    # simulate entering name/password then start
    inputs = iter(["1",  # select start
                   "user", "pass",  # credentials
                   ])
    monkeypatch.setattr(builtins, 'input', lambda prompt='': next(inputs))
    action, sound, user = Menu.cli_menu()
    assert action == 'start'
    # default user will be returned as provided
    assert user == 'user'
    # sound settings dict should exist
    assert isinstance(sound, dict)    # volume keys present
    assert sound.get('menu_volume', None) == 1.0
    assert sound.get('ingame_volume', None) == 1.0
    assert sound.get('vfx_volume', None) == 1.0

def test_cli_menu_quit(monkeypatch):
    inputs = iter(["4"])
    monkeypatch.setattr(builtins, 'input', lambda prompt='': next(inputs))
    action, sound, user = Menu.cli_menu()
    assert action == 'quit'
    assert sound is not None
    assert user is None


def test_cli_menu_volume(monkeypatch):
    # navigate to sound submenu, adjust menu volume to 75%, then quit
    # choices: 2 (sound), 4 (menu vol), input 75, 7 (back), 4 (quit)
    inputs = iter(["2", "4", "75", "7", "4"])
    monkeypatch.setattr(builtins, 'input', lambda prompt='': next(inputs))
    action, sound, user = Menu.cli_menu()
    assert action == 'quit'
    assert sound.get('menu_volume', 0) == pytest.approx(0.75)


def test_volume_bar_calc():
    # ensure _update_volume_from_bar produces correct ratios
    m = Menu(None, None)
    rect = pygame.Rect(10, 10, 200, 6)
    m.sound['menu_volume'] = 0.0
    m._update_volume_from_bar('menu_volume', 10, rect)
    assert m.sound['menu_volume'] == pytest.approx(0.0)
    m._update_volume_from_bar('menu_volume', 110, rect)
    assert m.sound['menu_volume'] == pytest.approx(0.5)
    m._update_volume_from_bar('menu_volume', 210, rect)
    assert m.sound['menu_volume'] == pytest.approx(1.0)
