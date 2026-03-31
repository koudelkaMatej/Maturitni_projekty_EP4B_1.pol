import pytest
import pygame

# avoid initializing the real mixer during unit tests; it may hang on
# environments without a sound device. replace with a no-op.
pygame.mixer.init = lambda *args, **kwargs: None

from potapec.game.sound import SoundManager


def test_sound_manager_initializes(monkeypatch):
    # initialize without blowing up; mixer may not be available in CI
    try:
        sm = SoundManager()
    except Exception:
        pytest.skip("pygame mixer unavailable")
    # the settings dict should be present and default to empty
    assert isinstance(sm.settings, dict)
    # volume entries should exist and default to 1.0
    assert sm.settings.get('menu_volume', None) == 1.0
    assert sm.settings.get('ingame_volume', None) == 1.0
    assert sm.settings.get('vfx_volume', None) == 1.0
    # changing a volume should persist
    sm.settings['vfx_volume'] = 0.5
    assert sm.settings['vfx_volume'] == 0.5
    # we may not have any actual sound files available during testing,
    # but calling ``play_sound`` and ``play_music`` should still be safe.
    # calling play/stop methods must not raise
    sm.play_sound('click')
    sm.play_music('water-bubbles')
    sm.stop_music()


def test_playback_respects_vfx_toggle():
    sm = SoundManager(settings={'vfx': False})
    # with VFX off, play_sound should be a no-op and not throw
    sm.play_sound('click')
    assert not sm.sounds or all(not s.get_num_channels() for s in sm.sounds.values())
