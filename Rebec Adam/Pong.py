import pygame
import random

# Inicializace Pygame
pygame.init()

# Nastavení okna
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong – Myš vs Bot")

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Herní objekty
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 15

# Hráč
left_paddle = pygame.Rect(50, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
# Pravá pálka (bot)
right_paddle = pygame.Rect(WIDTH - 60, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
# Míček
ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

ball_speed_x = random.choice([-5, 5])
ball_speed_y = random.choice([-3, 3])

# Skóre
score_left = 0
score_right = 0
font = pygame.font.SysFont("consolas", 40)

# Hlavní smyčka
clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Ovládání levé pálky myší
    mouse_y = pygame.mouse.get_pos()[1]
    left_paddle.centery = mouse_y
    if left_paddle.top < 0:
        left_paddle.top = 0
    if left_paddle.bottom > HEIGHT:
        left_paddle.bottom = HEIGHT

    # Pohyb bota
    # Bot sleduje míček s malým zpožděním
    if right_paddle.centery < ball.centery - 15:
        right_paddle.centery += 4
    elif right_paddle.centery > ball.centery + 15:
        right_paddle.centery -= 4

    # Omezení pohybu bota v okně
    if right_paddle.top < 0:
        right_paddle.top = 0
    if right_paddle.bottom > HEIGHT:
        right_paddle.bottom = HEIGHT

    # Pohyb míčku
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Kolize s okraji
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1

    # Kolize s pálkami
    if ball.colliderect(left_paddle):
        ball_speed_x *= -1
        ball.x = left_paddle.right  # předejde "prolomení" pálky
    if ball.colliderect(right_paddle):
        ball_speed_x *= -1
        ball.x = right_paddle.left - BALL_SIZE

    # skórování vlevo nebo vpravo
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

    # Vykreslení
    win.fill(BLACK)
    pygame.draw.rect(win, WHITE, left_paddle)
    pygame.draw.rect(win, WHITE, right_paddle)
    pygame.draw.ellipse(win, WHITE, ball)
    pygame.draw.aaline(win, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

    # Skóre
    score_text = font.render(f"{score_left}   {score_right}", True, WHITE)
    win.blit(score_text, (WIDTH//2 - 50, 20))

    pygame.display.flip()

pygame.quit()
