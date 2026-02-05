import pygame, random, math, time, os, urllib.request, urllib.parse
from .settings import *
from .player import Player
from .physics import move_and_collide
from .camera import world_to_screen
from .bubbles import generate_bubbles, inside_bubble
from .monsters import Monster
from .qte import QTE
from .collision import resolve_aabb
from .menu import Menu
from .obstacles import generate_side_cliffs
from .environment import get_background_colors
from .rasy import generate_bioluminescence, draw_bioluminescence
from .savegame import load_game, save_game
from database.database import ensure_db, save_score, top_scores

# vzdálenos, za nimiž jsou entity odstraňovány 
DESPAWN_DISTANCE_MONSTER = 5000
# zvětšit vzdálenost zmizení bublin, aby předem vygenerované hluboké bubliny nebyly okamžitě odstraněny
DESPAWN_DISTANCE_BUBBLE = 20000

def point_in_polygon(x, y, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and \
           (x < (x2 - x1) * (y - y1) / (y2 - y1 + 0.00001) + x1):
            inside = not inside
    return inside


def build_wall_polygon(profile, camera_y, sea_screen, side):
    pts = []
    for (x, wy) in profile:
        sy = wy - camera_y + SCREEN_H // 2
        if sy >= sea_screen:
            pts.append((int(x), int(sy)))

    if not pts:
        return []

    if side == "left":
        return [(0, sea_screen)] + pts + [(0, SCREEN_H)]
    else:
        return [(SCREEN_W, sea_screen)] + pts + [(SCREEN_W, SCREEN_H)]


def draw_stone_wall(screen, poly):
    if not poly:
        return

    pygame.draw.polygon(screen, (55, 50, 45), poly)

    for _ in range(120):
        x, y = random.choice(poly)
        pygame.draw.circle(
            screen,
            (80, 72, 65),
            (x + random.randint(-12, 12), y + random.randint(-12, 12)),
            random.randint(1, 3),
        )

    for _ in range(40):
        x, y = random.choice(poly)
        pygame.draw.circle(
            screen,
            (0, 200, 255),
            (x + random.randint(-18, 18), y + random.randint(-18, 18)),
            1,
        )

class Game:
    instance = None

    def __init__(self):
        Game.instance = self
        pygame.init()
        pygame.display.set_caption("Potápěč v1.6")

        info = pygame.display.Info()
        self.display_w, self.display_h = info.current_w, info.current_h
        self.display = pygame.display.set_mode(
            (self.display_w, self.display_h), pygame.FULLSCREEN
        )

        self.surface = pygame.Surface((SCREEN_W, SCREEN_H))
        self.screen = self.surface
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 26)
        self.small_font = pygame.font.SysFont(None, 20)
        self.loading_tips = [
            "Tip: Use arrow keys to swim smoothly.",
            "Tip: Collect bubbles to refill oxygen.",
            "Tip: Avoid jellyfish — they stun you.",
            "Tip: Sharks deplete oxygen faster on attack.",
            "Tip: Use QTE to escape octopus encounters.",
            "Tip: Press Esc to quit at any time.",
        ]

        self.state = "intro"
        ensure_db()
        self.menu = Menu(self.screen, self.font)
        self._log_debug("Game initialized")
        self.charge = 0
        self.charging = False
        # kontejner pro načtené sprity monster (typ -> Povrch)
        self.monster_sprites = {}
        # zkuste načíst zdroje (obrázky) brzy, aby je Draw mohl použít
        try:
            self.load_resources()
        except Exception:
            pass

    def _log_debug(self, msg):
        try:
            print(msg, flush=True)
        except Exception:
            pass
        try:
            with open('game_run.log', 'a', encoding='utf-8') as f:
                f.write(msg + '\n')
        except Exception:
            pass

    def reset_game(self):
        self.camera_y = START_SPAWN_Y
        self.player = Player(120, START_SPAWN_Y)
        self.camera_y = self.player.world_y
        self.charge = 0
        self.charging = False
        save = load_game()
        self.player.oxygen = save.get("oxygen", 100)
        self.score = save.get("score", 0)
        self.best_depth = save.get("best_depth", 0)
        self.player_name = getattr(getattr(self, 'menu', None), 'user', None) or save.get("name", "Player")
        
        if not hasattr(self, 'obstacles'):
            res = generate_side_cliffs()
            if hasattr(res, 'left_profile') and hasattr(res, 'right_profile'):
                self.obstacles = res
                self.left_profile = res.left_profile
                self.right_profile = res.right_profile
            else:
                self.obstacles, self.left_profile, self.right_profile = res
            try:
                if hasattr(self.obstacles, 'ensure_to'):
                    self.obstacles.ensure_to(SEA_LEVEL_Y + SCREEN_H * 3)
            except Exception:
                pass
        try:
            left_x = int(self.left_profile[0][0]) if hasattr(self, 'left_profile') and self.left_profile else 40
        except Exception:
            left_x = 40
        # počáteční útes: šířka/výška, vycentrované pod spawnem hráče
        sc_w = 200
        sc_h = 200
        start_x = int(self.player.world_x - sc_w // 2)
        start_x = max(-200, min(SCREEN_W - sc_w, start_x))
        self.starting_cliff = pygame.Rect(start_x, SEA_LEVEL_Y - sc_h, sc_w, sc_h)
        self.cliffs = [self.starting_cliff]
        # ujisti se, že počáteční útes je mezi kolizními překážkami, aby hráč nespadl při spawnování
        try:
            if not any(getattr(o, 'x', None) == self.starting_cliff.x and getattr(o, 'y', None) == self.starting_cliff.y for o in self.obstacles):
                self.obstacles.append(self.starting_cliff)
        except Exception:
            pass

        # umístit hráče stojícího na vrcholu počátečního útesu
        try:
            self.player.world_x = float(self.starting_cliff.x + (self.starting_cliff.width - self.player.w) // 2)
            # umístit hráče o něco výše nad útes, aby stál pohodlně
            self.player.world_y = float(self.starting_cliff.top - self.player.h - 20)
            self.camera_y = self.player.world_y
        except Exception:
            pass

        if not hasattr(self, 'bubbles'):
            self.bubbles = generate_bubbles()
        self.monsters = []
        self.spawn_timer = 0

        self.qte = QTE()
        self.qte_source = None

        if not hasattr(self, 'algae'):
            self.algae = generate_bioluminescence()
        self.score = 0

    def _loading_update(self, text, fraction=None, tip=None):
        # vykreslit obrazovku načítání s volitelným ukazatelem postupu na interním povrchu a přepnout na displej
        self.surface.fill((10, 30, 60))
        t = self.font.render(text, True, (255, 255, 255))
        self.surface.blit(t, (SCREEN_W // 2 - t.get_width() // 2, SCREEN_H // 2 - t.get_height() // 2 - 24))

        if fraction is not None:
            bar_w = min(800, SCREEN_W - 200)
            bar_h = 22
            bx = SCREEN_W // 2 - bar_w // 2
            by = SCREEN_H // 2 + 8
            # obrys
            pygame.draw.rect(self.surface, (200, 200, 200), (bx - 2, by - 2, bar_w + 4, bar_h + 4), border_radius=6)
            # pozadí
            pygame.draw.rect(self.surface, (40, 40, 80), (bx, by, bar_w, bar_h), border_radius=6)
            # vyplněná část
            fill_w = int(max(0, min(1.0, fraction)) * bar_w)
            if fill_w > 0:
                pygame.draw.rect(self.surface, (30, 200, 160), (bx, by, fill_w, bar_h), border_radius=6)

        if tip is None:
            tip = random.choice(self.loading_tips)
        tip_surf = self.small_font.render(tip, True, (200, 200, 200))
        tip_x = SCREEN_W // 2 - tip_surf.get_width() // 2
        tip_y = SCREEN_H // 2 + 40
        self.surface.blit(tip_surf, (tip_x, tip_y))
        scaled = pygame.transform.scale(self.surface, (self.display_w, self.display_h))
        self.display.blit(scaled, (0, 0))
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

    def load_resources(self):
        # Hledejte sprity monster v souboru potapec/assets/monsters/<type>.png
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'monsters'))
        types = ['shark', 'octopus', 'jelly', 'purple', 'red']
        for t in types:
            fn = os.path.join(base, f"{t}.png")
            try:
                if os.path.exists(fn):
                    img = pygame.image.load(fn).convert_alpha()
                    self.monster_sprites[t] = img
                else:
                    # ujistěte se, že adresář s aktivy existuje
                    try:
                        os.makedirs(os.path.dirname(fn), exist_ok=True)
                    except Exception:
                        pass
                    alt = os.path.join(os.path.dirname(__file__), f"{t}.png")
                    if os.path.exists(alt):
                        img = pygame.image.load(alt).convert_alpha()
                        self.monster_sprites[t] = img
                    else:
                        #vygeneruje jednoduchý zástupný sprite a uloži ho
                        try:
                            surf = pygame.Surface((40, 40), pygame.SRCALPHA)
                            col = {
                                'shark': (200, 50, 50),
                                'octopus': (150, 80, 200),
                                'jelly': (255, 150, 50),
                                'purple': (180, 50, 200),
                                'red': (220, 40, 40),
                            }.get(t, (180, 180, 180))
                            surf.fill((0, 0, 0, 0))
                            pygame.draw.circle(surf, col, (20, 20), 18)
                            pygame.image.save(surf, fn)
                            self.monster_sprites[t] = surf
                        except Exception:
                            pass
            except Exception:
                try:
                    self._log_debug(f'Failed loading sprite for {t}')
                except Exception:
                    pass
        return

    def load_map_resources(self):
        self._log_debug('Starting map load steps')
        steps = [
            ("Loading save...", lambda: load_game()),
            ("Generating cliffs...", lambda: generate_side_cliffs()),
            ("Generating bubbles...", lambda: generate_bubbles()),
            ("Generating bioluminescence...", lambda: generate_bioluminescence()),
        ]

        total = len(steps)
        results = []
        for i, (label, fn) in enumerate(steps):
            frac = i / total
            tip = self.loading_tips[i % len(self.loading_tips)]
            self._loading_update(label, fraction=frac, tip=tip)
            try:
                self._log_debug(f'Executing step: {label}')
                res = fn()
                self._log_debug(f'Finished step: {label}')
            except Exception as e:
                self._log_debug(f'Error during step {label}: {e}')
                raise
            results.append(res)
            self.clock.tick(30)

        # uložit výsledky do příslušných atributů
        # results[0] je save (zde nepoužito přímo)
        if len(results) > 1 and results[1] is not None:
            res = results[1]
            if hasattr(res, 'left_profile') and hasattr(res, 'right_profile'):
                self.obstacles = res
                self.left_profile = res.left_profile
                self.right_profile = res.right_profile
            else:
                self.obstacles, self.left_profile, self.right_profile = res
        if len(results) > 2 and results[2] is not None:
            self.bubbles = results[2]
        if len(results) > 3 and results[3] is not None:
            self.algae = results[3]
        self._loading_update("Map ready", fraction=1.0)

    def run(self):
        while True:
            # zde vždy zpracovávat události, aby OS nezobrazil aplikaci jako nereagující
            try:
                pygame.event.pump()
            except Exception:
                pass

            dt = self.clock.tick(FPS) / 1000
            self._dt = dt

            # debug: zaznamenat změny stavu
            prev = getattr(self, '_prev_state', None)
            if prev != self.state:
                self._log_debug(f'State change: {prev} -> {self.state}')
                self._prev_state = self.state

            if self.state == "intro":
                self.state = "menu"
            elif self.state == "menu":
                self.menu_loop()
            elif self.state == "playing":
                self._log_debug('Entering game_loop')
                self.game_loop(dt)
                self._log_debug('Exiting game_loop')
            elif self.state == "gameover":
                self.gameover_loop(dt)

    def menu_loop(self):
        for ev in pygame.event.get():
            # přepočet souřadnic myši z displeje -> povrch, aby kliky trefily správná tlačítka
            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                dx, dy = ev.pos
                sx = int(dx * SCREEN_W / self.display_w)
                sy = int(dy * SCREEN_H / self.display_h)
                attrs = {k: getattr(ev, k) for k in ev.__dict__ if not k.startswith('_')}
                attrs['pos'] = (sx, sy)
                ev = pygame.event.Event(ev.type, attrs)
            res = self.menu.handle_event(ev)
            if res == "start":
                # zobrazit obrazovku načítání a načíst (možná pomalé) zdroje mapy nyní
                self._loading_update("Loading map...")
                self.load_map_resources()
                # nyní resetovat herní stav (používá výše načtené zdroje)
                self.reset_game()
                self.state = "playing"
            if res == "quit":
                pygame.quit()
                raise SystemExit

        self.menu.draw()
        self._flip()

    def game_loop(self, dt):
        self.is_grounded = False
        try:
            pr = self.player.rect()
            probe = pygame.Rect(pr.x, pr.y + pr.height, pr.width, 4)
            for o in getattr(self, 'obstacles', []):
               if probe.colliderect(o):
                     self.is_grounded = True    
                     break
        except Exception:
         self.is_grounded = False
        # zpracovat události, aby okno zůstalo responzivní
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # pomocná funkce pro zjištění, zda hráč stojí na překážce
            def _check_grounded():
                try:
                    pr = self.player.rect()
                    probe = pygame.Rect(pr.x, pr.y + pr.height, pr.width, 4)
                    for o in getattr(self, 'obstacles', []):
                        try:
                            if probe.colliderect(o):
                                return True
                        except Exception:
                            try:
                                ox = getattr(o, 'x', None); oy = getattr(o, 'y', None)
                                ow = getattr(o, 'width', None) or getattr(o, 'w', None)
                                oh = getattr(o, 'height', None) or getattr(o, 'h', None)
                                if None not in (ox, oy, ow, oh):
                                    if (probe.x < ox + ow and probe.x + probe.width > ox and probe.y < oy + oh and probe.y + probe.height > oy):
                                        return True
                            except Exception:
                                pass
                    return False
                except Exception:
                    return False

            if ev.type == pygame.KEYDOWN:
                # zda je střed hráče ve vodě
                in_water = self.player.world_y >= SEA_LEVEL_Y

                # zpracovat vstupy QTE jako první, pokud aktivní
                if getattr(self, 'qte', None) and self.qte.active:
                    def _disable_monster():
                        try:
                            if getattr(self, 'qte_source', None) in self.monsters:
                                self.monsters.remove(self.qte_source)
                        except Exception:
                            pass
                        self.qte_source = None

                    self.qte.handle_key(ev.key, self.player, disable_callback=_disable_monster)
                    continue

                # globální klávesy
                if ev.key == pygame.K_ESCAPE:
                    self.state = 'menu'
                    return

                if ev.key == pygame.K_SPACE:
                    in_water = self.player.world_y >= SEA_LEVEL_Y
                    grounded = _check_grounded()
                    stunned = getattr(self.player, 'stunned_until', 0) > time.time()
                    # povolit nabíjení při stání na zemi nebo pod vodou, ale
                    # nedovolit začít nabíjení pokud je hráč omráčen
                    if not stunned and (grounded or in_water):
                        self.charging = True
                    else:
                        self.charging = False
                    self.charge = 0

            elif ev.type == pygame.KEYUP:
                # uvolnění nabití -> impulz směrem k myši při uvolnění mezerníku
                if ev.key == pygame.K_SPACE and getattr(self, 'charging', False):
                    in_water = self.player.world_y >= SEA_LEVEL_Y
                    grounded = _check_grounded()
                    stunned = getattr(self.player, 'stunned_until', 0) > time.time()
                    if stunned:
                        self.charging = False
                        self.charge = 0
                        continue
                    if not in_water and not grounded:
                        self.charging = False
                        self.charge = 0
                        continue
                    mx, my = pygame.mouse.get_pos()
                    sx = int(mx * SCREEN_W / self.display_w)
                    sy = int(my * SCREEN_H / self.display_h)
                    wx = sx
                    wy = sy + self.camera_y - SCREEN_H // 2
                    dx = (wx - (self.player.world_x + self.player.w / 2))
                    dy = (wy - (self.player.world_y + self.player.h / 2))
                    dist = math.hypot(dx, dy) or 1
                    nx = dx / dist
                    ny = dy / dist
                    H_BIAS = 2.0
                    V_BIAS = 1.2
                    nx *= H_BIAS
                    ny *= V_BIAS
                    nlen = math.hypot(nx, ny) or 1
                    nx /= nlen
                    ny /= nlen
                    if self.player.world_y < SEA_LEVEL_Y:
                        force = self.charge * 1.6
                        vfactor = 1.0 if ny > 0 else 1.6
                    else:
                        force = self.charge * 0.6
                        vfactor = 1.8 if ny > 0 else 1.0

                    self.player.apply_impulse(nx * force, ny * force * vfactor)
                    self.charging = False
                    self.charge = 0

        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT]
        right = keys[pygame.K_RIGHT]
        up = keys[pygame.K_UP]
        down = keys[pygame.K_DOWN]
        if left:
            self.player.velocity_x -= 0.6 * dt * 60
        if right:
            self.player.velocity_x += 0.6 * dt * 60
        if getattr(self, 'charging', False):
            if getattr(self.player, 'stunned_until', 0) > time.time():
                self.charging = False
                self.charge = 0
            else:
                self.charge = min(MAX_CHARGE, self.charge + CHARGE_RATE * dt * 60)
        if self.player.world_y < SEA_LEVEL_Y:
            self.player.velocity_y += GRAVITY_PX_PER_FRAME
        else:
            self.player.velocity_y += PASSIVE_DESCENT_PX_PER_FRAME
            if up:
                self.player.velocity_y -= SWIM_UP_PX_PER_FRAME
            if down:
                self.player.velocity_y += FAST_DESCENT_PX_PER_FRAME
        from .physics import move_and_collide
        move_and_collide(self.player, self.obstacles)
        try:
            self.spawn_timer += dt
        except Exception:
            self.spawn_timer = getattr(self, 'spawn_timer', 0) + dt

        # spawnovat častěji (zkrácený interval)
        # frekvence a množství spawnu škálují podle hloubky: hlouběji -> častěji a větší skupiny
        depth_px = max(0, self.player.world_y - SEA_LEVEL_Y)
        depth_m = depth_px / PIXELS_PER_METER
        # spawn less often: increase base interval and scale
        spawn_interval = max(3.5, 6.0 - (min(depth_m, 500.0) / 500.0) * 3.0)
        if getattr(self, 'spawn_timer', 0) > spawn_interval:
            self.spawn_timer = 0
            try:
                obs = getattr(self, 'obstacles', [])
                spawn_count = 1 + int(depth_m / 180)
                spawn_count = min(spawn_count, 4)
                for _ in range(spawn_count):
                    attempts = 0
                    while attempts < 10:
                        attempts += 1
                        mx = int(self.player.world_x + random.randint(-300, 300))
                        min_y = int(self.player.world_y + 50)
                        max_extra = 2000 + int(depth_m * 6)
                        lower = max(SEA_LEVEL_Y + 20, min_y)
                        upper = SEA_LEVEL_Y + max_extra
                        # zajistěte horní hranici >= dolní, abyste se vyhnuli ValueError a umožnili objevení se poblíž hráče, když je velmi hluboko
                        if upper < lower:
                            upper = lower + max(800, int(depth_m * 2))
                        my = int(random.randint(lower, upper))
                        d = my - SEA_LEVEL_Y
                        # určete možné typy monster na základě hloubky
                        if d < 150:
                            possible = ['jelly', 'purple', 'red']
                        elif d < 400:
                            possible = ['jelly', 'octopus', 'purple', 'red']
                        else:
                            possible = ['shark', 'octopus', 'purple', 'red', 'jelly']
                        mtyp = random.choice(possible)
                        # vyber velikost kandidáta odpovídající velikosti monstra 
                        # použijte velikost hitboxu pro kontrolu umístění/kolize při spawnu
                        sw = 40
                        sh = sw
                        cand = pygame.Rect(mx, my, sw, sh)
                        if not (0 < mx < SCREEN_W - sw):
                            continue
                        collision = False
                        for o in obs:
                            try:
                                if cand.colliderect(o):
                                    collision = True
                                    break
                            except Exception:
                                try:
                                    ox = getattr(o, 'x', None)
                                    oy = getattr(o, 'y', None)
                                    ow = getattr(o, 'width', None) or getattr(o, 'w', None)
                                    oh = getattr(o, 'height', None) or getattr(o, 'h', None)
                                    if None not in (ox, oy, ow, oh):
                                        if (mx < ox + ow and mx + 40 > ox and my < oy + oh and my + 40 > oy):
                                            collision = True
                                            break
                                except Exception:
                                    pass

                        if collision:
                            continue
                        # 30% šance, že se zde skutečně objeví monstrum
                        if random.random() > 0.30:
                            continue
                        mon = Monster(mtyp, mx, my)
                        self.monsters.append(mon)
                        try:
                            self._log_debug(f"Spawned monster: {mtyp} at ({mx},{my}) depth={d}")
                        except Exception:
                            pass
                        break
            except Exception:
                pass
        for m in list(getattr(self, 'monsters', [])):
            try:
                m.update(self.player)
                r = pygame.Rect(int(m.x), int(m.y), m.w, m.h)
                for o in getattr(self, 'obstacles', []):
                    try:
                        if r.colliderect(o):
                            if m.y < o.top:
                                m.y = o.top - m.h
                            else:
                                m.y = o.bottom + 1
                            break
                    except Exception:
                        try:
                            ox = getattr(o, 'x', None)
                            oy = getattr(o, 'y', None)
                            ow = getattr(o, 'width', None) or getattr(o, 'w', None)
                            oh = getattr(o, 'height', None) or getattr(o, 'h', None)
                            if None not in (ox, oy, ow, oh):
                                if (int(m.x) < ox + ow and int(m.x) + m.w > ox and int(m.y) < oy + oh and int(m.y) + m.h > oy):
                                    if m.y < oy:
                                        m.y = oy - m.h
                                    else:
                                        m.y = oy + oh + 1
                                    break
                        except Exception:
                            pass
                try:
                    if m.y < SEA_LEVEL_Y + 5:
                        m.y = SEA_LEVEL_Y + 5
                        if getattr(m, 'state', None) == 'chase':
                            m.state = 'patrol'
                except Exception:
                    pass
            except Exception:
                pass
            try:
                for m in list(getattr(self, 'monsters', [])):
                    try:
                        if getattr(m, 'state', None) != 'attack':
                            continue
                        pr = self.player.rect()
                        mr = pygame.Rect(int(m.x), int(m.y), m.w, m.h)
                        if pr.colliderect(mr):
                            if m.typ == 'shark':
                                try:
                                    self.player.oxygen -= SHARK_O2_PENALTY
                                except Exception:
                                    self.player.oxygen -= 1.0
                            elif m.typ == 'jelly':
                                try:
                                    import random as _r
                                    self.player.stunned_until = time.time() + _r.uniform(JELLY_STUN_MIN, JELLY_STUN_MAX)
                                except Exception:
                                    self.player.stunned_until = time.time() + 2.0
                            elif m.typ == 'octopus':
                                if getattr(self, 'qte', None) and not self.qte.active:
                                    self.qte.start()
                                    self.qte_source = m
                                    m.still_until = time.time() + 2.0
                    except Exception:
                        pass
            except Exception:
                pass
            except Exception:
                pass

        # zmizí monstra, která jsou daleko od hráče
        try:
            for m in list(getattr(self, 'monsters', [])):
                try:
                    dx = (m.x + m.w/2) - (self.player.world_x + self.player.w/2)
                    dy = (m.y + m.h/2) - (self.player.world_y + self.player.h/2)
                    if math.hypot(dx, dy) > DESPAWN_DISTANCE_MONSTER:
                        try:
                            self.monsters.remove(m)
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

        try:
            if getattr(self, 'qte', None) and not self.qte.active:
                for m in list(getattr(self, 'monsters', [])):
                    try:
                        if m.typ == 'octopus' and m.state == 'attack':
                            self.qte.start()
                            self.qte_source = m
                            m.still_until = time.time() + 2.0
                            break
                    except Exception:
                        pass

            if getattr(self, 'qte', None) and self.qte.active:
                self.qte.check_timeout(self.player)
                if not self.qte.active:
                    self.qte_source = None
        except Exception:
            pass

        # manipulace s kyslíkem
        # zmizení bublin, které jsou daleko od hráče
        try:
            for b in list(getattr(self, 'bubbles', [])):
                try:
                    bx = b.x
                    by = b.y
                    px = self.player.world_x + self.player.w/2
                    py = self.player.world_y + self.player.h/2
                    if math.hypot(bx - px, by - py) > DESPAWN_DISTANCE_BUBBLE:
                        try:
                            self.bubbles.remove(b)
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

        in_air_bubble = any(inside_bubble(self.player, b) for b in self.bubbles)
        if self.player.world_y >= SEA_LEVEL_Y and not in_air_bubble:
            self.player.oxygen -= OXYGEN_DEPLETION_PER_FRAME
        else:
            self.player.oxygen = min(OXYGEN_MAX, self.player.oxygen + OXYGEN_RECOVER_PER_FRAME)
        self.camera_y = self.player.world_y
        try:
            if hasattr(self, 'obstacles') and hasattr(self.obstacles, 'ensure_to'):
                target = int(self.camera_y + SCREEN_H * 2)
                self.obstacles.ensure_to(target)
        except Exception:
            pass

        sea_screen = int(SEA_LEVEL_Y - self.camera_y + SCREEN_H // 2)
        px = self.player.world_x + self.player.w / 2
        py = self.player.world_y + self.player.h
        sx = int(px)
        sy = int(py - self.camera_y + SCREEN_H // 2)

        left_poly = build_wall_polygon(self.left_profile, self.camera_y, sea_screen, "left")
        right_poly = build_wall_polygon(self.right_profile, self.camera_y, sea_screen, "right")

        # Nepřidávat žádný další neviditelný posun, když je hráč uvnitř
        # polygonu stěny. Kolize jsou řešeny pomocí `move_and_collide` proti
        # `self.obstacles`. Odebrání posunu zabraňuje fiktivní bariéře na
        # hranách útesů.

        if self.player.oxygen <= 0:
            depth_m = int((self.player.max_depth_reached - SEA_LEVEL_Y) / PIXELS_PER_METER)
            self._pending_score = depth_m
            self._pending_oxygen = 0
            try:
                pname = getattr(self, 'input_name', None) or self.player_name or 'Player'
                pending_o2 = int(max(0, getattr(self.player, 'oxygen', 0)))
                save_score(pname, int(depth_m), int(pending_o2))
                self._save_message = f"Score saved as {pname}"
                self._save_message_until = time.time() + 3.0
            except Exception:
                pass
            try:
                from .settings import WEB_URL, WEB_API_TOKEN
                if WEB_URL:
                    url = WEB_URL.rstrip('/') + '/submit'
                    payload = {'name': pname, 'depth': str(int(depth_m)), 'oxygen': str(int(pending_o2))}
                    if WEB_API_TOKEN:
                        payload['token'] = WEB_API_TOKEN
                    data = urllib.parse.urlencode(payload).encode('utf-8')
                    req = urllib.request.Request(url, data=data, method='POST')
                    try:
                        urllib.request.urlopen(req, timeout=2.0)
                    except Exception:
                        pass
            except Exception:
                pass
            self.state = "gameover"

        self.draw()

    def draw(self):
        sky, water, fog = get_background_colors(self.player.world_y)
        self.screen.fill(water)

        sea_screen = int(SEA_LEVEL_Y - self.camera_y + SCREEN_H // 2)
        pygame.draw.rect(self.screen, sky, (0, 0, SCREEN_W, sea_screen))

        draw_bioluminescence(self.screen, self.camera_y, self.algae, self._dt)

        left_poly = build_wall_polygon(self.left_profile, self.camera_y, sea_screen, "left")
        right_poly = build_wall_polygon(self.right_profile, self.camera_y, sea_screen, "right")

        draw_stone_wall(self.screen, left_poly)
        draw_stone_wall(self.screen, right_poly)

        # vykreslit obdélníky překážek pro ladění / viditelnost
        try:
            screen_rect = pygame.Rect(0, 0, SCREEN_W, SCREEN_H)
            # nakreslit pouze počáteční útes jako viditelnou platformu; vyhnout se kreslení surových obdélníků překážek
            if hasattr(self, 'starting_cliff'):
                sc = self.starting_cliff
                sc_draw = pygame.Rect(sc.x, sc.y - self.camera_y + SCREEN_H // 2, sc.width, sc.height)
                pygame.draw.rect(self.screen, (120, 80, 40), sc_draw)
        except Exception:
            pass

        # vykreslit bubliny (svět -> obrazovka)
        try:
            for b in getattr(self, 'bubbles', []):
                try:
                    bx = int(b.x)
                    by = int(b.y - self.camera_y + SCREEN_H // 2)
                    # only draw if on-screen (with small margin)
                    if by < -10 or by > SCREEN_H + 10:
                        continue
                    pygame.draw.circle(self.screen, (180, 220, 255), (bx, by), int(b.r), 1)
                except Exception:
                    continue
        except Exception:
            pass

        # vykreslit příšery (preferovat PNG spritey, fallback na obdélníky)
        try:
            for m in getattr(self, 'monsters', []):
                mx = int(m.x)
                my = int(m.y - self.camera_y + SCREEN_H // 2)
                sprite = None
                try:
                    sprite = self.monster_sprites.get(m.typ)
                except Exception:
                    sprite = None
                if sprite:
                    try:
                        draw_w = getattr(m, 'render_w', m.w)
                        draw_h = getattr(m, 'render_h', m.h)
                        dx = mx - (draw_w - m.w) // 2
                        dy = my - (draw_h - m.h) // 2
                        img = pygame.transform.scale(sprite, (draw_w, draw_h))
                        self.screen.blit(img, (dx, dy))
                    except Exception:
                        pygame.draw.rect(self.screen, (180, 180, 180), (mx, my, m.w, m.h))
                else:
                    # typy map na viditelné barvy: červená -> žralok, fialová -> chobotnice, meduza -> oranžová
                    color_map = {
                        'shark': (200, 50, 50),
                        'red': (200, 50, 50),
                        'octopus': (150, 80, 200),
                        'purple': (150, 80, 200),
                        'jelly': (255, 150, 50),
                    }
                    color = color_map.get(m.typ, (180, 180, 180))
                    draw_w = getattr(m, 'render_w', m.w)
                    draw_h = getattr(m, 'render_h', m.h)
                    dx = mx - (draw_w - m.w) // 2
                    dy = my - (draw_h - m.h) // 2
                    pygame.draw.rect(self.screen, color, (dx, dy, draw_w, draw_h))
        except Exception:
            pass

        sx, sy = world_to_screen(
            self.player.world_x, self.player.world_y, self.camera_y, SCREEN_H
        )

        # vykreslit šipku nabití (průhlednou) zobrazující směr a nabití
        try:
            if getattr(self, 'charging', False) and getattr(self, 'charge', 0) > 0:
                mx, my = pygame.mouse.get_pos()
                msx = int(mx * SCREEN_W / self.display_w)
                msy = int(my * SCREEN_H / self.display_h)
                wx = msx
                wy = msy + self.camera_y - SCREEN_H // 2
                dx = wx - (self.player.world_x + self.player.w / 2)
                dy = wy - (self.player.world_y + self.player.h / 2)
                dist = math.hypot(dx, dy) or 1
                nx = dx / dist
                ny = dy / dist
                frac = max(0.0, min(1.0, float(self.charge) / float(MAX_CHARGE if 'MAX_CHARGE' in globals() else 1)))
                max_len = min(180, SCREEN_W // 4)
                length = int(frac * max_len)
                start = (int(sx + self.player.w / 2), int(sy + self.player.h / 2))
                end = (int(start[0] + nx * length), int(start[1] + ny * length))
                arrow_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

                # barevný přechod: zelená -> žlutá -> červená
                if frac <= 0.5:
                    t = frac * 2.0
                    r = int(0 + t * 255)
                    g = 255
                else:
                    t = (frac - 0.5) * 2.0
                    r = 255
                    g = int(255 * (1.0 - t))
                b = 0
                line_col = (r, g, b, 150)

                # nakreslit silnější osu (širší) a větší trojúhelníkovou hlavu
                shaft_w = 10 + int(frac * 8)
                pygame.draw.line(arrow_surf, line_col, start, end, shaft_w)
                head_w = 18 + int(frac * 12)
                px = -ny
                py = nx
                p1 = (end[0] + int(px * head_w), end[1] + int(py * head_w))
                p2 = (end[0] - int(px * head_w), end[1] - int(py * head_w))
                pygame.draw.polygon(arrow_surf, (r, g, b, 220), [end, p1, p2])
                self.screen.blit(arrow_surf, (0, 0))
        except Exception:
            pass

        # vykreslit sekvenci QTE pokud aktivní (ukázat šipky a další požadovaný klíč)
        try:
            if getattr(self, 'qte', None) and self.qte.active:
                seq = getattr(self.qte, 'seq', [])
                idx = getattr(self.qte, 'index', 0)
                spacing = 64
                total_w = max(0, len(seq) * spacing)
                cx = SCREEN_W // 2
                start_x = cx - total_w // 2
                qy = SCREEN_H - 110
                for i, key in enumerate(seq):
                    rx = start_x + i * spacing
                    r = pygame.Rect(rx, qy, 48, 48)
                    col = (240, 100, 100) if i == idx else (200, 200, 200)
                    pygame.draw.rect(self.screen, col, r, border_radius=6)
                    # nakreslit jednoduchý symbol šipky pomocí textu pro spolehlivost
                    glyph = '^' if key == 'up' else 'v' if key == 'down' else '<' if key == 'left' else '>'
                    gsurf = self.font.render(glyph, True, (0, 0, 0))
                    self.screen.blit(gsurf, (r.x + r.width // 2 - gsurf.get_width() // 2, r.y + r.height // 2 - gsurf.get_height() // 2))
                # napoveda text
                hint = self.small_font.render('Press the arrows shown (timed)', True, (240,240,200))
                self.screen.blit(hint, (cx - hint.get_width()//2, qy - 28))
        except Exception:
            pass

        pygame.draw.rect(self.screen, (240, 240, 240), (sx, sy, self.player.w, self.player.h))

        # vizuální efekt omráčení když je hráč omráčen (zásahy medúzy)
        try:
            if getattr(self.player, 'stunned_until', 0) > time.time():
                t = time.time()
                radius = 48 + int(math.sin(t * 6.0) * 8)
                halo_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(halo_surf, (255, 200, 80, 110), (radius, radius), radius)
                self.screen.blit(halo_surf, (int(sx + self.player.w/2 - radius), int(sy + self.player.h/2 - radius)))

                for i in range(4):
                    ang = t * (1.5 + i * 0.2) + i * 1.2
                    ox = int(math.cos(ang) * (32 + i * 6))
                    oy = int(math.sin(ang) * (18 + i * 4)) - 12
                    star = self.small_font.render('*', True, (255, 240, 160))
                    self.screen.blit(star, (int(sx + self.player.w/2 + ox - star.get_width()/2), int(sy + self.player.h/2 + oy - star.get_height()/2)))
        except Exception:
            pass

        # debug překryv
        try:
            keys = pygame.key.get_pressed()
            dbg = [
                f"pos: {self.player.world_x:.1f},{self.player.world_y:.1f}",
                f"vel: {self.player.velocity_x:.2f},{self.player.velocity_y:.2f}",
                f"oxygen: {self.player.oxygen:.1f}",
                f"bubbles: {len(self.bubbles) if hasattr(self, 'bubbles') else 0}",
                f"monsters: {len(self.monsters) if hasattr(self, 'monsters') else 0}",
                f"charging: {getattr(self, 'charging', False)}",
                f"charge: {getattr(self, 'charge', 0):.1f}",
                f"keys L/R/U/D: {int(keys[pygame.K_LEFT])}/{int(keys[pygame.K_RIGHT])}/{int(keys[pygame.K_UP])}/{int(keys[pygame.K_DOWN])}",
            ]
            for i, line in enumerate(dbg):
                surf = self.small_font.render(line, True, (255, 255, 255))
                self.screen.blit(surf, (12, 12 + i * 18))
        except Exception:
            pass

        # vykreslit oznámení o uložení pokud je přítomné
        try:
            if getattr(self, '_save_message', None) and getattr(self, '_save_message_until', 0) > time.time():
                sm = self._save_message
                surf = self.font.render(sm, True, (240, 240, 120))
                self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, 80))
            else:
                try:
                    if getattr(self, '_save_message_until', 0) <= time.time():
                        del self._save_message
                        del self._save_message_until
                except Exception:
                    pass
        except Exception:
            pass
        except Exception:
            pass

        self._flip()

    def gameover_loop(self, dt):
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                self.reset_game()
                self.state = "playing"
        depth = int((self.player.max_depth_reached - SEA_LEVEL_Y) / PIXELS_PER_METER)

        save_game({
            "name": getattr(self, 'input_name', None) or self.player_name,
            "best_depth": max(self.best_depth, depth),
            "last_depth": depth,
            "oxygen": 100,
            "score": self.score,
        })
        try:
            if hasattr(self, '_pending_score'):
                pname = getattr(self, 'input_name', None) or self.player_name or 'Player'
                save_score(pname, int(self._pending_score), int(getattr(self, '_pending_oxygen', 0)))
                try:
                    del self._pending_score
                except Exception:
                    pass
                try:
                    del self._pending_oxygen
                except Exception:
                    pass
                try:
                    self._save_message = f"Score saved as {pname}"
                    self._save_message_until = time.time() + 3.0
                except Exception:
                    pass
        except Exception:
            pass

        self.screen.fill((0, 0, 0))
        t = self.font.render("GAME OVER", True, (255, 255, 255))
        self.screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 160))

        # zobrazit žebříček top 10 z místní databáze
        try:
                rows = top_scores(10)
                header = self.small_font.render("Top 10", True, (200, 200, 200))
                self.screen.blit(header, (SCREEN_W // 2 - header.get_width() // 2, 220))
                start_y = 250
                for i, r in enumerate(rows, start=1):
                    name = str(r[0])
                    depth_v = int(r[1])
                    oxy = int(r[2])
                    ts = str(r[3]) if len(r) > 3 and r[3] is not None else ''
                    ts_short = ts.split('.')[0]
                    line = f"{i}. {name[:12]:12}  depth:{depth_v:4}  oxy:{oxy:3}  {ts_short}"
                    surf = self.small_font.render(line, True, (220, 220, 220))
                    self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, start_y + (i - 1) * 22))
        except Exception:
                pass

        note = self.small_font.render("Press any key to play again", True, (180, 180, 180))
        self.screen.blit(note, (SCREEN_W // 2 - note.get_width() // 2, SCREEN_H - 80))
        self._flip()

    def _flip(self):
        scaled = pygame.transform.scale(self.surface, (self.display_w, self.display_h))
        self.display.blit(scaled, (0, 0))
        pygame.display.flip()
