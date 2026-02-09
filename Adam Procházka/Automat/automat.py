# Importy
import pygame
import random
import sys
import json
import os
from pathlib import Path

def base_dir() -> Path:
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent

        for candidate in [
            exe_dir / "_internal",
            exe_dir
        ]:
            if (candidate / "assets").exists():
                return candidate

        return exe_dir

    return Path(__file__).resolve().parent

BASE = base_dir()

def load_image(rel_path):
    return pygame.image.load(BASE / rel_path)

pygame.init()
#Rozlišení
screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
WIDTH, HEIGHT = screen.get_size()
#Název
pygame.display.set_caption("PixSpin")
#Ikona
icon = load_image("assets/images/icon.png")
SlotsBorder = load_image("assets/images/SlotsBorder.png")
logo = load_image("assets/images/PixSpin.png").convert_alpha()
pygame.display.set_icon(icon)

# ========== Barvy ==========
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# ========== Definice Symbolů ==========
symbols = {
    "apple": load_image("assets/images/apple.png"),
    "banana": load_image("assets/images/banana.png"),
    "cherry": load_image("assets/images/cherry.png"),
    "grape": load_image("assets/images/grape.png"),
    "lemon": load_image("assets/images/lemon.png"),
    "orange": load_image("assets/images/orange.png"),
    "watermelon": load_image("assets/images/watermelon.png"),
    "pear": load_image("assets/images/pear.png"),
    "strawberry": load_image("assets/images/strawberry.png"),
    "pomelo": load_image("assets/images/pomelo.png"),
    "seven": load_image("assets/images/seven.png"),
    "shiny_apple": load_image("assets/images/shiny_apple.png"),
    "shiny_banana": load_image("assets/images/shiny_banana.png"),
    "shiny_cherry": load_image("assets/images/shiny_cherry.png"),
    "shiny_grape": load_image("assets/images/shiny_grape.png"),
    "shiny_lemon": load_image("assets/images/shiny_lemon.png"),
    "shiny_orange": load_image("assets/images/shiny_orange.png"),
    "shiny_watermelon": load_image("assets/images/shiny_watermelon.png"),
    "shiny_pear": load_image("assets/images/shiny_pear.png"),
    "shiny_strawberry": load_image("assets/images/shiny_strawberry.png"),
    "shiny_pomelo": load_image("assets/images/shiny_pomelo.png"),
    "golden_seven": load_image("assets/images/golden_seven.png"),
    "reroll": load_image("assets/images/reroll.png"),
    "mirror": load_image("assets/images/mirror.png"),
    "diamond": load_image("assets/images/diamond.png"),
    "bomb": load_image("assets/images/bomb.png"),
    "star": load_image("assets/images/star.png")
}

# Nepatří mezi symboly
chest_image = load_image("assets/images/chest.png").convert_alpha()
chip_icon = load_image("assets/images/chip.png")
chip_icon_small = pygame.transform.scale(chip_icon, (35, 35))

mirror_img = load_image("assets/images/mirror.png").convert_alpha()
diamond_img = load_image("assets/images/diamond.png").convert_alpha()
golden_seven_img = load_image("assets/images/golden_seven.png").convert_alpha()
chest_img = load_image("assets/images/chest.png").convert_alpha()
reroll_img = load_image("assets/images/reroll.png").convert_alpha()
bomb_img = load_image("assets/images/bomb.png").convert_alpha()
star_img = load_image("assets/images/star.png").convert_alpha()
shiny_orange_img = load_image("assets/images/shiny_orange.png").convert_alpha()

# Zmenšení obrázků na rozumnou velikost (např. 64x64 px)
mirror_img = pygame.transform.scale(mirror_img, (100, 100))
diamond_img = pygame.transform.scale(diamond_img, (100, 100))
golden_seven_img = pygame.transform.scale(golden_seven_img, (100, 100))
chest_img = pygame.transform.scale(chest_img, (100, 100))
reroll_img = pygame.transform.scale(reroll_img, (100, 100))
bomb_img = pygame.transform.scale(bomb_img, (100, 100))
star_img = pygame.transform.scale(star_img, (100, 100))
shiny_orange_img = pygame.transform.scale(shiny_orange_img, (100, 100))

# ========== Hodnoty Symbolů ==========
symbol_names = list(symbols.keys())
symbol_values = {
    "strawberry": 5,
    "apple": 10,
    "banana": 20,
    "cherry": 30,
    "grape": 15,
    "pomelo": 15,
    "lemon": 25,
    "orange": 35,
    "watermelon": 40,
    "pear": 45,
    "seven": 60,
    "shiny_strawberry": 10,
    "shiny_apple": 20,
    "shiny_banana": 40,
    "shiny_cherry": 60,
    "shiny_grape": 30,
    "shiny_pomelo": 30,
    "shiny_lemon": 50,
    "shiny_orange": 70,
    "shiny_watermelon": 80,
    "shiny_pear": 90,
    "golden_seven": 335,
    "reroll": 0,
    "mirror": 0,
    "diamond": 0,
    "bomb": 0
}

# ========== Rarita Symbolů ==========
symbol_rarity = { #čím nižší, tím vzácnejší
    "strawberry": 500,
    "apple": 490,
    "banana": 480,
    "cherry": 470,
    "grape": 460,
    "pomelo": 450,
    "lemon": 440,
    "orange": 430,
    "watermelon": 420,
    "pear": 410,
    "seven": 400,
    "shiny_strawberry": 50,
    "shiny_apple": 49,
    "shiny_banana": 48,
    "shiny_cherry": 47,
    "shiny_grape": 46,
    "shiny_pomelo": 45,
    "shiny_lemon": 44,
    "shiny_orange": 42,
    "shiny_watermelon": 40,
    "shiny_pear": 38,
    "golden_seven": 30,
    "reroll": 150,
    "mirror": 150,
    "diamond": 150,
    "bomb": 150
}

# ---------- Fonty ----------
FONT_PATH = str(BASE / "assets/fonts/VT323.ttf")

font = pygame.font.Font(FONT_PATH, 36)
big_font = pygame.font.Font(FONT_PATH, 48)
bigg_font = pygame.font.Font(FONT_PATH, 72)
bold_font = pygame.font.Font(FONT_PATH, 72)
desc_font = pygame.font.Font(FONT_PATH, 48)
title_font = pygame.font.Font(FONT_PATH, 96)
icon_font = pygame.font.Font(FONT_PATH, 36)
text_font = pygame.font.Font(FONT_PATH, 50)
# ========== Proměnné  ==========
slots = ["apple", "banana", "cherry"]           # Seznam aktuálních symbolů
result_text = ""                                # Text pro zobrazení výsledku
total_score = 0                                 # Celkové skóre hráče
spins_left = 10                                 # Počet zbývajících spinů (zde je nelze přidávat)
spins_used = 0                                  # Počet použitých spinů
show_bonus_spin = False                         # Zda se má zobrazit animace bonusu
show_bonus_spin_amount = [1]                    # Kolik spinů se má ukázat
bonus_timer = 0                                 # Timer pro animaci bonusu
game_state = "menu"                             # Stav Hry
score_multiplier = 1                            # Aktivní násobič skóre
pending_multiplier = 1                          # Násobič čekající na další kolo
bomb_penalty_next_spin = False                  # Jestli má být příští výhra záporná
chip_count = 0                                  # aktuální počet

leaderboard_file = os.path.join("data", "leaderboard.json")           # Leaderboard File
stats_file = os.path.join("data", "stats.json")                       # Stats File
leaderboard = []
player_name = ""

flash_timer = 0                                 # Animace
shake_timer = 0
shake_offset = (0, 0)
reel_anim_timer = 0
animating = False

help_page = 0
offset_surface = pygame.Surface((WIDTH, HEIGHT))# MEGA DŮLEŽITÝ

stats = {
    "total_spins": 0,
    "jackpots": 0,
    "max_spins": 0,
    "lowest_score": None,
    "max_score_spin": 0,
    "current_jackpot_streak": 0,
    "max_jackpot_streak": 0
}

# ========== Definice Funkcí (poznat podle názvu) ==========
def load_stats():
    global stats
    if os.path.exists(stats_file):
        try:
            with open(stats_file, "r") as f:
                stats = json.load(f)
        except json.JSONDecodeError:
            pass

def save_stats():
    with open(stats_file, "w") as f:
        json.dump(stats, f)

def load_leaderboard():
    global leaderboard
    if os.path.exists(leaderboard_file):
        try:
            with open(leaderboard_file, "r", encoding="utf-8") as f:
                leaderboard = json.load(f)
        except json.JSONDecodeError:
            leaderboard = []
    else:
        leaderboard = []

def save_leaderboard():
    with open(leaderboard_file, "w") as f:
        json.dump(leaderboard, f)

def spin():
    weighted_symbols = []
    for symbol, rarity in symbol_rarity.items():
        weighted_symbols.extend([symbol] * rarity)

    base = random.choice(weighted_symbols)

    # # ========== Šance na jednotlivé kombinace ==========
    roll = random.random()
    if roll < 0.35:                                         # 35 % šance na jackpot
        return [base, base, base]
    elif roll < 0.80:                                       # dalších 45 % šance na dvě stejné (jakoby 35+45=80)
        second = base
        third = random.choice(weighted_symbols)
        if third == base:
            third = random.choice([s for s in weighted_symbols if s != base])
        return [base, second, third]
    else:                                                   # zbylých 20 % šance na NIC
        options = [s for s in weighted_symbols if s != base]
        second = random.choice(options)
        third = random.choice([s for s in options if s != second])
        return [base, second, third]

# ============================== Nejdůležitější Definice na kalkulaci skóre ==============================

def calculate_score(slots): # Ano píše to že je tam víc než je povoleno ale funguje to
    global result_text, spins_left, show_bonus_spin, bonus_timer, flash_timer, shake_timer, stats, score_multiplier
    global score_multiplier, pending_multiplier, bomb_penalty_next_spin

    # ---------- BOMB ----------
    if slots.count("bomb") == 3:                            # 3x bomb
        bomb_penalty_next_spin = True
        result_text = "3x bomb | Další skóre záporné!"
        return 0
    if slots.count("bomb") == 2:                            # 2x bomb
        result_text = "2x bomb | NIC"
        return 0

    # ========== Multipliery + Zápory ==========
    # Použije pending_multiplier jako násobič, pak se resetuje
    score_multiplier = pending_multiplier
    pending_multiplier = 1

    # Pokud je aktivní bomba, invertuje skóre
    invert_score = bomb_penalty_next_spin
    bomb_penalty_next_spin = False

    # Nejprve ignoruje diamanty a zjistí, jestli jsou 3 stejné nebo 2 stejné jiné symboly
    filtered_slots = [s for s in slots if s != "diamond"]

    # ----------REROLL ----------
    if slots.count("reroll") == 3:                          # 3x reroll
        result_text = "3x reroll | +3 zatočení"
        spins_left += 3
        show_bonus_spin = True
        bonus_timer = pygame.time.get_ticks()
        show_bonus_spin_amount[0] = 3
        return 0
    elif slots.count("reroll") == 2:                        # 2x reroll
        result_text = "2x reroll | +2 zatočení"
        spins_left += 2
        show_bonus_spin = True
        bonus_timer = pygame.time.get_ticks()
        show_bonus_spin_amount[0] = 2
        return 0

    # ---------- MIRROR ----------
    mirror_count = slots.count("mirror") # Mirrors
    non_mirrors = [s for s in slots if s != "mirror"] # Ostatní symboly

    if mirror_count == 3:                                   # 3x mirror
        result_text = "3x mirror | NIC"
        return 0
    elif mirror_count == 2 and len(non_mirrors) == 1:
        symbol = non_mirrors[0]
        if symbol in symbol_values:
            value = symbol_values[symbol] * 3 * score_multiplier
            result_text = f"2x mirror + {symbol} | +{value}"
            spins_left += 1
            show_bonus_spin = True
            bonus_timer = pygame.time.get_ticks()
            flash_timer = pygame.time.get_ticks()
            shake_timer = pygame.time.get_ticks()
            stats["jackpots"] += 1
            return value
    elif mirror_count == 1 and len(non_mirrors) == 2:       # 2x mirror
        if non_mirrors[0] == non_mirrors[1]:
            symbol = non_mirrors[0]
            value = symbol_values[symbol] * 3 * score_multiplier
            result_text = f"mirror + 2x {symbol} | +{value}"
            spins_left += 1
            show_bonus_spin = True
            bonus_timer = pygame.time.get_ticks()
            flash_timer = pygame.time.get_ticks()
            shake_timer = pygame.time.get_ticks()
            stats["jackpots"] += 1
            return value
        else:
            sym1, sym2 = non_mirrors                        # 1x mirror
            higher = sym1 if symbol_values[sym1] >= symbol_values[sym2] else sym2
            value = symbol_values[higher] * 2 * score_multiplier
            result_text = f"mirror + {higher} | +{value}"
            return value

    # ========== JACKPOT ==========
    if len(filtered_slots) == 3 and filtered_slots.count(filtered_slots[0]) == 3:
        symbol = filtered_slots[0]
        if symbol in symbol_values:
            base_value = symbol_values[symbol] * 3                      # Sečtou se všechny symboly (symbol 3x)
            value = base_value * 5 * score_multiplier                   # Vynásobí se součet symbolů x5 a poté podle multiplieru
            if invert_score:                                            # Ztráta pokud přetím bomby
                value = -value
                result_text = f"3× {symbol.upper()} | ZTRÁTA {value}"
            else:                                                       # Normální jackpot
                result_text = f"3× {symbol} | JACKPOT! +{value}"
                spins_left += 1                                         # Přičtení spinu po jackpotu
                show_bonus_spin = True
                bonus_timer = pygame.time.get_ticks()
            flash_timer = pygame.time.get_ticks()
            shake_timer = pygame.time.get_ticks()
            stats["jackpots"] += 1                                      # Přičítání do statů
            stats['current_jackpot_streak'] += 1
            if stats['current_jackpot_streak'] > stats['max_jackpot_streak']:          # Nejvíce jackpotů v kuse (stat)
                stats['max_jackpot_streak'] = stats['current_jackpot_streak']
            if stats.get("max_score_spin") is None or value > stats["max_score_spin"]: # Pokud největší skóre (stat)
                stats["max_score_spin"] = value
            return value
    else:
        stats['current_jackpot_streak'] = 0                             # Pokud nepadne jackpot tak reset statu na 0 

    # ========== 2 Stejné Symboly ==========
    for symbol in symbol_names:
        if filtered_slots.count(symbol) == 2 and symbol in symbol_values:
            value = symbol_values[symbol] * 2 * score_multiplier        # Sečtou se oba symboly a případně se vynásobí multiplierem
            result_text = f"2× {symbol} | +{value}"
            if invert_score:
                value = -value
                result_text = f"2× {symbol.upper()} | ZTRÁTA {value}"
            return value
        
    # ---------- DIAMOND ----------
    diamond_count = slots.count("diamond")
    if diamond_count >= 2:                                  # 2x+ diamond = multiplier podle počtu
        pending_multiplier = min(diamond_count, 3)
        result_text = f"{diamond_count}x diamant | Násobič x{pending_multiplier} příště"
        return 0
    elif diamond_count == 1:                                # 1x diamond
        result_text = "1x diamant | NIC"
        return 0

    result_text = "NIC"                                     # Pokud nepadne vůbec nic
    score_multiplier = 1
    return 0

# ============================== Konec definice kalkulace skóre ==============================

# ========== Button Designs ==========
# ---------- Button Design (velké - hrát, leaderboard, zpět) ----------
def draw_button(text, x, y, width, height, callback, surface=screen):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    rect = pygame.Rect(x, y, width, height)

    if rect.collidepoint(mouse):
        color = DARK_GRAY
        if click[0] == 1:
            if callback:  # ✅ VOLÁME callback JEN pokud existuje
                callback()
    else:
        color = GRAY

    pygame.draw.rect(surface, color, (x, y, width, height), border_radius=8)
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 2, border_radius=8)

    font = pygame.font.Font(str(BASE / "assets/fonts/VT323.ttf"), 64)
    text_render = font.render(text, True, WHITE)
    surface.blit(text_render, (x + width // 2 - text_render.get_width() // 2,
                               y + height // 2 - text_render.get_height() // 2))
    
    return rect

# ---------- Button Design (malé - credits, stats) ----------
def draw_icon_button(x, y, width, height, callback, surface=None, label="", action=None):
    if surface is None:
        surface = screen  # fallback

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, width, height)

    # Hover efekt: změní barvu pozadí
    color = GRAY if rect.collidepoint(mouse) else DARK_GRAY

    # Vykreslí pozadí + okraj
    pygame.draw.rect(surface, color, rect, border_radius=5)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=5)

    # Vykreslí text (ikonu)
    if label:
        label_text = icon_font.render(label, True, WHITE)
        surface.blit(label_text, (
            x + (width - label_text.get_width()) // 2,
            y + (height - label_text.get_height()) // 2
        ))

    # Reakce na kliknutí
    if rect.collidepoint(mouse) and click[0] == 1:
        pygame.time.delay(200)
        if callback:
            callback()
        if action:
            action()

# ========== Nastavení začátku hry ==========
def go_to_name_input():
    global game_state, total_score, spins_left, result_text, player_name, spins_used
    total_score = 0                                        # Počáteční Skóre
    spins_left = 10                                         # Počáteční počet spinů
    spins_used = 0
    result_text = ""
    player_name = ""
    game_state = "name_input"

def start_game():
    global game_state
    game_state = "game"

def restart_game():
    global game_state
    game_state = "menu"

def quit_game():
    pygame.quit()
    sys.exit()

def show_leaderboard():
    global game_state
    game_state = "leaderboard"

def show_stats():
    global game_state
    game_state = "stats"

def show_credits():
    global game_state
    game_state = "credits"

def show_help():
    global game_state
    game_state = "help"

def change_help_page(direction):
    global help_page
    max_page = (len(help_lines) - 1) // lines_per_page
    help_page = max(0, min(help_page + direction, max_page))

# ---------- Bonus (Bedny) ----------
def start_bonus_phase():
    global game_state, bonus_chests, bonus_selected, bonus_multiplier
    game_state = "bonus"
    multipliers = [1]*3 + [2]*2 + [3]                       # Počet jednotlivých multiplierů (v [] je multiplier a bez závorky je kolikrát tam je)
    random.shuffle(multipliers)
    bonus_chests = [{"x": 110 + (i % 3) * 130, "y": 100 + (i // 3) * 120, "value": multipliers[i], "revealed": False} for i in range(6)]
    bonus_selected = False
    bonus_multiplier = 1

load_leaderboard()
load_stats()
running = True
input_active = False

clock = pygame.time.Clock()

# ============================== Loop Hry ==============================
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_stats()
            running = False

        # ==== NAME INPUT State (I nastavení ovádání pro psaní jména) ====
        elif game_state == "name_input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name.strip():
                    game_state = "game"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 10:
                    player_name += event.unicode

        # ==== SPIN State (lze točit myškou i spacem ) ====
        elif game_state == "game":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Levé tlačítko
                mx, my = pygame.mouse.get_pos()
#                if (not exchange_button_rect.collidepoint((mx, my)) and
#                    not upgrade_button_rect.collidepoint((mx, my))):
#                    # Klik mimo tlačítka = spusť spin
            if not animating and spins_left > 0:                            #PRO UPGRADY PAK ODSUNOUT TO IF
                animating = True
                reel_anim_timer = pygame.time.get_ticks()

#            if event.type == pygame.MOUSEBUTTONDOWN:
#                if exchange_button_rect.collidepoint(pygame.mouse.get_pos()):
#                    if total_score >= 100:
#                        total_score -= 100
#                        chip_count += 1
#                elif upgrade_button_rect.collidepoint((mx, my)):
#                    game_state = "upgrades"

#        elif game_state == "upgrades":
#            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#                mx, my = pygame.mouse.get_pos()
#                # Klik na "Zpět"
#                if back_button_rect.collidepoint((mx, my)):
#                    game_state = "game"  # Návrat do hry
#                # Klik na upgrade
#                if upgrade1_rect.collidepoint((mx, my)):
#                    if chip_count >= 5:
#                        chip_count -= 5
#                    # Zde aktivuj vylepšení, např. score_multiplier += 1
#                    print("Upgrade koupen!")
#                else:
#                    print("Nemáš dost chipů.")

        # ==== SHOW RESULT State (lze pokračovat myškou i spacem) ====
        elif game_state == "show_result":
            if (event.type == pygame.MOUSEBUTTONDOWN or
                (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)):
                start_bonus_phase()

        # ==== BONUS State ====
        elif game_state == "bonus":
            if event.type == pygame.MOUSEBUTTONDOWN and not bonus_selected:
                mx, my = pygame.mouse.get_pos()
                for chest in bonus_chests:
                    rect = pygame.Rect(chest["x"], chest["y"], 80, 80)
                    if rect.collidepoint(mx, my):
                        chest["revealed"] = True
                        bonus_multiplier = chest["value"]
                        bonus_selected = True
                        total_score *= bonus_multiplier             # Celkové skóre se násobí multiplierem z bedny

                        # Spustíme časovač pro postup do výsledků
                        pygame.time.set_timer(pygame.USEREVENT + 1, 1500) # Poslední číslo je prodleva v ms

        if event.type == pygame.USEREVENT + 1:
        # ==== Uložení Statistik ====
            stats["total_spins"] += spins_used
            stats["max_spins"] = max(stats["max_spins"], spins_used)
            if stats["lowest_score"] is None or total_score < stats["lowest_score"]:
                stats["lowest_score"] = total_score
            save_stats()

            # ==== Uložení do leaderboardu ====
            leaderboard.append({"name": player_name, "score": total_score})
            leaderboard.sort(key=lambda x: x["score"], reverse=True)
            leaderboard = leaderboard[:10]  # udrž 10 nejlepších
            save_leaderboard()

            game_state = "end"
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # vypneme časovač (idk co to je?)

    screen.fill(BLACK)
    offset_surface.fill(BLACK)

    if animating:
        now = pygame.time.get_ticks()
        if now - reel_anim_timer < 1000:
            slots = [random.choice(symbol_names) for _ in range(3)]
        else:
            slots = spin()                                  # tohle kontroluje zbývající počet spinů 
            gained = calculate_score(slots)                 
            total_score += gained
            spins_left -= 1
            spins_used += 1
            if spins_left == 0:                             # pokud spinů zbývá 0 tak to skončí
                game_state = "show_result"
            animating = False

    # ==== Animace u jackpotu ====
    if flash_timer and pygame.time.get_ticks() - flash_timer < 150:
        offset_surface.fill(WHITE)
    elif shake_timer and pygame.time.get_ticks() - shake_timer < 300:
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        shake_offset = (offset_x, offset_y)
    else:
        shake_offset = (0, 0)

    offset_surface.fill(BLACK)

    # ==== Menu Design ====
    if game_state == "menu":
        logo_width = 600  # uprav podle chuti
        logo_height = int(logo.get_height() * (logo_width / logo.get_width()))
        logo_scaled = pygame.transform.scale(logo, (logo_width, logo_height))

        center_y = HEIGHT // 2 - 300  # posuň výš/dolů podle potřeby
        offset_surface.blit(
            logo_scaled,
            (WIDTH // 2 - logo_scaled.get_width() // 2, center_y)
        )

        draw_button("Hrát", WIDTH // 2 - 250, 500, 500, 65, go_to_name_input, surface=offset_surface)            # Hrát Button
        draw_button("Leaderboard", WIDTH // 2 - 250, 570, 500, 65, show_leaderboard, surface=offset_surface)     # Leaderboard Button
        draw_button("Konec", WIDTH // 2 - 250, 640, 500, 65, quit_game, surface=offset_surface)                  # Quit Button
        draw_icon_button(WIDTH - 60, 10, 60, 60, show_stats, label="S", surface=offset_surface)                  # Stats Button
        draw_icon_button(WIDTH - 130, 10, 60, 60, show_credits, label="C", surface=offset_surface)                # Credits Button
        draw_icon_button(WIDTH - 200, 10, 60, 60, show_help, label="H", surface=offset_surface)                  # Help Button

        screen.blit(offset_surface, (0, 0))

    # ==== Name Input Design ====
    elif game_state == "name_input":
        info_text = "Zadej jméno a stiskni ENTER:"
        cursor = "|" if pygame.time.get_ticks() % 1000 < 500 else ""  # blikající kurzor
        name_display_text = player_name + cursor

        # Větší fonty pro fullscreen
        info = big_font.render(info_text, True, WHITE)
        name_display = title_font.render(name_display_text, True, YELLOW)

        # Výpočet pozic pro zarovnání na střed
        info_x = WIDTH // 2 - info.get_width() // 2
        name_x = WIDTH // 2 - name_display.get_width() // 2

        # Výškově zarovnáno kolem středu obrazovky
        center_y = HEIGHT // 2
        offset_surface.blit(info, (info_x, center_y - 80))
        offset_surface.blit(name_display, (name_x, center_y))

    # ==== Spin Design ====

    elif game_state in ("game", "show_result"):
        slot_size = 360
        slot_spacing = 58
        n = len(slots)

        total_slot_width = n * slot_size + (n - 1) * slot_spacing

        # 1) umístění rámečku = vystředit podle obrázku rámečku
        border_x = WIDTH // 2 - SlotsBorder.get_width() // 2
        border_y = HEIGHT // 2 - SlotsBorder.get_height() // 2

        offset_surface.blit(SlotsBorder, (border_x, border_y))

        inset_x = (SlotsBorder.get_width() - total_slot_width) // 2
        inset_y = (SlotsBorder.get_height() - slot_size) // 2

        slot_start_x = border_x + inset_x
        slot_y = border_y + inset_y + 20

        # Velikost tlačítek
        button_width = 380
        button_height = 70
        button_margin = 10  # mezera mezi tlačítky

        # Umístění pravý dolní roh
        button_x = WIDTH - button_width - 20  # 20 px odsazení od pravého okraje
        button_y = HEIGHT - (button_height * 2 + button_margin) - 20  # 20 px od spodního okraje
        
#        # Uložíme Rect pro klikání
#        exchange_button_rect = draw_button("Vyměnit (100 za 1 chip)", button_x, button_y, button_width, button_height, None, surface=offset_surface)
#        upgrade_button_rect = draw_button("Upgrady", button_x, button_y + button_height + button_margin, button_width, button_height, None, surface=offset_surface)

#        draw_button("Vyměnit (100 za 1 chip) ", button_x, button_y, button_width, button_height, None, surface=offset_surface)
#        draw_button("Upgrady", button_x, button_y + button_height + button_margin, button_width, button_height, None, surface=offset_surface)

        # Vykreslení slotů
        for i in range(n):
            x = slot_start_x + i * (slot_size + slot_spacing)
            y = slot_y

            sym_name = slots[i]
            img = pygame.transform.scale(symbols[sym_name], (slot_size, slot_size))
            offset_surface.blit(img, (x, y))

        # === Chip count design ===
#        display_x = WIDTH - 80
#        display_y = HEIGHT - 215

        # === Text s počtem chipů ===
#        text = big_font.render(str(chip_count), True, (255, 255, 255))

        # === Vykreslit text ===
#        offset_surface.blit(text, (display_x, display_y))

        # === Vykreslit ikonu chipu vedle textu ===
#        img_x = display_x + text.get_width() + 5
#        img_y = display_y + (text.get_height() - chip_icon_small.get_height()) // 2
#        offset_surface.blit(chip_icon_small, (img_x, img_y))

        # === Text: Výsledek === (výš nad sloty)
        text = bigg_font.render(result_text, True, WHITE)
        offset_surface.blit(text, (WIDTH // 2 - text.get_width() // 2, slot_y - 255))

        # === Skóre (větší a blíž ke slotům) ===
        score_text = big_font.render("Skóre: " + str(total_score), True, YELLOW)
        offset_surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, slot_y + slot_size + 90))

        # === Zbývající zatočení (pod skórem) ===
        spins_color = RED if spins_left <= 3 else WHITE
        spins_text = big_font.render("Zbývající zatočení: " + str(spins_left), True, spins_color)
        offset_surface.blit(spins_text, (WIDTH // 2 - spins_text.get_width() // 2, slot_y + slot_size + 140))

        # === Bonus spin (bliknutí +X) ===
        if show_bonus_spin:
            now = pygame.time.get_ticks()
            if now - bonus_timer < 1000:
                bonus_text = big_font.render(f"+{show_bonus_spin_amount[0]}", True, GREEN)
                offset_surface.blit(bonus_text, (
                    WIDTH // 2 + spins_text.get_width() // 2 + 20,
                    slot_y + slot_size + 140
                ))
            else:
                show_bonus_spin = False
                show_bonus_spin_amount[0] = 1

        # === Když dojdou spiny ===
        if game_state == "show_result":
            prompt = big_font.render("Klikni pro bonus", True, WHITE)
            offset_surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, slot_y + slot_size + 200))

    # ==== Upgrades Design ====
    elif game_state == "upgrades":
        # Pozadí
        offset_surface.fill((30, 30, 30))

        # Nadpis
        title = title_font.render("Upgrady", True, WHITE)
        offset_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Ukázka upgrade tlačítka
        upgrade1_rect = pygame.Rect(WIDTH // 2 - 150, 150, 300, 80)
        pygame.draw.rect(offset_surface, GRAY, upgrade1_rect, border_radius=8)
        pygame.draw.rect(offset_surface, WHITE, upgrade1_rect, 2, border_radius=8)
        upgrade_text = font.render("Lepší výhry (5 chipů)", True, WHITE)
        offset_surface.blit(upgrade_text, (
            upgrade1_rect.centerx - upgrade_text.get_width() // 2,
            upgrade1_rect.centery - upgrade_text.get_height() // 2))

        # Tlačítko zpět
        back_button_rect = pygame.Rect(20, HEIGHT - 90, 200, 60)
        pygame.draw.rect(offset_surface, GRAY, back_button_rect, border_radius=8)
        pygame.draw.rect(offset_surface, WHITE, back_button_rect, 2, border_radius=8)
        back_text = font.render("Zpět", True, WHITE)
        offset_surface.blit(back_text,(
            back_button_rect.centerx - back_text.get_width() // 2,
            back_button_rect.centery - back_text.get_height() // 2))
    
    # ==== Bonus Design ====
    elif game_state == "bonus":
        title_text = title_font.render("Vyber si bednu", True, YELLOW)
        offset_surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 300))
        chest_size = 120  # zvětšené truhly pro fullscreen
        spacing = 60
        total_width = len(bonus_chests) * chest_size + (len(bonus_chests) - 1) * spacing
        start_x = WIDTH // 2 - total_width // 2
        chest_y = HEIGHT // 2 - chest_size // 2

        for i, chest in enumerate(bonus_chests):
            chest["x"] = start_x + i * (chest_size + spacing)
            chest["y"] = chest_y
            offset_surface.blit(pygame.transform.scale(chest_image, (chest_size, chest_size)), (chest["x"], chest["y"]))
            if chest["revealed"]:
                val = font.render(f"{chest['value']}x", True, GREEN)
                text_x = chest["x"] + chest_size // 2 - val.get_width() // 2
                text_y = chest["y"] + chest_size + 10
                offset_surface.blit(val, (text_x, text_y))

    # ==== End Design ====
    elif game_state == "end":
        end_text = title_font.render("KONEC HRY", True, YELLOW)
        final_score = big_font.render(f"Celkové skóre: {total_score}", True, WHITE)
        total_spins = big_font.render(f"Celkový počet zatočení: {spins_used}", True, WHITE)

        y_start = HEIGHT // 2 - 100
        spacing = 50

        offset_surface.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, y_start))
        offset_surface.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, y_start + spacing + 80))
        offset_surface.blit(total_spins, (WIDTH // 2 - total_spins.get_width() // 2, y_start + spacing * 2 +80))

        button_width = 300
        button_height = 70
        draw_button(
            "Zpět do menu",
            WIDTH // 2 - button_width // 2,
            y_start + spacing * 3 + 324,
            button_width,
            button_height,
            restart_game,
            surface=offset_surface
        )

    # ==== Leaderboard Design ====
    elif game_state == "leaderboard":
        title = title_font.render("LEADERBOARD", True, YELLOW)  # Stejný font jako u stats
        offset_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        line_spacing = 50
        start_y = 250

        # Vytvoř 10 slotů – buď hráč, nebo prázdné
        lines = []
        for i in range(10):
            if i < len(leaderboard):
                entry = leaderboard[i]
                lines.append((f"{i+1}. {entry['name']}", f"{entry['score']}"))          # Připrav si data jako páry: [(jméno, skóre), ...]
            else:
                lines.append((f"{i+1}. ---", "---"))

        # Render textů
        rendered_labels = [text_font.render(label, True, WHITE) for label, _ in lines]
        rendered_values = [text_font.render(value, True, WHITE) for _, value in lines]

        # Vypočítej zarovnání
        max_label_width = max(lbl.get_width() for lbl in rendered_labels) if rendered_labels else 0
        max_value_width = max(val.get_width() for val in rendered_values) if rendered_values else 0

        label_value_gap = 100
        total_width = max_label_width + label_value_gap + max_value_width
        start_x = WIDTH // 2 - total_width // 2

        for i, (label, value) in enumerate(lines):
                y = start_y + i * line_spacing
                label_surf = text_font.render(label, True, WHITE)
                value_surf = text_font.render(value, True, WHITE)
                label_x = start_x
                value_x = start_x + max_label_width + label_value_gap + (max_value_width - value_surf.get_width())
                offset_surface.blit(label_surf, (label_x, y))
                offset_surface.blit(value_surf, (value_x, y))

        draw_button("Zpět", WIDTH // 2 - 500 // 2, 380 + len(lines) * line_spacing + 40,
                    500, 65, restart_game, surface=offset_surface)


    # ==== Stats Design ====
    elif game_state == "stats":
        title = title_font.render("STATISTIKY", True, YELLOW)                                         # Nadpis
        offset_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        line_spacing = 60

        lines = [
            ("Celkový počet zatočení:", f"{stats['total_spins']}"),
            ("Nejvíce zatočení v jedné hře:", f"{stats['max_spins']}"),
            ("Počet jackpotů:", f"{stats['jackpots']}"),
            ("Nejvíc jackpotů v kuse:", f"{stats['max_jackpot_streak']}"),
            ("Největší skóre z jednoho zatočení:", f"{stats['max_score_spin']}"),
            ("Nejnižší skóre:", f"{stats['lowest_score'] if stats['lowest_score'] is not None else 'N/A'}")
        ]

        # Render textů
        rendered_labels = [text_font.render(label, True, WHITE) for label, _ in lines]
        rendered_values = [text_font.render(value, True, WHITE) for _, value in lines]

        # Vypočítej největší šířku pro zarovnání
        max_label_width = max(lbl.get_width() for lbl in rendered_labels)
        max_value_width = max(val.get_width() for val in rendered_values)

        label_value_gap = 100
        total_width = max_label_width + label_value_gap + max_value_width

        start_x = WIDTH // 2 - total_width // 2
        start_y = 260  # nebo 270 či 280 – podle potřeby

        for i, (lbl_surf, val_surf) in enumerate(zip(rendered_labels, rendered_values)):
            y = start_y + i * line_spacing
            label_x = start_x
            value_x = start_x + max_label_width + label_value_gap + (max_value_width - val_surf.get_width())
            offset_surface.blit(lbl_surf, (label_x, y))
            offset_surface.blit(val_surf, (value_x, y))


        draw_button("Zpět", WIDTH //2 - 500 // 2, 520 + len(lines) * line_spacing + 40,
                    500, 65, restart_game, surface=offset_surface)

    # ==== Credits Design ====
    elif game_state == "credits":
        title = title_font.render("CREDITS", True, YELLOW)
        offset_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        credits_lines = [
        "AUTOŘI",
        "Adam Procházka (Main)",
        "Tomáš Pulchart",
        "Bára Lapuníková",
        "Patrik Salaba",
        "",
        "TESTEŘI",
        "Vojtěch Procházka",
        "Lukáš Čarada",
        "William Nobilis",
        "Helena Procházková",
        "",
        "Veliká pomoc od ChatGPT",
        "Vytvořeno 12.5.2025"
        ]

        line_spacing = 45
        total_height = len(credits_lines) * line_spacing
        start_y = HEIGHT // 2 - total_height // 2 + 20

        for i, line in enumerate(credits_lines):
            txt = font.render(line, True, WHITE)
            offset_surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, start_y + i * line_spacing))

        draw_button("Zpět", WIDTH // 2 - 230, start_y + total_height + 40, 480, 70, restart_game, surface=offset_surface)

    # ==== Help Design ====
    elif game_state == "help":
        title = title_font.render("NÁPOVĚDA", True, YELLOW)
        offset_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        help_lines = [
        ("Diamond", "Násobí skóre dalšího kola"),
        ("Golden Seven", "Největší skóre ze hry (až +5000)"),
        ("Chests", "Možnost znásobit své skóre"),
        ("Mirror", "Může nahradit většinu symbolů"),
        ("Reroll", "Vrací zpět několik zatočení"),
        ("Bomb", "V dalším kole se skóre odečítá"),
        ("Star", "PLACEHOLDER"),
        ("Shiny Symboly", "Dávají 2x víc skóre než normální")
        ]

        symbol_images = {
        "Diamond": diamond_img,
        "Golden Seven": golden_seven_img,
        "Chests": chest_img,
        "Mirror": mirror_img,
        "Reroll": reroll_img,
        "Bomb": bomb_img,
        "Star": star_img,
        "Shiny Symboly": shiny_orange_img
        }

        lines_per_page = 4
        line_spacing = 140  # ⬅️ Zvětšený vertikální prostor mezi položkami
        total_pages = (len(help_lines) + lines_per_page - 1) // lines_per_page
        start_line = help_page * lines_per_page
        end_line = start_line + lines_per_page

        clip_rect = pygame.Rect(80, 120, WIDTH - 160, lines_per_page * line_spacing + 80)
        help_surface = pygame.Surface((clip_rect.width, clip_rect.height), pygame.SRCALPHA)
        help_surface.fill((0, 0, 0, 0))

        # Horní a dolní mezera (červená a modrá čára)
        top_y = 15
        bottom_y = 650
        total_space = bottom_y - top_y

        # Počet mezer = počet položek + 1 (mezera i nahoře a dole)
        num_items = lines_per_page
        spacing = total_space // (num_items + 1)  # tedy 440 // 5 = 88 px

        for i, (title_line, desc_line) in enumerate(help_lines[start_line:end_line]):
            y_base = top_y + (i + 1) * spacing  # (i + 1), protože chceme mezeru i nahoře

             # Texty
            title_txt = bold_font.render(title_line, True, WHITE)
            desc_txt = desc_font.render(desc_line, True, WHITE)

            # Šířka obou textů
            max_text_width = max(title_txt.get_width(), desc_txt.get_width())
            text_x = clip_rect.width // 2 - max_text_width // 2  # zarovnání na střed v rámci clip_rect

            text_x = 470
            help_surface.blit(title_txt, (text_x, y_base))
            help_surface.blit(desc_txt, (text_x, y_base + 60))

            # Ikona zarovnaná doprava
            if title_line in symbol_images:
                img = symbol_images[title_line]
                img_x = 1200
                img_y = y_base + 10
                help_surface.blit(img, (img_x, img_y))

        offset_surface.blit(help_surface, (clip_rect.x, clip_rect.y))

        # ===== Tlačítka dole =====
        button_y = clip_rect.y + clip_rect.height + 155
        button_width = 480
        button_height = 70

        def previous_page():
            global help_page
            if help_page > 0:
                help_page -= 1

        def next_page():
            global help_page
            if (help_page + 1) * lines_per_page < len(help_lines):
                help_page += 1

        # Tlačítko Zpět na střed
        draw_button("Zpět", WIDTH // 2 - button_width // 2, button_y, button_width, button_height, restart_game, surface=offset_surface)

        # Šipky těsně vedle tlačítka
        arrow_margin = 40
        draw_button("<", WIDTH // 2 - button_width // 2 - arrow_margin - 50, button_y, 80, button_height, previous_page, surface=offset_surface)
        draw_button(">", WIDTH // 2 + button_width // 2 + arrow_margin - 30, button_y, 80, button_height, next_page, surface=offset_surface)

        # Číslo stránky
        page_text = font.render(f"Strana {help_page + 1} / {total_pages}", True, WHITE)
        offset_surface.blit(page_text, (WIDTH // 2 - page_text.get_width() // 2, button_y - 40))

    screen.blit(offset_surface, shake_offset)

    # ==== Jackpot effect ====
    if flash_timer and pygame.time.get_ticks() - flash_timer < 200:                                 # Jak dlouho to bude v ms (asi?)
        flash_overlay = pygame.Surface((WIDTH, HEIGHT))
        flash_overlay.set_alpha(80)                                                                 # Průhlednost
        flash_overlay.fill(WHITE)                                                                   # Barva flashe
        screen.blit(flash_overlay, (0, 0))

    pygame.display.flip()

pygame.quit()
sys.exit()