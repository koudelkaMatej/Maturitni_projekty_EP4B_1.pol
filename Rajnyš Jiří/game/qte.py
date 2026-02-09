import random, pygame
from .settings import QTE_LENGTH, QTE_TIME_PER_KEY_MS, OCTOPUS_O2_PENALTY

class QTE:
    def __init__(self):
        self.active = False; self.seq = []; self.index = 0; self.started_at = 0
    def start(self):
        self.seq = [random.choice(['up','down','left','right']) for _ in range(QTE_LENGTH)]
        self.index = 0; self.started_at = pygame.time.get_ticks(); self.active = True
    def handle_key(self, key, player, disable_callback=None):
        if not self.active: return
        mapping = {pygame.K_UP:'up', pygame.K_DOWN:'down', pygame.K_LEFT:'left', pygame.K_RIGHT:'right'}
        cur = self.seq[self.index]
        if key in mapping and mapping[key] == cur:
            self.index += 1; self.started_at = pygame.time.get_ticks()
            if self.index >= len(self.seq):
                self.active = False
                if disable_callback: disable_callback()
        else:
            player.oxygen -= OCTOPUS_O2_PENALTY; self.active = False
    def check_timeout(self, player):
        if not self.active: return
        if pygame.time.get_ticks() - self.started_at > QTE_TIME_PER_KEY_MS:
            player.oxygen -= OCTOPUS_O2_PENALTY; self.active = False
