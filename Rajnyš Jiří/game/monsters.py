import pygame, math, time, random

class Monster:
    def __init__(self, typ, x, y):
        typ = {'red': 'shark', 'purple': 'octopus', 'orange': 'jelly'}.get(typ, typ)
        self.typ = typ
        self.x = x
        self.y = y
        # visual size vs hitbox: render size large, hitbox small
        base = 40
        if typ == 'shark':
            mult = 4
        else:
            mult = 2
        # render size (visual)
        self.render_w = base * mult
        self.render_h = base * mult
        # hitbox size (used for collisions) small
        self.w = base
        self.h = base

        self.aggro_range = 500
        self.attack_range = 40

        self.vy = 0.0
        self.state = "idle"
        self.state_timer = time.time()
        self.speed = {
            "octopus": 0.9,
            "shark": 1.6,
            "jelly": 0.56,
        }.get(typ, 0.9)

        self.dir = random.choice([-1, 1])
        self.origin_x = x
        self.origin_y = y
        self.active = True
        self.still_until = 0
        try:
            import time as _time
            self.spawned_at = _time.time()
        except Exception:
            self.spawned_at = 0

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def distance_to_player(self, player):
        return math.hypot(
            (player.world_x - self.x),
            (player.world_y - self.y)
        )

    def update(self, player):
        now = time.time()

        if now < self.still_until:
            return

        dist = self.distance_to_player(player)

        # ---- PŘECHODY STAVŮ ----
        if self.state in ("idle", "patrol") and dist < self.aggro_range:
            if self.state != 'alert':
                self.state = 'alert'
                self.state_timer = now

        if self.state == 'alert' and now - self.state_timer > 0.5:
            self.state = 'chase'

        if self.state == "chase" and dist < self.attack_range:
            self.state = "attack"
            self.state_timer = now

        if self.state == "attack" and now - self.state_timer > 0.4:
            self.state = "cooldown"
            self.state_timer = now

        if self.state == "cooldown" and now - self.state_timer > 0.8:
            self.state = "patrol"

        # ---- CHOVÁNÍ ----
        if self.state == "idle":
            self.y += math.sin(now * 2) * 0.2

        elif self.state == "patrol":
            self.x += self.dir * self.speed * 0.6
            self.y += math.sin(now * 1.5) * 0.4
            if abs(self.x - self.origin_x) > 80:
                self.dir *= -1

        elif self.state == "chase":
            dx = player.world_x - self.x
            dy = player.world_y - self.y
            dist = math.hypot(dx, dy) or 1
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

        elif self.state == "attack":
            if self.typ == "shark":
                player.oxygen -= 0.4
            elif self.typ == "jelly":
                player.stunned_until = time.time() + 2
            elif self.typ == "octopus":
                pass  # QTE 

        elif self.state == "cooldown":
            pass
