import pygame
import os
from typing import Dict, Optional


class SoundManager:
    """Načítá zvukové efekty a hudbu ze složky assets/sounds a poskytuje jednoduché pomocníky pro jejich přehrávání s ohledem na slovník nastavení.

    Slovník nastavení používá stejné klíče jako :class:`Menu` ("menu_music", "ingame_music" a "vfx"). Je předáván odkazem, takže přepínání v menu okamžitě ovlivňuje přehrávání.
    """

    def __init__(self, settings: Optional[Dict[str, bool]] = None):
        # inicializovat mixer samostatně, abychom mohli zpracovat případy, kdy hlavní aplikace ještě nezavolala ``pygame.init()`` (Game to dělá brzy).
        try:
            pygame.mixer.init()
        except Exception:
            pass
        # zkopírovat slovník nastavení, aby úpravy neovlivnily volajícího neúmyslně
        self.settings = settings or {}
        # zajistit, že klíče pro přepínače a hlasitost existují s rozumnými výchozími hodnotami
        for k in ('menu_music','ingame_music','vfx'):
            self.settings.setdefault(k, True)
        for vk in ('menu_volume','ingame_volume','vfx_volume'):
            self.settings.setdefault(vk, 1.0)

        # Uložit předchozí hodnoty hlasitosti pro detekci změn
        self._prev_volumes = {
            'menu_volume': self.settings.get('menu_volume', 1.0),
            'ingame_volume': self.settings.get('ingame_volume', 1.0),
            'vfx_volume': self.settings.get('vfx_volume', 1.0)
        }

        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_files: Dict[str, str] = {}
        self._base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assets", "sounds")
        )
        self._load_all()

    def _load_all(self):
        if not os.path.isdir(self._base_path):
            return
        for fname in os.listdir(self._base_path):
            if not fname.lower().endswith(('.wav', '.mp3', '.ogg', '.m4a')):
                continue
            key = os.path.splitext(fname)[0]
            full = os.path.join(self._base_path, fname)
            try:
                # cokoli obsahujícího „hudbu“ považovat za hudební stopu; ostatní jako zvukový efekt.  To umožňuje mít delší hudební stopy, které se nenahrají celé do paměti, a zároveň mít rychlé načítání pro kratší efekty.
                if 'music' in key or key.startswith('menu') or key.startswith('ingame'):
                    self.music_files[key] = full
                else:
                    self.sounds[key] = pygame.mixer.Sound(full)
            except Exception:
                pass

    def play_sound(self, name: str) -> None:
        if not self.settings.get('vfx', True):
            return
        vol = self.settings.get('vfx_volume', 1.0)
        snd = self.sounds.get(name)
        if snd:
            try:
                snd.set_volume(vol)
                snd.play()
            except Exception:
                pass
            return
        for key, snd in self.sounds.items():
            if name in key:
                try:
                    snd.set_volume(vol)
                    snd.play()
                except Exception:
                    pass
                return

    def play_music(self, name: str, loops: int = -1) -> None:
        if name == 'menu':
            if not self.settings.get('menu_music', True):
                return
        else:
            if not self.settings.get('ingame_music', True):
                return
        vol_key = 'menu_volume' if name == 'menu' else 'ingame_volume'
        vol = self.settings.get(vol_key, 1.0)
        path = self.music_files.get(name)
        if not path:
            for key, p in self.music_files.items():
                if name in key:
                    path = p
                    break
        if path:
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(vol)
                pygame.mixer.music.play(loops)
            except Exception:
                pass
            return
        snd = self.sounds.get(name)
        if snd:
            try:
                snd.set_volume(vol)
                snd.play(loops=loops)
            except Exception:
                pass
            return
        for key, snd in self.sounds.items():
            if name in key:
                try:
                    snd.set_volume(vol)
                    snd.play(loops=loops)
                except Exception:
                    pass
                return

    def stop_music(self) -> None:
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def update_volumes(self, context: str = 'ingame') -> None:
        volumes_changed = False
        for vk in ('menu_volume', 'ingame_volume', 'vfx_volume'):
            current_vol = self.settings.get(vk, 1.0)
            if abs(current_vol - self._prev_volumes[vk]) > 0.01:  
                volumes_changed = True
                self._prev_volumes[vk] = current_vol
        
        if volumes_changed:
            try:
                if pygame.mixer.music.get_busy():
                    if context == 'menu':
                        vol = self.settings.get('menu_volume', 1.0)
                    else:
                        vol = self.settings.get('ingame_volume', 1.0)
                    pygame.mixer.music.set_volume(vol)
            except Exception:
                pass
