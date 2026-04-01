"""
Flappy Dino
Autor: Toby

Popis:
- Menu s hover efektem.
- Okno resizable.
- HUD se skóre a jménem hráče.
- Pozadí a překážky nahrazeny reálnými obrázky.
- Překážky jsou kamenné pilíře: horní a dolní část, mezera je dostatečně velká pro dva ptáčky.
- Hudba: MP3 soubor přehráván stále dokola.
"""

import pygame
import random
import sys
from db import init_db, get_db, is_registered_user
import webbrowser
import urllib.request
import urllib.error
import socket

# --------------------------- Konfigurace ---------------------------------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# Cesty k obrázkům
BIRD_IMG_PATH = "imgs/Bird.png"
BACKGROUND_IMG_PATH = "imgs/Džungle.png"
PILLAR_IMG_PATH = "imgs/Pilíř2.png"
MENU_IMG_PATH = "imgs/MenuTitle.png"
GAME_OVER_IMG_PATH = "imgs/Konec.png"

# Cesta k hudbě
MUSIC_PATH = "imgs/Untitled #9 - Smáskifa 1 - Sigur Rós.mp3"

# Barvy a styl
BG_COLOR = (15, 30, 15)
TEXT_COLOR = (240, 240, 240)
BUTTON_COLOR = (70, 20, 20)
BUTTON_HOVER = (120, 20, 20)
BIRD_COLOR = (240, 200, 60)
SLIDER_COLOR = (180, 180, 180)
SLIDER_KNOB = (255, 255, 255)

# Pták
BIRD_SIZE = 128
GRAVITY = 0.45
FLAP_STRENGTH = -9.5

# Překážky
PILLAR_WIDTH = 110
PILLAR_MIN_HEIGHT = 60
PILLAR_MAX_HEIGHT = 260
SPAWN_INTERVAL = 1100
BASE_SPEED = 3.4
SPEED_INCREMENT_PER_SCORE = 0.18
MAX_HEIGHT_DIFF = 120
MIN_GAP_RATIO = 0.25
NEXT_GAP_EXTRA = 90
MIN_HORIZONTAL_GAP = 3 * 200

# --------------------------- Datové struktury ----------------------------
class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = 0
    def rect(self):
        return pygame.Rect(int(self.x - BIRD_SIZE/2), int(self.y - BIRD_SIZE/2), BIRD_SIZE, BIRD_SIZE)

class Pillar:
    def __init__(self, x, height, is_top):
        self.x = x
        self.height = height
        self.width = PILLAR_WIDTH
        self.is_top = is_top
    def rect(self, screen_height):
        if self.is_top:
            return pygame.Rect(int(self.x), 0, self.width, self.height)
        else:
            return pygame.Rect(int(self.x), screen_height - self.height, self.width, self.height)

# --------------------------- Pomocné funkce ------------------------------
def draw_background(surface, width, height, bg_image):
    if bg_image:
        surface.blit(pygame.transform.scale(bg_image, (width, height)), (0,0))
    else:
        for i in range(height):
            color = (15, 15 + int(i*20/height), 15)
            pygame.draw.line(surface, color, (0,i), (width,i))
        for i in range(6):
            cx = i*(width//6)+30
            cy = height - 60
            pygame.draw.rect(surface, (30,20,10), (cx, cy-100, 20, 100))
            pygame.draw.ellipse(surface, (10,50,10), (cx-30, cy-120, 80, 80))

def draw_bird(surface, bird, bird_image):
    r = bird.rect()
    if bird_image:
        surface.blit(pygame.transform.scale(bird_image, (BIRD_SIZE,BIRD_SIZE)), (r.x,r.y))
    else:
        pygame.draw.ellipse(surface, BIRD_COLOR, r)

def draw_pillar(surface, pillar, pillar_image, screen_height):
    r = pillar.rect(screen_height)
    if pillar_image:
        surface.blit(pygame.transform.scale(pillar_image, (r.width, r.height)), (r.x, r.y))
    else:
        if pillar.is_top:
            for i in range(r.height):
                shade = 80 + int(i*(50/r.height))
                pygame.draw.line(surface, (shade, shade, shade), (r.x, r.y+i), (r.x+r.width, r.y+i))
        else:
            for i in range(r.height):
                shade = 130 - int(i*(50/r.height))
                pygame.draw.line(surface, (shade, shade, shade), (r.x, r.y+i), (r.x+r.width, r.y+i))

def draw_hud(surface, score, player_name, width, font):
    score_s = font.render(f"Skóre: {score}", True, TEXT_COLOR)
    player_s = font.render(f"Hráč: {player_name}", True, TEXT_COLOR)
    surface.blit(score_s, (11,11))
    surface.blit(player_s, (width - player_s.get_width() -11, 11))
    surface.blit(score_s, (10,10))
    surface.blit(player_s, (width - player_s.get_width() -10, 10))

def draw_button(surface, rect, text, font, hover=False):
    color = BUTTON_HOVER if hover else BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=12)
    text_s = font.render(text, True, TEXT_COLOR)
    surface.blit(text_s, text_s.get_rect(center=rect.center))

def draw_volume_controls(surface, mute_rect, slider_rect, knob_rect, font, is_muted):
    draw_button(surface, mute_rect, "🔇" if is_muted else "🔊", font, False)
    pygame.draw.rect(surface, SLIDER_COLOR, slider_rect)
    pygame.draw.circle(surface, SLIDER_KNOB, knob_rect.center, knob_rect.width//2)
def get_player_name(screen, font):
    name = ""
    entering = True
    clock = pygame.time.Clock()


    while entering:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(name) > 0:
                    entering = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 12 and event.unicode.isprintable():
                        name += event.unicode

        screen.fill((10, 15, 30))
        title = font.render("Zadej jméno hráče", True, (240,240,240))
        name_txt = font.render(name, True, (0,255,0))
        hint = font.render("ENTER pro potvrzení", True, (200,200,200))

        screen.blit(title, title.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 60)))
        screen.blit(name_txt, name_txt.get_rect(center=(screen.get_width()//2, screen.get_height()//2)))
        screen.blit(hint, hint.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50)))

        pygame.display.flip()
        clock.tick(30)

    return name

def save_score(player, score):
    try:
        score_val = int(score)
    except Exception:
        print(f"save_score: invalid score for player={player}: {score}")
        return
    player_val = str(player).strip()[:64]
    if not player_val:
        print(f"save_score: empty player name, not saving score={score_val}")
        return

    db = get_db()
    existing = db.execute(
        "SELECT score FROM scores WHERE player = ?",
        (player_val,)
    ).fetchone()

    if existing is None:
        db.execute(
            "INSERT INTO scores (player, score) VALUES (?, ?)",
            (player_val, score_val)
        )
        print(f"Saved new player -> player={player_val} score={score_val}")
    else:
        existing_score = existing[0]
        if score_val > existing_score:
            db.execute(
                "UPDATE scores SET score = ? WHERE player = ?",
                (score_val, player_val)
            )
            print(f"Updated best score -> player={player_val} old={existing_score} new={score_val}")
        else:
            print(f"Skipped save -> player={player_val} existing={existing_score} new={score_val}")

    db.commit()
    db.close()

# ---------------------- Countdown helper -------------------------------
def draw_countdown(screen, font, label, width, height):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0,0))
    text_s = font.render(label, True, (255, 230, 130))
    screen.blit(text_s, text_s.get_rect(center=(width//2, height//2)))

# --------------------------- Hlavní hra ----------------------------------
def main():
    pygame.init()
    pygame.mixer.init()
    init_db()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Flappy Dino")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('Verdana', 28, bold=True)
    large_font = pygame.font.SysFont('Verdana', 46, bold=True)

    # Načtení obrázků
    try:
        bird_img = pygame.image.load(BIRD_IMG_PATH)
    except:
        bird_img = None
    try:
        bg_img = pygame.image.load(BACKGROUND_IMG_PATH)
    except:
        bg_img = None
    try:
        pillar_img = pygame.image.load(PILLAR_IMG_PATH)
    except:
        pillar_img = None
    try:
        menu_img = pygame.image.load(MENU_IMG_PATH)
    except:
        print("Menu obrázek se nepodařilo načíst, bude použit text")
        menu_img = None

    try:
        game_over_img = pygame.image.load(GAME_OVER_IMG_PATH)
    except:
        print("Game over obrázek se nepodařilo načíst, bude použit text")
        game_over_img = None

    # Hudba
    try:
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.play(-1)  # nekonečné opakování
        volume = 0.5
        pygame.mixer.music.set_volume(volume)
        is_muted = False
    except:
        print("Hudbu se nepodařilo načíst")
        volume = 0.5
        is_muted = False

    in_menu = True
    in_countdown = False
    in_sound_menu = False
    countdown_start = 0
    web_error_message = ""
    login_error_message = ""
    countdown_duration = 4.0
    fullscreen = False
    running = True

    bird = None
    pillars = []
    score = 0
    distance = 0
    player_name = ""
    score_saved = False
    speed = BASE_SPEED
    last_spawn = 0
    game_over = False
    last_top_height = None

    def start_new_game(width, height):
        bird = Bird(width*0.28, height/2)
        pillars = []
        score = 0
        distance = 0.0
        speed = BASE_SPEED
        last_spawn = pygame.time.get_ticks()
        last_top_height = None
        return bird, pillars, score, distance, speed, last_spawn, last_top_height

    while running:
        dt = clock.tick(FPS)/1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_W, SCREEN_H = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if in_sound_menu:
                        in_sound_menu = False
                    elif in_menu:
                        running = False
                    else:
                        in_menu = True
                elif event.key == pygame.K_m:
                    is_muted = not is_muted
                    pygame.mixer.music.set_volume(0 if is_muted else volume)
                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                elif event.key == pygame.K_SPACE:
                    if bird and not game_over:
                        bird.vy = FLAP_STRENGTH
                elif event.key == pygame.K_r and game_over:
                    SCREEN_W, SCREEN_H = screen.get_size()
                    bird, pillars, score, distance, speed, last_spawn, last_top_height = start_new_game(SCREEN_W, SCREEN_H)
                    game_over = False
                    score_saved = False
                    in_countdown = True
                    countdown_start = pygame.time.get_ticks()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if in_menu:
                    if button_rect.collidepoint(mx, my):
                        player_name = get_player_name(screen, font)
                        if not player_name:
                            login_error_message = "Jméno je povinné."
                        elif not is_registered_user(player_name):
                            login_error_message = "Uživatel není registrován. Registrovat se můžete na webu." 
                            player_name = ""
                        else:
                            login_error_message = ""
                            in_menu = False
                            in_countdown = True
                            countdown_start = pygame.time.get_ticks()
                            SCREEN_W, SCREEN_H = screen.get_size()
                            bird, pillars, score, distance, speed, last_spawn, last_top_height = start_new_game(SCREEN_W, SCREEN_H)
                            game_over = False
                            score_saved = False
                    elif website_rect.collidepoint(mx, my):
                        try:
                            urllib.request.urlopen('http://127.0.0.1:5000', timeout=1)
                            webbrowser.open_new_tab('http://127.0.0.1:5000')
                            web_error_message = ""
                        except (urllib.error.URLError, socket.timeout, ConnectionRefusedError):
                            web_error_message = "Flask server not running at 127.0.0.1:5000. Start app.py and try again."
                        except Exception as e:
                            web_error_message = f"Web open error: {e}"
                    elif sound_rect.collidepoint(mx, my):
                        in_menu = False
                        in_sound_menu = True
                    elif exit_rect.collidepoint(mx, my):
                        running = False
                    continue

                if not in_sound_menu and mute_rect.collidepoint(mx,my):
                    is_muted = not is_muted
                    pygame.mixer.music.set_volume(0 if is_muted else volume)
                elif slider_rect.collidepoint(mx,my):
                    knob_rect.centerx = max(slider_rect.left, min(mx, slider_rect.right))
                    volume = (knob_rect.centerx - slider_rect.left)/slider_rect.width
                    pygame.mixer.music.set_volume(volume)
                    is_muted = volume==0

            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0] and slider_rect.collidepoint(event.pos):
                    mx = event.pos[0]
                    knob_rect.centerx = max(slider_rect.left, min(mx, slider_rect.right))
                    volume = (knob_rect.centerx - slider_rect.left)/slider_rect.width
                    pygame.mixer.music.set_volume(volume)
                    is_muted = volume==0

        w, h = screen.get_size()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        MIN_GAP_CURRENT = max(int(h*MIN_GAP_RATIO), BIRD_SIZE*2 + 20)

        if in_menu:
            if fullscreen:
                button_width = 260
                button_height = 70
                play_y = h//2 - 35
                website_y = h//2 + 50
                sound_y = h//2 + 135
                exit_y = h//2 + 220
                hint_y = h - 30
            else:
                button_width = 200
                button_height = 50
                play_y = h//2 - 25
                website_y = h//2 + 30
                sound_y = h//2 + 85
                exit_y = h//2 + 140
                hint_y = h - 20

            button_rect = pygame.Rect(w//2 - button_width//2, play_y, button_width, button_height)
            website_rect = pygame.Rect(w//2 - button_width//2, website_y, button_width, button_height)
            sound_rect = pygame.Rect(w//2 - button_width//2, sound_y, button_width, button_height)
            exit_rect = pygame.Rect(w//2 - button_width//2, exit_y, button_width, button_height)

            hover = button_rect.collidepoint(mouse_x, mouse_y)
            hover_website = website_rect.collidepoint(mouse_x, mouse_y)
            hover_sound = sound_rect.collidepoint(mouse_x, mouse_y)
            hover_exit = exit_rect.collidepoint(mouse_x, mouse_y)

        # --- Hud ovládání hlasitosti ---
        if in_sound_menu:
            slider_rect = pygame.Rect(w//2 - 100, h//2 - 7.5, 200, 15)
            knob_rect = pygame.Rect(0, h//2 - 7.5, 25, 15)
            knob_rect.centerx = slider_rect.left + int(volume*slider_rect.width)
        else:
            mute_rect = pygame.Rect(10, h-50, 50, 40)
            slider_rect = pygame.Rect(70, h-40, 150, 10)
            knob_rect = pygame.Rect(0, h-45, 20, 20)
            knob_rect.centerx = slider_rect.left + int(volume*slider_rect.width)

        # --- Menu ---
        if in_menu:
            draw_background(screen, w, h, bg_img)
            
            if menu_img:
                img_w = int(w * 0.30)
                img_h = int(menu_img.get_height() * (img_w / menu_img.get_width()))
                scaled_img = pygame.transform.scale(menu_img, (img_w, img_h))
                screen.blit(scaled_img, scaled_img.get_rect(center=(w//2, h//4)))
            else:
                title = large_font.render("Flappy Dino", True, TEXT_COLOR)
                screen.blit(title, title.get_rect(center=(w//2, h//4)))

            draw_button(screen, button_rect, "Play", font, hover)
            draw_button(screen, website_rect, "Website", font, hover_website)
            draw_button(screen, sound_rect, "Sound", font, hover_sound)
            draw_button(screen, exit_rect, "Exit", font, hover_exit)

            if web_error_message:
                error_s = font.render(web_error_message, True, (255, 120, 120))
                screen.blit(error_s, error_s.get_rect(center=(w//2, exit_y + 80)))

            if login_error_message:
                error_s = font.render(login_error_message, True, (255, 120, 120))
                screen.blit(error_s, error_s.get_rect(center=(w//2, exit_y + 110)))

            pygame.display.flip()
            continue

        # --- Sound Menu ---
        if in_sound_menu:
            draw_background(screen, w, h, bg_img)
            
            # Table overlay
            table_width, table_height = 400, 200
            table_x = w//2 - table_width//2
            table_y = h//2 - table_height//2
            overlay = pygame.Surface((table_width, table_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (table_x, table_y))
            
            title = large_font.render("Music", True, TEXT_COLOR)
            screen.blit(title, title.get_rect(center=(w//2, table_y + 30)))

            pygame.draw.rect(screen, SLIDER_COLOR, slider_rect)
            pygame.draw.circle(screen, SLIDER_KNOB, knob_rect.center, knob_rect.width//2)

            esc_text = font.render("ESC to go back", True, TEXT_COLOR)
            screen.blit(esc_text, esc_text.get_rect(center=(w//2, table_y + table_height - 30)))

            pygame.display.flip()
            continue

        # --- Hra ---
        if in_countdown:
            w, h = screen.get_size()
            elapsed = (pygame.time.get_ticks() - countdown_start) / 1000.0
            if elapsed < 1.0:
                label = "3"
            elif elapsed < 2.0:
                label = "2"
            elif elapsed < 3.0:
                label = "1"
            elif elapsed < 4.0:
                label = "GO!"
            else:
                in_countdown = False
                label = "GO!"

            draw_background(screen, w, h, bg_img)
            for p in pillars:
                draw_pillar(screen, p, pillar_img, h)
            if bird:
                draw_bird(screen, bird, bird_img)
            draw_hud(screen, score, player_name, w, font)
            draw_volume_controls(screen, mute_rect, slider_rect, knob_rect, font, is_muted)
            draw_countdown(screen, large_font, label, w, h)
            pygame.display.flip()
            continue

        if bird and not game_over:
            if not pillars:
                gap_x = w * 0.6
            else:
                gap_x = pillars[-1].x + MIN_HORIZONTAL_GAP

            if not pillars or (pillars[-1].x + PILLAR_WIDTH < w):
                if last_top_height is None:
                    last_top_height = random.randint(PILLAR_MIN_HEIGHT, h - MIN_GAP_CURRENT - PILLAR_MIN_HEIGHT)
                max_diff = min(MAX_HEIGHT_DIFF, h - MIN_GAP_CURRENT - PILLAR_MIN_HEIGHT - PILLAR_MIN_HEIGHT)
                delta = random.randint(-max_diff, max_diff)
                top_height = max(PILLAR_MIN_HEIGHT, min(last_top_height + delta, h - MIN_GAP_CURRENT - PILLAR_MIN_HEIGHT))
                bottom_height = h - top_height - MIN_GAP_CURRENT
                pillars.append(Pillar(gap_x, top_height, True))
                pillars.append(Pillar(gap_x, bottom_height, False))
                last_top_height = top_height

            for p in pillars:
                p.x -= speed
            pillars = [p for p in pillars if p.x + p.width > -50]

            bird.vy += GRAVITY
            bird.y += bird.vy
            if bird.y - BIRD_SIZE/2 <=0 or bird.y + BIRD_SIZE/2 >= h:
                game_over = True

            bird_rect = bird.rect()
            passed_any = False
            for i in range(0, len(pillars), 2):
                top_p, bottom_p = pillars[i], pillars[i+1]
                if bird_rect.colliderect(top_p.rect(h)) or bird_rect.colliderect(bottom_p.rect(h)):
                    game_over = True
                    break
                center_x = top_p.x + top_p.width/2
                if center_x < bird.x and center_x + speed >= bird.x:
                    score +=1
                    passed_any = True
            if passed_any:
                speed += SPEED_INCREMENT_PER_SCORE
            distance += speed*dt*12

            draw_background(screen, w, h, bg_img)
            for p in pillars:
                draw_pillar(screen, p, pillar_img, h)
            draw_bird(screen, bird, bird_img)
            draw_hud(screen, score, player_name, w, font)
            draw_volume_controls(screen, mute_rect, slider_rect, knob_rect, font, is_muted)
            pygame.display.flip()
            continue

        # Game over
        if game_over:
            if not score_saved:
                save_score(player_name, score)
                score_saved = True

            draw_background(screen, w, h, bg_img)
            for p in pillars:
                draw_pillar(screen, p, pillar_img, h)
            if bird:
                draw_bird(screen, bird, bird_img)
            draw_hud(screen, score, player_name, w, font)

            if game_over_img:
                max_width = int(w * 0.5)
                img_w = min(max_width, game_over_img.get_width())
                img_h = int(game_over_img.get_height() * (img_w / game_over_img.get_width()))
                scaled = pygame.transform.scale(game_over_img, (img_w, img_h))
                screen.blit(scaled, scaled.get_rect(center=(w//2, h//2 - img_h//4)))
                text_y = h//2 - img_h//4 + img_h//2 + 25
            else:
                over_text = large_font.render("Game Over", True, (220,40,40))
                screen.blit(over_text, over_text.get_rect(center=(w//2, h//2-40)))
                text_y = h//2 + 10

            sub = font.render("Stiskni R pro restart, ESC pro menu", True, TEXT_COLOR)
            screen.blit(sub, sub.get_rect(center=(w//2, text_y)))
            draw_volume_controls(screen, mute_rect, slider_rect, knob_rect, font, is_muted)
            pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__=='__main__':
    main()
