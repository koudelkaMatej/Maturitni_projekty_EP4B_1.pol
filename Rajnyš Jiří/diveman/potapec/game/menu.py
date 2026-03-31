import pygame
import webbrowser
import socket
import json
import os
try:
    from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore[import]
except ImportError:
    try:
        from passlib.context import CryptContext  # type: ignore[import]
    except ImportError:
        def generate_password_hash(p: str) -> str:  # type: ignore[override]
            return p
        def check_password_hash(h: str, p: str) -> bool:  # type: ignore[override]
            return h == p
    else:
        ctx = CryptContext(schemes=["pbkdf2_sha256"])
        generate_password_hash = ctx.hash
        check_password_hash = ctx.verify

from potapec.database.database import create_user, get_user
from potapec.game.settings import SCREEN_W, WEB_URL, WEB_HOST, WEB_PORT


def open_leaderboard_url():
    for p in (WEB_PORT, 5001, 5000, 8000):
        try:
            with socket.create_connection((WEB_HOST, int(p)), timeout=0.2):
                webbrowser.open(f'http://{WEB_HOST}:{p}')
                return True
        except Exception:
            pass
    try:
        webbrowser.open(WEB_URL)
        return True
    except Exception:
        return False


class Menu:
    MAIN = ('Start Game', 'Sound...', 'Open Leaderboard (web)', 'Quit')
    SOUND_KEYS = ('menu_music', 'ingame_music', 'vfx')
    VOLUME_KEYS = ('menu_volume', 'ingame_volume', 'vfx_volume')

    def __init__(self, screen, font, sound_settings=None):
        self.screen = screen
        self.font = font
        self.selected = 0
        self.mode = 'main'
        self.button_rects = []
        self.user = None
        self._dragging_volume = None
        if sound_settings is None:
            self.sound = {k: True for k in self.SOUND_KEYS}
            for vk in self.VOLUME_KEYS:
                self.sound[vk] = 1.0
        else:
            self.sound = sound_settings
            for k in self.SOUND_KEYS:
                self.sound.setdefault(k, True)
            for vk in self.VOLUME_KEYS:
                self.sound.setdefault(vk, 1.0)

        self.u = ''
        self.p = ''
        self.auth_active = 'u'
        self.auth_msg = ''
        self._u_rect = None
        self._p_rect = None

    def draw(self):
        self.screen.fill((10, 30, 60))
        title = self.font.render('POTÁPĚČ', True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 60))

        self.button_rects = []
        if self.mode == 'auth':
            self._draw_auth(160)
        elif self.mode == 'sound':
            self._draw_sound_menu(160)
        else:
            self._draw_list(160, self.MAIN)

        pygame.display.flip()

    def _draw_list(self, y, items):
        for i, t in enumerate(items):
            r = pygame.Rect(SCREEN_W // 2 - 140, y + i * 80, 280, 56)
            c = (30, 144, 255) if i == self.selected else (20, 90, 160)
            pygame.draw.rect(self.screen, c, r, border_radius=8)
            self.screen.blit(self.font.render(t, True, (255, 255, 255)), (r.x + 20, r.y + 12))
            self.button_rects.append(r)

    def _draw_sound_menu(self, y):
        self.slider_info = []
        idx = 0
        for vk in self.VOLUME_KEYS:
            r = pygame.Rect(SCREEN_W // 2 - 140, y + idx * 80, 280, 80)
            c = (30, 144, 255) if idx == self.selected else (20, 90, 160)
            pygame.draw.rect(self.screen, c, r, border_radius=8)
            vol = int(self.sound.get(vk, 0) * 100)
            label = vk.replace('_volume', '').replace('_', ' ').title()
            self.screen.blit(self.font.render(f"{label}: {vol}%", True, (255, 255, 255)), (r.x + 20, r.y + 12))
            bar_x = r.x + 20
            bar_y = r.y + 44
            bar_w = r.width - 40
            bar_rect = pygame.Rect(bar_x, bar_y, bar_w, 6)
            pygame.draw.rect(self.screen, (50, 50, 50), bar_rect)
            fill = int(bar_w * self.sound.get(vk, 0))
            pygame.draw.rect(self.screen, (50, 200, 50), (bar_x, bar_y, fill, 6))
            self.button_rects.append(r)
            self.slider_info.append((vk, bar_rect))
            idx += 1
        r = pygame.Rect(SCREEN_W // 2 - 140, y + idx * 80, 280, 56)
        c = (30, 144, 255) if idx == self.selected else (20, 90, 160)
        pygame.draw.rect(self.screen, c, r, border_radius=8)
        self.screen.blit(self.font.render('Save Settings', True, (255, 255, 255)), (r.x + 20, r.y + 12))
        self.button_rects.append(r)
        idx += 1
        r = pygame.Rect(SCREEN_W // 2 - 140, y + idx * 80, 280, 56)
        c = (30, 144, 255) if idx == self.selected else (20, 90, 160)
        pygame.draw.rect(self.screen, c, r, border_radius=8)
        self.screen.blit(self.font.render('Back', True, (255, 255, 255)), (r.x + 20, r.y + 12))
        self.button_rects.append(r)

    def _draw_auth(self, y):
        urect = pygame.Rect(SCREEN_W // 2 - 80, y, 360, 48)
        pygame.draw.rect(self.screen, (255, 255, 255) if self.auth_active == 'u' else (180, 180, 180), urect, border_radius=6)
        self.screen.blit(self.font.render(self.u or '<enter>', True, (0, 0, 0)), (urect.x + 8, urect.y + 10))
        self._u_rect = urect

        prect = pygame.Rect(SCREEN_W // 2 - 80, y + 80, 360, 48)
        pygame.draw.rect(self.screen, (255, 255, 255) if self.auth_active == 'p' else (180, 180, 180), prect, border_radius=6)
        self.screen.blit(self.font.render(('*' * len(self.p)) or '<enter>', True, (0, 0, 0)), (prect.x + 8, prect.y + 10))
        self._p_rect = prect

        btns = ('Login/Signup', 'Open Web', 'Back')
        for i, t in enumerate(btns):
            r = pygame.Rect(SCREEN_W // 2 - 180 + i * 140, y + 160, 160, 44)
            pygame.draw.rect(self.screen, (20, 120, 200), r, border_radius=6)
            self.screen.blit(self.font.render(t, True, (255, 255, 255)), (r.x + 12, r.y + 8))
            self.button_rects.append(r)

        if self.auth_msg:
            m = self.font.render(self.auth_msg, True, (240, 240, 120))
            self.screen.blit(m, (SCREEN_W // 2 - m.get_width() // 2, y + 220))

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if self.mode == 'auth':
                return self._auth_key(ev)
            if ev.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % max(1, len(self.button_rects))
            elif ev.key == pygame.K_UP:
                self.selected = (self.selected - 1) % max(1, len(self.button_rects))
            elif ev.key in (pygame.K_LEFT, pygame.K_RIGHT) and self.mode == 'sound':
                sel = self.selected
                if 0 <= sel < len(self.VOLUME_KEYS):
                    vk = self.VOLUME_KEYS[sel]
                    change = 0.1 if ev.key == pygame.K_RIGHT else -0.1
                    self.sound[vk] = max(0.0, min(1.0, self.sound.get(vk, 0) + change))
                    return None
            elif ev.key == pygame.K_RETURN:
                return self.activate(self.selected)

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            x, y = ev.pos
            if self.mode == 'auth':
                if self._u_rect.collidepoint(x, y):
                    self.auth_active = 'u'
                    return None
                if self._p_rect.collidepoint(x, y):
                    self.auth_active = 'p'
                    return None
            if self.mode == 'sound':
                for vk, bar in self.slider_info:
                    if bar.collidepoint(x, y):
                        self._dragging_volume = vk
                        self._update_volume_from_bar(vk, x, bar)
                        return None
            for i, r in enumerate(self.button_rects):
                if r.collidepoint(x, y):
                    if self.mode == 'auth':
                        return self._auth_btn(i)
                    return self.activate(i)
        elif ev.type == pygame.MOUSEMOTION and getattr(self, '_dragging_volume', None):
            x, y = ev.pos
            for vk, bar in self.slider_info:
                if vk == self._dragging_volume:
                    self._update_volume_from_bar(vk, x, bar)
                    break
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            self._dragging_volume = None
        return None

    def _update_volume_from_bar(self, vk, x, bar_rect):
        rel = (x - bar_rect.x) / max(1, bar_rect.width)
        self.sound[vk] = max(0.0, min(1.0, rel))

    def _auth_key(self, ev):
        if ev.key == pygame.K_TAB:
            self.auth_active = 'p' if self.auth_active == 'u' else 'u'
        elif ev.key == pygame.K_BACKSPACE:
            if self.auth_active == 'u':
                self.u = self.u[:-1]
            else:
                self.p = self.p[:-1]
        elif ev.key == pygame.K_RETURN:
            return self._attempt_login()
        elif ev.unicode and len(ev.unicode) == 1:
            if self.auth_active == 'u':
                self.u += ev.unicode
            else:
                self.p += ev.unicode
        return None

    def _auth_btn(self, idx):
        if idx == 0:
            return self._attempt_login()
        if idx == 1:
            open_leaderboard_url()
            return None
        self.mode = 'main'
        return None

    def activate(self, idx):
        if self.mode == 'main':
            if idx == 0:  # Start
                if not self.user:
                    self.mode = 'auth'
                    self.auth_active = 'u'
                    self.auth_msg = ''
                    return None
                return 'start'
            if idx == 1:  # Sound
                self.mode = 'sound'
                self.selected = 0
                return None
            if idx == 2:
                open_leaderboard_url()
                return None
            if idx == 3:
                return 'quit'
        else:  # sound
            if idx < len(self.VOLUME_KEYS):
                return None
            if idx == len(self.VOLUME_KEYS):
                # Save Settings
                self.save_settings()
                return None
            self.mode = 'main'
            self.selected = 0
        return None

    def _attempt_login(self):
        name = self.u.strip()
        pwd = self.p
        if not name or not pwd:
            self.auth_msg = 'Enter username and password'
            return None
        row = get_user(name)
        if row and check_password_hash(row[2], pwd):
            return self._login_ok(name, 'Logged in')
        ph = generate_password_hash(pwd)
        if create_user(name, ph):
            return self._login_ok(name, 'Account created and logged in')
        self.auth_msg = 'Invalid credentials or username taken'
        return None

    def _login_ok(self, name, msg):
        self.user = name
        self.mode = 'main'
        self.u = ''
        self.p = ''
        self.auth_msg = msg
        return 'start'

    def save_settings(self):
        """Save current sound settings to a file."""
        try:
            settings_file = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
            with open(settings_file, 'w') as f:
                json.dump(self.sound, f, indent=2)
            self.auth_msg = 'Settings saved!' 
        except Exception as e:
            self.auth_msg = f'Save failed: {e}'

    @classmethod
    def cli_menu(cls, sound_settings=None):
        """Text-based menu alternative for environments without a graphical display.

        Returns a tuple ``(action, sound_settings, user)`` where ``action`` is
        one of ``'start'`` or ``'quit'``. The sound_settings dict is mutable and
        shares the same keys used by the normal UI so toggles remain consistent.
        Authentication is handled using the same helpers as the GUI menu.
        """
        m = cls(screen=None, font=None, sound_settings=sound_settings)
        while True:
            print("\n=== POTÁPĚČ MENU ===")
            print("1) Start game")
            print("2) Sound settings")
            print("3) Open leaderboard (web)")
            print("4) Quit")
            choice = input("Select option: ").strip()
            if choice == '1':
                if not m.user:
                    # perform authentication
                    while True:
                        uname = input("Username: ").strip()
                        pwd = input("Password: ")
                        m.u = uname
                        m.p = pwd
                        res = m._attempt_login()
                        if res == 'start':
                            break
                        print(m.auth_msg or "Login failed, try again")
                return 'start', m.sound, m.user
            elif choice == '2':
                while True:
                    print("\nSound settings:")
                    for i, k in enumerate(cls.SOUND_KEYS, start=1):
                        print(f"{i}) {k}: {'On' if m.sound.get(k, True) else 'Off'}")
                    base = len(cls.SOUND_KEYS)
                    for j, vk in enumerate(cls.VOLUME_KEYS, start=1):
                        vol = int(m.sound.get(vk, 1.0) * 100)
                        print(f"{base+j}) {vk.replace('_volume','').title()} vol: {vol}%")
                    print(f"{base+len(cls.VOLUME_KEYS)+1}) Back")
                    sub = input("Select: ").strip()
                    if not sub.isdigit():
                        break
                    idx = int(sub) - 1
                    if idx < len(cls.SOUND_KEYS):
                        key = cls.SOUND_KEYS[idx]
                        m.sound[key] = not m.sound.get(key, True)
                        continue
                    elif idx < len(cls.SOUND_KEYS) + len(cls.VOLUME_KEYS):
                        vk = cls.VOLUME_KEYS[idx - len(cls.SOUND_KEYS)]
                        try:
                            newv = float(input("Enter volume (0-100): ").strip()) / 100.0
                            m.sound[vk] = max(0.0, min(1.0, newv))
                        except Exception:
                            pass
                        continue
                    else:
                        break
            elif choice == '3':
                open_leaderboard_url()
            elif choice == '4':
                return 'quit', m.sound, m.user
            else:
                print("Unknown option")
