import pygame
import os
from .settings import PLAYER_SIZE, OXYGEN_MAX, SEA_LEVEL_Y

class Player:
    """Třída reprezentující hráče ve hře Potápěč.
    
    Spravuje pozici, rychlost, kyslík, animace a stav hráče.
    """
    def __init__(self, x, y):
        self.w, self.h = PLAYER_SIZE
        self.world_x = float(x)
        self.world_y = float(y)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.stunned_until = 0.0
        self.oxygen = OXYGEN_MAX
        self.max_depth_reached = int(self.world_y)
        
        # Animation system
        self.animation_frames = {}
        self.current_animation = 'idle'
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.animation_speeds = {
            'idle': 0.3,
            'jump': 0.2,  
            'swim': 0.12,
            'drown': 0.2,
            'electrocuted': 0.09,
            'eaten_by_shark': 0.5
        }
        self.animation_loops = {
            'idle': True,
            'jump': False,
            'swim': True,
            'drown': False,
            'electrocuted': True,
            'eaten_by_shark': False
        }
        self.facing_right = True
        self.death_cause = None 
        self.was_jumping_on_surface = False  
        self.aiming_straight_down = False  
        self.load_animations()

    def load_animations(self):
        """Načte animační snímky z assets/diver/"""
        base_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'diver')
        
        # Definuje animační sekvence s aktualizovanými názvy souborů - zahrnuje všechny možné snímky
        animations = {
            'idle': ['idle-removebg-preview.png'],
            'jump': [f'jump{i}-removebg-preview.png' for i in range(1, 7)],  # skok1 až skok6
            'swim': [f'swim{i}-removebg-preview.png' for i in range(1, 8)],  # plavání1 až plavání7
            'drown': [f'drown{i}-removebg-preview.png' for i in range(1, 4)],  # utonutí1 až utonutí3
            'electrocuted': [f'el{i}-removebg-preview.png' for i in range(1, 4)],  # ele1 až ele3
            'eaten_by_shark': ['sharkd-removebg-preview.png']
        }
        
        # Zkusí načíst animace, s fallbackem na původní názvy pokud nové neexistují
        for anim_name, files in animations.items():
            self.animation_frames[anim_name] = []
            for filename in files:
                filepath = os.path.join(base_path, filename)
                if os.path.exists(filepath):
                    try:
                        img = pygame.image.load(filepath).convert_alpha()
                        self.animation_frames[anim_name].append(img)
                    except Exception as e:
                        # Pokud pygame není ještě inicializováno, načteme později
                        if "video mode" in str(e).lower():
                            self.animation_frames[anim_name] = []  # Vymazat a označit pro lazy loading
                            break
                        else:
                            print(f"Failed to load {filepath}: {e}")
                else:
                    # Zkusit původní název souboru bez přípony
                    original_name = filename.replace('-removebg-preview.png', '.png')
                    original_path = os.path.join(base_path, original_name)
                    if os.path.exists(original_path):
                        try:
                            img = pygame.image.load(original_path).convert_alpha()
                            self.animation_frames[anim_name].append(img)
                        except Exception as e:
                            if "video mode" in str(e).lower():
                                self.animation_frames[anim_name] = []
                                break
                            else:
                                print(f"Failed to load {original_path}: {e}")
                    else:
                        print(f"Animation file not found: {filepath} or {original_path}")

    def ensure_animations_loaded(self):
        """Zajistí načtení animací (volat po plné inicializaci pygame)"""
        if not self.animation_frames or not any(self.animation_frames.values()):
            self.load_animations()

    def set_animation(self, animation_name):
        """Nastaví aktuální animaci"""
        if animation_name in self.animation_frames and animation_name != self.current_animation:
            self.current_animation = animation_name
            self.animation_frame = 0
            self.animation_timer = 0.0

    def update_animation(self, dt):
        """Aktualizuje snímek animace"""
        if self.current_animation not in self.animation_frames:
            return
            
        frames = self.animation_frames[self.current_animation]
        if len(frames) <= 1:
            return
            
        speed = self.animation_speeds.get(self.current_animation, 0.15)
        self.animation_timer += dt
        if self.animation_timer >= speed:
            self.animation_timer = 0.0
            if self.animation_loops.get(self.current_animation, True):
                self.animation_frame = (self.animation_frame + 1) % len(frames)
            else:
                if self.animation_frame < len(frames) - 1:
                    self.animation_frame += 1

    def get_current_frame(self):
        """Získá aktuální povrch snímku animace"""
        self.ensure_animations_loaded()
        if self.current_animation not in self.animation_frames:
            return None
        frames = self.animation_frames[self.current_animation]
        if not frames:
            return None
        return frames[self.animation_frame]

    def rect(self):
        return pygame.Rect(int(self.world_x), int(self.world_y), self.w, self.h)

    def apply_impulse(self, ix, iy):
        self.velocity_x += ix
        self.velocity_y += iy

    def update(self):
        # rychlost
        # aktualizace pozice se provádí ve fyzice hry
        # treni/zpomaleni
        if self.world_y < SEA_LEVEL_Y:
            self.velocity_x *= 0.92
        else:
            self.velocity_x *= 0.995
        self.velocity_y *= 0.999
        if abs(self.velocity_x) < 1e-4: self.velocity_x = 0.0
        if abs(self.velocity_y) < 1e-4: self.velocity_y = 0.0
        
        # Aktualizuje směr pohledu na základě rychlosti
        if self.velocity_x > 0.1:
            self.facing_right = True
        elif self.velocity_x < -0.1:
            self.facing_right = False
            
        # Aktualizuje příznak skoku
        if self.world_y <= SEA_LEVEL_Y:
            if self.velocity_y < -1.0:
                self.was_jumping_on_surface = True
        else:
            self.was_jumping_on_surface = False
            self.aiming_straight_down = False  # Resetovat při vstupu do vody
            
        # Určí animaci na základě stavu
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Prioritní pořadí: sněden žralokem > utonutí > elektrifikace > skok > plavání > nečinnost
        if self.death_cause == 'shark' and self.oxygen <= 5:
            self.set_animation('eaten_by_shark')
        elif self.oxygen <= 0 or (self.death_cause == 'octopus' and self.oxygen <= 5):
            self.set_animation('drown')
        elif self.death_cause == 'jelly' and self.oxygen <= 5:
            self.set_animation('electrocuted')
        elif self.stunned_until > current_time and self.death_cause == 'jelly':
            self.set_animation('electrocuted')
        # animace skoku pouze nad vodou (včetně skoku na povrchu), nikdy pod vodou
        elif (self.world_y <= SEA_LEVEL_Y and (self.velocity_y < -1.0 or self.velocity_y > 1.0 or self.was_jumping_on_surface)):
            self.set_animation('jump')
        elif self.world_y > SEA_LEVEL_Y and self.aiming_straight_down:  # pod vodou a míří přímo dolů
            self.set_animation('idle')
        elif self.world_y > SEA_LEVEL_Y:  # pod vodou
            self.set_animation('swim')
        elif self.world_y <= SEA_LEVEL_Y and abs(self.velocity_x) <= 0.5 and abs(self.velocity_y) <= 1.0 and not self.was_jumping_on_surface:  # na povrchu, nepohybuje se horizontálně, nízká vertikální rychlost (přibližně stojí na pevném), a neskáče
            self.set_animation('idle')
        else:
            self.set_animation('idle')  # výchozí
            
        # Aktualizuje animaci
        self.update_animation(1/60.0)  # 60 FPS
        
        # zaznamená maximální hloubku
        self.max_depth_reached = max(self.max_depth_reached, int(self.world_y))
