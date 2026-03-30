import pygame, webbrowser, socket
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import create_user, get_user
from .settings import SCREEN_W, SCREEN_H, WEB_URL, WEB_HOST, WEB_PORT


def open_leaderboard_url():
    """Zkus otevřít žebříček na dosažitelné lokální portu.

    Pořadí preference: nakonfigurovaný `WEB_PORT`, pak běžné vývojové porty 5001,5000,8000.
    Otevře první, který přijme TCP spojení na `WEB_HOST`.
    """
    ports = [WEB_PORT, 5001, 5000, 8000]
    seen = set()
    for p in ports:
        if p in seen:
            continue
        seen.add(p)
        try:
            with socket.create_connection((WEB_HOST, int(p)), timeout=0.25):
                url = f'http://{WEB_HOST}:{p}'
                try:
                    webbrowser.open(url)
                    return True
                except Exception:
                    pass
        except Exception:
            continue
    try:
        webbrowser.open(WEB_URL)
        return True
    except Exception:
        return False


class Menu:
    def __init__(self, screen, font, sound_settings=None):
        self.screen = screen; self.font = font
        self.selected = 0
        self.sound_settings = sound_settings if sound_settings is not None else {'menu_music': True, 'ingame_music': True, 'vfx': True}
        self.mode = 'main'  # 'main', 'sound' nebo 'auth'
        self.button_rects = []
        self.user = None
        self._auth_username = ''
        self._auth_password = ''
        self._auth_active = 'username'  # or 'password' or 'none'
        self._auth_message = ''

    def draw(self):
        self.screen.fill((10,30,60))  # pozadí v tématu oceánu
        title = self.font.render('POTÁPĚČ', True, (255,255,255))
        self.screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 60))
        start_y = 160
        self.button_rects = []
        if self.mode == 'main':
            options = ['Start Game', 'Sound...', 'Open Leaderboard (web)', 'Quit']
        else:
            options = [f'Menu Music: {"On" if self.sound_settings.get("menu_music") else "Off"}',
                       f'Ingame Music: {"On" if self.sound_settings.get("ingame_music") else "Off"}',
                       f'VFX: {"On" if self.sound_settings.get("vfx") else "Off"}',
                       'Back']

        if self.mode == 'auth':
            ulabel = self.font.render('Username:', True, (255,255,255))
            self.screen.blit(ulabel, (SCREEN_W//2 - 200, start_y))
            uname_rect = pygame.Rect(SCREEN_W//2 - 80, start_y, 360, 48)
            self._uname_rect = uname_rect
            pygame.draw.rect(self.screen, (255,255,255) if self._auth_active == 'username' else (180,180,180), uname_rect, border_radius=6)
            uname_txt = self.font.render(self._auth_username or '<enter>', True, (0,0,0))
            self.screen.blit(uname_txt, (uname_rect.x + 8, uname_rect.y + 10))

            plabel = self.font.render('Password:', True, (255,255,255))
            self.screen.blit(plabel, (SCREEN_W//2 - 200, start_y + 80))
            pwd_rect = pygame.Rect(SCREEN_W//2 - 80, start_y + 80, 360, 48)
            self._pwd_rect = pwd_rect
            pygame.draw.rect(self.screen, (255,255,255) if self._auth_active == 'password' else (180,180,180), pwd_rect, border_radius=6)
            pwd_mask = '*' * len(self._auth_password)
            pwd_txt = self.font.render(pwd_mask or '<enter>', True, (0,0,0))
            self.screen.blit(pwd_txt, (pwd_rect.x + 8, pwd_rect.y + 10))

            btns = ['Login/Signup', 'Open Web', 'Back']
            self.button_rects = []
            for i,opt in enumerate(btns):
                rect = pygame.Rect(SCREEN_W//2 - 180 + i*140, start_y + 160, 160, 44)
                pygame.draw.rect(self.screen, (20,120,200), rect, border_radius=6)
                txt = self.font.render(opt, True, (255,255,255))
                self.screen.blit(txt, (rect.x + 12, rect.y + 8))
                self.button_rects.append(rect)

            if self._auth_message:
                msg = self.font.render(self._auth_message, True, (240,240,120))
                self.screen.blit(msg, (SCREEN_W//2 - msg.get_width()//2, start_y + 220))

            pygame.display.flip()
            return

        for i,opt in enumerate(options):
            rect = pygame.Rect(SCREEN_W//2 - 140, start_y + i*80, 280, 56)
            color = (30,144,255) if i == self.selected else (20,90,160)
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            txt = self.font.render(opt, True, (255,255,255))
            self.screen.blit(txt, (rect.x + 20, rect.y + 12))
            self.button_rects.append(rect)
        pygame.display.flip()

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if self.mode == 'auth':
                try:
                    print(f"[menu-debug] KEYDOWN auth key={ev.key} unicode='{getattr(ev, 'unicode', '')}' active={self._auth_active}")
                except Exception:
                    pass
                if ev.key == pygame.K_TAB:
                    self._auth_active = 'password' if self._auth_active == 'username' else 'username'
                    return None
                if ev.key == pygame.K_BACKSPACE:
                    if self._auth_active == 'username':
                        self._auth_username = self._auth_username[:-1]
                    else:
                        self._auth_password = self._auth_password[:-1]
                    return None
                if ev.key == pygame.K_RETURN:
                    return self._attempt_login()
                if ev.unicode and len(ev.unicode) == 1:
                    if self._auth_active == 'username':
                        self._auth_username += ev.unicode
                    else:
                        self._auth_password += ev.unicode
                return None
            else:
                if ev.key == pygame.K_DOWN: self.selected = (self.selected + 1) % len(self.button_rects)
                if ev.key == pygame.K_UP: self.selected = (self.selected - 1) % len(self.button_rects)
                if ev.key == pygame.K_RETURN:
                    return self.activate(self.selected)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mx,my = ev.pos
            try:
                print(f"[menu-debug] MOUSEDOWN pos={ev.pos} mode={self.mode} has_uname_rect={hasattr(self, '_uname_rect')} has_pwd_rect={hasattr(self, '_pwd_rect')}")
            except Exception:
                pass
            if self.mode == 'auth':
                try:
                    if getattr(self, '_uname_rect', None) and self._uname_rect.collidepoint(mx, my):
                        self._auth_active = 'username'
                        return None
                    if getattr(self, '_pwd_rect', None) and self._pwd_rect.collidepoint(mx, my):
                        self._auth_active = 'password'
                        return None
                except Exception:
                    pass
            for i,r in enumerate(self.button_rects):
                if r.collidepoint(mx,my):
                    if self.mode == 'auth':
                        if i == 0:
                            return self._attempt_login()
                        if i == 1:
                            open_leaderboard_url()
                            return None
                        if i == 2:
                            self.mode = 'main'
                            return None
                    else:
                        return self.activate(i)
        return None

    def activate(self, idx):
        if self.mode == 'main':
            options = ['Start Game', 'Sound...', 'Open Leaderboard (web)', 'Quit']
            opt = options[idx]
            if opt == 'Start Game':
                if not self.user:
                    self.mode = 'auth'
                    self._auth_active = 'username'
                    self._auth_message = ''
                    return None
                return 'start'
            if opt == 'Sound...':
                self.mode = 'sound'
                self.selected = 0
                return None
            if opt == 'Open Leaderboard (web)':
                open_leaderboard_url()
                return None
            if opt == 'Quit':
                return 'quit'
        else:
            if idx == 0:
                self.sound_settings['menu_music'] = not self.sound_settings.get('menu_music', True)
                return None
            if idx == 1:
                self.sound_settings['ingame_music'] = not self.sound_settings.get('ingame_music', True)
                return None
            if idx == 2:
                self.sound_settings['vfx'] = not self.sound_settings.get('vfx', True)
                return None
            if idx == 3:
                self.mode = 'main'
                self.selected = 0
                return None

    def _attempt_login(self):
        uname = self._auth_username.strip()
        pwd = self._auth_password
        if not uname or not pwd:
            self._auth_message = 'Enter username and password'
            return None
        row = get_user(uname)
        if row and check_password_hash(row[2], pwd):
            self.user = uname
            self.mode = 'main'
            self._auth_username = ''
            self._auth_password = ''
            self._auth_message = 'Logged in'
            return 'start'
        ph = generate_password_hash(pwd)
        ok = create_user(uname, ph)
        if ok:
            self.user = uname
            self.mode = 'main'
            self._auth_username = ''
            self._auth_password = ''
            self._auth_message = 'Account created and logged in'
            return 'start'
        self._auth_message = 'Invalid credentials or username taken'
        return None
