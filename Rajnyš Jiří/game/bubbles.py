import random, math
from .settings import PIXELS_PER_METER, SCREEN_W

class AirBubble:
    def __init__(self, x, y, r):
        self.x = x; self.y = y; self.r = r

def generate_bubbles():
    from .settings import MAP_DEPTH_METERS
    bubbles = []
    y_m = 15
    while y_m < MAP_DEPTH_METERS:
        # menší rozsah -> častější skupiny bublin
        spacing_m = random.randint(20, 250)
        y_m += spacing_m
        if y_m >= MAP_DEPTH_METERS:
            break
        y_px = int(y_m * PIXELS_PER_METER)
        # objeví 1-3 bubliny na pásmo 
        for _ in range(random.randint(1, 3)):
            x = random.randint(40, SCREEN_W - 40)
            jitter = random.randint(-max(1, int(spacing_m * PIXELS_PER_METER // 4)), max(1, int(spacing_m * PIXELS_PER_METER // 4)))
            r = random.randint(30, 120)
            bubbles.append(AirBubble(x, y_px + jitter, r))
    return bubbles

def inside_bubble(player, bubble):
    px = player.world_x + player.w/2
    py = player.world_y + player.h/2
    return math.hypot(px-bubble.x, py-bubble.y) < bubble.r
