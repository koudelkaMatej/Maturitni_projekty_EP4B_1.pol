"""
Flappy Dino - plně flexibilní temná verze s kamennými pilíři a hudbou
Autor: Toby

Popis:
- Menu s moderním tlačítkem Hrát s hover efektem.
- Okno resizable + fullscreen (klávesa F).
- HUD se skóre a vzdáleností s elegantním fontem.
- Pozadí a překážky lze nahradit reálnými obrázky.
- Překážky jsou kamenné pilíře: horní a dolní část, mezera je dostatečně velká pro dva ptáčky.
- Hudba: MP3 soubor přehráván stále dokola + tlačítko ztlumit a posuvník hlasitosti v levém dolním rohu.
"""

import pygame
import random
import sys
from db import init_db, get_db

# --------------------------- Konfigurace ---------------------------------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# Cesty k obrázkům
BIRD_IMG_PATH = "imgs/Bird.png"
BACKGROUND_IMG_PATH = "imgs/Džungle.png"
PILLAR_IMG_PATH = "imgs/Pilíř2.png"
MENU_IMG_PATH = "imgs/MenuTitle.png"

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

def draw_hud(surface, score, distance, width, font):
    score_s = font.render(f"Skóre: {score}", True, TEXT_COLOR)
    dist_s = font.render(f"Vzdálenost: {int(distance)} m", True, TEXT_COLOR)
    surface.blit(score_s, (11,11))
    surface.blit(dist_s, (width - dist_s.get_width() -11, 11))
    surface.blit(score_s, (10,10))
    surface.blit(dist_s, (width - dist_s.get_width() -10, 10))

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
        # Ensure score is an integer and player is a short string
        score_val = int(score)
    except Exception:
        # If score cannot be converted, don't save
        print(f"save_score: invalid score for player={player}: {score}")
        return
    player_val = str(player).strip()[:64]
    if not player_val:
        print(f"save_score: empty player name, not saving score={score_val}")
        return
    db = get_db()
    db.execute(
        "INSERT INTO scores (player, score) VALUES (?, ?)",
        (player_val, score_val)
    )
    db.commit()
    db.close()
    print(f"Saved score -> player={player_val} score={score_val}")
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
                    if in_menu:
                        running = False
                    else:
                        in_menu = True
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

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if mute_rect.collidepoint(mx,my):
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

        # --- Hud ovládání hlasitosti ---
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

            button_rect = pygame.Rect(w//2-130, h//2-35, 260, 70)
            hover = button_rect.collidepoint(mouse_x, mouse_y)
            draw_button(screen, button_rect, "Hrát", font, hover)
            hint = font.render("Stiskni F pro fullscreen.", True, TEXT_COLOR)
            screen.blit(hint, hint.get_rect(center=(w//2, h//2 + 60)))

            draw_volume_controls(screen, mute_rect, slider_rect, knob_rect, font, is_muted)
            
            if pygame.mouse.get_pressed()[0] and hover:
                    player_name = get_player_name(screen, font)
                    in_menu = False
                    SCREEN_W, SCREEN_H = screen.get_size()
                    bird, pillars, score, distance, speed, last_spawn, last_top_height = start_new_game(SCREEN_W, SCREEN_H)
                    game_over = False
                    score_saved = False
            pygame.display.flip()
            continue

        # --- Hra ---
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
            draw_hud(screen, score, distance, w, font)
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
            draw_hud(screen, score, distance, w, font)
            over_text = large_font.render("Game Over", True, (220,40,40))
            screen.blit(over_text, over_text.get_rect(center=(w//2, h//2-40)))
            sub = font.render("Stiskni R pro restart, ESC pro menu", True, TEXT_COLOR)
            screen.blit(sub, sub.get_rect(center=(w//2, h//2+10)))
            draw_volume_controls(screen, mute_rect, slider_rect, knob_rect, font, is_muted)
            pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__=='__main__':
    main()
