import pygame
import random

pygame.init()

# Nastavení
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong – Myš vs Bot")
clock = pygame.time.Clock()
running = True

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

# Zrychlování míčku
BALL_ACCELERATION = 1.05
MAX_BALL_SPEED = 12

# MENU
start_button = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 80, 400, 80)
difficulty_button = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 + 20, 400, 60)

easy_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 100, 300, 50)
medium_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 160, 300, 50)
hard_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 220, 300, 50)

# Obtížnost
BOT_SPEEDS = {
    "easy": 3,
    "medium": 5,
    "hard": 8
}

difficulty = "medium"
show_difficulty = False

# Stav hry
game_state = "menu"
waiting_for_click = False
ball_speed_x = 0
ball_speed_y = 0

# Funkce
def reset_game():
    global left_paddle, right_paddle, ball
    global ball_speed_x, ball_speed_y
    global score_left, score_right

    left_paddle = pygame.Rect(50, HEIGHT//2 - 50, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(WIDTH - 60, HEIGHT//2 - 50, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

    ball_speed_x = random.choice([-5, 5])
    ball_speed_y = random.choice([-3, 3])

    score_left = 0
    score_right = 0

def draw_button(rect, text):
    pygame.draw.rect(win, GRAY, rect)
    pygame.draw.rect(win, WHITE, rect, 2)
    t = font.render(text, True, WHITE)
    win.blit(
        t,
        (rect.centerx - t.get_width()//2,
         rect.centery - t.get_height()//2)
    )

def accelerate_ball():
    global ball_speed_x, ball_speed_y

    if abs(ball_speed_x) < MAX_BALL_SPEED:
        ball_speed_x *= BALL_ACCELERATION
    if abs(ball_speed_y) < MAX_BALL_SPEED:
        ball_speed_y *= BALL_ACCELERATION

reset_game()

# Hlavní loop
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ===== MENU OVLÁDÁNÍ =====
        if game_state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:

            if start_button.collidepoint(event.pos):
                reset_game()
                game_state = "game"

            elif difficulty_button.collidepoint(event.pos):
                show_difficulty = not show_difficulty

            elif show_difficulty:
                if easy_button.collidepoint(event.pos):
                    difficulty = "easy"
                    show_difficulty = False
                elif medium_button.collidepoint(event.pos):
                    difficulty = "medium"
                    show_difficulty = False
                elif hard_button.collidepoint(event.pos):
                    difficulty = "hard"
                    show_difficulty = False

        # Klik po skórování
        if game_state == "game" and waiting_for_click:
            if event.type == pygame.MOUSEBUTTONDOWN:
                ball_speed_x = random.choice([-5, 5])
                ball_speed_y = random.choice([-3, 3])
                waiting_for_click = False

    # Menu
    if game_state == "menu":
        win.fill(BLACK)

        title = menu_font.render("PONG", True, WHITE)
        win.blit(title, (WIDTH//2 - title.get_width()//2, 100))

        draw_button(start_button, "START")
        draw_button(difficulty_button, f"Obtiznost: {difficulty.capitalize()}")

        if show_difficulty:
            draw_button(easy_button, "Easy")
            draw_button(medium_button, "Medium")
            draw_button(hard_button, "Hard")

        pygame.display.flip()
        continue

    # Hra
    left_paddle.centery = pygame.mouse.get_pos()[1]
    left_paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    bot_speed = BOT_SPEEDS[difficulty]
    if right_paddle.centery < ball.centery - 15:
        right_paddle.centery += bot_speed
    elif right_paddle.centery > ball.centery + 15:
        right_paddle.centery -= bot_speed

    right_paddle.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    ball.x += ball_speed_x
    ball.y += ball_speed_y

    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1

    if ball.colliderect(left_paddle):
        ball_speed_x *= -1
        ball.left = left_paddle.right
        accelerate_ball()

    if ball.colliderect(right_paddle):
        ball_speed_x *= -1
        ball.right = right_paddle.left
        accelerate_ball()

    if ball.left <= 0:
        score_right += 1
        ball.center = (WIDTH//2, HEIGHT//2)
        ball_speed_x = ball_speed_y = 0
        waiting_for_click = True

    if ball.right >= WIDTH:
        score_left += 1
        ball.center = (WIDTH//2, HEIGHT//2)
        ball_speed_x = ball_speed_y = 0
        waiting_for_click = True

    win.fill(BLACK)
    pygame.draw.rect(win, WHITE, left_paddle)
    pygame.draw.rect(win, WHITE, right_paddle)
    pygame.draw.ellipse(win, WHITE, ball)
    pygame.draw.aaline(win, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

    score_text = font.render(f"{score_left}   {score_right}", True, WHITE)
    win.blit(score_text, (WIDTH//2 - 50, 20))

    pygame.display.flip()

pygame.quit()
