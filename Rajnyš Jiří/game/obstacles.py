import random
import pygame
from .settings import SCREEN_W, START_SPAWN_Y, SEA_LEVEL_Y, PIXELS_PER_METER


class InfiniteCliffs:
    """Líný generátor útesů/překážek.

    Udržuje interní seznamy pro `obstacles`, `left_profile` a `right_profile`
    a generuje další segmenty na vyžádání pomocí `ensure_to(depth_px)`.
    """

    def __init__(self):
        self._obstacles = []
        self.left_profile = []
        self.right_profile = []
        self._y = START_SPAWN_Y - 200
        self._init_done = False
        self.base_left_x = 200
        self.base_right_x = SCREEN_W - self.base_left_x
        self._generate_to(SEA_LEVEL_Y)

    def __iter__(self):
        return iter(self._obstacles)

    def __len__(self):
        return len(self._obstacles)

    def __getitem__(self, idx):
        return self._obstacles[idx]

    def append(self, item):
        self._obstacles.append(item)

    def _generate_to(self, depth_px):
        """Interní generátor: rozšíří profily a překážky dokud y >= depth_px."""
        if not self.left_profile:
            y = self._y
            while y < SEA_LEVEL_Y:
                lx = self.base_left_x + random.randint(-10, 10)
                rx = self.base_right_x + random.randint(-10, 10)
                self.left_profile.append((lx, y))
                self.right_profile.append((rx, y))
                y += 90
            self._y = y
            cliff_h = 200
            cliff_w = 120
            self._obstacles.append(pygame.Rect(self.base_left_x, SEA_LEVEL_Y - cliff_h, cliff_w, cliff_h))
            self._obstacles.append(pygame.Rect(self.base_right_x - cliff_w, SEA_LEVEL_Y - cliff_h, cliff_w, cliff_h))

        left_prev = self.left_profile[-1][0]
        right_prev = self.right_profile[-1][0]

        step = 160
        y = self._y

        while y < depth_px:
            left_new = left_prev + random.randint(-25, 25)
            right_new = right_prev + random.randint(-25, 25)

            left_new = max(-200, min(200, left_new))
            right_new = max(SCREEN_W - 180, min(SCREEN_W + 200, right_new))

            self.left_profile.append((left_new, y))
            self.right_profile.append((right_new, y))

            block_h = random.randint(130, 240)
            block_w_l = random.randint(60, 120)
            block_w_r = random.randint(60, 120)

            self._obstacles.append(pygame.Rect(left_new, y + random.randint(-10, 15), block_w_l, block_h))
            self._obstacles.append(pygame.Rect(right_new - block_w_r, y + random.randint(-10, 15), block_w_r, block_h))

            left_prev = left_new
            right_prev = right_new
            y += step + random.randint(-30, 40)

        self._y = y

    def ensure_to(self, depth_px):
        """Veřejné API: zajistí, že mapa je vygenerovaná až do `depth_px` (v pixelech)."""
        target = max(depth_px, SEA_LEVEL_Y)
        if target > self._y:
            self._generate_to(target)


def generate_side_cliffs():
    """Fabrika vracející línou instanci `InfiniteCliffs`."""
    return InfiniteCliffs()
