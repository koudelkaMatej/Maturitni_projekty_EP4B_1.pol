import pygame, math, time, random, os

class Monster:
    def __init__(self, typ, x, y):
        typ = {'red': 'shark', 'purple': 'octopus', 'orange': 'jelly'}.get(typ, typ)
        self.typ = typ
        self.x = x
        self.y = y
        # vizuální velikost vs hitbox: render velikost velká, hitbox malá
        base = 40
        if typ == 'shark':
            mult = 2
        else:
            mult = 2
        # render velikost (vizuální)
        self.render_w = base * mult
        self.render_h = base * mult
        # velikost hitboxu (používá se pro kolize) malá
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
            
        # Systém animací
        self.animation_frames = {}
        self.current_animation = 'idle'
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.animation_speeds = {
            'idle': 0.3,  # 300ms
            'swim': 0.12,  # 120ms
            'bite': 0.09,  # 90ms
            'grab': 0.12,  # 120ms for grab
            'swim_charging': 0.15,  # 150ms
            'shock': 0.3,  # 300ms
            'stun': 0.3  # 300ms
        }
        self.animation_loops = {
            'idle': True,
            'swim': True,
            'bite': False,  # kousnutí se neopakuje
            'grab': False,  # uchopení se neopakuje
            'swim_charging': True,
            'shock': True,
            'stun': True
        }
        self.facing_right = self.dir > 0
        self.load_animations()

    def load_animations(self):
        """Načte animační snímky z assets/monsters/"""
        base_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'monsters')
        
        if self.typ == 'jelly':
            animations = {
                'idle': ['jelly idle.png'],
                'swim': ['jelly_swim1.png', 'jelly_swim2.png'],
                'swim_charging': ['jelly_shock_charge.png'],
                'shock': ['jelly_shock.png'],
                'stun': ['jelly_shock.png']
            }
        elif self.typ == 'octopus':
            animations = {
                'idle': ['octopus.png'],
                'swim': ['octo_swim1.png', 'octo_swim2.png'],
                'grab': ['octo_grab1.png', 'octo_grab2.png']
            }
        elif self.typ == 'shark':
            animations = {
                'idle': ['shark idle.png'],
                'swim': [f'shark swim {i}.png' for i in range(1, 5)],  # žralok plave 1 až 4
                'bite': [f'shark bite {i}.png' for i in range(1, 4)]  # žralok kouše 1 až 3
            }
        else:
            # Záloha pro ostatní typy
            animations = {
                'idle': [f'{self.typ}.png'] if os.path.exists(os.path.join(base_path, f'{self.typ}.png')) else [],
                'swim': [f'{self.typ}.png'] if os.path.exists(os.path.join(base_path, f'{self.typ}.png')) else []
            }
        
        for anim_name, files in animations.items():
            self.animation_frames[anim_name] = []
            for filename in files:
                filepath = os.path.join(base_path, filename)
                if os.path.exists(filepath):
                    try:
                        img = pygame.image.load(filepath).convert_alpha()
                        self.animation_frames[anim_name].append(img)
                    except Exception as e:
                        print(f"Failed to load {filepath}: {e}")
                else:
                    print(f"Animation file not found: {filepath}")

    def ensure_animations_loaded(self):
        """Ensure animations are loaded (call after pygame is fully initialized)"""
        if not self.animation_frames or not any(self.animation_frames.values()):
            self.load_animations()

    def set_animation(self, animation_name):
        """Set the current animation"""
        if animation_name in self.animation_frames and animation_name != self.current_animation:
            self.current_animation = animation_name
            self.animation_frame = 0
            self.animation_timer = 0.0

    def update_animation(self, dt):
        """Update animation frame"""
        if self.current_animation not in self.animation_frames:
            return
            
        frames = self.animation_frames[self.current_animation]
        if len(frames) <= 1:
            return
            
        speed = self.animation_speeds.get(self.current_animation, 0.2)
        self.animation_timer += dt
        if self.animation_timer >= speed:
            self.animation_timer = 0.0
            if self.animation_loops.get(self.current_animation, True):
                self.animation_frame = (self.animation_frame + 1) % len(frames)
            else:
                if self.animation_frame < len(frames) - 1:
                    self.animation_frame += 1

    def get_current_frame(self):
        """Get the current animation frame surface"""
        self.ensure_animations_loaded()
        if self.current_animation not in self.animation_frames:
            return None
        frames = self.animation_frames[self.current_animation]
        if not frames:
            return None
        return frames[self.animation_frame]

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

         # Vždy čelem k hráči
        dx = player.world_x - self.x
        self.facing_right = dx > 0

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

        # ---- ANIMACE ----
        # Nastavení animace na základě stavu s větším množstvím detailů
        if self.state == "idle":
            self.set_animation('idle')
        elif self.state == "patrol":
            self.set_animation('swim')
        elif self.state == "alert":
            # Rychlé blikání mezi idle a plaváním pro stav pohotovosti
            if int(now * 4) % 2 == 0:
                self.set_animation('swim')
            else:
                self.set_animation('idle')
        elif self.state == "chase":
            self.set_animation('swim')
        elif self.state == "attack":
            if self.typ == "jelly":
                # Medúza: nabití -> šok -> omračující sekvence
                attack_time = now - self.state_timer
                if attack_time < 0.2:
                    self.set_animation('swim_charging')
                elif attack_time < 0.4:
                    self.set_animation('shock')
                else:
                    self.set_animation('stun')
            elif self.typ == "octopus":
                self.set_animation('grab')
            elif self.typ == "shark":
                self.set_animation('bite')
            else:
                self.set_animation('attack')
        elif self.state == "cooldown":
            self.set_animation('idle') 
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
            
        # Update animation
        self.update_animation(1/60.0)  # 60 FPS
