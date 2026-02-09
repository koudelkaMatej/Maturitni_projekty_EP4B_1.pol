import time, pygame
from .settings import PLAYER_SIZE, OXYGEN_MAX, SEA_LEVEL_Y

class Player:
    def __init__(self, x, y):
        self.w, self.h = PLAYER_SIZE
        self.world_x = float(x)
        self.world_y = float(y)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.stunned_until = 0.0
        self.oxygen = OXYGEN_MAX
        self.max_depth_reached = int(self.world_y)

    def rect(self):
        return pygame.Rect(int(self.world_x), int(self.world_y), self.w, self.h)

    def apply_impulse(self, ix, iy):
        self.velocity_x += ix
        self.velocity_y += iy

    def update(self):
        # rychlost
        self.world_x += self.velocity_x
        self.world_y += self.velocity_y
        # treni/spomaleni
        if self.world_y < SEA_LEVEL_Y:
            self.velocity_x *= 0.92
        else:
            self.velocity_x *= 0.995
        self.velocity_y *= 0.999
        if abs(self.velocity_x) < 1e-4: self.velocity_x = 0.0
        if abs(self.velocity_y) < 1e-4: self.velocity_y = 0.0
        # record max hloubku
        self.max_depth_reached = max(self.max_depth_reached, int(self.world_y))
