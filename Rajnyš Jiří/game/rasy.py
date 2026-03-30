import random, time, pygame, math
from .settings import PIXELS_PER_METER, SEA_LEVEL_Y, SCREEN_W, MAP_DEPTH_METERS
class AlgaeBlob:
    def __init__(self, x, y, color, phase, intensity):
        self.x = x
        self.y = y
        self.color = color
        self.phase = phase          # pulzační fáze
        self.intensity = intensity  # síla svitu
        self.size = random.choice([1, 2, 2, 3])

def generate_bioluminescence(count=200, min_depth_m=40, max_depth_m=MAP_DEPTH_METERS):
    blobs = []

    min_y = SEA_LEVEL_Y + int(min_depth_m * PIXELS_PER_METER)
    max_y = SEA_LEVEL_Y + int(max_depth_m * PIXELS_PER_METER)
    if max_y <= min_y:
        max_y = min_y + int(500 * PIXELS_PER_METER)

    for _ in range(count):
        # preferovat hlubší vrstvy
        y = random.randint(min_y, max_y)
        depth_factor = (y - min_y) / (max_y - min_y)
        # mění barvu podle hloubky
        if depth_factor < 0.33:
            color = (70, 230, 255)
        elif depth_factor < 0.66:
            color = (0, 255, 180)
        else:
            color = (0, 200, 160)
        x = random.randint(40, SCREEN_W - 40)
        # náhodná pulzační fáze
        phase = random.random() * 6.28
        # síla světla
        intensity = 0.6 + depth_factor * 0.6
        blobs.append(AlgaeBlob(x, y, color, phase, intensity))

    return blobs

def draw_bioluminescence(surface, camera_y, blobs, dt):
    h = surface.get_height()
    for b in blobs:
        sy = int(b.y - camera_y + h//2)
        if sy < -10 or sy > h + 10:
            continue

        # aktualizace fáze pulzování
        b.phase += dt * (0.9 + b.intensity * 0.5)
        pulse = (0.5 + 0.5 * math.sin(b.phase)) ** 1.4
        alpha = int(70 + 160 * pulse * b.intensity)
        alpha = max(0, min(255, alpha))
        # světelný kruh
        col = (b.color[0], b.color[1], b.color[2], alpha)
        size = b.size
        surf = pygame.Surface((size*2+2, size*2+2), pygame.SRCALPHA)
        pygame.draw.circle(surf, col, (size+1, size+1), size)
        sx = int(b.x)
        surface.blit(surf, (sx - (size+1), sy - (size+1)))
