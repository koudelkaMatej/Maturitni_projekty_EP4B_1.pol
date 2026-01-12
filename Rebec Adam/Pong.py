import pygame
import random

pygame.init()

# Nastavení okna
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong – Myš vs Bot")

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Fonty
font = pygame.font.SysFont("consolas", 40)
menu_font = pygame.font.SysFont("consolas", 60)

# Herní objekty
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 15

# Tlačítko START
start_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 50, 300, 100)

clock = pygame.time.Clock()
running = True
game_state = "menu"  # "menu" nebo "game"

# ---------- Funkce pro reset hry ----------
def reset_game():
    global left_paddle, right_paddle, ball
    global ball_speed_x, ball_speed_y
    global score_left, score_right

    left_paddle = pygame.Rect(50, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(WIDTH - 60, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

    ball_speed_x = random.choice([-5, 5])
    ball_speed_y = random.choice([-3, 3])

    score_left = 0
    score_right = 0


# Inicializace hry poprvé
reset_game()

# ---------- Hlavní smyčka ----------
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Kliknutí v menu
        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    reset_game()
                    game_state = "game"

    # ---------- MENU ----------
    if game_state == "menu":
        win.fill(BLACK)

        title = menu_font.render("PONG", True, WHITE)
        win.blit(title, (WIDTH//2 - title.get_width()//2, 150))

        pygame.draw.rect(win, GRAY, start_button)
        pygame.draw.rect(win, WHITE, start_button, 3)

        start_text = font.render("START", True, WHITE)
        win.blit(
            start_text,
            (start_button.centerx - start_text.get_width()//2,
             start_button.centery - start_text.get_height()//2)
        )

        pygame.display.flip()
        continue

    # ---------- HRA ----------
    # Ovládání levé pálky myší
    mouse_y = pygame.mouse.get_pos()[1]
    left_paddle.centery = mouse_y
    left_paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    # Pohyb bota
    if right_paddle.centery < ball.centery - 15:
        right_paddle.centery += 4
    elif right_paddle.centery > ball.centery + 15:
        right_paddle.centery -= 4

    right_paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    # Pohyb míčku
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Kolize s okraji
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1

    # Kolize s pálkami
    if ball.colliderect(left_paddle):
        ball_speed_x *= -1
        ball.x = left_paddle.right

    if ball.colliderect(right_paddle):
        ball_speed_x *= -1
        ball.x = right_paddle.left - BALL_SIZE

    # Skórování
    if ball.left <= 0:
        score_right += 1
        ball.center = (WIDTH//2, HEIGHT//2)
        ball_speed_x = random.choice([-5, 5])
        ball_speed_y = random.choice([-3, 3])

    if ball.right >= WIDTH:
        score_left += 1
        ball.center = (WIDTH//2, HEIGHT//2)
        ball_speed_x = random.choice([-5, 5])
        ball_speed_y = random.choice([-3, 3])

    # Vykreslení hry
    win.fill(BLACK)
    pygame.draw.rect(win, WHITE, left_paddle)
    pygame.draw.rect(win, WHITE, right_paddle)
    pygame.draw.ellipse(win, WHITE, ball)
    pygame.draw.aaline(win, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

    score_text = font.render(f"{score_left}   {score_right}", True, WHITE)
    win.blit(score_text, (WIDTH//2 - 50, 20))

    pygame.display.flip()

pygame.quit()
