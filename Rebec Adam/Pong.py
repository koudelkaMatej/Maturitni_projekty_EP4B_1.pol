import pygame
import random
import requests

# Inicializace
pygame.init()

# Nastavení okna
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong – Myš vs Bot (Propojeno s Flaskem)")
clock = pygame.time.Clock()

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Fonty
font = pygame.font.SysFont("consolas", 30)
menu_font = pygame.font.SysFont("consolas", 60)

# Herní konstanty
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 15
BALL_ACCELERATION = 1.08  # Zrychlení o 8 % při každém odrazu
MAX_BALL_SPEED = 15
SCORE_LIMIT = 10

# API Nastavení
API_URL = "http://127.0.0.1:5000/api/save_score"

# Proměnné stavu
game_state = "login"  # login -> menu -> game
user_email = ""
difficulty = "medium"
show_difficulty = False
waiting_for_click = False

# Obtížnost bota
BOT_SPEEDS = {"easy": 3, "medium": 5, "hard": 8}


def reset_game():
    global left_paddle, right_paddle, ball, score_left, score_right
    global ball_speed_x, ball_speed_y, ball_pos_x, ball_pos_y

    left_paddle = pygame.Rect(50, HEIGHT // 2 - 50, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(
        WIDTH - 60, HEIGHT // 2 - 50, PADDLE_WIDTH, PADDLE_HEIGHT
    )
    ball = pygame.Rect(
        WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE
    )

    # Používáme float pro plynulé zrychlování (aby se rychlost nezaokrouhlovala)
    ball_pos_x = float(ball.x)
    ball_pos_y = float(ball.y)

    ball_speed_x = random.choice([-5.0, 5.0])
    ball_speed_y = random.choice([-3.0, 3.0])

    score_left = 0
    score_right = 0


def send_score_to_web():
    data = {
        "email": user_email,
        "score_left": score_left,
        "score_right": score_right,
        "difficulty": difficulty,
    }
    try:
        r = requests.post(API_URL, json=data, timeout=3)
        print("Data odeslána:", r.status_code)
    except:
        print("Chyba: Server neběží, skóre nebylo uloženo.")


def draw_button(rect, text):
    pygame.draw.rect(win, GRAY, rect)
    pygame.draw.rect(win, WHITE, rect, 2)
    t = font.render(text, True, WHITE)
    win.blit(t, (rect.centerx - t.get_width() // 2, rect.centery - t.get_height() // 2))


# Definice tlačítek
start_button = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 80, 400, 80)
difficulty_button = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 + 20, 400, 60)
diff_rects = {
    "easy": pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 40),
    "medium": pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 150, 300, 40),
    "hard": pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 200, 300, 40),
}

reset_game()
running = True

while running:
    clock.tick(60)
    win.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # OVLÁDÁNÍ LOGINU
        if game_state == "login":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and "@" in user_email:
                    game_state = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    user_email = user_email[:-1]
                else:
                    user_email += event.unicode

        # OVLÁDÁNÍ MENU
        elif game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    reset_game()
                    game_state = "game"
                elif difficulty_button.collidepoint(event.pos):
                    show_difficulty = not show_difficulty
                elif show_difficulty:
                    for d, rect in diff_rects.items():
                        if rect.collidepoint(event.pos):
                            difficulty = d
                            show_difficulty = False

        # OVLÁDÁNÍ HRY
        elif game_state == "game" and waiting_for_click:
            if event.type == pygame.MOUSEBUTTONDOWN:
                ball_speed_x = random.choice([-5.0, 5.0])
                ball_speed_y = random.choice([-3.0, 3.0])
                waiting_for_click = False

    # --- LOGIKA VYKRESLOVÁNÍ ---

    if game_state == "login":
        txt = menu_font.render("Zadej svůj email:", True, WHITE)
        win.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 150))
        em = font.render(user_email + "_", True, WHITE)
        win.blit(em, (WIDTH // 2 - em.get_width() // 2, 280))
        hint = font.render("Stiskni ENTER pro vstup", True, GRAY)
        win.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 400))

    elif game_state == "menu":
        title = menu_font.render("PONG ONLINE", True, WHITE)
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        draw_button(start_button, "HRÁT")
        draw_button(difficulty_button, f"Obtížnost: {difficulty.upper()}")
        if show_difficulty:
            for d, rect in diff_rects.items():
                draw_button(rect, d.capitalize())

    elif game_state == "game":
        # Pohyb pálky
        left_paddle.centery = pygame.mouse.get_pos()[1]
        left_paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        # Pohyb bota
        b_speed = BOT_SPEEDS[difficulty]
        if right_paddle.centery < ball.centery - 10:
            right_paddle.y += b_speed
        if right_paddle.centery > ball.centery + 10:
            right_paddle.y -= b_speed
        right_paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        # Fyzika míčku (přesná desetinná pozice)
        if not waiting_for_click:
            ball_pos_x += ball_speed_x
            ball_pos_y += ball_speed_y
            ball.x = int(ball_pos_x)
            ball.y = int(ball_pos_y)

        # Odrazy od stěn
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_speed_y *= -1

        # Odrazy od pálek + ZRYCHLENÍ
        if ball.colliderect(left_paddle) and ball_speed_x < 0:
            ball_speed_x = abs(ball_speed_x) * BALL_ACCELERATION
            ball_speed_y *= BALL_ACCELERATION
            ball_pos_x = float(left_paddle.right)
            if abs(ball_speed_x) > MAX_BALL_SPEED:
                ball_speed_x = MAX_BALL_SPEED

        if ball.colliderect(right_paddle) and ball_speed_x > 0:
            ball_speed_x = -abs(ball_speed_x) * BALL_ACCELERATION
            ball_speed_y *= BALL_ACCELERATION
            ball_pos_x = float(right_paddle.left - BALL_SIZE)
            if abs(ball_speed_x) > MAX_BALL_SPEED:
                ball_speed_x = -MAX_BALL_SPEED

        # Skórování
        if ball.left <= 0:
            score_right += 1
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_pos_x, ball_pos_y = float(ball.x), float(ball.y)
            ball_speed_x = ball_speed_y = 0
            waiting_for_click = True
        elif ball.right >= WIDTH:
            score_left += 1
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_pos_x, ball_pos_y = float(ball.x), float(ball.y)
            ball_speed_x = ball_speed_y = 0
            waiting_for_click = True

        # KONEC HRY
        if score_left >= SCORE_LIMIT or score_right >= SCORE_LIMIT:
            send_score_to_web()
            game_state = "menu"

        # Vykreslení hry
        pygame.draw.rect(win, WHITE, left_paddle)
        pygame.draw.rect(win, WHITE, right_paddle)
        pygame.draw.ellipse(win, WHITE, ball)
        pygame.draw.aaline(win, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        s_txt = font.render(f"{score_left} : {score_right}", True, WHITE)
        win.blit(s_txt, (WIDTH // 2 - s_txt.get_width() // 2, 20))

    pygame.display.flip()

pygame.quit()
